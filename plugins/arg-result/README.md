# arg-result

A pros-and-cons list tells you what each side would say. This tells you which
of those things are still standing after the other side has had a go at them.

```bash
claude plugin install arg-result@wiwihaun-skills
```

```
/arg-result:arg-result 現在 AI 這麼方便，資深工程師的意義在哪？ n=5
```

The proposition is everything you type; a trailing `n=K` sets the number of
rounds. Replies and the report are in Traditional Chinese.

## Three agents, strictly in turn

| Role | Who | What it sees |
| :- | :- | :- |
| Moderator | the session running the skill | everything; relays, keeps the record, stops to ask you |
| Pro / Con | one independent subagent each, kept for the whole debate | the proposition, what the other side *said*, the judge's public rulings |
| Judge | one independent subagent | every speech and the ledger; takes no side |

One side speaks, the judge rules on it, and only then does the other side get
to read it. Neither side ever sees the other's notes or research. Running both
sides in one context lets one quietly go easy on the other, and lets each
rebuttal land exactly where the writer knew it would; a separate judge exists
because debaters who rule on themselves either concede at the first push or
never concede at all.

## What counts as surviving

- **A claim survives** if it withstood at least one valid attack, or the other
  side explicitly conceded it. A claim nobody attacked is listed separately and
  does not count.
- **Narrowing is how it digs.** A claim that is hit can be narrowed to a
  version that dodges the attack; the narrowed version can survive, and the
  report shows each step of how it got there.
- **Hollow claims are thrown out.** If nothing could prove a claim wrong, or no
  one would argue the opposite, the judge rejects it. Otherwise everything would
  survive as a truism.
- **Partial concessions are split.** If a side accepts only part of the other
  side's claim, the judge splits the accepted sentence off as its own entry and
  the rest stays in dispute. Counting the whole claim as conceded would let the
  part the other side refused survive.
- **Sources are spot-checked.** The judge checks the citations carrying the
  most weight; a fabricated or misquoted source overturns whatever rested on it.
- **From round 3, no new fronts.** New claims have to dig under existing ones.
  At the end of a round the judge names a hidden premise both sides lean on,
  and the side it hurts must attack it or concede it.
- **The closing round takes no new claims.** A claim may still be narrowed
  there, but the narrowed version is marked as untested and does not count
  unless the other side concedes it.

In the test run on the example above, "senior engineers matter because of
organisational knowledge" was narrowed twice, ending at "someone still has to
own decisions whose results take years to show, and that is who a senior
engineer is expected to be". The claim that experience makes those decisions
*better* did not make it.

## When it stops to ask

Only when it has to: a term in the proposition with two readings that would
have the sides arguing different things; a premise inside the question that is
itself the main dispute; an undecided point that goes two rounds without
progress; a rule gap the judge flags that you have not already decided. A
dropped network connection is retried once on its own.

## Cost

It is slow on purpose. By default it runs up to 5 rounds (at least 3, ending
early when a whole round changes nothing): about 10 debater speeches and 11
rulings, each with web search. A 3-round run took about 75 minutes and a
5-round run about 1 hour 45 minutes.

## Output

`./arg-result/<proposition>-<date>.md`, asking first if the current directory
is a git repository:

- what is left at the bottom, in the judge's words, each sentence tied to a
  claim number
- surviving claims grouped by what rests on what, each with the attacks it
  withstood and how it evolved
- the disputes that stayed open, and what evidence would settle them
- every claim that was overturned, withdrawn or replaced
- the full transcript

Working files go in the session's scratchpad, not your project.

## Requirements

Claude Code with subagents. `SendMessage` keeps each debater's context between
turns; without it the skill respawns a debater every turn from the written
record, which gives the same result more slowly. Web search is used for
evidence.
