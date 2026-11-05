# cover-letter-tailor

Old résumés contradict each other: a title that was later corrected, a number
rounded differently, a job still marked 「至今」 years after it ended. A cover
letter written straight from them launders those contradictions into claims an
interviewer will check. This skill keeps two things apart — what you once wrote,
and what you have confirmed is true — and writes letters only from the second.

```bash
claude plugin install cover-letter-tailor@wiwihaun-skills
```

Replies are in Traditional Chinese. The letter's language follows the job
description.

## Three modes, one folder

| Mode | Say | What happens |
| :- | :- | :- |
| **0 整併** | 「整理履歷」 | Reads every résumé version in `raw/`, merges them into a draft, and lists every conflicting date, title and number with each version's original sentence. You answer one question at a time; nothing reaches `profile/` until you do. |
| **1 寫信** | paste a JD, then 「寫求職信」 | Builds a requirements table, matches each line to evidence in `profile/` (direct, adjacent, or none), gives a verdict, writes the letter and a gap report that only you see. Saved to `applications/<公司>-<職稱>-<日期>/`. |
| **2 現況核對** | 「核對履歷」 | Walks through entries not confirmed for six months, oldest first: correct, change, ended, delete. Always ends by asking about new jobs, projects and skills. |

```
RESUME_ROOT/
  raw/            every résumé version (pdf / docx / md). Only Mode 0 opens these
  profile/        the confirmed version: resume.md, projects/*.md, skills.md,
                  writing_sample.md, CHANGELOG.md
  applications/   one folder per application
```

`RESUME_ROOT` defaults to `~/履歷資料`. For a personal install, change the one
line in `SKILL.md`. For a plugin install, where an update would overwrite that
edit, point a symlink at your real folder instead:

```bash
ln -s "/path/to/your/résumé folder" ~/履歷資料
```

## How the letter is written

- **Only facts in `profile/`.** Not what you probably did, not what anyone in
  that job would have done. A requirement with no evidence is marked 「無」 and
  stays out of the letter; the gap report lists it with a way to close it and a
  skeleton answer for the interview.
- **Relevance decides detail.** Experience in the job's own field gets the
  tools and the numbers. Experience from another field gets one sentence naming
  the method that carries over — the reader cannot weigh another field's
  machinery, and it spends the word limit on the least relevant part.
- **One storyline, not an inventory.** Each paragraph leads into the next.
  True, evidenced points that would break the line go on a 「留給面試」 list
  instead. Filling the word limit is not a goal.
- **"Why this company" uses only the JD and what you supply.** No web search —
  that would be guessing, and it would put your target employer into search
  queries.

Before anything is shown, a self-check runs: every claim maps to a line in
`profile/`, no empty virtue phrases, no run of 8+ characters copied from the JD
(`scripts/letter_check.py` counts length and finds the overlaps), the length is
within the limit, and the company name and job title match the JD character for
character.

## What it refuses to do

- **Pick the winner of a conflict.** The newest file looks authoritative, but
  it is also where a rounded figure or a title typo first appears.
- **Open `raw/` outside Mode 0**, even when an old résumé has the detail a
  thin `profile/` entry lacks.
- **Write to `profile/` without your yes.** `raw/` is never changed or deleted.
- **Upload anything.** The folder is personal data: no cloud documents, no
  artifacts, no search engine, no personal data in a URL. The letter is a local
  markdown file; convert it to docx yourself when you need one.

## Requirements

macOS: `.docx` is read with the built-in `textutil`, dates come from BSD
`date`. Python 3 for the self-check script (the system 3.9 is enough). PDFs are
read with Claude's own file reader. `.pages` files are not read — export them to
PDF or Word first.

No résumé, profile or application from any real person is in this repository.
