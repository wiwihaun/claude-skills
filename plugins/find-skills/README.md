# find-skills (fork)

A modified fork of [`vercel-labs/skills`](https://github.com/vercel-labs/skills)
→ `skills/find-skills`, MIT, Copyright (c) 2026 Vercel, Inc. Their licence is
kept beside this file at [LICENSE](LICENSE) and governs this plugin.

Upstream finds skills by searching [skills.sh](https://skills.sh/). This fork
searches three places in order of cost — your own machine, then the two catalogs
already sitting on disk, then skills.sh — and reports what *using* a skill costs
rather than only what installing it costs.

## What changed

`+189 / −13` lines against upstream.

| Area | Change |
| :- | :- |
| **Step 2** | Was "Check the Leaderboard First". Now searches locally first, in two parts |
| **2a** (new) | Is it already installed? Reads the CLI's `Source:` field, which says whether `npx skills update` would overwrite a skill you have edited |
| **2b** (new) | `jq` searches the two on-disk catalogs — ~3,600 and ~2,300 entries — with no network |
| **Step 3** | Now explicitly *after* the local search rather than instead of it |
| **Step 4** | Adds cost as a fourth criterion, split into two questions that look like one: is the skill free, and is *using* it free |
| **Step 5** | Reports which catalog a result came from, since the three carry different vetting |
| **Step 6** | Warns off `--force`, which is how local edits disappear |

## Why the local search went first

Three findings, each of which cost a wrong answer to learn:

**The CLI's list of installed skills is incomplete.** On one machine
`npx skills list -g` reported three skills while eight skill directories
existed — four were plugin skills it cannot see, and one was a directory with no
`SKILL.md`, which it skips.

**Being listed in the built-in directory is not being reviewed.** Each entry
carries `checks.review.state`, and on a 3,604-entry cache the split was 442
`done` against 3,162 `none`, about 12%. A plugin appearing in two catalogs with
`none` in each has been *listed* twice, not vetted twice.

**Matching on `.name` alone finds almost nothing.** A query for `threads` matched
0 entries by name and 26 by name-plus-summary. Worse, an empty result and
"unreviewed" look identical unless the name is printed beside the state.

## Note on the name

This plugin is called `find-skills`, the same as upstream. If you already have
the upstream version installed through `npx skills add`, installing this one
leaves you with two skills claiming that name — pick one.
