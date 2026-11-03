# prebuild-gate

Writing code stopped being the bottleneck, which means a weekend is now enough to
ship a product nobody buys. This gate asks the two questions that actually decide
the outcome, while they are still cheap to answer: **how does this charge**, and
**where do the first paying customers come from**.

It researches what comparable products earn in the **last 30 days** rather than
reasoning from first principles, because lifetime revenue hides a collapse
completely — a product with $1M lifetime and $2k last month is a cautionary tale
wearing a success story's clothes. Every figure is labelled for how strong its
source is: a number synced live from a payment processor beats a screenshot,
which beats a claim in a thread.

The output is a go / no-go memo in Traditional Chinese, written to
`<短名>-prebuild.md`. The most common honest verdict is "not enough evidence yet,
and here is the cheapest way to go find out". The last test in it is to write the
launch post today, before any code — if it cannot be written, something
load-bearing is missing, and that is cheaper to discover now.

## Install

```bash
claude plugin install prebuild-gate@wiwihaun-skills
```

Invoke it explicitly. It will not trigger on its own, on the grounds that a gate
you did not ask for is just friction:

```
/prebuild-gate:prebuild-gate 我想做一個 X，賣給 Y
```

Credit for the two-gate structure, and the full argument behind it, are in
[the repository README](../../README.md#prebuild-gate).
