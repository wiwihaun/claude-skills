# Known issues

Published deliberately. A transcription tool's whole value is that you can
trust the text, so the places where that trust is thinner than the README
suggests belong in the open.

## 1. Translated-track detection depends on YouTube's URL format

**Fixed in 1.1.0 (2026-11-10). What remains is a dependency, not a hole.**

Up to 1.0.1, yt2script recognised a machine-translated caption track by the
`" from X"` marker in the track's name. That gap was listed here as
theoretical. On 2026-11-10 it was observed on an English video: YouTube now
names a translated track just `Chinese (Traditional)`, the check flagged none
of the 155 translated tracks, and the pipeline would have picked the
machine-translated `zh-Hant` track over the original English.

`is_translated` in `cli/driver.py` now looks for the `tlang` parameter in the
track URL, which YouTube adds only when it translates, and keeps the name check
as a fallback. On that video it marks 155 of 157 tracks as translations and
leaves exactly `en-orig` and `en`.

The remaining risk: if YouTube stops putting `tlang` in the URL, translated
tracks would again look native. The `[探路]` line shows the split
(`原生 2，二次翻譯 155`); a video with dozens of "native" auto tracks means the
marker has moved again. If you see that, pass `--lang <spoken language>` or
`--force-whisper`.

## 1a. The skill used to prefer Chinese subtitles over the spoken language

Up to 1.0.1 the subtitle order was fixed at zh-TW → zh-Hant → … → en, so an
English talk with human Chinese subtitles produced the Chinese translation, not
a transcript. 1.1.0 puts the video's own language first (YouTube's `language`
field) and adds `--lang` to override. If that field is missing or wrong, the
old order applies.

## 1b. English auto-captions came out with every line twice

Up to 1.0.1 the de-duplication handled only captions that grow word by word.
YouTube's current English auto-captions roll up two lines at a time, each cue
repeating the previous cue's last line, so every line appeared twice — and the
`[驗證] ✓` check could not see it, because it proves nothing was *lost*, not
that nothing was *doubled*. 1.1.0 drops a line carried over from the cue just
before. Side effect to know about: if a speaker repeats an entire caption line
immediately and YouTube lays it out as its own identical line, one copy is
dropped. Use `--force-whisper` where exact repetition matters.

## 2. `av` is capped below 19.0, and it is not our bug

`faster-whisper` 1.2.1 calls `av.open(..., metadata_errors="ignore")`. `av`
19.0 removed that argument, and `faster-whisper` declares a bare `av`
dependency with no upper bound, so an unconstrained install resolves to 19 and
then fails at transcription time with:

```
TypeError: open() got an unexpected keyword argument 'metadata_errors'
```

`requirements.txt` therefore carries `av<19`. Tested against 18.1.0. Drop the
cap once `faster-whisper` ships a fix; the pin exists because upstream is
missing a bound, not because of anything in this pipeline.

## 3. Only tested on macOS, Apple Silicon

The pipeline is plain Python and nothing in it is platform-specific, but it has
only been run on macOS on Apple Silicon. `install.sh` is POSIX `sh` and has not
been exercised on Linux, and not at all on Windows. The timing figure in
`SKILL.md` (~1.7× the video's duration) is an Apple Silicon CPU measurement and
says nothing about your machine.

## 4. Whisper runs on CPU only

No CUDA or Metal path. `faster-whisper` can use a GPU; this wrapper does not
ask it to. On a machine with a usable GPU you are leaving a large speedup on
the table.
