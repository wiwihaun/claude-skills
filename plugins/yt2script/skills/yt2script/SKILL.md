---
name: yt2script
description: Turn a YouTube link into a verbatim transcript in the language the video is spoken in — Traditional Chinese (繁體中文逐字稿) for Chinese audio, the original language (e.g. an English transcript, 英文逐字稿) for everything else, never translated — using a local, free, no-API-key pipeline — human subtitles first, native auto-captions second, local Whisper large-v3 third. Use this skill whenever the user supplies a YouTube or video URL and wants a transcript, 逐字稿, captions, subtitles, 字幕, 文字稿, "轉文字", "轉逐字稿", speech-to-text, or asks what was said in a video — even if they only paste a link with no other instruction, and even if they don't name Whisper or yt-dlp. Also use it when a transcript run fails and needs troubleshooting (extractor breakage, "no video formats", "Sign in to confirm you're not a bot", cookie access denied).
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
- Picking the **language the video is spoken in** first (YouTube's own
  `language` field), then zh-TW → zh-Hant → … → en. An English talk with
  human Chinese subtitles yields the English transcript; the Chinese track is a
  translation. `--lang` overrides this.
- Refusing machine-translated tracks (twice degraded). They are recognised by
  the `tlang` parameter in the track URL, not by the track name: since 2026-11
  YouTube names a translated track just "Chinese (Traditional)", and a
  name-only check let all 155 translations of one English video through.
- Falling back to local Whisper `large-v3` with VAD and `beam_size=5`
- Scrolling-caption de-duplication **only** for auto-captions — both the old
  word-by-word growth and the current two-line roll-up, where each cue repeats
  the previous cue's last line
- Spacing Latin text correctly when cues are joined (`plan. Well`, not
  `plan.Well`); Chinese still joins with no space
- Breaking paragraphs at a sentence end once they pass ~400 characters
  (hard cap 600), or at a pause of 3 s or more
- Converting to Traditional Chinese only when the text is actually simplified;
  English and other languages pass through untouched
- Verifying every source cue survived into the output

## Reading the report

```
[影片] <title> | <duration> | <uploader> （字幕 client=…, 媒體 client=…）
[探路] 人工字幕 1 軌 | 自動字幕 157 軌（原生 2，二次翻譯 155） | 影片語言 en
[取得] 第 1 步 人工字幕 en
[清理] source=manual cues=427/427 segments=37 chars=14405
[字體] trad_only=0 simp_only=0 → none (source already traditional)
[驗證] 427/427 cue 無損 ✓
[完成] ./<標題>.md
```

Report to the user which step produced the text (人工字幕 / 自動字幕 /
Whisper), the language of the track used, the segment count, and the file
paths. Say so plainly if anything was degraded — the user would rather hear it
than discover it. If the video was not in Chinese and a human Chinese track
exists, mention it and that `--lang zh-TW` fetches it — as a translation, not
a transcript.

Four things deserve a closer look:

- `[驗證] … ✗` means cues went missing. Investigate before handing over; the
  whole point of this pipeline is that nothing is lost.
- `cues=362/373` on a Whisper or human-subtitle run means de-duplication ran
  where it should not have. Genuine repeated lines are content — in a comedy
  skit, saying it twice *is* the joke. On an auto-caption run, about half the
  cues disappearing (`138/273`) is normal: every other cue is a 10 ms copy of
  the line just finished.
- `[字體] … none (source already traditional)` on an English run only means
  there was no Chinese to convert.
- **`[驗證] ✓` proves nothing was lost; it does not prove nothing was
  doubled.** On a first run against a new kind of track, skim the output for
  repeated phrases. That is how the roll-up duplication was found.

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

The same goes for language: an English video gives an English transcript.
Translating it into Chinese is a separate artifact too — say so, and build it
from the transcript only if asked. Bracketed sound notes in human subtitles
(`(Laughter)`, `(Applause)`, `[Music]`) are part of the subtitle and stay.

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
| `--lang en` / `--lang zh-TW,en` | Choose which subtitle language to look for first, instead of the spoken language |
| `--allow-translated` | Last resort: a machine-translated track is genuinely all there is |
| `--no-timestamps` | Only the plain prose version |
| `--yes` | Non-interactive; download a missing model without asking |

Whisper on CPU takes roughly **1.7× the video's own duration** (measured 1.71×
and 1.73× on Apple Silicon), so a 10-minute video is about 17 minutes of
compute. Run it in the background and give the user that estimate up front
rather than letting them watch a silent terminal.
