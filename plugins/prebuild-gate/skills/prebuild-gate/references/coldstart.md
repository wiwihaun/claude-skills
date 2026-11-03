# Gate B — Where do the first payers come from?

The answer must be specific enough to execute on launch day. Most "marketing
plans" fail this because they name a surface ("Twitter", "SEO", "Reddit")
instead of an action.

Three patterns recur for products with no audience and no budget. They are not
alternatives — the ones that work tend to run all three at once, because each
feeds a different stage.

---

## Pattern 1 — The demonstration artifact

A short recording where the product does the thing, end to end, with no
narration about how clever it is. Ideally under 30 seconds. Input → output,
visibly compressing something the viewer knows is tedious.

**Why it works:** it collapses explanation into evidence. The viewer does not
have to trust a claim, and the "before" state is their own current workload, so
the value is computed by them rather than asserted by you.

**Worked example (as reported in the source material):** Sleek's co-founder
posted a 23-second screen recording — an app idea typed in, a full set of mobile
screens out in under two minutes — with a closing line asking people to comment
a keyword for beta access. A thousand views at bedtime, over 300,000 by morning,
~890,000 and 2,800+ comments in the end. They cancelled the beta within twelve
hours and opened it to everyone. MRR crossed $10k about a month later, with
nothing spent on ads.

**The part worth copying, and the part that isn't:** the founder later said
outright that there was no beta — the comment-gate existed because comments feed
the recommendation algorithm *and* open a one-to-one conversation with every
person who leaves one. The transferable mechanism is "give the platform the
engagement signal it rewards, and buy yourself a direct line to each interested
person." The specific move — fake scarcity via comment-gating — is now widely
used and correspondingly less effective. Reach for the mechanism and find a
move that hasn't saturated.

**Does the product qualify?** It needs a visible before/after inside ~20
seconds. If the value is invisible (a backend, a slow-burn benefit, something
whose payoff arrives in three weeks), this pattern is weak and you should lean
on the other two.

---

## Pattern 2 — The free tool as front door

A small, genuinely useful, no-signup utility adjacent to the paid product. It
sells nothing. Its only job is to be the reason someone arrives.

**Why it works:** it converts a search query into a visit without asking for
anything, and it ranks — single-purpose tool pages are one of the few things an
unknown domain can still rank for. The visitor leaves having experienced your
competence rather than your marketing.

**Worked example:** Sleek runs a row of free browser tools (one is green-screen
background removal, no signup). They report ~15,000 visitors a month from that
one tool alone.

**Generating candidates:** look for the step *immediately before or after* your
paid product in the user's workflow, where the sub-task is annoying, searchable,
and small enough to do client-side. Converters, extractors, validators,
calculators, previewers, formatters. The test: would someone type this into a
search engine with the word "free" or "online" attached?

The failure mode is building a free tool that serves a different audience than
the paid product. Traffic that cannot convert is a hosting bill.

---

## Pattern 3 — Parasitize an existing ecosystem

Package the core capability as something a platform's existing users install and
run inside the tool they already use. The ecosystem's distribution does the work.

**Why it works:** you inherit an audience that is already assembled, already in
a buying mindset for that category, and reachable through a directory you did
not have to build. This is an old pattern wearing new clothes — WordPress
plugins, Shopify apps, VS Code extensions, Chrome extensions, and now skills and
MCP servers for AI coding tools.

**Worked example:** Sleek also packaged its design capability as a skill that
Claude Code and Codex can call directly.

**The trade:** you are renting the distribution. Platform rules change, the
directory's ranking changes, and the platform can ship your feature. Worth it
for cold start; not a long-term moat on its own.

---

## Choosing and specifying

Pick the one the user can actually execute this week given what they have, then
write down:

- **Channel** — named, with the specific venue (not "Reddit" but "the weekly
  thread in r/<subreddit>")
- **First action** — a thing that takes under a day
- **Why it should work here** — the mechanism, in one sentence
- **What would tell you it's not working** — a number and a date, so the user
  can abandon it on evidence rather than on mood

Then check the honest gap: what did the comparable have at launch that the user
doesn't? An existing audience is the usual answer, and it is the hole where
their launch was. A product that launches to 60,000 followers and one that
launches to nobody are not running the same experiment, no matter how similar
the business model.
