#!/usr/bin/env python3
"""VTT -> Markdown transcript.

Five steps, in order: strip tags, unescape entities, (optionally) repair
YouTube's scrolling auto-captions, segment on pauses, convert script
direction only when the text really is simplified. Nothing is rewritten:
no word is added, removed or reworded anywhere in here.
"""
import html, re, os, sys, glob

TAG = re.compile(r'<[^>]*>')            # all HTML tags incl. <00:00:12.500>, <c>, </c>
TS  = re.compile(r'(\d+):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d+):(\d{2}):(\d{2})[.,](\d{3})')
PUNCT_END = re.compile(r'[　-〿＀-￯.!?,;:…]$')


def _opencc():
    """opencc, from the venv or a user-site install, or None."""
    try:
        import opencc; return opencc
    except ImportError:
        pass
    for d in glob.glob(os.path.expanduser('~/Library/Python/3.*/lib/python/site-packages')):
        if d not in sys.path: sys.path.append(d)
    try:
        import opencc; return opencc
    except ImportError:
        return None


def secs(h, m, s, ms):
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0


def parse(path):
    """VTT -> [{start, end, text}], tags and entities already gone."""
    cues = []
    with open(path, encoding='utf-8-sig') as f:
        lines = f.read().splitlines()
    state = {'start': None, 'end': None, 'buf': []}

    def flush():
        if state['start'] is None: return
        txt = TAG.sub('', ' '.join(state['buf']).strip())
        txt = html.unescape(txt)
        txt = re.sub(r'\s+', ' ', txt).strip()
        if txt:
            cues.append({'start': state['start'], 'end': state['end'], 'text': txt})

    for ln in lines:
        m = TS.search(ln)
        if m:
            flush()
            state.update(start=secs(*m.groups()[:4]), end=secs(*m.groups()[4:]), buf=[])
        elif state['start'] is not None:
            if ln.strip() == '':
                flush(); state.update(start=None, buf=[])
            elif (not re.match(r'^(WEBVTT|Kind:|Language:|NOTE|STYLE|REGION)', ln)
                  and not ln.strip().isdigit()):
                state['buf'].append(ln.strip())
    flush()
    return cues


def dedup(cues):
    """Repair scrolling auto-captions, where each cue restates the last one.

    Only for YouTube's AUTO captions. Human subtitles and Whisper output have
    no such structure, and running this over them deletes genuine repeated
    lines -- in a comedy skit, saying it twice IS the joke.
    """
    out = []
    for c in cues:
        if not out:
            out.append(c); continue
        p = out[-1]
        a, b = p['text'], c['text']
        if a == b:                        # identical -> drop
            p['end'] = c['end']; continue
        if b.startswith(a):               # prefix growth -> supersede
            p['text'] = b; p['end'] = c['end']; continue
        if a.startswith(b):               # already contained -> drop
            p['end'] = c['end']; continue
        out.append(c)
    return out


def cjk_len(s):
    return len(re.sub(r'\s+', '', s))


def segment(cues, gap=3.0, maxchars=400):
    """Break on a pause of >= gap seconds, or after about maxchars."""
    segs, cur, n = [], [], 0
    for i, c in enumerate(cues):
        if cur and (c['start'] - cues[i-1]['end'] >= gap or n >= maxchars):
            segs.append(cur); cur, n = [], 0
        cur.append(c); n += cjk_len(c['text'])
    if cur: segs.append(cur)
    return segs


def join(seg):
    """Concatenate cues verbatim; a space only where the source had no punctuation."""
    out = ''
    for c in seg:
        if not out:
            out = c['text']
        elif PUNCT_END.search(out):
            out += c['text']
        else:
            out += ' ' + c['text']
    return re.sub(r'[ \t]+', ' ', out).strip()


def pick_conversion(text):
    """(convert_fn, mode, trad_only, simp_only).

    OpenCC's s2* configs assume simplified input. Run them over text that is
    already traditional and characters valid in both (了 才 吃 台) get pushed
    to the wrong variant, so convert only when simplified markers dominate.
    """
    cc = _opencc()
    if cc is None:
        return (lambda x: x), 'none (opencc unavailable)', 0, 0
    t2s, s2t = cc.OpenCC('t2s'), cc.OpenCC('s2tw')
    trad_only = sum(1 for a, b in zip(text, t2s.convert(text)) if a != b)
    simp_only = sum(1 for a, b in zip(text, s2t.convert(text)) if a != b)
    if simp_only > trad_only:
        return s2t.convert, 's2tw (simplified source detected)', trad_only, simp_only
    return (lambda x: x), 'none (source already traditional)', trad_only, simp_only


def mmss(s):
    return f"{int(s)//60}:{int(s)%60:02d}"


def safe_name(title):
    return re.sub(r'[/\\:*?"<>|]', '_', title).strip() or 'transcript'


def verify(vtt_path, out_text, convert):
    """Every source cue must survive into the output. Returns (total, missing)."""
    norm = lambda s: re.sub(r'\s+', '', s)
    body = norm(out_text)
    total = missing = 0
    for c in parse(vtt_path):
        t = norm(convert(c['text']))
        if not t: continue
        total += 1
        if t not in body: missing += 1
    return total, missing


def build(vtt_path, title, url, outdir, source='auto', timestamps=True):
    """VTT -> markdown file(s). Returns a report dict."""
    cues_raw = parse(vtt_path)
    cues = dedup(cues_raw) if source == 'auto' else cues_raw
    segs = segment(cues)
    paras = [(s[0]['start'], join(s)) for s in segs]
    raw = '\n'.join(p for _, p in paras)

    convert, mode, trad_only, simp_only = pick_conversion(raw)
    title_c = convert(title)
    paras_c = [(t, convert(p)) for t, p in paras]

    os.makedirs(outdir, exist_ok=True)
    base = safe_name(title_c)
    hdr = f"# {title_c}\n\n來源：{url}\n\n---\n\n"

    plain = os.path.join(outdir, f"{base}.md")
    body = hdr + '\n\n'.join(p for _, p in paras_c) + '\n'
    with open(plain, 'w', encoding='utf-8') as f:
        f.write(body)
    files = [plain]

    if timestamps:
        stamp = os.path.join(outdir, f"{base}（時間戳版）.md")
        with open(stamp, 'w', encoding='utf-8') as f:
            f.write(hdr + '\n\n'.join(f"**[{mmss(t)}]** {p}" for t, p in paras_c) + '\n')
        files.append(stamp)

    total, missing = verify(vtt_path, body, convert)
    return {
        'source': source, 'cues_raw': len(cues_raw), 'cues_kept': len(cues),
        'segments': len(segs), 'chars': cjk_len(raw),
        'trad_only': trad_only, 'simp_only': simp_only, 'conversion': mode,
        'verified_total': total, 'verified_missing': missing, 'files': files,
    }


if __name__ == '__main__':
    a = sys.argv[1:]
    r = build(a[0], a[1], a[2], a[3], a[4] if len(a) > 4 else 'auto')
    print(' '.join(f'{k}={v}' for k, v in r.items() if k != 'files'))
    for f in r['files']: print(f)
