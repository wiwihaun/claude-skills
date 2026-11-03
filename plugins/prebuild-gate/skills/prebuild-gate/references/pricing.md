# Gate A — How does this charge?

> **About the numbers in this file.** Every figure here is dated, and they are
> worked examples of *how to read evidence* — not current market data. Revenue
> moves, and a skill that confidently feeds stale numbers into a verdict is
> worse than one carrying none. Treat anything verified more than ~90 days ago
> as a teaching example only, and go get a live figure: Step 2 of `SKILL.md`
> exists for exactly that. The shapes these examples illustrate — a one-time
> sale collapsing when the buyer's AI can reproduce it, a lifetime total hiding
> a dead month — outlive the specific dollar amounts.

Two tests, in this order. The first decides the *structure* of the pricing. The
second decides whether there is anything to price at all.

---

## Test 1: Who pays for the marginal unit?

This is the question that decides subscription vs. one-time, and it has a
mechanical answer rather than a strategic one.

**If the marginal cost of each use lands on you**, one-time pricing is a time
bomb. You collect once and pay forever, so your best outcome — a hit — is also
the thing that bankrupts you. Every heavy user is a liability. You need revenue
that recurs on the same clock as the cost.

Marginal cost lands on you when the product involves: inference on your own
infrastructure or your own API keys, GPU time, generous storage or bandwidth,
per-seat upstream licences, or any human in the loop (review, support,
onboarding).

**If the marginal cost lands on the customer**, one-time pricing is safe and
becomes a conversion lever. A lifetime deal that costs you nothing to honour is
pure margin, and it closes the buyers who hate subscriptions — a large group,
especially among developers.

Marginal cost lands on the customer when the thing runs inside the tooling they
already pay for: a skill, prompt pack, config or template executed by *their*
Claude/Codex/Copilot subscription; a static asset they download; a local binary;
a self-hosted deployment with their own keys.

**Mixed is common and fine.** A free tier on your infra plus a lifetime deal on
the parts that run on theirs is a coherent structure. What is not coherent is a
lifetime price on something whose cost scales with use.

### Applying it

State explicitly where each cost sits before recommending a model:

| Component | Cost falls on | Implication |
|---|---|---|
| e.g. image generation | you (API) | must be metered or subscription |
| e.g. the prompt library | customer (their AI) | can be sold outright |

A single "falls on you" component is enough to force recurring revenue for that
component. It does not force the whole product onto a subscription — unbundling
the metered part is often the better answer.

---

## Test 2: Can the buyer's own AI produce this in five minutes?

If yes, the price trends to zero. Not slowly.

This is the test the template and boilerplate businesses failed.

| Product | What it sold | Peak | Later | Stated cause | Evidence |
|---|---|---|---|---|---|
| Tailwind UI | UI component templates | ~$2M revenue in ~5 months after launch (2020) | revenue down ~80%, three quarters of the engineering team laid off | AI's impact on the business, per the founder | founder's own account |
| ShipFast | Next.js SaaS boilerplate, $199–$299 one-time | ~$126,000 in a month (2024), per the founder | **$1,395 in the last 30 days; MRR $0.00; 0 active subscriptions; −6.6% month on month** against **$1,272,892 lifetime** | mainly AI, per the founder | **payment-processor sync, read-only, verified 2026-11-02** |

The ShipFast row is worth dwelling on, because it is the whole rule in one
line: **$1.27M lifetime, $1,395 last month.** Anyone reading the lifetime total
sees a million-dollar success. The same page, one field over, shows a business
that has stopped. The founder's own figure and the verified figure agree, and
the verified one is worse — which is the usual direction, because a founder
quotes the number from when they last looked.

Tailwind UI's figures remain the founder's own account; re-verify before relying
on them.

The mechanism: both sold *an artifact a competent model now generates on
demand*. The buyer's willingness to pay collapsed not because the artifact got
worse but because the alternative got free.

### What survives the test

Things models are bad at by default, or structurally cannot do:

- **Taste and curation.** Models produce the median competently and the
  distinctive rarely. Someone who has decided what good looks like, and shipped
  it as a ready-made thing, is selling a judgment the buyer cannot prompt for.
- **Trust and accountability.** A name on the work, liability, support, "this
  was reviewed by someone who knows the domain".
- **Proprietary data or access.** Something the model cannot know.
- **Ongoing maintenance.** The artifact decays — APIs change, rules change — and
  you keep it current. This converts a one-time artifact into a subscription
  honestly.
- **Distribution itself.** Being the place people look is a durable asset even
  when the contents are commoditized.
- **Doing it inside the user's workflow.** Saving the buyer the orchestration,
  not the generation.

Note what is *not* on this list: being first, being cheaper, having more
features, or having a nicer landing page.

### The honest version of this test

Actually try it. Ask the model to produce the thing the user plans to sell, in
the session, and look at the result. If the output is 80% as good, that 20% is
the entire business and must be nameable in one sentence. If it is 100% as good,
say so — this is the single highest-value moment in the whole gate, and softening
it to be encouraging wastes the only chance to catch the problem cheaply.

---

## Reading other people's prices

Reach for this when revenue numbers don't exist. Most categories have no public
MRR at all, and a pricing page is the next best evidence — weaker, but it is
primary-source and it is sitting right there. It leaks the founder's cost
structure, because they had to solve the same cost-incidence problem you are
solving in Test 1, and the price is their answer:

- **Lifetime deal exists** → their marginal cost is near zero, or they are
  desperate for cash. Check which by looking at whether the product runs on
  their infra.
- **Usage credits / metered tiers** → marginal cost is real and they know it.
- **Price went up over time** → they found the floor was too low; a signal the
  buyer values it more than the founder first guessed.
- **Enterprise "contact us"** → the real money is in a motion you probably
  cannot run solo.

What this cannot tell you is whether anyone is buying. A category where every
competitor sells a lifetime licence has told you that marginal cost is near zero
— which derisks *your* pricing — but it has told you nothing about demand. Two
different findings; keep them apart in the memo, because conflating "safe to
price this way" with "people pay for this" is how a clean cost structure gets
mistaken for a market.

### When the whole category is silent

If no competitor anywhere publishes revenue, resist both available temptations.
It is not proof the market is dead, and it is not permission to assume the
market is fine. It is an absence, and the honest move is to name it as the
reason the verdict rests on something else — the reproducibility test, the cold
start plan, the user's own distribution. Those you *can* assess from here.

A verdict that would flip if one revenue number turned up is a verdict that
should say so.
