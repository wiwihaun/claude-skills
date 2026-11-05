---
name: cover-letter-tailor
description: >-
  Tailor job applications from one private résumé folder, in three modes that share it.
  Mode 0 (整併): merge every résumé version in raw/ into one user-confirmed profile/, listing
  conflicting dates, titles and numbers instead of picking one — use for 「整理履歷」「更新履歷資料」
  「合併我的履歷」, or when profile/ is missing or empty or raw/ has new files. Mode 1 (寫信): from a pasted
  job description, build a requirements table, an evidence map, a fit verdict, a cover letter and
  a private gap report, using only facts already in profile/ — use whenever the user pastes a JD,
  職缺 or job posting with 「寫求職信」「看看我適不適合」「分析這個職缺」「這個能投嗎」「cover
  letter」, even if they only paste the posting. Mode 2 (現況核對): walk through stale profile
  entries one by one and update them — use for 「核對履歷」「檢查現況」「哪些該更新」「履歷要更新嗎」,
  or when Mode 1 finds entries not confirmed for over six months. Output is local markdown only;
  the folder is never uploaded, shared or searched.
---

# cover-letter-tailor

One folder of personal résumé material, three modes that share it:

| Mode | 名稱 | What it does | Opens | Writes |
|---|---|---|---|---|
| 0 | 整併 | merges every résumé version into one confirmed profile | `raw/` | `profile/`, only after the user confirms |
| 1 | 寫信 | JD → requirements, evidence, verdict, letter, gap report | `profile/` | `applications/` |
| 2 | 現況核對 | walks through stale profile entries one by one | `profile/` | `profile/`, each answer being the confirmation |

The design rests on one separation: **`raw/` is what the user once wrote;
`profile/` is what the user has confirmed is true.** Old résumés contradict each
other — a title that was later corrected, a number rounded differently, a job
still marked 「至今」 three years after it ended. A letter written from `raw/`
launders those into claims an interviewer will check. So Mode 1 never opens
`raw/`, and nothing reaches `profile/` without the user's yes.

Templates live in `references/`:

- `references/profile-templates.md` — field layout of every file in `profile/`, plus `CHANGELOG.md`
- `references/review-template.md` — `REVIEW.md` for a first run and for an incremental run
- `references/application-templates.md` — `requirements.md`, `cover_letter.md`, `gap_report.md`, and the chat output for Modes 1 and 2

`scripts/letter_check.py` does the mechanical half of Mode 1's self-check.

> **Maintenance note — never write a dollar sign immediately before a digit in
> this file.** Slash-command invocation replaces a dollar sign followed by a
> positional index with whatever the user typed after the command. The
> corruption lands inside the instructions being executed and raises no error.
> Salaries and amounts in examples are written `USD 300` or `TWD 60,000`.
> Self-check, which must print nothing:
>
>     grep -nE '(NT)?[$][0-9]' SKILL.md

## The folder

`RESUME_ROOT` = `~/履歷資料` — the only machine-specific line in this skill.
Change it to the folder you keep your résumé material in. If it does not
exist, Step 0b stops and asks before creating anything.

```
RESUME_ROOT/
  raw/              every résumé version (pdf / docx / md). Only Mode 0 opens these
  profile/          the single confirmed version. Mode 1 reads only this
    resume.md           學歷與經歷；每條目：時間／單位／職稱／職責／成果數字／last_confirmed
    projects/*.md       一個專案一檔：背景／我的角色／做了什麼／技術或方法／結果（數字）／證據連結／last_confirmed
    skills.md           技能與熟練度（會用／做過產品／能教人）＋證照，每條含 last_confirmed
    writing_sample.md   the user's own prose, used only to match tone
    REVIEW.md           Mode 0's draft and conflict list (deletable once confirmed)
    CHANGELOG.md        every change: 日期／條目／改前／改後, plus the raw/ snapshot
  applications/     one folder per application
```

## Ground rules — every mode

1. **The folder is private.** Never upload, publish, share or search with its
   contents. Concretely: no web search or fetch containing anything from it —
   the letter's "why this company" paragraph uses only the JD and what the user
   supplied, so there is nothing to search for anyway; no artifacts, no docs
   connector, no Google Drive, no cloud session; no personal data in a URL.
   General-purpose document skills may claim "cover letter" as theirs — this
   skill's letter is a local markdown file in `applications/`, full stop. If the
   user later asks for docx, convert locally and only then.
2. **`raw/` is read-only, forever, and only Mode 0 opens its files.** Modes 1
   and 2 may list names, sizes and modification times to notice new files. They
   never open one, not even "just to check a number".
3. **`profile/` changes only with the user's confirmation.** The one exception
   is Mode 0 writing `REVIEW.md`, which is a draft by definition.
4. **Ask before acting in exactly three cases:** the folder is empty or its
   structure does not match; the JD's language differs from the language the
   user asked for; the JD is too short to extract requirements from. Otherwise
   proceed, and state every assumption at the top of the output.
5. **Reply in Traditional Chinese.** The letter's language follows the JD
   (including simplified vs traditional script — note it in the assumptions).
6. **Scratch files stay out of the folder.** Text extracted from PDFs and docx
   goes in a `mktemp -d` directory outside `RESUME_ROOT` and is deleted at the
   end of the run — it is personal data.
7. **Name what you write before writing it.** One line — which files, where.
   Only `profile/` writes wait for a yes.
8. **Dates come from the shell.** Today: `date +%F`. The six-month cutoff:
   `date -v-6m +%F` (macOS; for N months, `date -v-<N>m +%F`). `last_confirmed`
   is always `YYYY-MM-DD`.

## Step 0 — Route, then check the folder (every invocation)

### 0a. Pick the mode

| Situation | Mode |
|---|---|
| 「整理履歷」「更新履歷資料」, or the skill invoked with nothing else | 0 |
| A JD pasted with 「寫求職信」「看看我適不適合」「分析這個職缺」, or a JD pasted alone | 1 |
| 「核對履歷」「檢查現況」「哪些該更新」 | 2 |
| `profile/` missing, or has no `resume.md` | 0 first, then the requested mode |
| `raw/` has unprocessed files and no other mode was asked for | 0 |

When `raw/` has unprocessed files but the user asked for Mode 1 or 2, do not
switch. Mode 1 notes it in the assumptions line; Mode 2 reminds at the end.

"Unprocessed" means a file whose name, size or modification time does not match
the `raw/ 快照` table at the bottom of `profile/CHANGELOG.md`. List without
opening anything:

```bash
cd "<RESUME_ROOT>/raw" && find . -type f ! -name '.DS_Store' \
  -exec stat -t '%Y-%m-%d %H:%M' -f '%N%t%z%t%Sm' {} +
```

### 0b. Check the structure

- `RESUME_ROOT` missing, or `raw/` missing or empty → **stop.** Say what you
  found and ask whether to create empty `raw/`, `profile/`, `applications/`.
  Create nothing without a yes. If résumé files sit elsewhere in the folder,
  say so and let the user move them — do not move them yourself.
- `profile/` missing or empty → normal before the first Mode 0, which creates it or fills it (say so).
- `applications/` missing when Mode 1 needs to save → structure mismatch; ask.
- Anything else at the root (loose files, other folders) → mention once; do not
  read, move or count it.

## Mode 0 — 整併與確認

### 0.1 Inventory and extract

Open every file in `raw/` (first run) or only the new and changed ones (see 0.6).

| Format | How |
|---|---|
| `.md` | read directly |
| `.docx` | `textutil -convert txt -stdout "<file>" > "<TMPDIR>/<n>.txt"` (built into macOS) |
| `.pdf` | the Read tool with `pages`. No text layer means a scan: transcribe from the page images and mark the file 「掃描檔」 so the user double-checks its numbers |
| anything else (`.pages`, `.doc`, images…) | do not guess. List it under 未讀取 with how to export it — Pages: 檔案 → 輸出為 → PDF 或 Word |

For each file record a **version date**: a date stated in the document itself
(「更新於 2026/10」, a header or footer date) first; otherwise the file's
modification time. Record which one you used (日期來源：檔內／修改時間) —
copying a file resets its modification time, and the user can only catch a
wrong version order if they can see where the date came from.

Sort the versions by date. **最新兩版** are the two newest. With two or fewer
files nothing counts as old, so [可能過時] and [仍會用嗎？] cannot fire — say so
in `REVIEW.md` rather than silently showing empty lists.

Extract every entry — 學歷、經歷、專案、技能、證照 — with its source filename,
version date and the original sentence.

### 0.2 Merge into a draft

Same entry means: same organisation with an overlapping period (經歷、學歷);
the same project (專案); the same skill after normalising spelling ("Python 3"
= "Python"); the same certificate. **If you cannot tell whether two items are
the same entry, do not merge** — list it as a conflict titled 「同一條嗎？」.

Then apply the user's rules exactly:

- **Same entry in several versions → merge, keep the most complete
  description** — the one with more specific facts, not more adjectives.
- **Time, title or numbers differ → conflict, never your pick.** List every
  version's original sentence with its source; the draft shows `⟨衝突 N⟩` in
  that field. "Numbers" means any figure — percentages, headcount, revenue,
  durations, GPA. 「約 30%」 vs 「32%」 is a conflict too; the user decides
  which is true.
- **Entry only in older versions (not in the newest two) → [可能過時].**
- **「至今」「present」「迄今」「現在」 → [確認現況].**
- **Skill only in older versions → [仍會用嗎？].**

Where things go: 學歷 and 經歷 → `resume.md`; 專案 → `projects/<slug>.md`;
技能 and 證照 → `skills.md`.

Résumés rarely state proficiency as 會用／做過產品／能教人. Leave 熟練度 as `？`
with a suggestion and its reason from the draft's own entries (「建議：做過產品 —
<專案> 用它上線」). The user decides.

`writing_sample.md` is not extracted from résumé bullets — bullets are not the
user's voice. If a raw file has a 自傳 or other prose paragraph, offer it as a
candidate in `REVIEW.md`; otherwise ask for one in 0.5.

### 0.3 Write `REVIEW.md`

Say you are creating `profile/` (if absent) and `profile/REVIEW.md`, then write
it from `references/review-template.md`: files read and not read, the conflict
list (numbered, every version's wording, source), the three marker lists, and
the full draft with a checkbox before every entry.

### 0.4 Stop and wait

Tell the user in Chinese: how many conflicts, how many of each marker, where
`REVIEW.md` is, and the two ways to answer — edit the file directly, or answer
here one question at a time. Then stop.

**Answering here.** Conflicts first, **one per question**, with
AskUserQuestion when available: each distinct wording is an option (label = the
value, description = source file and version date), plus an option
「以上皆非，我來改」. Identical wordings from several files collapse into one
option listing all sources. The tool holds four options; with more than three
distinct versions, list them in text and ask in plain text. Then the markers,
one per question:

| Marker | Options |
|---|---|
| [可能過時] | 保留／刪除／要改（我說） |
| [確認現況] | 仍在進行／已結束（問結束年月）／要改（我說） |
| [仍會用嗎？] | 仍會用／已生疏／刪除 |

**Editing the file.** When the user says they are done, re-read `REVIEW.md` and
take their edits verbatim. Ask once about every entry left unticked (收／不收)
and every conflict still open.

Never resolve a conflict yourself, even when one version is obviously newer.
Newer résumés also carry typos and rounded numbers.

### 0.5 Promote to `profile/`

Once every conflict is resolved and the user confirms:

1. Write `resume.md`, `projects/*.md`, `skills.md` from
   `references/profile-templates.md`. Every entry gets `last_confirmed` = today.
2. `writing_sample.md`: if it does not exist, ask the user to paste a paragraph
   they wrote themselves (or confirm the 自傳 candidate). Write only their text.
   If they skip it, leave it absent — Mode 1 will say so.
3. `CHANGELOG.md`: append a dated section (first run: every entry as 新增), and
   rewrite the `raw/ 快照` table — name, size, modification time, first 12
   characters of `shasum -a 256`, version date, date source.
4. Leave `raw/` exactly as it was. Delete the scratch directory.
5. Tell the user `REVIEW.md` can now be deleted; delete it only if they say so.

### 0.6 Later runs

1. Compare `raw/` against the snapshot. New = name not in the table. Changed =
   same name, different hash. Unchanged files are not reopened.
2. Extract only the new and changed files, and diff each entry against the
   current `profile/` — not against old raw files:
   - **新增** — no matching entry in `profile/`.
   - **變更** — matching entry, different content. Time, title and number
     changes become conflicts exactly as in 0.2.
   - **消失** — an entry in `profile/` that the newest résumé no longer has.
     Judge this only when a new or changed file is among the newest two
     versions, and propose [可能過時] rather than deletion.
3. Write `REVIEW.md` from the incremental template, stop, confirm as in 0.4,
   apply as in 0.5.

## Mode 1 — 寫求職信

**Input:** the full JD. Optional: target language, length limit, extra company
information, points to stress or avoid. **Defaults:** language follows the JD;
Chinese up to 350 字, English up to 300 words.

Ask first (rule 4) if the JD's language differs from the language the user
specified, or if the JD is too short to extract requirements. Everything else
you assume goes in a 假設 block at the top of the output.

### 1.0 Check `profile/`

- `profile/` missing, or has no `resume.md` → run Mode 0 first.
- Read every file in `profile/` **except `REVIEW.md`** (unconfirmed draft) and
  `CHANGELOG.md` (history, not evidence).
- List every entry whose `last_confirmed` is before the six-month cutoff. Keep
  the list; the question about it comes after 1.4, once you know which entries
  the letter leans on.
- `writing_sample.md` missing → assumption line, plain first-person tone.
- `raw/` has unprocessed files → assumption line (「raw/ 有 N 個未整併的新檔，這封信沒用到」).

### 1.1 Parse the JD

One requirement per row; split compound bullets (「熟悉 Python 與 SQL」 → two
rows). Each row gets:

- **必備／加分** — 必備 for required / must / 須 / 至少 / 必要, or anything under
  條件、Requirements、Qualifications; 加分 for preferred / plus / nice to have /
  佳 / 優先 / 加分. If the JD labels nothing, judge from placement and say so in
  the assumptions.
- **Type** — 硬技能／軟技能／領域知識／年資／語言／其他.
- The JD sentence it came from.

Then a separate list of **隱性要求**: what the duties imply but the JD never
states, each with the duty sentence it comes from. 「跨部門協調」 implies
explaining technical work to non-technical people; 「從零建立」 implies working
without a spec. These get evidence like any requirement, but are **not counted
in coverage** — they are your inference, and the score should not move on it.

### 1.2 Match evidence

Every requirement, explicit or implied, gets one level:

- **直接證據** — `profile/` shows the user doing this thing: the same skill,
  tool, task or domain.
- **相鄰證據** — the same kind of task with a different tool, domain or scale.
- **無** — nothing in `profile/`.

Each row cites `profile/<file>:L<line>` and quotes the sentence. **Only facts in
`profile/` count.** Not what the user probably did, not what anyone in that job
would have done, not what an old résumé in `raw/` said. If it is not there, the
level is 無. A `skills.md` line proves the skill exists but carries no result;
the letter's "result" half needs a `resume.md` or `projects/` line.

### 1.3 Score

- 必備 coverage: direct a/n, direct-or-adjacent b/n.
- 加分 coverage: the same.
- Verdict, with one sentence of reasoning. Guidance, not a formula:
  - **建議投** — every 必備 has evidence, most of it direct.
  - **可投但要補強** — some 必備 only adjacent, or one 必備 with none that is not a hard gate.
  - **不建議** — a hard gate (years, certificate, language, degree stated as required) at 無, or several 必備 at 無.

### 1.4 Choose the themes

Pick **3–4 themes at the intersection of what the JD weighs most and where the
evidence is strongest.** JD weight: 必備, listed first, repeated, in the title
or summary. Evidence strength is **relevance first, then directness**. Mark each
theme 同領域 (the experience is in the JD's own field or uses its tools) or
可轉移 (another field; only the method carries over). A 同領域 entry beats a
可轉移 one however many numbers the latter has — a number from an unrelated
field proves nothing this employer can weigh. Within the same relevance: direct
with a number > direct without > adjacent. The mark decides how 1.5 writes the
theme.
其餘有證據的點最多一句帶過 — in a 350-字 letter that is one sentence covering
them together. Points with no evidence never enter the letter.

**Then pick one storyline.** Order the themes so each one leads to the next
(最相關的經歷 → 「除了這個，我也……」接第二段相關經歷 → 別的領域的一句總結 →
為什麼是這家公司). A theme that cannot be linked to its neighbours is dropped, even with
direct evidence, and so is "其餘" when it would break the line — 最多一句 includes
zero. Dropped points go on the 留給面試 list in `requirements.md`, so the user
knows they were left out on purpose.

**Now the staleness question.** If any theme rests on an entry from 1.0's
stale list, ask once, listing those entries and their dates: 「現在核對（進模式
2）」 or 「照用」. 現在核對 → run Mode 2 scoped to those entries, then redo 1.4
with the updated profile. 照用 → the output opens by naming them as not recently
confirmed.

### 1.5 Write the letter

From `references/application-templates.md`:

- **Structure.** Open with the single strongest concrete result *for this JD*
  (relevance first) and name the position → 2–3 paragraphs, each answering one
  必備 requirement as "requirement → what I did → the resulting number" (the
  number only for 同領域 themes) → one paragraph on why this
  company, **using only the JD or what the user supplied** — if neither says
  anything specific, keep it short and anchored to the JD's own description of
  the work; never fill it from general knowledge about the company → one closing
  sentence with a concrete next step.
- **Tone.** Match `writing_sample.md`: sentence length, formality, connectives,
  how the user opens a point. Borrow the voice, not the content. First person,
  plain declarative sentences, neither humble nor boastful.
- **One storyline, not an inventory.** Each paragraph opens by connecting to
  the one before (「除了這個，我也……」). One paragraph carries one theme;
  never chain three unrelated duties in a sentence because each covers a
  requirement. Filling the word limit is not a goal — stop when the story is
  told.
- **Detail follows relevance.** 同領域 themes get the specifics: tools, scale,
  the number. A 可轉移 theme gets one sentence naming the method that carries
  over, not its field's machinery. For a 後端工程師 JD, a marketing-analytics
  project becomes 「獨立完成一套分析流程，先小規模驗證、再全面上線」 — no 轉換率
  模型, no A/B 檢定, no 信賴區間. The reader cannot weigh those details, and they spend the word
  limit on the least relevant part of the letter. The summary must still map
  to a `profile/` line and claim no more than that line says.
- **Gaps.** A 必備 with only adjacent evidence may get one strategic sentence
  (「雖未在生產環境用過 X，但以 Y 完成過同類任務」). Every other gap stays out
  of the letter — the gap report is where gaps live.
- **Format.** Markdown. No address block, no date line, no layout clutter.
  Sign off with 〔姓名〕.

### 1.6 Write the gap report

From `references/application-templates.md`, for the user only. Every
requirement at 無 or 相鄰 gets: the requirement; severity (必備缺口／加分缺口);
the closest thing the user has (with its source, or 「無」); a way to close it
— a small project doable in days, a course, a certificate, or reframing
existing experience — specific enough to start tomorrow; and a skeleton answer
for when an interviewer asks.

End with **things this JD mentions that the user may have done but `profile/`
does not show** — inferred from the JD plus adjacent entries, phrased as
questions. Nothing on this list touches the letter or `profile/` until the user
confirms; confirmed items go through Mode 2's new-entry questions (2.4).

### 1.7 Save

Folder: `applications/<公司>-<職稱>-<YYYYMMDD>/`. Replace `/`, `:` and spaces
with `-`; keep Chinese characters. If the folder exists, append `-2`. Files:

- `jd.md` — the JD verbatim, plus any optional inputs the user gave
- `requirements.md` — requirements table, evidence map, score, themes, and the source of every claim in the letter
- `cover_letter.md` — the letter alone
- `gap_report.md`

### 1.8 Self-check, then output

Check the saved files, fix, overwrite, and repeat until all pass. Only then show
anything.

1. Every claim in the letter maps to a line in `profile/` — the claim table in
   `requirements.md` must cover every sentence that states a fact about the user.
2. No empty virtue phrases: 「我是一個努力且有熱忱的人」「具備良好的溝通能力」
   「passionate」「hard-working」「team player」. If the sentence would fit any
   applicant, cut it.
3. No verbatim copying from the JD. Run:

   ```bash
   python3 -I "<skill base directory>/scripts/letter_check.py" \
     "<folder>/jd.md" "<folder>/cover_letter.md" --limit <上限> --lang <zh|en>
   ```

   `<skill base directory>` is the path printed at the top of this skill when
   it loads — `~/.claude/skills/cover-letter-tailor` for a personal install,
   the plugin cache for a plugin install.

   It prints the length and every run of 8+ tokens shared with the JD (a token
   is one CJK character or one Latin word). The company name, the job title and
   bare tool names may repeat; rewrite everything else it flags.
4. Length within the limit — the script's count, not an estimate. Chinese counts
   CJK characters plus each Latin word or number as one 字; English counts words.
5. Language and script match the JD (or what the user specified).
6. Company name and job title spelled exactly as in the JD, character for character.
7. Every technical detail and number belongs to a 同領域 theme; each 可轉移
   theme is one summary sentence.
8. Read it top to bottom as the hiring manager. Every paragraph follows from
   the one before; cut any sentence that is there only to tick off another
   requirement.

Then reply using the chat layout in `references/application-templates.md`:
假設 block first, then the stale-entry notice if the user chose 照用, verdict,
themes, the letter, the gap report, and where the files were saved.

## Mode 2 — 現況核對

**Scope:** 全部／超過 N 個月／one category (經歷、學歷、專案、技能、證照), or a
combination (「專案，超過 3 個月」). Default: entries whose `last_confirmed` is
more than six months old. Entries with no `last_confirmed` count as oldest.

### 2.1 List

Every entry in scope, oldest `last_confirmed` first: a one-line summary, its
`last_confirmed`, and its last change from `CHANGELOG.md` (date and what), or
「無紀錄」.

### 2.2 Ask one entry at a time

| Category | Options |
|---|---|
| 經歷、學歷、專案、證照 | 正確／要改（我說）／已結束（問結束日期）／刪除 |
| 技能 | the same plus 已生疏 |

With AskUserQuestion (four options plus a free-text box): for skills, put
正確／已生疏／要改／刪除 on the buttons and say in the question that 已結束 can be
typed in the free-text box. For every entry, say the user may type
「以下全部正確」 there to confirm everything remaining at once.

- **要改** — write the user's words into the field. If you had to restructure
  them into fields, show the resulting entry and confirm before writing.
- **已結束** — ask the end month (YYYY-MM) and replace 「至今」. Projects have no
  time field: append 「（已於 YYYY-MM 結束）」 to 背景. A certificate that ended
  has expired; record the expiry month.
- **已生疏** — append 「（已生疏）」 to the 熟練度.
- **刪除** — remove the entry (a project's whole file). Its full text goes into
  `CHANGELOG.md` as 改前, so nothing is lost.

### 2.3 Write after each answer

Update `profile/` immediately, set `last_confirmed` = today, append to
`CHANGELOG.md`. A batch 「以下全部正確」 is one changelog line listing the entries.

### 2.4 Three closing questions — always

Even after 「以下全部正確」, and even when Mode 1 sent you here:

1. 有沒有新的工作或職務變動？
2. 有沒有新專案？
3. 有沒有新技能或證照？

For each yes, build the entry on the spot, asking for **every field** of its
file's template (`references/profile-templates.md`). Do not fill a field
yourself; 「無」 is a valid answer only when the user gives it. Show the
finished entry, confirm, write it with `last_confirmed` = today, log it as 新增.

### 2.5 New files in `raw/`, then the summary

Check `raw/` with the listing command from Step 0a. If there are unprocessed
files, say the user can run Mode 0 (「整理履歷」) — do not run it. Close with the
Mode 2 summary template: 確認 N 條、修改 M 條、刪除 K 條、新增 J 條, and how many
entries are still older than the six-month cutoff.

## Failure modes

**Picking the winner of a conflict.** The newest file looks authoritative, so
its number gets used. But the newest file is also where a rounded figure or a
title typo first appears. Time, title and numbers are always the user's call —
that is the reason Mode 0 exists.

**Writing what the user "obviously" did.** A data analyst "must have" used
Excel; an engineer "surely" did code review. If `profile/` does not say it, the
evidence is 無 and it stays out of the letter. Put it on the gap report's
"你可能做過" list instead — that is how it gets into `profile/` legitimately.

**Opening `raw/` outside Mode 0.** Mode 1 finds a thin entry and an older résumé
had more detail. Using it skips the confirmation step that made `profile/`
trustworthy. Say the entry is thin, suggest Mode 2, and use only what is there.
The same goes for `REVIEW.md`: it sits in `profile/`, but it is unconfirmed.

**Sending the letter to a cloud document.** Document skills and connectors
present themselves as the default for any letter. Here the letter is
`applications/<…>/cover_letter.md`, on this machine. The folder's contents go to
no upload tool, no search engine, no URL.

**Researching the company.** Search-engine knowledge about the company is
exactly the "瞎猜" the user ruled out, and searching would put their target
employer and résumé context into queries. The paragraph uses the JD and what
the user supplied.

**Fitting in everything true.** After `profile/` gained five more duties from
a gap report's 「你可能做過」 list, the next letter fitted all of them in — 347
of 350 字, every sentence traceable, and the user found it disjointed: it read
like a skills list. The rewrite kept one storyline, left the rest for the
interview, and stopped at 296 字. More evidence is not a reason for more
sentences.

**Carrying another field's details into the letter.** A letter for an IT role
spent a whole paragraph on a side project's statistical validation — the test
design, the fold count, the confidence level. The details were true and
traceable, and still wrong: the hiring manager needs to know the user validates
before going live, not how a model in another field was cross-validated. The
user's correction was to keep only the summary 「先驗證、再上線」. Specifics
belong to 同領域 themes; the rest waits for the interview.

**Parroting the JD.** Mirroring the JD's phrasing feels tailored and reads as
copied. The script catches long runs; you catch the rest by restating each
requirement as something the user did. Its length count matters too — mixed-in
numbers and English tool names push a 350-字 letter 20% over without looking it.

**Trusting modification times silently.** A résumé copied to a new disk gets
today's date and jumps to "newest". Always show the date source so the user can
spot it.

**Guessing at an unreadable file.** A `.pages` file or a scan with no text layer
is not a reason to infer contents from the filename. List it as 未讀取 or
「掃描檔」 and tell the user how to give you something readable.
