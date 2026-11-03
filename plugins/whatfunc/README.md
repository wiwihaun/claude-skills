# whatfunc

Before you build something, the people who already built it have written your
requirements document for you. Every item in their documentation exists because
a paying user needed it, which makes it more honest than a feature list written
from imagination.

`whatfunc` surveys those products and writes a build spec: every feature found,
grouped into categories that come from the material rather than a fixed taxonomy,
each one attributed to the product it came from, and each marked for whether you
can actually build it — **本地可做** / **要公開端點** / **要常駐** /
**要付費 API** / **不值得**. It ends in a recommended build order, because a spec
that stops at the inventory leaves you holding forty undifferentiated items.

## Usage

```
/whatfunc:whatfunc 社群發文
```

Name the category, and name anything you already know you want — those go into a
*known requirements* list that is excluded from the survey, because the value is
in what you have **not** thought of.

Output is `<短名>-feature-spec.md` in the current directory, in Traditional
Chinese. It refuses to write into a public repository.

## Three things it does on purpose

**It looks on your own machine first.** An installed skill ships its whole
source — scripts, reference files, schemas — not a catalog summary, and that is
the deepest documentation available anywhere in the process. On one run the
richest source in the entire survey had 271 lines of prose sitting on top of
4,197 lines of Python and 19,730 lines of XSD schemas; ranked by prose alone it
did not appear in the top eight.

**It asks each product what it does, not whether it does what you expect.**
Checking five products against your own list and reporting "none of them have
these" confirms a hypothesis instead of finding the unknown unknowns. That is
the main way a survey produces nothing.

**It hunts the destructive-failure list.** The richest thing in a mature
product's documentation is never the feature list. It is the set of oddly
specific prohibitions — this colour format corrupts the file, this offset
corrupts the file, reordering these two XML siblings makes the document
unopenable — because nobody writes those from imagination. Every line is a bug
somebody already paid for.

## What it is not

Not a buy-vs-build verdict: it assumes you have already decided to build. Not a
pricing comparison: that belongs in `find-skills`. Not a trust assessment —
popularity decides what to *install*, not what is worth *reading*. On one run the
product with 105 stars had none of the wanted capabilities and the one with zero
stars had all of them.
