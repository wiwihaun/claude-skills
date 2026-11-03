# Known issues

Published deliberately. A transcription tool's whole value is that you can
trust the text, so the places where that trust is thinner than the README
suggests belong in the open.

## 1. A machine-translated caption track can slip through the filter

**Severity: this undercuts the tool's headline promise.**

yt2script refuses `xx-zh` tracks — captions machine-translated *from* the
original language — because they are twice degraded. The check is in
`cli/driver.py`:

```python
def is_translated(entries):
    """YouTube labels machine-translated auto-caption tracks '... from X'."""
    return any(' from ' in (e.get('name') or '') for e in entries)
```

It recognises a translated track by the `" from X"` marker YouTube puts in the
track's name. When a track arrives with no name, or with a bare name that
carries no marker, the check returns `False` and the track is accepted as
native.

So the guarantee is really: *tracks YouTube labels as translations are
refused.* An unlabelled translation is not caught.

No clean automatic fix exists. The obvious candidate — run Whisper's language
detector on a sample of the audio and compare it with the caption language —
costs a model load on every subtitle run, which is most runs, to catch a case
whose frequency nobody has measured. If you hit this, pass `--force-whisper`
and transcribe from audio.

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
