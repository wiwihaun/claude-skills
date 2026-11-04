# fairprice

A share price is a claim about the future. This skill makes that claim explicit
enough to argue with.

```bash
claude plugin install fairprice@wiwihaun-skills
```

```
/fairprice:fairprice TSLA
```

It writes a dated report in Traditional Chinese where every assumption carries
its source, ending in a bear/base/bull range and a list of checkpoints with
dates and numeric thresholds that would prove the model wrong.

## It picks the method before it picks a number

Step 0 asks one question — *can the current price be explained by the current
earnings?* — and routes to one of three paths. Taking the wrong one is the most
expensive mistake available:

| | When | Why |
| :- | :- | :- |
| **A — sum of the parts** | P/E absurd or negative; several businesses with **separable** economics | One multiple cannot price a car plant and a software subscription together |
| **B — normalized earnings × one multiple** | P/E explicable; one business, however many end markets it serves | Splitting it would invent companies that do not exist |
| **C — finite-life NPV** | Revenue with a **legal expiry date** — patent cliff, concession, mine life, licence | A multiple assumes the earnings continue; these stop on a date you can look up |

**A revenue breakdown by end market is not a set of segments.** Before splitting
anything, it asks whether each proposed segment could be sold off on its own. If
not, it is a mix, and the right tool is one multiple on the whole.

## What it refuses to do

- **Pick a multiple without naming a peer.** The same earnings at 14× and 40×
  differ by nearly 3×, so a multiple without a source is where a valuation
  becomes whatever you wanted it to be.
- **Take management's dates at face value.** It measures how late the company
  has been before and pushes every promise back by that ratio. A clean record
  gets 1.0× — this is a measurement, not a penalty box.
- **Guess at what it cannot estimate.** A business with no shipments, no pricing
  and no disclosure gets zero in the base case and a line of its own in the
  report. Keeping it out is what separates a projection from a wish.
- **Present a searched price as live.** Free tools cannot get a reliable live
  quote, so the price is always dated and labelled.

## The failure modes are the interesting part

Each one was paid for by a wrong answer. Among them: a right answer reached by a
wrong derivation, where two errors cancelled and the product survived while every
extrapolation built on it did not; margin expansion that is really a
depreciation denominator; a price assumption that contradicts the growth
assumption that justifies it; forward numbers that turn out to have no document
behind them at all.

## Credit

The method comes from a worked Tesla model by Terry Chen 泰瑞, in
[特斯拉值多少？](https://www.youtube.com/watch?v=tKIprp9qQzY) — the four-number
segment build, the management-timeline discount, peer-anchored multiples and
falsifiable checkpoints are all his. `references/method.md` reconstructs that
method with the arithmetic checked line by line and the unverifiable claims
flagged. What this plugin adds is the path router, the normalization steps, and
the failure-mode list.

## This is not investment advice

The output is an arithmetic table with stated assumptions. It never says buy or
sell, and it is not a price prediction. A fair value of 324 means "if every cell
in this table holds, it is worth this much" — and the table exists so you can
replace the cells you disagree with and run it again.
