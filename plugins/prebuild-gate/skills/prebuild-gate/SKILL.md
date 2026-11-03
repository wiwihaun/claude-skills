---
name: prebuild-gate
description: Gate a product idea before any code gets written. Pins down the two things that decide whether a build is worth starting — how the business charges, and where the first paying customers come from — researches what comparable products actually earn in the last 30 days, and returns a go / no-go memo. Use this when the user explicitly asks to validate, pressure-test, gate or sanity-check a product idea, asks whether something is worth building or could make money, or invokes it by name. Do NOT reach for it just because the user mentions building an app, a tool, a SaaS or a side project — if they want help writing the thing, help them write it.
---

# Pre-build gate

Writing code used to be the bottleneck. It isn't any more, which means a weekend
is now enough to ship a product nobody buys. This gate exists because the two
questions that actually decide the outcome — **how does this charge, and where
do the first payers come from** — are cheap to answer before the build and
expensive to answer after it.

Run it in five steps. Expect it to take a few minutes of real research, not a
vibes check; an answer the user could have produced themselves in thirty seconds
is not worth the invocation.

## Step 0 — Check this is the right tool

Get out of the way fast if the idea isn't trying to make money. A learning
project, an internal tool, a toy, a thing the user wants for themselves — none
of these need a revenue model, and gating them is just friction. Say so in one
line and offer to help build instead.

Also get out of the way if the user already has paying customers. Then the
question is growth, not viability, and this gate is aimed at the wrong thing.

**One exception, and it matters:** a user can knowingly ask you to gate
something that is currently a personal tool — "pretend I wanted to sell this",
"would this work as a product?", or a dry run to see what the gate does. Honour
that. Don't refuse on the grounds that it's a personal tool when the user has
already said they know. Note the counterfactual in one line at the top of the
memo ("this is currently a tool you use yourself; what follows assumes you
wanted to sell it") so the verdict can't be mistaken for a judgment on the tool
as it stands, and then run the gate properly. An off-ramp that can't be waived
by someone who knows where it leads is just a locked door.

## Step 1 — Three clarifying questions, no more

Ask only what you genuinely cannot infer from what they've said:

1. **Who is the buyer, and what are they paying to stop doing?** Vague buyers
   ("developers", "small businesses") are the single best predictor of a dead
   launch, because you can't go find a vague person on launch day.
2. **Where does the compute/inference run — your infrastructure or theirs?**
   This one question determines the entire pricing structure. See
   `references/pricing.md`.
3. **What distribution do you already have?** An audience, a mailing list, a
   community where you're known, an employer's reach. Zero is a valid answer and
   changes the plan rather than ending it.

Three questions is a deliberate ceiling. A long interview feels thorough and
mostly produces guesses; the research in Step 2 is worth more than the user's
fourth self-report.

## Step 2 — Go look at who is already making money

Do not reason from first principles about whether this market pays. Find
products that are *already charging for something adjacent* and look at their
numbers.

Search for comparable products and their revenue. Useful starting points:
public revenue leaderboards (TrustMRR, Indie Hackers, Starter Story), founders
posting MRR on X, Product Hunt launches with pricing pages, and the pricing page
itself (price point and whether lifetime deals exist tells you about marginal
cost).

For each comparable, record: **what it sells, its price and pricing model, its
most recent monthly revenue, the trend over the last few months, and where that
number came from.**

Two rules about the numbers, because getting these wrong is how people
confidently enter a collapsing market:

- **Read the last 30 days, not lifetime totals.** Lifetime revenue is a lagging
  indicator that hides a collapse completely. A product with $1M lifetime and
  $2k last month is a cautionary tale wearing a success story's clothes — and
  that is not a hypothetical: ShipFast's verified figures are $1,272,892
  lifetime against $1,395 in the last 30 days. `references/pricing.md` has the
  rest of that row.
- **Discount launch months.** A product in its first month is riding a spike
  that will not repeat. If you only have one month of data on something that
  just launched, you have no trend — say so rather than treating it as one.

Mark each figure's confidence. Almost all public indie revenue is
self-reported; a number synced live from a payment processor is stronger than a
screenshot, and a screenshot is stronger than a claim in a thread. If web search
isn't available in this session, say so plainly and label the whole memo as
unverified — an unresearched memo is still worth something, but the user must
know which one they're holding.

Find three to five comparables if they exist. How the search comes back is
itself a finding, and the three outcomes mean different things — say which one
you got rather than presenting whatever you found as if it were the full
picture:

- **No comparables at all.** The most important line in the memo. Either the
  market doesn't pay for this, or you haven't found the right search terms, and
  the user needs to know which before writing code.
- **Comparables and revenue.** The good case. Read the trend, not the total.
- **Comparables and prices, but no revenue anywhere.** Common, and not a dead
  end — whole categories go unreported, especially one-time-purchase desktop
  software, where founders have no build-in-public habit. Don't treat the
  silence as evidence of failure, and don't paper over it either. Say plainly
  that no revenue figure was findable, give both readings (nobody publishes in
  this category / nobody has anything worth publishing), and then fall back to
  the evidence that *is* available: the pricing pages. `references/pricing.md`
  has a section on what a price structure tells you about a business that its
  founder didn't. A verdict built on pricing structure is weaker than one built
  on revenue trends — label it as such.

## Step 3 — Gate A: how does this charge?

Read `references/pricing.md` and work through it. It covers the cost-incidence
rule (who pays for the inference decides subscription vs. one-time), the
reproducibility test (if the buyer's own AI can make the deliverable in five
minutes, the price goes to zero), and what actually survives that test.

The output of this gate is a recommended pricing model with the reason, plus an
honest note on what would break it.

## Step 4 — Gate B: where do the first payers come from?

Read `references/coldstart.md`. It covers the three channel patterns that
repeatedly work for small products with no audience, why each one works
mechanically, and how to generate candidates for a specific product.

The output of this gate is a named channel, a first action in it, and a rough
sense of whether the user can actually execute it. "Post on social media" is not
a channel. "A 20-second screen recording of the thing working, posted to the
r/notion weekly thread" is.

## Step 5 — Red flags, then the launch-post test

Read `references/traps.md` and run the four checks: survivorship bias in your
comparables, launch-spike distortion, move saturation, and unfair starting
assets the comparable had and the user doesn't.

Then the final test, which is the most useful thing in this whole gate:

> **Write the first launch post. Today. Before any code.**

Not a plan to write it — the actual post. If it can't be written, something
load-bearing is missing: there's no sharp buyer, or no visible before/after, or
nothing that separates this from what the reader's own AI would produce. All
three are cheaper to discover now than after the build.

Draft it for the user as part of the memo. If you can't draft something you'd
defend, that *is* the finding.

## Output

Write the memo to `<短名>-prebuild.md` in the current directory and summarize the
verdict in chat. Use this structure:

```markdown
# 開發前驗證：<產品一句話>

**結論：GO / NO-GO / 證據不足**　<一句話理由>

## 一、同類產品實況
| 產品 | 賣什麼 | 定價 | 最近月收 | 趨勢 | 來源可信度 |

## 二、怎麼收錢
建議模式：<賣斷 / 月費 / 混合>
理由：<成本落在誰身上>
可複製性測試：<客人自己的 AI 能不能幾分鐘做出來；不能的話，差在哪>
什麼會打破它：<...>

## 三、第一批付錢的客人
管道：<具體到可以今天就做的程度>
第一個動作：<...>
你缺的：<對照組有、使用者沒有的起跑資產>

## 四、紅旗
- <...>

## 五、上線第一則貼文（草稿）
<直接可發的版本>

## 六、如果 NO-GO / 證據不足：先去做這三件事
1. <...>
```

## Calibration

The user invoked a gate. A gate that never closes is decoration.

The most common honest verdict is **證據不足** — not "this is bad", but "you
cannot know yet, and here is the cheapest thing to go find out". Reach for that
instead of manufacturing confidence in either direction.

When the answer is NO-GO, say it in the first line and then be useful: what
would have to be true for this to work, and what the nearest adjacent idea is
that survives the gates. The point of stopping someone on day zero is to save
them the three months of looking for customers who were never there — so make
the stop short, specific, and followed by a door.

## Where this came from

The two-gate structure is not original to this skill. It comes from a talk by
Yihui, the independent developer behind Skillry, presented in the video
[上線一個月賺一萬美元：Vibe Coding 前先想兩件事](https://www.youtube.com/watch?v=QVZdJToew2c)
by the channel 「Agent 煉金術士」. Specifically his: the ordering (charge model
and cold start *before* code), the cost-incidence rule, "read the last 30 days,
not the lifetime total", the ShipFast / Tailwind UI / Sleek teardowns, and the
closing point that what you copy is the mechanism, not the move.

What this skill adds is the research procedure, the gate structure, the
evidence-strength labelling, and figures re-verified against primary sources
with dates attached. If a user wants the original argument rather than a
checklist, send them to the video — it is a better introduction than this file.
