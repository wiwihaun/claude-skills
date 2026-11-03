---
name: yt2script
description: Turn a YouTube link into a verbatim Traditional Chinese transcript (繁體中文逐字稿) using a local, free, no-API-key pipeline — human subtitles first, native auto-captions second, local Whisper large-v3 third. Use this skill whenever the user supplies a YouTube or video URL and wants a transcript, 逐字稿, captions, subtitles, 字幕, 文字稿, "轉文字", "轉逐字稿", speech-to-text, or asks what was said in a video — even if they only paste a link with no other instruction, and even if they don't name Whisper or yt-dlp. Also use it when a transcript run fails and needs troubleshooting (extractor breakage, "no video formats", "Sign in to confirm you're not a bot", cookie access denied).
---

# yt2script

A CLI already does the deterministic work. Your job is to run it, read its
report honestly, and apply judgment only where the script cannot.

```bash
yt2script <URL>
```

The plugin's `bin/` is on the Bash tool's `PATH` while the plugin is enabled,
so the bare command works. If it exits 127 and prints an installer path, the
one-time setup has not run on this machine yet:

```bash
sh "${CLAUDE_PLUGIN_ROOT}/cli/install.sh"
```

That builds a venv under `~/.local/share/yt2script/` (set `YT2SCRIPT_HOME` to
move it) and installs three packages. It does **not** download the 3 GB Whisper
model — that happens on the first run that actually needs Whisper.

Files land in the **current working directory**, so `cd` to where the user
wants them first. Two files per video: `<標題>.md` and
`<標題>（時間戳版）.md`.

## What the script already handles

Don't re-implement or second-guess these — it does them the same way every time:

- Probing every built-in player client and keeping the richest answer
- Preferring human subtitles, then **native** auto-captions
- Refusing `xx-zh` tracks (machine-translated *from* the original, so twice degraded)
- Falling back to local Whisper `large-v3` with VAD and `beam_size=5`
- Scrolling-caption de-duplication **only** for auto-captions
- Converting to Traditional Chinese only when the text is actually simplified
- Verifying every source cue survived into the output

## Reading the report

```
[影片] <title> | <duration> | <uploader> （字幕 client=…, 媒體 client=…）
[探路] 人工字幕 1 軌 | 自動字幕 157 軌（原生 0，二次翻譯 157）
[取得] 第 1 步 人工字幕 zh
[清理] source=manual cues=368/368 segments=11 chars=4330
[字體] trad_only=1038 simp_only=18 → none (source already traditional)
[驗證] 368/368 cue 無損 ✓
[完成] ./<標題>.md
```

Report to the user which step produced the text (人工字幕 / 自動字幕 /
Whisper), the detected language, the segment count, and the file paths. Say so
plainly if anything was degraded — the user would rather hear it than discover it.

Two lines deserve a closer look:

- `[驗證] … ✗` means cues went missing. Investigate before handing over; the
  whole point of this pipeline is that nothing is lost.
- `cues=362/373` on a Whisper run means de-duplication ran where it should not
  have. Genuine repeated lines are content — in a comedy skit, saying it twice
  *is* the joke.

## When it fails

Read `references/troubleshooting.md` and work through it in order. The short
version: these failures are almost always a broken extractor or a blocked
cookie store, not something to force past.

**Never** forge a client identity, rotate user agents, or route through proxy
pools to get around `Sign in to confirm you're not a bot`. That check is about
IP reputation. Try `yt-dlp -U`, then browser cookies, then a different network
— and if all three fail, stop and tell the user. Selecting among yt-dlp's own
built-in player clients is a documented fix for extractor breakage and is fine;
disguising the request as something it isn't is not.

## Fidelity

A transcript is a transcript. Do not summarize, paraphrase, tidy up grammar,
add punctuation the speaker didn't imply, or "improve" phrasing — not even when
the result reads awkwardly. If the user wants a summary, that's a separate
artifact they can ask for, built *from* the transcript.

Everything here is free and local: no paid APIs, no keys, no cloud inference.
Keep it that way. If a task seems to need a hosted service, say so and let the
user decide rather than quietly reaching for one.

## Options worth knowing

| Flag | Why you'd reach for it |
|---|---|
| `--out <dir>` | Write somewhere other than the current directory |
| `--force-whisper` | Subtitles exist but are visibly wrong or auto-generated garbage |
| `--model medium` | `large-v3` is too slow; prompts first, since it must be downloaded |
| `--keep-media` | User wants the audio kept (deleted by default) |
| `--allow-translated` | Last resort: a `xx-zh` track is genuinely all there is |
| `--no-timestamps` | Only the plain prose version |
| `--yes` | Non-interactive; download a missing model without asking |

Whisper on CPU takes roughly **1.7× the video's own duration** (measured 1.71×
and 1.73× on Apple Silicon), so a 10-minute video is about 17 minutes of
compute. Run it in the background and give the user that estimate up front
rather than letting them watch a silent terminal.
