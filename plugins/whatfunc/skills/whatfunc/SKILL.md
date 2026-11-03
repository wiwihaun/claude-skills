---
name: whatfunc
description: >-
  Survey the products that already exist in a category, extract the complete feature inventory from
  each one, and write it up as a build spec for a local version. Use when the user is about to build
  something and wants to know what the incumbents ship — "市面上有什麼功能", "別人都做了什麼",
  "做本地版要參考什麼", "what features do existing products have", "survey the market before I build",
  or invokes it by name. Produces a dated markdown spec with every feature grouped by category,
  attributed to its source, marked for local-build feasibility, and ending in a recommended build
  order. Not a buy-vs-build recommendation and not a pricing comparison — the output is a
  requirements menu for someone who has already decided to build.
---

# whatfunc

You are building something. Other people already built it. Their documentation is
a free requirements document, and it is more honest than any feature list you
would write from imagination, because every item in it exists because a paying
user needed it.

This skill turns that documentation into a build spec.

## What this is not

- **Not a buy-vs-build verdict.** The user has decided to build. Do not relitigate it.
- **Not a pricing comparison.** Cost belongs in `find-skills`, which has a whole
  section on it. Mention a price only where it reveals a feature boundary.
- **Not a trust assessment.** Stars and review state decide what to *install*,
  not what to *learn from*. See the failure modes below — this distinction is the
  one that trips up every run.

## Step 1 — Pin down the category and what is already known

Get two things from the user before searching:

1. **The category**, specific enough to search. "Social posting from an AI agent"
   works; "productivity" does not.
2. **What they already know they want.** Any feature they name goes in a *Known
   requirements* list that is **excluded from the survey**. The whole value of
   this skill is finding what they have *not* thought of, so spending the survey
   confirming their own list wastes it.

If they named nothing, say so in the doc and survey everything.

## Step 2 — Find the products

### 2a — First, what is already on this machine

An installed skill ships its **whole source** — scripts, reference files,
schemas — not a catalog summary. That is the deepest documentation available
anywhere in this process and it costs no network, so look here before searching
anything.

```bash
# Every installed skill, ranked by how much it ships.
for root in "$HOME/.claude/skills" "$HOME/.claude/plugins/cache" \
            "$HOME/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"; do
  find "$root" -name SKILL.md -maxdepth 8 2>/dev/null
done | while read -r f; do
  d=$(dirname "$f")
  n=$(find "$d" -type f \( -name '*.md' -o -name '*.py' -o -name '*.js' \
        -o -name '*.ts' -o -name '*.xsd' -o -name '*.json' \) \
        -exec cat {} + 2>/dev/null | wc -l | tr -d ' ')
  printf "%7s  %s\n" "$n" "$(basename "$d")"
done | sort -rn | head -15
```

Grep that list for the category and read the top hit in full. Nothing relevant
installed is a normal outcome and costs you one command — go on to 2b.

**Count code and data, not prose.** This is what makes the ranking work. On one
run the deepest source in the entire survey had **271 lines of SKILL.md** — less
than a trivial skill — sitting on **4,197 lines of Python and 19,730 lines of
XSD schemas**. Ranked by markdown alone it did not appear in the top eight at
all. Prose length measures how much the author felt like explaining; code and
schema volume measures how much reality they actually had to absorb.

### 2b — Then the catalogs

Search every one. There are three, they overlap only partly, and treating one as
the whole picture is the main way this skill produces a thin spec.

If the `find-skills` skill is available, use it — its Step 2b has the current
catalog list and search commands, and its 2a is the installed-skills check in a
form aimed at not re-installing something the user already has. Otherwise, the two local catalogs are JSON on
disk and `jq` searches them with no network:

```bash
# Anthropic directory (built in, ~3,600 entries)
jq -r '.listings[] | select(((.name//"") + " " + (.summary//"")) | ascii_downcase
  | test("QUERY")) | "\(.name)\t\(.source.repository.url // "-")"' \
  ~/.claude/plugins/plugin-directory-cache-v2.json

# claude-community (~2,300 entries)
jq -r '.plugins[] | select(((.name) + " " + (.description//"")) | ascii_downcase
  | test("QUERY")) | "\(.name)\t\(.source.url // .source // "-")"' \
  ~/.claude/plugins/marketplaces/claude-community/.claude-plugin/marketplace.json

# skills.sh (different catalog again; interactive, so close stdin)
npx skills find QUERY </dev/null
```

**Two or three query terms — and use the second one to reject noise.** A
category's products rarely share vocabulary, so a single term under-returns.
The bigger problem is the opposite: when the category's own noun is overloaded,
a single term massively *over*-returns. Searching `deck` in the built-in
directory gave 62 hits, of which roughly **60% were a different meaning of the
word** — tarot decks, Stream Deck, Clash Royale decks, telecom rate decks, a
statusline. Cross-check against a second domain term (`slide`,
`presentation`) before ranking anything.

Nouns that are overloaded and need filtering first: deck, card, slide, board,
sheet, frame, canvas, pipeline, agent, flow. If the category's name is one of
these, assume noise rather than discovering it later.

Then say in the doc how many each catalog returned **and what the noise rate
was** — a 62-hit query that is 60% noise is a different quality of evidence
from a clean one, and asymmetry between catalogs is itself a finding.

Look outside the catalogs too when the category has incumbents that are not
agent plugins at all. A category's best feature documentation often belongs to a
product that predates the whole plugin ecosystem.

## Step 3 — Pick what to read, by documentation depth

Rank candidates by **how much they document**, not by how popular or trustworthy
they are. One product with a documented tool list is worth five marketing pages.

Where the source is on disk or clonable, depth is **measurable** rather than a
judgment call — reuse the line count from Step 2a. Otherwise, signals that a
source will be rich:
- a named tool or API list with per-tool behaviour
- a README that states limits, required fields and error cases
- an explicit "not supported" list

Read at two depths, not one. **Two to four at full source depth** — every
script, every reference file — because that is where the non-obvious material
lives and a README never carries it. Then **six to ten at README depth** for
coverage and cross-checking. Fewer than four sources in total and the categories
will not emerge; more than ten read deeply and the duplicates swamp you.

## Step 4 — Extract the whole inventory from each product

**Ask each product what it does. Do not ask whether it does the thing you expect.**

This is the step that goes wrong. Checking five products against the user's
known requirements and reporting "none of them have these" is a wasted survey —
it confirms a hypothesis instead of finding the unknown unknowns. Go in with no
hypothesis and come out with a list.

For every product, pull:
- every tool or command, with what it actually does
- required and optional fields, and which are per-platform or per-target
- limits with numbers — sizes, counts, character caps, rate limits, windows
- failure and recovery behaviour, which is where the hard-won design lives
- **every condition that produces a broken output instead of an error message**
- anything stated as **not** supported

That second-to-last one deserves its own pass, because it is the single richest
thing in a mature product's documentation and it is never in the marketing. It
reads as a list of oddly specific prohibitions: a colour value with a `#` prefix
corrupts the file, a negative shadow offset corrupts the file, reordering two XML
siblings makes the document unopenable. Nobody writes those from imagination —
every line is a bug somebody already paid for. Pull each one with its condition
*and* its consequence, and expect the list to outrank the feature inventory when
you get to priorities: a missing feature disappoints, a corrupt output cannot be
undone.

Record the source for each item. An unattributed feature list cannot be checked
later, and some of these claims are vendor marketing.

Where two products contradict each other, note it. A capability one vendor calls
impossible while another ships it is a *choice*, not a platform limit — and that
is worth knowing before you conclude you cannot build it.

## Step 5 — Group, deduplicate, mark feasibility

Let the categories come from what you found. Do not force a fixed taxonomy;
every domain has its own joints. Validation, failure handling, scheduling, media,
per-target options, generation, analytics, permissions and rate limits were the
natural groups for one domain and will be wrong for the next.

**A category with one source is still a category — and is usually the best
find.** Deduplication is for the same feature appearing five times, not for a
feature appearing once. In one run the two most valuable categories were each
N=1: one product stored a sha256 of every code range it quoted, so it could later
tell you which slides quote code that has since changed; another split fonts into
those whose widths survive a local QA render and those that get substituted, so
the preview lies about overflow. Nobody else had either. That is precisely why
they were worth the read — a feature every competitor ships is table stakes, and
the one nobody else thought of is the whole reason to go through the docs. Mark
the count honestly (「N 家中只有 1 家」) so the user can see it is unproven rather
than consensus.

Mark every single item:

| Mark | Meaning |
|---|---|
| **本地可做** | pure logic, or needs only tools already on the machine |
| **要公開端點** | needs a URL reachable from outside |
| **要常駐** | needs a background process or scheduler |
| **要付費 API** | the upstream charges per call |
| **不值得** | buildable, but the cost dwarfs the value at this scale |

A feature list without these marks is a wish list. The marks are what make it a
spec.

## Step 6 — Write the doc

Write to `<短名>-feature-spec.md` in the current directory. **Never write it into
a public repository** — check with `git remote -v` if unsure, and put it in the
private parent directory instead. Say where you put it and why.

Required structure. **The priority section is not optional** — a spec that stops
at the inventory leaves the user holding forty undifferentiated items:

```markdown
# <類別>功能清單（本地版規格參考）

從 <N> 家產品的文件盤出來的功能，當作自建本地版的選單。
盤查對象：<逐一列名，規格最完整的排前面並註明>
搜尋範圍：<每個目錄各幾筆；雜訊比例；本機已安裝的最深來源是哪一個>
日期 <YYYY-MM-DD>

可行性標記：
**本地可做** / **要公開端點** / **要常駐** / **要付費 API** / **不值得**

## 已知的 N 項（使用者指定，不在此清單重複討論）
1. <...>

以下是**這些之外**找到的全部功能。

## A. <類別名> ★ <為什麼這類最值得抄，一句話>
| 功能 | 出處 | 可行性 |
|---|---|---|

## B. <類別名>
| 功能 | 出處 | 可行性 |

（依找到的內容決定類別數量）

## <明確做不到的 — 這也是參考價值>
<誰說不支援什麼；哪幾項其實別家做得到，所以是選擇不是限制>

## 建議的本地版優先順序

**第一批（零成本、高價值，都在「本地可做」）**
1. <...>

**第二批（有明確價值但工作量大）**
<...>

**要常駐才做**
<...>

**不做**
<...，附一句為什麼>
```

Order the first batch by value per unit of work, not by category order. Say
plainly which single category is the highest-value one and why — in one domain
it was pre-publish validation, because it is pure logic and prevents the one
failure state that cannot be undone.

Where a "要常駐" item exists on macOS, name `launchd` rather than letting the
user write a daemon.

## Failure modes

**Surveying one catalog.** The same query returned 22 hits in one catalog and 6
in another, each with entries the other lacked. Search all of them.

**Testing the user's hypothesis instead of surveying.** Covered in Step 4. It is
the most common way this skill produces nothing.

**Filtering candidates by trust before extracting features.** In one run the
product with 105 stars had none of the wanted capabilities and the one with zero
stars had all of them. Popularity predicts whether to *install*; it does not
predict whether a product is worth *reading*. Survey widely, then let
`find-skills` handle the install recommendation separately.

**Reporting marketing copy as fact.** "Free plan", "40+ tools", "14 platforms" —
one product's README said 14 platforms while its own repo description said 9.
Attribute, and flag contradictions rather than picking one.

**Ranking sources by prose length.** Covered in Step 2a. A 271-line SKILL.md on
top of 24,000 lines of scripts and schemas looks thin and was the richest source
in the survey. Count what the author had to *handle*, not what they chose to
explain.

**Taking an overloaded category noun at face value.** Covered in Step 2b. Sixty
percent of the hits meaning a different thing entirely is the normal case for a
common noun — not evidence that the category is crowded.

**Dropping the numbers.** "Supports media uploads" is useless; "20 items per
post, 100 MB video by URL, 8 MB base64, TikTok photo posts reject PNG" is a
spec. Carry the numbers through.
