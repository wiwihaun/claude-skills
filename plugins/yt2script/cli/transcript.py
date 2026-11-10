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
# After ASCII punctuation a Latin word still needs its space: "plan. Well", not "plan.Well".
ASCII_PUNCT_END = re.compile(r'[.!?,;:…]$')
LATIN_START = re.compile(r'^[A-Za-z0-9"\'(\[]')


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
    """VTT -> [{start, end, text, lines}], tags and entities already gone."""
    cues = []
    with open(path, encoding='utf-8-sig') as f:
        lines = f.read().splitlines()
    state = {'start': None, 'end': None, 'buf': []}

    def flush():
        if state['start'] is None: return
        rows = [re.sub(r'\s+', ' ', html.unescape(TAG.sub('', l))).strip() for l in state['buf']]
        rows = [r for r in rows if r]
        txt = ' '.join(rows)
        if txt:
            cues.append({'start': state['start'], 'end': state['end'], 'text': txt, 'lines': rows})

    for ln in lines:
        m = TS.search(ln)
        if m:
            flush()
            state.update(start=secs(*m.groups()[:4]), end=secs(*m.groups()[4:]), buf=[])
        elif state['start'] is not None:
            if ln == '':
                flush(); state.update(start=None, buf=[])
            elif ln.strip() == '':
                # A line holding only a space is payload, not the end of the cue.
                # YouTube's ASR tracks open every cue with one; ending the cue
                # there threw away the first sentence of the video.
                continue
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

    Two shapes occur. Roll-up captions show two lines per cue, the first being
    the previous cue's last line, with a 10 ms cue of the finished line between
    them; a line carried over from the cue just before is dropped. Older tracks
    grew one line word by word; the prefix rules below fold those.
    """
    out = []
    prev = []
    for c in cues:
        rows = c.get('lines') or [c['text']]
        fresh = [r for r in rows if r not in prev]
        prev = rows
        if not fresh:                     # nothing new: a carried-over line
            if out: out[-1]['end'] = c['end']
            continue
        c = dict(c, text=' '.join(fresh), lines=fresh)
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


SENT_END = re.compile(r'[。！？!?.…][」』"\'）)]?$')


def segment(cues, gap=3.0, maxchars=400, hardmax=600):
    """Break on a pause of >= gap seconds, or after about maxchars.

    Past maxchars, wait for a cue that ends a sentence before breaking, so a
    paragraph does not stop at "what's going to happen" and resume at "in terms
    of the future." Unpunctuated tracks never end a sentence; hardmax caps them.
    """
    segs, cur, n = [], [], 0
    for i, c in enumerate(cues):
        long_enough = n >= maxchars and (SENT_END.search(cues[i-1]['text']) or n >= hardmax)
        if cur and (c['start'] - cues[i-1]['end'] >= gap or long_enough):
            segs.append(cur); cur, n = [], 0
        cur.append(c); n += cjk_len(c['text'])
    if cur: segs.append(cur)
    return segs


def join(seg):
    """Concatenate cues verbatim.

    Chinese after punctuation joins directly (。 needs no space). Latin text
    always gets one: after ASCII punctuation the next English word still needs
    its space, or 'plan.Well' and 'begin,and' come out glued. Nothing is added
    but whitespace, so the cue-survival check cannot see this either way.
    """
    out = ''
    for c in seg:
        if not out:
            out = c['text']
        elif PUNCT_END.search(out) and not (ASCII_PUNCT_END.search(out)
                                            and LATIN_START.match(c['text'])):
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
