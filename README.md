# claude-skills

Five Claude Code plugins. The first two have nothing to do with each other
except that both exist to stop a particular kind of wasted effort. The other two
approach the same problem from opposite ends: finding out what already exists
before you build it, and finding out what you already have before you install
more.

| Plugin | What it does | Setup |
| :- | :- | :- |
| **yt2script** | Turns a YouTube link into a verbatim Traditional Chinese transcript, entirely on your machine | One command, then ~3 GB on first Whisper run |
| **prebuild-gate** | Pressure-tests a product idea *before* you write code: how it charges, and where the first paying customers come from | None |
| **whatfunc** | Surveys the products that already exist in a category and turns their documentation into a build spec, ending in a build order | None |
| **find-skills** | Finds and installs agent skills, searching your own machine and both on-disk catalogs before the network. A fork of `vercel-labs/skills` | None |
| **fairprice** | Values a stock by writing down what has to be true for today's price, picking the method before the number | None |

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

```bash
claude plugin install whatfunc@wiwihaun-skills
```

```bash
claude plugin install find-skills@wiwihaun-skills
```

```bash
claude plugin install fairprice@wiwihaun-skills
```

Install any one on its own — they share no code.

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

## whatfunc

Before you build something, the people who already built it have written your
requirements document for you. Every item in their documentation exists because a
paying user needed it, which makes it more honest than a feature list written from
imagination.

```
/whatfunc:whatfunc 社群發文
```

It writes `<短名>-feature-spec.md`: every feature found, grouped into categories
that come from the material rather than a fixed taxonomy, each attributed to the
product it came from and marked **本地可做** / **要公開端點** / **要常駐** /
**要付費 API** / **不值得**, ending in a recommended build order. Name what you
already know you want and it is excluded from the survey, because the value is in
what you have not thought of.

**It looks on your own machine before searching anything.** An installed skill
ships its whole source — scripts, reference files, schemas — not a catalog
summary. On one run the richest source in the entire survey had 271 lines of prose
sitting on 4,197 lines of Python and 19,730 lines of XSD schemas; ranked by prose
alone it did not make the top eight.

**It hunts the destructive-failure list**, which is the richest thing in a mature
product's docs and never in its marketing: the oddly specific prohibitions — this
colour format corrupts the file, reordering these two XML siblings makes the
document unopenable — because every one of them is a bug somebody already paid
for.

More in [`plugins/whatfunc/README.md`](plugins/whatfunc/README.md).

---

## find-skills

A modified fork of [vercel-labs/skills](https://github.com/vercel-labs/skills) →
`skills/find-skills`. Upstream searches [skills.sh](https://skills.sh/); this
version searches three places in order of cost — your own machine, then the two
catalogs already on disk, then skills.sh — and reports what *using* a skill costs
rather than only what installing it costs.

Three findings drove the change, each of which cost a wrong answer to learn:

- **The CLI's list of installed skills is incomplete.** On one machine
  `npx skills list -g` reported three while eight skill directories existed —
  four were plugin skills it cannot see, one had no `SKILL.md`.
- **Being listed in the built-in directory is not being reviewed.** On a
  3,604-entry cache, `checks.review.state` split 442 `done` against 3,162 `none`.
  A plugin in two catalogs with `none` in each was listed twice, not vetted twice.
- **Matching on `.name` alone finds almost nothing.** A query for `threads`
  matched 0 entries by name and 26 by name-plus-summary — and an empty result
  looks identical to "unreviewed" unless the name is printed beside the state.

What changed, and the note about sharing a name with upstream, are in
[`plugins/find-skills/README.md`](plugins/find-skills/README.md).

---

## fairprice

A share price is a claim about the future. This skill makes that claim explicit
enough to argue with.

```
/fairprice:fairprice TSLA
```

**It picks the method before it picks a number.** Step 0 asks whether today's
price can be explained by today's earnings, then routes to sum-of-the-parts
(several businesses with separable economics), normalized earnings times one
multiple (one business, however many end markets), or finite-life NPV (revenue
with a legal expiry date — a patent cliff, a concession, a mine life). Taking
the wrong path is the most expensive mistake available: it produces a detailed
table that looks rigorous and is built on companies that do not exist.

**A revenue breakdown by end market is not a set of segments.** Before splitting
anything it asks whether each piece could be sold off on its own. If not, it is
a mix, and one multiple on the whole is the honest tool.

**Every multiple has to name a peer who trades there.** The same earnings at 14×
and 40× differ by nearly 3×, so a multiple without a source is where a valuation
becomes whatever you wanted it to be. Where no comparable exists, the documented
fallback is PEG ≈ 1 — never "pick a number".

**Management's dates get discounted by the company's own record**, measured from
three to five years of its own guidance against what actually happened. A clean
record gets 1.0×.

The output is a dated report in Traditional Chinese with a bear/base/bull range,
a mandatory sensitivity table, a line saying what the market is already paying
for, and checkpoints with dates and numeric thresholds that would prove it
wrong. Written to a `fairprice/` folder, never into a public repository.

More, including the method's origin and the failure-mode list, in
[`plugins/fairprice/README.md`](plugins/fairprice/README.md).

**It is not investment advice.** The output is arithmetic with stated
assumptions; it never says buy or sell.

---

## Licence

MIT — see [LICENSE](LICENSE).

**Except [`plugins/find-skills/`](plugins/find-skills)**, which is a modified fork
of [vercel-labs/skills](https://github.com/vercel-labs/skills), MIT, Copyright (c)
2026 Vercel, Inc. Their licence is kept with it at
[plugins/find-skills/LICENSE](plugins/find-skills/LICENSE) and governs that
plugin; the modifications are listed in
[its README](plugins/find-skills/README.md).

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
