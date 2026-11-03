#!/usr/bin/env python3
"""faster-whisper -> VTT, so the same cleaning pipeline handles both paths."""
import os, sys, glob, time

# HF_HOME must be set BEFORE huggingface_hub
# is imported, or it falls back to ~/.cache/huggingface and re-downloads 3 GB.
# Must match driver.py. Deliberately duplicated rather than shared: this file
# also runs as its own process, where an import of a sibling is one more thing
# that can go wrong before HF_HOME is set.
_data = os.environ.get('YT2SCRIPT_HOME') or os.path.expanduser('~/.local/share/yt2script')
_models = os.path.join(_data, 'models', 'huggingface')
if os.path.isdir(_models):
    os.environ.setdefault('HF_HOME', _models)

for _d in glob.glob(os.path.expanduser('~/Library/Python/3.*/lib/python/site-packages')):
    if _d not in sys.path: sys.path.append(_d)
from faster_whisper import WhisperModel

media, out_vtt, model_size, compute = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

t0 = time.time()
print(f"loading model={model_size} compute_type={compute} ...", flush=True)
model = WhisperModel(model_size, device="cpu", compute_type=compute)
print(f"model ready in {time.time()-t0:.0f}s", flush=True)

segments, info = model.transcribe(
    media,
    beam_size=5,
    vad_filter=True,
    word_timestamps=False,
)
print(f"DETECTED_LANG={info.language} PROB={info.language_probability:.4f} "
      f"DURATION={info.duration:.1f}", flush=True)

def ts(s):
    h = int(s)//3600; m = (int(s)%3600)//60; sec = s - (h*3600 + m*60)
    return f"{h:02d}:{m:02d}:{sec:06.3f}"

n = 0
with open(out_vtt, 'w', encoding='utf-8') as f:
    f.write("WEBVTT\nKind: captions\nLanguage: " + info.language + "\n\n")
    for seg in segments:
        txt = seg.text.strip()
        if not txt: continue
        f.write(f"{ts(seg.start)} --> {ts(seg.end)}\n{txt}\n\n")
        n += 1
        if n % 25 == 0:
            print(f"  {n} segments, t={seg.end:.0f}s / {info.duration:.0f}s "
                  f"({time.time()-t0:.0f}s elapsed)", flush=True)
print(f"DONE segments={n} wall={time.time()-t0:.0f}s", flush=True)
