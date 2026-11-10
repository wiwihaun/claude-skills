# yt2script

A YouTube URL in, a verbatim transcript out in the language the video is
spoken in — Traditional Chinese for Chinese audio, the original language (for
example English) otherwise, never translated — entirely on your own machine.
No API keys, no paid services, no hosted inference — the only network traffic
is fetching the video's captions or audio.

Three sources are tried in order, stopping at the first that yields text:
human-written subtitles, then native auto-captions, then local Whisper
`large-v3`. The ordering is the point — most transcript tools reach straight for
speech recognition and throw away a human transcript that was sitting right
there.

It refuses machine-translated caption tracks — a translation of a
transcription, degraded twice — recognising them by the `tlang` parameter in the
track URL. They are usually what YouTube offers first and usually worse than
running Whisper yourself. It looks for the video's own spoken language first;
`--lang` overrides that. Simplified Chinese is converted to Traditional only
when the text actually is simplified, because running a converter over
Traditional text corrupts it.

A transcript is a transcript: no summarizing, no paraphrasing, no tidying up
grammar. Every source cue is verified to have survived into the output, and the
run reports the count.

## Install

```bash
claude plugin install yt2script@wiwihaun-skills
```

Then run `yt2script <URL>`. The Python environment is a separate one-time step —
a plugin install cannot create a venv — and the command exits with the exact
installer path to run. Needs Python 3.11+; `ffmpeg` is needed for the Whisper
path only.

Setup detail, what it will not do, and known issues:
[the repository README](../../README.md#yt2script) and
[KNOWN_ISSUES.md](KNOWN_ISSUES.md).

Tested on macOS, Apple Silicon only.
