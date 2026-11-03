# claude-skills

Two Claude Code plugins. They have nothing to do with each other except that
both exist to stop a particular kind of wasted effort.

| Plugin | What it does | Setup |
| :- | :- | :- |
| **yt2script** | Turns a YouTube link into a verbatim Traditional Chinese transcript, entirely on your machine | One command, then ~3 GB on first Whisper run |
| **prebuild-gate** | Pressure-tests a product idea *before* you write code: how it charges, and where the first paying customers come from | None |

## Install

```bash
claude plugin marketplace add wiwihaun/claude-skills
```

```bash
claude plugin install prebuild-gate@wiwihaun-skills
```

```bash
claude plugin install yt2script@wiwihaun-skills
```

Install either one on its own — they share no code.

---

## yt2script

A YouTube URL in, a `.md` transcript out, in Traditional Chinese. Three sources
are tried in order, stopping at the first that yields text:

1. **Human-written subtitles** — best quality, when they exist
2. **Native auto-captions** — machine-transcribed, but from the original audio
3. **Local Whisper `large-v3`** — when there are no usable captions at all

The ordering is the point. Most transcript tools reach straight for speech
recognition and throw away a human transcript that was sitting right there.

**It refuses `xx-zh` tracks.** Those are captions machine-translated *from* the
original language into Chinese — a translation of a transcription, degraded
twice. They are usually what YouTube shows you first, and they are usually
worse than running Whisper yourself. Override with `--allow-translated` if a
bad track is genuinely all there is.

**Simplified Chinese is converted to Traditional, and only when it actually is
simplified.** Running a converter over already-Traditional text corrupts it
(`台` becomes `臺`, `才` becomes `纔`), so the direction is detected per
document by counting characters exclusive to each script, and conversion is
skipped when the source is already Traditional.

**A transcript is a transcript.** No summarizing, no paraphrasing, no tidying
up grammar, no adding punctuation the speaker didn't imply. Every source cue is
verified to have survived into the output, and the run reports the count.

### Setup

Installing the plugin gives you the skill; the Python environment is a separate
one-time step, because a plugin install can't create a venv.

Just run it. The plugin's `bin/` is on Claude Code's `PATH`, so the bare
command works, and before setup it exits with the exact installer path to run:

```bash
yt2script https://www.youtube.com/watch?v=jNQXAC9IVRw
```

`install.sh` needs **Python 3.11+** (macOS still ships 3.9, so it looks for a
newer one, or has [`uv`](https://docs.astral.sh/uv/) fetch one) and installs
into `~/.local/share/yt2script/`. Set `YT2SCRIPT_HOME` to put it elsewhere.
**`ffmpeg`** is needed for the Whisper path only; the installer warns if it's
missing rather than failing.

Nothing is installed inside the plugin directory, so a plugin update never
costs you a 3 GB re-download.

### What it will not do

When YouTube answers `Sign in to confirm you're not a bot`, that is IP
reputation. The documented response is: upgrade yt-dlp, then try browser
cookies, then try a different network — and if all three fail, stop and say so.

It does not forge a client identity, rotate user agents, or route through proxy
pools. Selecting among yt-dlp's own built-in player clients is a documented fix
for extractor breakage and the pipeline does that; disguising a request as
something it isn't is a different thing, and this tool won't.

### Known issues

[`plugins/yt2script/KNOWN_ISSUES.md`](plugins/yt2script/KNOWN_ISSUES.md) — read
it. The first entry is a real gap in the `xx-zh` refusal above: an *unlabelled*
machine-translated track can still get through.

Tested on macOS, Apple Silicon only.

---

## prebuild-gate

Writing code stopped being the bottleneck, which means a weekend is now enough
to ship a product nobody buys. This gate asks the two questions that actually
decide the outcome, while they are still cheap to answer:

1. **How does this charge?** Who pays for the marginal unit decides
   subscription vs. one-time, mechanically. And if the buyer's own AI can
   produce the deliverable in five minutes, the price goes to zero no matter
   what the model is.
2. **Where do the first payers come from?** Named channel, first concrete
   action, and an honest look at which starting assets your comparables had and
   you don't.

It researches what comparable products earn **in the last 30 days** rather than
reasoning from first principles, labels how strong each figure's source is, and
returns a go / no-go memo in Traditional Chinese. The most common honest verdict
is "not enough evidence yet, and here is the cheapest way to go find out".

Invoke it explicitly. A plugin's skills are namespaced under the plugin name,
so the slash command carries the prefix:

```
/prebuild-gate:prebuild-gate 我想做一個 X，賣給 Y
```

Asking for it in plain words works too. What it won't do is trigger on its own:
its description tells Claude *not* to reach for it merely because you mentioned
building something, on the grounds that a gate you didn't ask for is just
friction.

### Credit

The two-gate structure is not original. It comes from a talk by Yihui, the
independent developer behind Skillry, in the video
[上線一個月賺一萬美元：Vibe Coding 前先想兩件事](https://www.youtube.com/watch?v=QVZdJToew2c)
by 「Agent 煉金術士」 — including the ordering, the cost-incidence rule, "read
the last 30 days, not the lifetime total", the ShipFast / Tailwind UI / Sleek
teardowns, and the closing point that what you copy is the mechanism, not the
move. If you want the argument rather than a checklist, watch that.

This plugin adds the research procedure, the gate structure, evidence-strength
labelling, and figures re-verified against primary sources with dates attached.
Those dates matter: the numbers in `references/pricing.md` are worked examples
of how to read evidence, not current market data, and the skill is built to go
fetch live figures instead of trusting them.

---

## Licence

MIT — see [LICENSE](LICENSE).

yt2script installs these at runtime rather than vendoring them, so their
licences don't attach to this repository, but for the record:

| Dependency | Licence |
| :- | :- |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Unlicense |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT |
| [CTranslate2](https://github.com/OpenNMT/CTranslate2) | MIT |
| [opencc-python-reimplemented](https://github.com/yichen0831/opencc-python) | Apache-2.0 |
| [PyAV](https://github.com/PyAV-Org/PyAV) | BSD-3-Clause |
| [onnxruntime](https://github.com/microsoft/onnxruntime) | MIT |
| [Systran/faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3) weights | MIT |

No paid APIs, no API keys, no hosted inference. The only network traffic is
fetching the video's captions or audio.
