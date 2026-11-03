---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)

## What is the Skills CLI?

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**

- `npx skills find [query] [--owner <owner>]` - Search for skills interactively or by keyword, optionally scoped to a GitHub owner
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Search Locally First

#### 2a — Is it already installed?

Recommending an install for something the user already has is this skill's worst
failure: they run a command, nothing visibly changes, and in the bad case it
overwrites a version they had edited. Checking costs two commands.

```bash
npx skills list -g </dev/null                  # user-level, with upstream source
npx skills list -p </dev/null                  # project-level, if cwd is a project
jq '.enabledPlugins' ~/.claude/settings.json   # plugin skills — the CLI cannot see these
```

**The CLI's list is incomplete, so run both.** `npx skills list -g` reports only
what lives in `~/.claude/skills/`. A skill that arrived inside a plugin lives
under `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/` and does
not appear in it at all. On one machine the CLI listed **three** skills while
**eight** skill directories existed — four were plugin skills it cannot see, and
one was a directory with no `SKILL.md`, which the CLI also skips, so an abandoned
skill shell stays invisible.

**Read the `Source:` field — it decides whether updating is destructive.**

| `Source:` | Means | Consequence |
|---|---|---|
| a repo, e.g. `vercel-labs/skills` | tracked; the CLI installed it | `npx skills update` **replaces it with upstream** — no diff, no backup |
| `untracked` (shown yellow) | hand-written, or copied in by hand | nothing upstream will touch it |

Nothing on disk records whether a tracked skill was edited after install. There
is no manifest, no hash and no version — a `--copy` install leaves a bare
`SKILL.md` and no provenance whatsoever. So when the user has customised a
tracked skill, say plainly that `update` discards those edits, and offer to set
it aside first:

```bash
mkdir -p ~/.claude/skills-local-backup
cp -r ~/.claude/skills/<name> ~/.claude/skills-local-backup/
```

**The backup must land outside `~/.claude/skills/`.** Every directory in there
that contains a `SKILL.md` is loaded, and the copy keeps the original's
`name:` frontmatter — so a backup sitting beside the original registers a second
skill claiming the same name. A sibling directory is not in the load path.

Being installed answers the first of Step 4's two cost questions and not the
second: the skill itself is free and on disk, but a skill that drives a hosted
service still bills for use.

#### 2b — Then the local catalogs

Two catalogs are already on disk as JSON. Search them with `jq` before touching
the network — they are bigger than skills.sh's leaderboard, they cost nothing,
and they carry vetting that skills.sh does not.

| Catalog | Entries | File | Vetting |
|---|---|---|---|
| Anthropic directory (built in) | ~3,600 | `~/.claude/plugins/plugin-directory-cache-v2.json` | **mostly none** — see below |
| `claude-community` | ~2,300 | `~/.claude/plugins/marketplaces/claude-community/.claude-plugin/marketplace.json` | automated security scan + approval |

**Being listed in the built-in directory is not being reviewed.** Each entry
carries `checks.review.state`, and on a 3,604-entry cache the split was **442
`done` against 3,162 `none`** — about 12% reviewed. Check the field for the
entries you are actually about to recommend rather than inheriting the
directory's reputation:

```bash
jq -r --arg q "QUERY" '.listings[]
  | select(((.name//"") + " " + (.summary//"")) | ascii_downcase | test($q))
  | "\(.checks.review.state)\t\(.name)"' \
  ~/.claude/plugins/plugin-directory-cache-v2.json
```

Match on name **and** summary, case-insensitively, and print the name beside the
state. Two reasons, both learned the hard way:

- **`.name` alone finds almost nothing.** A query for `threads` matched **0**
  entries by name and **26** by name-plus-summary — every one of them carries the
  word only in its description. Names are also capitalised (`Postiz`, not
  `postiz`), so an exact lowercase match returns nothing at all.
- **Empty output and "unreviewed" look identical** unless the name is printed.
  A silent empty result reads as "no review found" when it actually means the
  query missed. Printing `state<TAB>name` makes the two distinguishable.

Two unreviewed listings are also not two votes. A plugin appearing in both
catalogs with `state: none` in each has been *listed* twice, not vetted twice.

The two have different shapes. The built-in cache keys off `.listings[]` with
`name` / `summary` / `source` / `links` / `checks` / `surfaces`; the community
file keys off `.plugins[]` with `name` / `description` / `source` / `category`:

```bash
# Built-in directory
jq -r '.listings[] | select(((.name//"") + " " + (.summary//"")) | ascii_downcase
  | test("QUERY")) | "\(.name)\n  \(.summary)\n  surfaces: \(.surfaces|tostring)"' \
  ~/.claude/plugins/plugin-directory-cache-v2.json

# claude-community
jq -r '.plugins[] | select(((.name) + " " + (.description//"")) | ascii_downcase
  | test("QUERY")) | "\(.name)\n  \(.description)"' \
  ~/.claude/plugins/marketplaces/claude-community/.claude-plugin/marketplace.json
```

Search both. They overlap only partially — a query that returned 22 hits in the
built-in directory returned 6 in the community file, and each had entries the
other lacked. Reporting one as if it were the whole picture is the main way this
skill gives a wrong answer.

The built-in directory's `surfaces` field is worth reading out: it states
whether an entry installs on `claude_code`, `cowork` and `claude_ai`. A plugin
with a top-level `bin/` directory cannot be installed on chat or Cowork at all,
and `surfaces` is where that shows up without having to go read the docs.

Install from these with `claude plugin install <name>@<marketplace>`, not
`npx skills add`.

### Step 3: Then Search skills.sh

The leaderboard at [skills.sh](https://skills.sh/) ranks by total installs, and
the CLI searches the same catalog. This is a *different* set from the two local
ones, so it is worth checking even when the local search found something.

`find` is interactive-only — it has no `--json` flag — so close stdin or it
will hang:

```bash
npx skills find QUERY </dev/null
```

```bash
npx skills find [query] [--owner <owner>]
```

For example:

- User asks "how do I make my React app faster?" → `npx skills find react performance`
- User asks "can you help me with PR reviews?" → `npx skills find pr review`
- User asks "I need to create a changelog" → `npx skills find changelog`

### Step 4: Verify Quality Before Recommending

**Do not recommend a skill based solely on search results.** Always verify:

1. **Install count** — Prefer skills with 1K+ installs. Be cautious with anything
   under 100. Treat the number as weak evidence: one skill on skills.sh showed
   17.1K installs against 2 GitHub stars and no licence file. When installs and
   stars disagree wildly, believe the stars.
2. **Source reputation** — Official sources (`vercel-labs`, `anthropics`,
   `microsoft`) are more trustworthy than unknown authors. "Official X skills"
   where X is the vendor's own product means official *to that vendor*, not
   vetted by anyone else.
3. **GitHub stars** — Check the source repository. A skill from a repo with <100
   stars should be treated with skepticism. Also check the licence field is
   actually populated — "open source" in a description is not a licence.
4. **Cost — and separate two questions that look like one.**

   **Is the skill free?** vs **is using it free?** A MIT-licensed skill that
   drives a $29/month hosted service is free to download and not free to use.
   Report both or neither.

   The catalogs mostly do not say. Of the **26** entries matching `threads` in
   name or summary in the built-in directory, exactly **two** mentioned pricing
   at all (`socialync`, `JuzPost`) — and all 26 were `review.state: none`. So
   infer from structure rather than hunting for a price in the summary:

   | Signal in the entry | What it means for cost |
   |---|---|
   | "hosted MCP", "remote MCP", or a product name | a vendor with a pricing page — **assume paid until checked** |
   | "free plan", "no credit card" | a free tier exists, but check what it caps |
   | "open source", "self-host", AGPL/MIT + a self-host path | the software is free; **the infrastructure may not be cheap** |
   | "bring your own key", "your own API key" | skill is free; **the upstream API may bill you** |
   | pure markdown, no service, no API | genuinely free |

   Two traps worth naming when they apply:

   - **Self-hosting is not the same as cheap.** One open-source option in this
     category needs nine containers, two Postgres instances and Elasticsearch,
     with 8 GB RAM recommended by its own docs.
   - **"Bring your own key" hides the real bill.** Posting to X costs $0.015 per
     post and $0.200 if the post contains a link, so a free skill can still run
     up a few hundred dollars a month for an account that posts links. Threads
     and Instagram APIs are free by contrast, which can flip the recommendation
     entirely depending on the platform.

   If cost could not be established, say "pricing not stated in the catalog; not
   checked" rather than implying it is free.

### Step 5: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. **Which catalog it came from** — the three have different vetting, and the
   user is choosing a trust level as much as a tool
3. The install count and source, with stars where the source is a repo
4. **Cost**, as the two separate questions from Step 4: skill free? using it free?
5. The install command they can run
6. A link to learn more

Where the result set is more than three or four entries, use a table with a cost
column rather than prose. A list of twelve near-identical hosted schedulers is
not useful; what distinguishes them is cost, vetting and whether a third party
ends up holding the user's credentials.

Say so plainly when every option shares a drawback. If each candidate routes
through a vendor's own server, the user is picking which company holds their
posting authorization, and that is the actual decision in front of them — not
the feature lists, which will all look alike.

Example response:

```
I found a skill that might help! The "react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.
(185K installs)

To install it:
npx skills add vercel-labs/agent-skills@react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### Step 6: Offer to Install

If the user wants to proceed, you can install the skill for them:

```bash
npx skills add <owner/repo@skill> -g -y
```

The `-g` flag installs globally (user-level) and `-y` skips confirmation prompts.

Do not reach for `--force`. Plain `add` skips a skill that is already installed,
which is the safe behaviour; `--force` reinstalls over it and is how a user's
local edits disappear. If `add` reports the skill is already there, that is the
2a check catching something you missed — go back and tell the user they already
have it rather than forcing past it.

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest the user could create their own skill with `npx skills init`

Example:

```
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill:
npx skills init my-xyz-skill
```
