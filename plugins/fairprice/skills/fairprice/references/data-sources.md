# 免費資料路徑：每種數字不只一扇門

**實測日期 2026-11-05。** 路徑會變。用之前先打一次；壞了就照順序換下一條，
並把新發現（能用的、壞掉的）連同日期寫回這份檔案。

規則在 SKILL.md〈When a source refuses you〉：**換門，不換裝。**
被擋就換下一條官方路徑；不偽裝瀏覽器、不輪換身分、不用代理、不解驗證碼。

---

## 台股

上市查 TWSE，上櫃查 TPEx。代號在一邊查不到，就到另一邊試。

| 要什麼 | 第 1 條 | 第 2 條 | 第 3 條 |
|---|---|---|---|
| 月營收 | TWSE OpenAPI `t187ap05_L`（上市）／TPEx OpenAPI `mopsfin_t187ap05_O`（上櫃） | 公司 IR 的月營收公告 | 網路搜尋新聞（二手，標出處） |
| 本益比、殖利率、淨值比 | TWSE `exchangeReport/BWIBBU_ALL`（當日全市場）；個股整月 `rwd/zh/afterTrading/BWIBBU` | TPEx `tpex_mainboard_peratio_analysis` | 網路搜尋（標日期） |
| 收盤價 | TWSE `rwd/zh/afterTrading/STOCK_DAY`（整月逐日） | 網路搜尋（標日期） | — |
| 最新一季財報 | TWSE OpenAPI `t187ap06_L_ci`（損益）、`t187ap07_L_ci`（資產負債）；上櫃 `mopsfin_t187ap06_O_ci`／`mopsfin_t187ap07_O_ci` | mopsov `ajax_t164sb04`（損益）／`03`（資產負債）／`05`（現金流量） | doc.twse 財報 PDF |
| 歷年財報 | mopsov `ajax_t164sb03/04/05`，逐年逐季查 | doc.twse 財報 PDF（`mtype=A`） | 公司 IR |
| 重大訊息 | MOPS 新站 `POST mops/api/t05st01` | mopsov `ajax_t05st01`（`step=1` 清單、`step=2` 明細） | 公司 IR 新聞稿 |
| 年報、股東會資料 | doc.twse（`mtype=F`） | 公司 IR | Wayback Machine |
| 法說會簡報 | 公司 IR | MOPS 法說會公告附檔 | Wayback Machine |

### 完整網址

```
TWSE OpenAPI   https://openapi.twse.com.tw/v1/opendata/<名稱>
               https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL
               清單：https://openapi.twse.com.tw/v1/swagger.json
TPEx OpenAPI   https://www.tpex.org.tw/openapi/v1/<名稱>
               清單：https://www.tpex.org.tw/openapi/swagger.json
個股整月       https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date=<YYYYMMDD>&stockNo=<代號>&response=json
               （BWIBBU 同格式）
mopsov 財報    POST https://mopsov.twse.com.tw/mops/web/ajax_t164sb04
               encodeURIComponent=1&step=1&firstin=1&off=1&queryName=co_id&inpuType=co_id
               &TYPEK=all&isnew=false&co_id=<代號>&year=<民國年>&season=<01-04>
mopsov 重訊    POST https://mopsov.twse.com.tw/mops/web/ajax_t05st01
               encodeURIComponent=1&step=1&firstin=1&off=1&keyword4=&code1=&TYPEK2=&checkbtn=
               &queryName=co_id&inpuType=co_id&TYPEK=all&co_id=<代號>&year=<民國年>&month=&b_date=&e_date=
doc.twse       https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=<代號>&year=<民國年>&seamon=&mtype=<A|F>
               A = 財務報告書，F = 股東會相關資料（含年報）；回 Big5 編碼
```

### 讀台股資料要注意的

- **年度是民國年**：西元 − 1911。2026 = 115。
- **OpenAPI 金額單位是千元**，而且**財報是年初累計**：`季別 3` 是 1–9 月，
  要單季就減掉前一季。實測：創意 115 年 Q3 損益表營收 44,098,869（千元），
  等於月營收表的 1–9 月累計 44,098,869。
- **OpenAPI 財報只有最新一期，且只有已經申報的公司。** 2026-11-05 一般業只有
  108 家（全部上市約 1,088 家）。申報季剛開始時大部分公司查不到，要改走 mopsov。
- **產業後綴**：`_ci` 一般業、`_basi` 金融業、`_bd` 證券期貨業、`_fh` 金控業、
  `_ins` 保險業、`_mim` 異業。銀行股去查 `_ci` 會查不到。
- **MOPS 舊的 `t05st32`／`t05st34` 已經壞了**，不要再試。

---

## 美股

| 要什麼 | 第 1 條 | 第 2 條 | 第 3 條 |
|---|---|---|---|
| 財報數字（營收、營益、現金、負債、股數） | `data.sec.gov/api/xbrl/companyfacts/CIK<10位>.json` | `www.sec.gov/Archives` 的 filing 本體（要附聯絡方式，見下） | 公司 IR 新聞稿 |
| filing 清單與日期 | `data.sec.gov/submissions/CIK<10位>.json` | EDGAR 網頁（同上） | 網路搜尋 |
| 管理層說過什麼 | `efts.sec.gov/LATEST/search-index?q="<字>"&forms=8-K&ciks=<CIK>` 全文搜尋 | 法說逐字稿（IR、網路搜尋） | 新聞（二手，標出處） |
| 代號 → CIK | 網路搜尋 `<TICKER> CIK` | `www.sec.gov/files/company_tickers.json`（要附聯絡方式） | — |

CIK 要補零到 10 位：Tesla 是 `CIK0001318605`。

### SEC 要你說清楚自己是誰

SEC 拒絕「未申報的自動化工具」，要求 User-Agent 寫明工具名稱與聯絡方式。
**這是要你多報身分，跟偽裝剛好相反**，照做是對的。實測：

| 路徑 | 不帶 UA | 只寫工具名稱 |
|---|---|---|
| `data.sec.gov`（companyfacts、submissions） | 403 | **200** |
| `efts.sec.gov` 全文搜尋 | — | **200** |
| `www.sec.gov`（Archives、browse-edgar、company_tickers） | 403 | 403，要聯絡方式 |

所以數字走 `data.sec.gov` 就夠。需要 filing 原文時，**問使用者要不要提供聯絡
信箱給 SEC**；不要自己填使用者的信箱，也不要編一個。使用者不給，就改走公司
IR 的新聞稿與簡報。

---

## 其他

| 情況 | 路徑 |
|---|---|
| 網頁改版或內容被撤下 | `https://archive.org/wayback/available?url=<網址>`，取最接近日期的快照，並寫明快照日期 |
| 官方路徑全部失敗 | 新聞報導（鉅亨、經濟日報、MoneyDJ、Reuters…）標成二手，數字要能對到原始公告的日期 |

---

## 拿到回應之後，先做兩件事

1. **阻擋頁可能回 HTTP 200。** 先讀內容再解析。MOPS 的阻擋頁寫
   「因為安全性考量，您所執行的頁面無法呈現」，SEC 的寫
   "Your Request Originates from an Undeclared Automated Tool"。
   沒檢查就解析，「被拒絕」會變成「這家公司沒有公告」。
2. **確認是你要的那家公司。** 重複使用同一條 MOPS 連線，曾經回過別家公司的資料。
   每次請求開新 session，並確認回應裡印的代號與公司名
   （MOPS 會寫「本資料由（上市公司）<代號> <公司> 公司提供」）。

---

## 實測紀錄

| 日期 | 路徑 | 結果 |
|---|---|---|
| 2026-11-05 | MOPS 新站 `api/t05st01`，一般 curl | **被擋**（HTTP 200 的阻擋頁），隔 20 秒重試仍擋 |
| 2026-11-05 | mopsov `ajax_t05st01`，同一個一般 curl | 通，回 3443 全年公告清單 |
| 2026-11-05 | mopsov `ajax_t164sb04` | 通，回應含「創意公司提供」 |
| 2026-11-05 | TWSE OpenAPI 月營收／本益比／損益表／資產負債表 | 通 |
| 2026-11-05 | TPEx OpenAPI 月營收／本益比／損益表 | 通 |
| 2026-11-05 | TWSE `STOCK_DAY`、`BWIBBU` | 通 |
| 2026-11-05 | doc.twse `mtype=A`、`mtype=F` | 通，回 PDF 清單 |
| 2026-11-05 | SEC，見上表 | `data.sec.gov`、`efts` 只要工具名稱；`www.sec.gov` 要聯絡方式 |
| 2026-11-05 | Wayback `available` API | 通 |
| 2026-11-05 之前 | MOPS `t05st32`／`t05st34` | 壞了 |
| 2026-11-09 | sandisk.com newsroom 新聞稿，一般請求 | 通，一手 |
| 2026-11-09 | investor.sandisk.com、investor.wdc.com | 403（Akamai）；改走公司 newsroom 或 Wayback 存檔 |
| 2026-11-09 | files.quartr.com 的 10-Q／10-K／簡報鏡像（由 stockanalysis.com/filings 連過去） | 通；是原始文件的副本，不必碰 `www.sec.gov` |
| 2026-11-09 | Business Wire、Macrotrends、Benzinga、MarketBeat、Seeking Alpha | 403；同一個數字改從其他來源或 Wayback 存檔拿 |
| 2026-11-09 | Wayback `available` API | 一度回 429，稍後可用 |
| 2026-11-09 | Kioxia IR 資料 xlsx（ssl4.eir-parts.net） | 通 |
| 2026-11-09 | `data.sec.gov` 已下市公司（舊 SanDisk，CIK 0001000180） | 通；XBRL 約從 2009 年起，更早的年度走 Wayback 上的 10-K 存檔 |

**目前已知唯一一次違規**：2026-11-05 跑 3443 時，一個 subagent 被 MOPS 新站擋下後，
改用瀏覽器 User-Agent 硬闖成功。它沒看過這條規則。同一份公告清單，
另外兩個 agent 都從官方 API 拿到了；上表也顯示舊站可以拿到。
**這次硬闖不是唯一的路，只是最順手的一條。**
