# Step 5 — Red flags when copying what works

Copying a working product is the right instinct. These four failure modes are
how it goes wrong anyway, and all four are invisible unless you look for them
deliberately.

---

## 1. Survivorship bias in your comparables

Public revenue leaderboards and MRR posts contain only the people who chose to
publish. Everyone who built the same thing and made nothing is absent, so the
visible success rate of the category is inflated by an unknown and large factor.

Base rates from founders who have shipped many products are a useful corrective.
As reported in the source material: one well-known indie developer says 70+
projects produced 4 that made money; another says half of 36 products never
earned a dollar; the developer whose framework this is had four products in six
months with one success. On the leaderboard cited, close to 70% of listed
products were under $1,000/month — and that is the self-selected, willing-to-
publish population.

**What to do:** state the base rate in the memo. Not to be discouraging — to
make sure the user's plan survives being one of the likely outcomes. A plan that
only makes sense if it works is not a plan.

---

## 2. Launch-spike distortion

A product's first month is not its run rate. Launch day traffic, a Product Hunt
placement, the founder's audience converting all at once, and annual plans
bought up front all land in month one and do not repeat.

Equally: a single recent month can be down for reasons that mean nothing. The
source material notes Sleek's trailing-30-day revenue had fallen 17.5% at the
time — real, but one data point.

**What to do:** prefer three or more months of trend. Where only one month
exists, say "one month, no trend available" rather than treating the number as a
steady state. Flag any comparable that launched within the last 60 days as
un-trendable.

---

## 3. Move saturation

A tactic's effectiveness is a function of how many people are currently running
it. The first comment-gated viral demo was novel; the hundredth is wallpaper. The
first "I built this in a weekend with AI" thread got attention precisely because
it was surprising.

This is why the distinction between *move* and *mechanism* matters. Mechanisms
(platforms reward engagement; evidence beats claims; free utilities rank) are
stable. Moves (fake beta gates, build-in-public countdowns, specific hook
formats) decay as they spread.

**What to do:** for each tactic you're recommending from a comparable, ask how
many people are visibly doing it right now. If the answer is "many", keep the
mechanism and find a fresh move. Say which is which in the memo.

---

## 4. Unfair starting assets

The most common invisible dependency. A comparable's launch may have worked
because of something that was already in place and is not purchasable:

- an existing audience (the source material notes one product could broadcast to
  60,000+ followers on launch)
- an established domain with search authority
- a community where the founder is already trusted
- an employer's or previous product's user base
- being early to a platform before it got crowded

**What to do:** list what the comparable had that the user doesn't, explicitly.
Then either find a substitute (borrowed audience: someone else's newsletter, a
podcast, a community where the user is a genuine member) or accept that the cold
start will be slower and plan for a longer runway. What doesn't work is copying
the launch plan and quietly assuming the audience will appear.

---

## Reading a revenue number at all

Almost every public indie revenue figure is self-reported. Rank the evidence:

| Strength | Form |
|---|---|
| Strongest | synced live from the payment processor to a public page |
| Medium | a dashboard screenshot with the product and date visible |
| Weak | a number stated in a post or interview |
| Worthless | "6 figures", "life-changing", "we hit our goal" |

Two further distinctions worth getting right: **revenue is not profit** (ad
spend and inference costs are invisible in an MRR figure), and **MRR is not
cash** (annual plans and lifetime deals inflate the month they land in and show
up as churn later).

Record which tier each number came from in the comparables table. A GO verdict
resting entirely on bottom-tier evidence should say so out loud.

### An MRR leaderboard has a one-time-purchase-shaped hole

Revenue leaderboards rank by MRR, so a product that sells outright reads as
near-dead on the metric everyone looks at while still taking money. ShipFast's
verified profile shows MRR $0.00 and 0 active subscriptions next to $1,395 in
the last 30 days — all of it one-time sales. Read the 30-day revenue field, not
the MRR field, or you will mis-score every boilerplate, template, plugin and
desktop app in the category.

The same hole means **absence from a leaderboard is weak evidence of anything**.
Listings are founder-initiated, so these databases are self-selected by design,
and a whole one-time-purchase category can be missing because the unit of
measurement doesn't fit it. Say "not listed" rather than "no revenue".

### A second-hand number big enough to flip the verdict

When a figure turns up that would reverse your conclusion — a surprise ARR, a
funding round, an acquisition price — and it is a single second-hand claim, go
verify it before you build on it, and keep the original verdict until you have.
These claims fail in a specific way: the number is real but belongs to a
different, similarly-named company, or it conflates a parent holding company
with the product. Check for a primary source (the company's own announcement,
press coverage, a filing), and check whether the company's own pages contradict
it — a product whose About page says "bootstrapped, no investors" has already
answered a Series B rumour.

The asymmetry is the reason: a verdict only flips on evidence at least as strong
as the evidence it rests on.
