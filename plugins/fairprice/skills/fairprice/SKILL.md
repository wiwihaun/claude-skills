---
name: fairprice
description: >-
  Estimate what a stock is worth with a sum-of-the-parts model — split the company into business
  segments, project each one to a target year as 量×價×利潤率×稅×本益比, sum them, add net cash,
  divide by the future share count, then discount back to today. Use this whenever the user names
  a stock ticker and asks what it is worth — "合理價", "值多少", "估值", "現在買貴不貴", "該買嗎",
  "目標價", "fair value", "what's TSLA worth", "is NVDA overvalued", "price target" — or invokes it
  by name. Also use it when they want an existing valuation checked or a thesis pressure-tested.
  Produces a dated Traditional Chinese report where every assumption carries its source, with a
  bear/base/bull range and falsifiable checkpoints. It is a calculation whose assumptions the user
  can argue with, not a buy/sell recommendation and not a price prediction. Picks between two
  methods: sum-of-the-parts when the price cannot be explained by current earnings, and
  normalized-earnings × one multiple when it can.
---

# fairprice

A share price is a claim about the future. This skill makes that claim explicit
enough to argue with: it writes down what has to be true for today's price to
make sense, and prices each piece separately.

The method comes from a worked Tesla model — see `references/method.md` for the
full derivation. Two filled-in examples, one per path:
`references/worked-example-tsla.md` (Path A, sum of the parts) and
`references/worked-example-tsm.md` (Path B, one multiple). Their closing
comparison is worth reading before you pick a path.

> **Maintenance note — never write a dollar sign immediately before a digit in
> this file.** Slash-command invocation replaces a dollar sign followed by a
> positional index (zero for the first argument, one for the second, and so on)
> with whatever the user typed after the command. An amount written with a
> dollar sign and a one was silently rewritten to the second argument plus
> ".4T", and the Step 5 rule that says to value something at zero became a rule
> to value it at the ticker. The corruption lands inside the instructions being
> executed and raises no error at all.
>
> Write amounts as `USD 324` and `TWD 2,100` instead. Self-check, which must
> print nothing:
>
>     grep -nE '(NT)?[$][0-9]' SKILL.md

## What this is and is not

- **Not a recommendation.** The output is an arithmetic model with stated
  assumptions. It never says buy or sell. If the user wants that, the honest
  answer is that no model gives it to them, and you are not their advisor.
- **Not a prediction.** `USD 324` is not where the stock will go. It is what the
  stock is worth *if* the assumptions in the table hold, and the table exists so
  the user can replace the ones they disagree with.
- **Not a screener.** This takes real work per company. Say so up front.
- **Free tools only.** SEC EDGAR, TWSE / TPEx open data and MOPS, company IR
  pages and web search. No paid data
  API, no key. See *Where the numbers come from* for what that costs you.

## Step 0 — Pick the path

Ask one question before any research: **can the current price be explained by
the current earnings?**

| What you see | Path | Why |
|---|---|---|
| P/E absurd or negative; several businesses with **separable** economics; the story is about something that does not exist yet | **A — sum of the parts** | One multiple cannot price a car plant and a software subscription together, and most of the value sits in businesses with no earnings yet |
| P/E explicable; one business (however many end markets it serves); earnings real and growing | **B — normalized earnings × one multiple** | Splitting it would invent companies that do not exist. The question is not *what are the parts worth* but *what does it earn through a cycle, and at what multiple* |
| Revenue with a **legal expiry date** — patent cliff, concession, mine life, power-purchase agreement, licence | **C — finite-life NPV** | A multiple assumes the earnings continue. These stop on a date you can look up, so you model the remaining years and never apply a terminal multiple |

Tesla, 2026-09: earning USD 6.1B, valued at USD 1.4T, P/E ≈ 200 → **Path A**.
TSMC, 2026-11: forward P/E ≈ 19–21, net margin 51%, revenue +41% → **Path B**.

Path A is Steps 1–2, Path B is Step 2B, Path C is Step 2C.
**From Step 3 on A and B are identical; C skips Step 3 entirely.**

**Say which path you took and why in the report's first lines.** Taking A for a
company that deserves B is the most expensive mistake available here: it produces
a detailed table that looks rigorous and is built on companies that do not exist.
Taking B for a company that deserves A hides the whole question inside one
multiple nobody can defend.

**Then fix three things with the user before you start:**

| | What to settle | Default if they shrug |
|---|---|---|
| 目標年 | How far out to model | 4 years |
| 折現率 | What return they want for the risk | 12% |
| 情境權重 | bear / base / bull | 25 / 50 / 25 |

These three are quietly as powerful as any multiple in the table, and almost
nobody argues about them. Put them in the report header so they can be argued
about.

## Step 1 — Path A only: split the company into segments

**Use the company's own segment reporting.** Do not invent categories; the
10-K/20-F already tells you how management runs the business, and inventing your
own split is how a segment gets double-counted or lost.

Two rules:

- A segment that is a *different kind of business* gets its own line even if the
  company lumps it in. Hardware sold once and software billed monthly cannot
  share a multiple.
- A segment with **no data at all** does not get a made-up number. It goes to
  Step 5.

**A revenue breakdown by end market is not a set of segments.** This is the
distinction that decides whether the whole model applies. Segments deserve
different multiples only when their economics are *separable* — their own cost
structure, their own assets, their own margin. TSMC reports revenue as HPC 68% /
smartphone 21% / IoT / automotive, but those are demand categories served by one
shared fab network at one blended margin: a wafer is a wafer. Give them separate
multiples and you have invented five companies that do not exist. Before
splitting, ask of each proposed segment: **could it be sold off on its own?** If
not, it is a mix, and the right tool is one multiple on the whole.

## Step 2 — Path A only: four numbers per segment

```
量 × 價 = 營收
營收 × 利潤率 = 營業利益
營業利益 × (1 − 稅率) = 稅後利益
稅後利益 × 本益比 = 這塊業務的價值
```

**Do not skip the tax line.** It sits between operating income and the multiple,
it is worth about 15% of the answer, and it is the single most commonly dropped
step in this model.

## Step 2B — Path B only: normalize the earnings

**Never multiply today's earnings by a multiple.** A company at a growth peak is
usually also at a margin peak, and peak × peak is a number that has never been
true and will not become true. Path B is almost entirely this one step — get it
right and the rest is arithmetic.

Two normalizations, in this order.

### 2B-1 — Growth: read the long-horizon guidance against the near-term guidance

Companies publish a multi-year CAGR and a current-year number in different
places, and almost nobody puts them in the same table. When the near term runs
hot, **the long-run CAGR silently requires the out-years to slow** — and the size
of that slowdown is management's own forecast, which they never state out loud.

```
隱含剩餘年成長 = ( 基準年 × (1+長期CAGR)^N ÷ 最近一年實績 ) ^ (1/(N−k)) − 1
                 N = 長期財測涵蓋年數，k = 基準年到最近實績的年數
```

TSMC, 2026-11: base year 2024 USD 90.08B, guided ≈25% CAGR to 2029, 2026E USD 176.3B
after a +44% year → the remaining three years imply **16%/yr**. Management said
25% and said 44%. They never said 16%, and 16% is the number the model needs.

Where no long-horizon guidance exists, say so and build the path from the
industry's own history — never from the current year extended forward.

### 2B-2 — Margin: find the gap to management's own through-cycle target

Today's margin against the target the company publishes for itself, plus any
dilution it has already quantified.

Then work *down the income statement* with two ratios held constant, instead of
guessing a net margin directly:

```
目標毛利率 − 營業費用率 = 營業利益率
營業利益率 × (淨利 ÷ 營業利益) = 淨利率
```

Holding the opex ratio and the operating-to-net conversion is what keeps this
honest: you are changing **one** assumption, not three. State both ratios and
where you read them.

TSMC, 2026-11: gross margin 66.4% today against a published "56% and higher
through the cycle", with overseas-fab dilution quantified by the CFO at 2pp in
2026 widening to 3–4pp from 2027. Base took 60% — regression admitted, but held
above the company's own floor.

**When no target is published, the company's own multi-year record IS the
through-cycle anchor** — and it is often better evidence than a target, because
it is what happened rather than what was promised. Pull ten-plus years of annual
operating margin from the filings before concluding that today's level is
structural. LandMark 3081, 2026-11: operating margin 49.4% looked like a
breakout until the FY2014–2025 series showed 54.1% / 57.7% / 49.7% in
2014–2016 — the company had earned *more* than this before, then decayed for
eight straight years to −26.4%, and its EPS eleven years earlier (14.89) was
within 5% of today's (15.68). The twelve-year mean was 26.3%. None of that is in
any guidance document; all of it is in the annual filings.

### What Step 2B produces

**One number: normalized earnings in the target year.** Before moving on, say
whether it grows faster or slower than revenue. If margin is compressing,
earnings growth is slower than revenue growth, and that single line is usually
the most important sentence in a Path B report.

Because Path B has exactly one multiple, there is nowhere to hide an assumption —
so **the sensitivity table in the report is mandatory, not optional.**

Then rejoin at Step 3.

## Step 2C — Path C only: model the remaining life

**A multiple assumes perpetuity.** Use one only where the earnings have no known
end date. When revenue expires on a date you can look up, applying any multiple
to the final year values decades of earnings that will not exist.

How to tell: ask **when does this revenue lose its legal protection?** A patent,
a concession, a mine's reserves, a power-purchase agreement, a licence, a
rent-controlled lease — each gives a date, and that date is usually in the
filings rather than in any summary.

Then build it year by year to that date and past it:

1. **Find every expiry and its source.** Drugs have several patents of different
   strength — composition-of-matter is the one that matters; formulation and
   method-of-use patents are routinely designed around, so they belong in the
   bull case, not the base. Say which you relied on.
2. **Model the decline, not a cliff to zero.** Small-molecule drugs typically
   lose 75–90% of revenue within two years of generic entry; other asset types
   differ. Use a number and name where it came from.
3. **Let the cost base follow the revenue.** A company losing its main product
   cuts the sales force. Flat costs against collapsing revenue manufactures a
   loss that will not happen; unchanged costs is an assumption, not a default.
4. **Terminal value after the last expiry: zero**, by the Step 5 rule — and say
   out loud that this understates value, because it does. The gap between that
   zero and the market price is the most informative number in the report.

ACADIA, 2026-11: NUPLAZID composition-of-matter patent to 2030 on 61% of
revenue; DAYBUE use patent to 2032, extendable to 2036. Base case cash flows
plus net cash came to USD 11.91/share against a USD 20.18 price — and the USD 8.27 gap
could not be closed by any discount rate, not even zero. That isolated the whole
disagreement into the pipeline, which is exactly where it belonged.

**Path C has no multiple, so it skips Step 3 and goes straight to Step 4.**
Everything else — scenarios, market-implied, checkpoints — is unchanged.

## Step 3 — Both paths: anchor every multiple to a named peer

This is the number that decides the answer. The same earnings at 14× and at 40×
differ by nearly 3×, so a multiple without a source is where a valuation becomes
whatever you wanted it to be.

For every multiple, record **which company trades there today**:

> 賣車 14× ← Toyota forward P/E 11×、Honda 14×、比亞迪 15.5×

When there is no comparable company at all — a business nobody has run before —
the legitimate fallback is **PEG ≈ 1**: set the multiple near the growth rate
you are projecting, and say that is what you did. Never let "no comparable"
become "pick a number".

Peer multiples move. Fetch them, date them, and put the date in the table.

## Step 4 — Discount management's timeline by its own track record

Never use a date management gave you. **Measure how late this company has been
before, then push every promise back by that ratio.**

How to measure it: pull 3–5 years of the company's own guidance — earnings
calls, shareholder decks, product announcements — and compare each dated promise
to when it actually happened. Divide. That ratio is the discount.

For Tesla the source model used **2.3×**, built on hardware promises landing 2–2.4×
late, and backed by a New York Times count of 602 public Musk targets of which
**19% arrived on time**. Operationally: *anything management says will happen in
2027, assume 2030.*

**A company with a clean record gets 1.0×.** This is not a penalty box — it is a
measurement. Do not import another company's ratio because it feels right, and
say in the report how you measured this one.

## Step 5 — Anything you cannot estimate gets zero

A segment with no shipments, no pricing, no disclosure does not get a guess. It
gets **a value of zero in the base case** and a line of its own in the report:

> Optimus：base case 給 0。完全沒有可參考的數據。把它當成買股票附贈的 call option。

Put it in the bull case if you like. Keeping it out of the base case is what
separates a projection from a wish, and the user can still decide to pay extra
for it — but now they know they are doing that.

## Step 6 — Sum, and divide by the *future* share count

```
Σ 各業務價值 + 淨現金 = 目標年企業價值
÷ 目標年股數 = 目標年每股
÷ (1 + 折現率)^年數 = 今天的合理價
```

**Net cash is cash and short-term investments minus total debt** — read both off
the balance sheet, do not take a headline "cash" figure.

**The share count must be the target year's, not today's.** Stock compensation
dilutes, buybacks concentrate; using today's count silently moves the answer.
Project it from the last 3 years of diluted share count.

## Step 7 — Three scenarios, then weight them

Run the whole table three times. The scenarios should differ in **assumptions**,
not in mood:

- **bear** — the one thing the thesis depends on fails, and multiples compress to
  the boring-industry level
- **base** — Step 2–6 as built
- **bull** — the timeline discount in Step 4 is kinder, penetration is higher, and
  the Step 5 zero becomes a number

Weight and report the expected value. A single point estimate is false precision.

## Step 8 — Say what the market is already paying for

**This is the most useful line in the report, and the one most reports leave out.**

Compare the model to the live price and name what the gap implies. The source
model's version:

> 現在 USD 356 裡，Robotaxi 一塊在 base case 就值 USD 412/股 —— 所以你付的錢
> 絕大部分是在買「Robotaxi 在 2030 年做到百萬台規模」這件事。

Then run the **concentration check**: if one segment is more than half the base
case value, the table is not valuing a company, it is pricing a single bet. Put
that in the report's first three lines, not buried in a table.

## Step 9 — Leave checkpoints that can prove you wrong

Before writing the report, name **the next date, the specific number, and the
threshold**:

| 時間 | 看什麼 | 達標門檻 |
|---|---|---|
| 下一季財報 | 無監督 Robotaxi 累積里程 | > 200 萬英里 |
| 下一季財報 | FSD 訂閱數 | > 170 萬 |

A valuation with no checkpoint cannot be scored later, which means it cost the
reader nothing to believe and teaches them nothing when it is wrong. The Tesla
example's two checkpoints came due two months later and can now be graded —
`references/worked-example-tsla.md` has the scorecard.

## Where the numbers come from

Free sources only. In order of how much you should trust them:

1. **Exchange and regulator filings** — primary, dated, free. Use them for
   deliveries, revenue, operating income, cash, debt, share count.
   US: SEC EDGAR through `data.sec.gov`. Taiwan: TWSE / TPEx open data and MOPS
   (公開資訊觀測站). Elsewhere: the company's own IR releases.
   **`references/data-sources.md` has the exact routes — three per kind of
   number, in the order to try them.**
2. **Earnings call transcripts** — for guidance and for the Step 4 track record.
3. **Web search** — for peer multiples and analyst targets. Always date them.

### When a source refuses you: another door, never a disguise

The same number almost always sits behind more than one official door. A
Taiwanese monthly revenue figure is published by the exchange's open-data API,
by MOPS and by the company's own release; a US company's reported numbers are in
SEC's XBRL API and in the filing itself. So when one route blocks you, **go to
the next route for the same number**, and keep going down the list in
`references/data-sources.md`. Stopping at the first refusal leaves a hole the
model did not need.

Another door means: a different official endpoint, a different format of the
same publication (API, HTML page, PDF), the company's IR site, an archived copy
on the Wayback Machine, and last — labelled as second-hand — a news report that
quotes the figure.

It never means dressing the request up as something it is not: no browser
User-Agent on a script, no rotating identities, no proxies, no solving a
CAPTCHA. A block page is the site declining *this client*; the answer is a
different door, not a costume. On 2026-11-05 the new MOPS API refused a plain
request for 3443's announcement list, and the old MOPS site returned the same
list to the same plain request.

Declaring *more* about yourself is the opposite, and is fine. SEC refuses
undeclared automated tools and asks for a User-Agent that names the tool and a
contact. A tool name is enough for `data.sec.gov`; `www.sec.gov` also wants a
contact address — ask the user whether to give one, and never fill in theirs or
invent one.

Two checks before trusting anything a route returns:

- **A block page can arrive as HTTP 200.** Read the body before parsing it.
  Parsed blindly, a refusal becomes "this company made no announcements".
- **Confirm it is the company you asked for.** A reused MOPS connection has
  returned another company's data. Use a fresh session per request and check the
  ticker printed in the response.

**When subagents gather the data, put this subsection and the route table in
their prompt verbatim.** They do not read this file, and the one known breach of
this rule came from a subagent that had never seen it.

In the report's source list, say which route each figure came through. If every
route for a figure fails, it is a labelled hole (below) — and list the routes you
tried.

**What this costs you: there is no reliable live quote.** Web search returns
yesterday's close at best, and sometimes a foreign listing in another currency.
So:

- **Ask the user for the current price**, or label the one you found with its
  exact date and source and say it may be stale.
- Never present a searched price as live.

If any required figure cannot be sourced, say which one and what you substituted.
A model with one labelled hole is useful; a model with one hidden hole is not.

**Verify in order of value weight, not in order of the table.** The segment
carrying most of the value is where checking pays. In the Tesla example three
unverified parameters sat under 78% of the value and two others sat under 17%;
checking the first three moved the answer 22%, and the rest could wait. Say in
the report which assumptions you checked and which you carried over, with the
share of value each group covers.

## Step 10 — Write the report

Reports go in a **`fairprice/` folder** in the current directory — create it if
it is not there (`mkdir -p fairprice`). Check `git remote -v` first — **never
write it into a public repository.**

**Taiwan-listed stocks** (TWSE / TPEx) are named by code and company name, with
no method in the filename:

```
fairprice/<代號>-<公司名>-<YYYY-MM-DD>.md     ← e.g. 3443-創意電子-2026-11-05.md
```

Use the company name exactly as the report's title line writes it (鴻海,
台積電, 聯亞光電, 日月光投控). A Taiwan company's US ADR report (TSM) takes
the Taiwan code: `2330-台積電-…`. The method lives in the title line instead
(「— 單一倍數法」「— 分業務加總」), so the first line must always say it.

**Everything else** keeps the method in the filename:

```
fairprice/<代號>-fairprice-<YYYY-MM-DD>.md          ← Path A
fairprice/<代號>-earnings-multiple-<YYYY-MM-DD>.md  ← Path B
fairprice/<代號>-patent-npv-<YYYY-MM-DD>.md         ← Path C
```

There the method is in the filename because a different method should not
share a name with Path A — the folder collects them, it does not merge them.
For Taiwan names, a second method on the same ticker and day is a filename
collision: treat it like a re-run below and write `-v2`.

**If that exact file already exists, this is a re-run.** Say so, and either
overwrite on purpose or write `-v2`; never silently replace a report the user
may have read. Re-running the same ticker on the same day is common and
legitimate — it is what you do after an earnings release lands. Path C borrows Path A's template, swapping the segment
table for a year-by-year cash-flow table and the multiple column for the
remaining life.

### Path A（分業務加總）

```markdown
# <公司>（<代號>）合理價推算

市價 $<X>（<來源>，<日期>）　目標年 <YYYY>　折現率 <X>%　資料日期 <YYYY-MM-DD>

## 結論

**base case 合理價 $<X>**　市價比它<高/低> <X>%
加權期望值 $<X>（bear <X>% / base <X>% / bull <X>%）

**這張表有 <X>% 的價值來自 <某業務>。買這檔股票主要是在賭 <那件事>。**

## 一、業務拆解
| 業務 | 量 | 價 | 營收 | 利潤率 | 稅後 | 本益比 | 對標 | 價值 | 每股 |
|---|---|---|---|---|---|---|---|---|---|

## 二、每個假設的根據
| 假設 | 用的數字 | 出處 | 日期 | 可信度 |
|---|---|---|---|---|

## 三、管理層時程折扣
這家公司過去的承諾 vs 實際：<怎麼量的> → 用 <X> 倍

## 四、沒有給價值的東西
<逐項，附「為什麼現在無法估計」>

## 五、三情境
| 情境 | 權重 | <目標年>每股 | 折現回今天 | 差別在哪個假設 |
|---|---|---|---|---|

## 六、市場已經 price in 了什麼
<對照市價，講出那個差額代表的具體事件>

## 七、可以驗證的檢查點
| 時間 | 看什麼 | 達標門檻 | 沒達標代表什麼 |
|---|---|---|---|

## 八、什麼會打破這個模型
<列出模型結構上處理不了的東西，不是列風險清單>
```

### Path B（正常化獲利 × 單一倍數）

```markdown
# <公司>（<代號>）合理價推算 — 單一倍數法

市價 $<X>（<來源>，<日期>）　目標年 <YYYY>　折現率 <X>%　資料日期 <YYYY-MM-DD>
**方法：正常化獲利 × 本益比**（不是 SOTP，理由見第一節）

## 結論
**base case 合理價 $<X>**　市價比它<高/低> <X>%
加權期望值 $<X>（bear/base/bull <X>/<X>/<X>%）
**bear 到 bull 只差 <X> 倍** ← 區間窄本身就是發現，代表價格可用獲利解釋

## 一、為什麼不用 SOTP
<Step 0 的兩個理由，具體到這家公司>

## 二、正常化獲利
### 調整一：成長
| 年度 | 營收 | 年增 | 出處 |
<把長期 CAGR 和今年的數字放進同一張表，算出隱含的剩餘年成長>
### 調整二：利潤率
| 項目 | 數字 | 出處 |
<今天的毛利率、公司自己的長期目標、已量化的稀釋>
<逐行往下算到淨利率，寫出營業費用率與營益→淨利的轉換係數>
→ 目標年淨利 $<X>　（獲利成長 <快/慢>於營收成長，因為<原因>）

## 三、倍數的錨點
| 參考點 | 數字 | 出處 |
<10 年均值／區間／同業；base 取幾倍，以及為什麼偏離均值>

## 四、三情境
| 情境 | 權重 | 營收 | 利潤率 | 淨利 | 倍數 | 目標年每股 | 折現回今天 |

## 五、敏感度（必填）
| 動什麼 | 答案變成 | 變動 |

## 六、市場已經 price in 了什麼
<用 base 的獲利回推，市價相當於付幾倍；對照歷史均值>

## 七、管理層時程折扣
<量到的倍數，或說明證據不足只能給 1.0×>

## 八、可以驗證的檢查點
| 時間 | 看什麼 | 達標門檻 | 沒達標代表什麼 |

## 九、什麼會打破這個模型
```

Report in chat: the base case, the one or two assumptions the answer is most
sensitive to, and — for Path B — the bear/bull ratio, because a narrow range is
itself the finding. Not the whole table.

## Failure modes

**Picking the multiple to reach a number.** The one that ruins this model. If you
find yourself nudging the P/E, the discount rate or the target year after seeing
the output, stop and write down what you were trying to reach — that number was
your real conclusion and the model was decoration.

**Dropping the tax line.** Between 營業利益 and 本益比. Costs 15% of the answer and
leaves no trace.

**Mixing a quarterly figure with an annual one.** 13.7 GWh is one quarter; 46.7 GWh
is a year. Label every figure with its period as you collect it, not afterwards.

**Using today's share count for a future year.** Silent, and always in the
optimistic direction for companies that pay in stock.

**Presenting a searched price as live.** Covered above. It is the one input the
user can check in five seconds, so getting it wrong discredits the whole report.

**Reporting a point estimate.** `USD 324` alone is false precision. `USD 61 / USD 324 /
USD 1,723` is the actual finding — the answer depends enormously on one thing, and
saying so *is* the result.

**Missing the concentration.** If 80% of the value is one segment, a reader who
takes away "fair value USD 324" has learned the wrong thing. They needed "this is a
bet on robotaxis".

**A right answer reached by a wrong derivation.** When an assumption is a product
of components — fleet size × trips per day × miles per trip — check each
component, not the result. In the Tesla example the daily-mileage figure was
right (≈90) while *both* its inputs were wrong (fleet 4,000 vs ~3,067, trip
length 5 vs 3.9 miles) and the two errors cancelled. The product survived; every
extrapolation built on that derivation did not. A number that matches reality by
coincidence is more dangerous than one that is plainly wrong, because it passes
the sanity check and then quietly licenses the next step.

**A price assumption that contradicts the growth assumption.** Ask of every
price: does the story justifying the volume also require this price to fall? The
Tesla model held today's pilot fare flat to 2030 while the entire reason the
fleet reaches millions of vehicles is that the service undercuts human drivers —
and the most bullish third-party model on the same company assumed a consumer
price **one fifth** of it. A price that only holds while supply is scarce cannot
also hold at the scale the volume line needs. These two cells are not
independent, and a model that treats them as independent is optimistic twice.

**Multiplying a peak by a peak.** Path B's version of picking the multiple to
reach a number, and harder to spot because no single cell looks wrong. A company
growing 44% at a 66% gross margin is at two peaks at once; carrying both to the
target year and multiplying produces a figure that has never been true. Covered
in Step 2B — normalize growth and margin separately, each against something the
company published about itself.

**A one-time item wearing the costume of earnings.** ACADIA's FY2025 EPS was
USD 2.30, which against a USD 20 share price reads as a P/E under 9 — until you walk
the income statement: USD 1.07B of revenue against USD 878M of R&D and SG&A leaves a
fraction of that, and USD 274M of the USD 391M net income landed in a single quarter.
It was a deferred-tax valuation-allowance release, the standard event when a
biotech first turns profitable. Never take an EPS without walking down from
revenue and checking the bottom line follows from the lines above it.

**Charging a cost while crediting none of its benefit.** A model that expenses
R&D every year *and* values the pipeline at zero has penalised the company twice
for one fact. Pick one and say which: carry the spend and give the pipeline a
probability-weighted value, or cut the spend to maintenance and keep the zero.
In the ACADIA model those two choices differed by **USD 2.68 a share** — more than
any other single assumption in it. The same trap waits wherever a cost buys an
option you then decline to value.

**Margin expansion that is really a depreciation denominator.** Operating
margin rising while depreciation falls as a share of revenue is not the same
thing as the business getting better, and the two are easy to confuse because
only one of them shows up in the margin line. Pull depreciation as a percentage
of revenue alongside the margin series. LandMark 3081, 2026-11: 49.4% operating
margin with depreciation at 4.9% of revenue, against 43.0% of revenue three
years earlier — and TWD 9.4bn of board-authorised capex against TWD 2.3bn of net
PP&E waiting to reverse it, worth about 8 points of margin once it is in
service. The expansion being capitalised at a high multiple was in large part
the gap before the new plant starts depreciating.

**Forward numbers with no document behind them.** Before building on any
guidance, establish that it exists in a filing, a deck or a transcript — do not
infer it from press coverage. The test is cheap and the failure is total.
LandMark 3081, 2026-11: the capacity path (~2.5x in 2027, ~2.5x again in 2028),
the order book and the quarterly revenue guide were all in wide circulation and
all in the model. Fetching the company's eight 2026 investor decks showed the
Q3 deck is six pages — cover, disclaimer, a revenue chart, two statements, "Q&A"
— with no capacity, capex, order-book or guidance slide at all, and the
regulator's forecast-filing endpoint held no record for the company. Every
forward figure traced to the verbal Q&A of two broker-hosted calls, as rendered
by journalists who disagreed with each other on whether the subject was capacity
or output. Carry such numbers if nothing better exists, but label them, and say
in the report that the largest assumption rests on no document.

**Treating the model as the conclusion.** The arithmetic being correct says
nothing about the assumptions being right. The source model's arithmetic checked
out line by line and its biggest assumption was still a guess about a business
that does not exist yet. Say which is which.
