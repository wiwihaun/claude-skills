#!/usr/bin/env python3
"""yt2script -- YouTube link -> Traditional Chinese verbatim transcript.

Order of preference, stopping at the first that yields text:
  1. human-written subtitles   (best quality)
  2. native automatic captions (machine-translated xx-zh tracks are refused)
  3. local Whisper transcription (no network beyond fetching the audio)
"""
import argparse, os, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# The 3 GB model cache lives OUTSIDE the plugin directory on purpose: a plugin
# update moves ${CLAUDE_PLUGIN_ROOT}, and re-downloading it would be a rude
# surprise. Point YT2SCRIPT_HOME somewhere else to move it.
DATA = os.environ.get('YT2SCRIPT_HOME') or os.path.expanduser('~/.local/share/yt2script')
# HF_HOME must be set before huggingface_hub is imported anywhere, or the
# model resolves to ~/.cache/huggingface and re-downloads 3 GB.
_models = os.path.join(DATA, 'models', 'huggingface')
if os.path.isdir(_models):
    os.environ.setdefault('HF_HOME', _models)
sys.path.insert(0, HERE)

import transcript

# The default extractor is currently broken for YouTube on some setups
# ("The page needs to be reloaded"). These are yt-dlp's own built-in player
# clients, tried in order as a breakage workaround -- no spoofed user agents,
# no proxies, nothing aimed at an anti-bot check.
UNSET = object()          # None already means "the default client"
CLIENTS = [None, 'ios', 'android']
PREFERRED_LANGS = ['zh-TW', 'zh-Hant', 'zh-HK', 'zh', 'zh-Hans', 'zh-CN', 'en']


def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)


def ydl_opts(client, **extra):
    o = {'quiet': True, 'no_warnings': True, 'ignore_no_formats_error': True,
         'noprogress': True}
    if client:
        o['extractor_args'] = {'youtube': {'player_client': [client]}}
    o.update(extra)
    return o


def has_audio(info):
    """A real audio-bearing format, not a storyboard image track."""
    for f in info.get('formats') or []:
        if f.get('acodec') not in (None, 'none') and f.get('ext') != 'mhtml':
            return True
    return False


def probe(url):
    """(info, sub_client, media_client).

    Extracting without raising is not the same as extracting usefully: a
    client can report zero subtitle tracks, or one it cannot then fetch,
    while another sees all of them. The default client is the flaky one here,
    so score every client by how many tracks it actually reports and keep the
    richest answer. Captions and media often come from different clients.
    """
    from yt_dlp import YoutubeDL
    first = first_info = None
    media_client = UNSET
    best_info, best_client, best_score = None, None, -1
    last = None
    for c in CLIENTS:
        try:
            with YoutubeDL(ydl_opts(c, skip_download=True)) as y:
                got = y.extract_info(url, download=False)
        except Exception as e:
            last = e; continue
        if not got:
            continue
        if first_info is None:
            first, first_info = c, got
        # manual tracks are worth far more than auto ones
        score = len(got.get('subtitles') or {}) * 1000 + len(got.get('automatic_captions') or {})
        if score > best_score:
            best_info, best_client, best_score = got, c, score
        if media_client is UNSET and has_audio(got):
            media_client = c
    if first_info is None:
        raise SystemExit(f"[失敗] 無法取得影片資訊：{last}\n"
                         f"        見 {os.path.join(HERE, 'TROUBLESHOOTING.md')}")
    if best_score <= 0:
        best_info, best_client = first_info, first
    return best_info, best_client, media_client


def is_translated(entries):
    """YouTube labels machine-translated auto-caption tracks '... from X'."""
    return any(' from ' in (e.get('name') or '') for e in entries)


def pick_lang(tracks, allow_translated):
    avail = {k: v for k, v in (tracks or {}).items()
             if allow_translated or not is_translated(v)}
    for want in PREFERRED_LANGS:
        for k in avail:
            if k.lower() == want.lower():
                return k
    return next(iter(avail), None)


def fetch_subs(url, preferred, lang, auto, outdir):
    """Download one subtitle track, trying each client until a file appears.

    A client that *reports* a track cannot always *fetch* it. Treating that
    failure as "this video has no subtitles" is how you end up running a
    27-minute transcription over a video that had human subtitles all along,
    so every client gets a turn before we give up on the track.
    """
    from yt_dlp import YoutubeDL
    key = 'writeautomaticsub' if auto else 'writesubtitles'
    order = [preferred] + [c for c in CLIENTS if c != preferred]
    for c in order:
        opts = ydl_opts(c, skip_download=True, subtitleslangs=[lang],
                        subtitlesformat='vtt',
                        outtmpl=os.path.join(outdir, '%(id)s.%(ext)s'), **{key: True})
        try:
            with YoutubeDL(opts) as y:
                y.download([url])
        except Exception as e:
            log('警告', f"client={c or 'default'} 字幕下載失敗："
                       f"{str(e).splitlines()[0][:80]}")
            continue
        got = [os.path.join(outdir, f) for f in os.listdir(outdir) if f.endswith('.vtt')]
        if got:
            if c != preferred:
                log('取得', f"改用 client={c or 'default'} 成功取得字幕")
            return got[0]
        log('警告', f"client={c or 'default'} 回報成功但沒有寫出字幕檔")
    return None


def fetch_audio(url, client, outdir):
    """bestaudio, else the progressive mp4 -- both carry a decodable track."""
    from yt_dlp import YoutubeDL
    if client is UNSET:
        raise SystemExit("[失敗] 沒有任何 client 提供可下載的音訊格式（YouTube SABR 限制）\n"
                         f"        見 {os.path.join(HERE, 'TROUBLESHOOTING.md')}")
    opts = ydl_opts(client, format='bestaudio/18/best',
                    outtmpl=os.path.join(outdir, 'media.%(ext)s'))
    try:
        with YoutubeDL(opts) as y:
            y.download([url])
    except Exception as e:
        raise SystemExit(f"[失敗] 音訊下載失敗：{str(e).splitlines()[0][:120]}")
    files = [os.path.join(outdir, f) for f in os.listdir(outdir)
             if not f.endswith('.vtt')]
    if not files:
        raise SystemExit("[失敗] 找不到可下載的音訊格式")
    return max(files, key=os.path.getsize)


def model_is_cached(size):
    """Can faster-whisper load this model offline?

    Don't ask snapshot_download: huggingface_hub >= 2.4 raises
    IncompleteSnapshotError when cosmetic files (.gitattributes, README.md)
    are absent, even though faster-whisper fetches only the weights and
    tokenizer and loads perfectly well without them. The honest test is
    whether the files inference actually needs are on disk.
    """
    root = os.path.join(os.environ.get('HF_HOME', ''), 'hub',
                        f'models--Systran--faster-whisper-{size}', 'snapshots')
    if not os.path.isdir(root):
        return False
    needed = ('model.bin', 'config.json', 'tokenizer.json')
    for snap in os.listdir(root):
        d = os.path.join(root, snap)
        if all(os.path.exists(os.path.join(d, f)) for f in needed):
            return True
    return False


def ensure_model(size, assume_yes):
    """Confirm before pulling a model that is not cached (1-3 GB)."""
    if model_is_cached(size) or assume_yes:
        return True
    log('模型', f"{size} 不在本地快取，需從網路下載（約 1-3 GB）")
    try:
        ans = input("        要下載嗎？[y/N] ").strip().lower()
    except EOFError:
        ans = ''
    if ans not in ('y', 'yes'):
        cached = [m for m in ('large-v3', 'medium', 'small', 'base', 'tiny')
                  if model_is_cached(m)]
        hint = f"已在本地的模型：{', '.join(cached)}" if cached else "本地沒有任何模型"
        raise SystemExit(f"[中止] 未下載模型。{hint}")
    return True


def run_whisper(media, out_vtt, size, compute):
    from faster_whisper import WhisperModel
    model = WhisperModel(size, device='cpu', compute_type=compute)
    segments, info = model.transcribe(media, beam_size=5, vad_filter=True)
    log('音訊', f"{info.duration:.1f}s | 偵測語言 {info.language} "
                f"({info.language_probability*100:.1f}%)")

    def ts(s):
        h, m = int(s)//3600, (int(s) % 3600)//60
        return f"{h:02d}:{m:02d}:{s - (h*3600 + m*60):06.3f}"

    n, last = 0, 0.0
    with open(out_vtt, 'w', encoding='utf-8') as f:
        f.write(f"WEBVTT\nKind: captions\nLanguage: {info.language}\n\n")
        for s in segments:
            txt = s.text.strip()
            if not txt: continue
            f.write(f"{ts(s.start)} --> {ts(s.end)}\n{txt}\n\n")
            n, last = n + 1, s.end
            if n % 25 == 0:
                pct = int(20 * last / max(info.duration, 1))
                log('轉錄', f"{'█'*pct}{'░'*(20-pct)} {last:.0f}/{info.duration:.0f}s")
    log('轉錄', f"完成 {n} 段")
    return info.language


def main():
    ap = argparse.ArgumentParser(prog='yt2script', add_help=True,
                                 description='YouTube 連結 -> 繁體中文逐字稿')
    ap.add_argument('url')
    ap.add_argument('--out', default='.', help='輸出目錄（預設：當前目錄）')
    ap.add_argument('--model', default='large-v3', help='Whisper 模型尺寸')
    ap.add_argument('--compute', default='int8', help='量化方式（int8/float32）')
    ap.add_argument('--force-whisper', action='store_true', help='略過字幕直接轉錄')
    ap.add_argument('--keep-media', action='store_true', help='保留下載的音訊')
    ap.add_argument('--no-timestamps', action='store_true', help='只產純文字版')
    ap.add_argument('--allow-translated', action='store_true',
                    help='允許 xx-zh 機器翻譯字幕軌（品質差，預設拒絕）')
    ap.add_argument('--yes', action='store_true', help='不詢問即下載模型')
    args = ap.parse_args()

    info, sub_client, media_client = probe(args.url)
    title = info.get('title') or info.get('id')
    if media_client is UNSET:
        mc = '無'
    else:
        mc = media_client or 'default'
    via = f"（字幕 client={sub_client or 'default'}, 媒體 client={mc}）"
    log('影片', f"{title} | {info.get('duration_string') or '?'} | "
               f"{info.get('uploader') or '?'} {via}")

    man, auto = info.get('subtitles') or {}, info.get('automatic_captions') or {}
    native_auto = {k: v for k, v in auto.items() if not is_translated(v)}
    log('探路', f"人工字幕 {len(man)} 軌 | 自動字幕 {len(auto)} 軌"
               f"（原生 {len(native_auto)}，二次翻譯 {len(auto)-len(native_auto)}）")

    tmp = tempfile.mkdtemp(prefix='yt2script.')
    media = None
    try:
        vtt = src = None
        if not args.force_whisper:
            lang = pick_lang(man, args.allow_translated)
            if lang:
                log('取得', f"第 1 步 人工字幕 {lang}")
                vtt, src = fetch_subs(args.url, sub_client, lang, False, tmp), 'manual'
            else:
                lang = pick_lang(auto, args.allow_translated)
                if lang:
                    log('取得', f"第 2 步 自動字幕 {lang}")
                    vtt, src = fetch_subs(args.url, sub_client, lang, True, tmp), 'auto'

        if not vtt:
            if args.force_whisper:
                why = '指定 --force-whisper'
            elif src:
                why = '字幕軌存在但所有 client 都抓不到'
                log('警告', '這不是「沒有字幕」——若在意品質，建議稍後重試再落 Whisper')
            else:
                why = '無可用字幕軌'
            log('取得', f"第 3 步 Whisper {args.model} 本地轉錄（{why}）")
            ensure_model(args.model, args.yes)
            media = fetch_audio(args.url, media_client, tmp)
            log('音訊', f"已下載 {os.path.getsize(media)/1e6:.1f} MB")
            vtt = os.path.join(tmp, 'whisper.vtt')
            run_whisper(media, vtt, args.model, args.compute)
            src = 'whisper'

        r = transcript.build(vtt, title, args.url, args.out,
                             source=src, timestamps=not args.no_timestamps)
        log('清理', f"source={r['source']} cues={r['cues_kept']}/{r['cues_raw']} "
                   f"segments={r['segments']} chars={r['chars']}")
        log('字體', f"trad_only={r['trad_only']} simp_only={r['simp_only']} "
                   f"→ {r['conversion']}")
        ok = '✓' if r['verified_missing'] == 0 else f"✗ 缺 {r['verified_missing']}"
        log('驗證', f"{r['verified_total']-r['verified_missing']}/{r['verified_total']} cue 無損 {ok}")

        if media and args.keep_media:
            dst = os.path.join(args.out, transcript.safe_name(title) + os.path.splitext(media)[1])
            shutil.move(media, dst); media = None
            log('影音', f"保留 {dst}")
        for f in r['files']:
            log('完成', f)
        return 0 if r['verified_missing'] == 0 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
