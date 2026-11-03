# yt2script 排錯

依序往下。每一節先說**怎麼確認是這個問題**，再說怎麼處理。

## 1. `無法取得影片資訊` / `The page needs to be reloaded`

所有 client 都擷取失敗。先確認是全域性還是單支影片的問題：

```bash
~/.local/share/yt2script/venv/bin/yt-dlp --list-subs "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

這是 YouTube 第一支影片，永遠存在。它也失敗 → 環境問題，不是影片問題。

依序試，**成功就停**：

1. 升級：`~/.local/share/yt2script/venv/bin/pip install -U --pre "yt-dlp[default]"`
   （`--pre` 是**全局生效**的，不是只作用在你指名的套件上。套用到整組依賴
   會讓 pip 去解 prerelease 版本，可能挑到沒有預編譯 wheel 的套件而嘗試
   從源碼編譯失敗。要 nightly 就只給 yt-dlp。）
2. 瀏覽器 cookies：`--cookies-from-browser chrome`（或 firefox / safari / edge / brave）
3. 若跑在雲端機器或 VPS 上，就是機房 IP 被擋 —— 換到本機跑

三步都失敗就停下來告訴使用者。**不要**偽造 client 身分、輪換 user-agent
或接代理池。那是為了繞過 bot 檢查，不在這個工具的範圍內。

## 2. `Sign in to confirm you're not a bot`

同上第 1 節的三步。這是 IP 信譽問題，不是程式缺陷。

macOS 上 Safari 的 cookie 檔受系統隱私權限（TCC）保護：

```
ERROR: [Errno 1] Operation not permitted: .../Cookies.binarycookies
```

這需要使用者手動到「系統設定 → 隱私權與安全性 → 完全取硬碟取用權」
把終端機或 Claude 加進去，再重啟該 app。**你無法代為授權**，請直接說明。

## 3. `沒有任何 client 提供可下載的音訊格式`

YouTube 的 SABR streaming 限制。有些影片只有 `web` client 看得到格式，
而 `web` 又可能壞掉；有些只剩 progressive mp4（format 18）。

自 2026-11 升級到 Python 3.12 與新版 yt-dlp 後，純音訊格式通常是看得到的
（例如 `139-drc m4a`，約 3-4 MB），`bestaudio` 會自然解到它。若又退回只剩
format 18（32 MB 的 progressive mp4），那是 YouTube 端的限制或 yt-dlp again
過時 —— 先試第 1 節的升級。

腳本會試 `bestaudio/18/best`。全失敗時：

```bash
~/.local/share/yt2script/venv/bin/yt-dlp --extractor-args "youtube:player_client=android" -F "<URL>"
```

看實際有什麼。只有 `sb0`–`sb3`（storyboard 圖片軌）就是真的沒有媒體可抓。

## 4. `字幕軌存在但所有 client 都抓不到`

**這不等於沒有字幕。** 某個 client 回報有軌，但沒有任何 client 能把它下載下來。
通常是暫時性的，稍後重試常常就好。

直接落 Whisper 會拿到品質較差的結果，而且要花 20–30 分鐘。先重試一次，
再決定要不要落。務必告知使用者這是降級。

## 5. `[驗證] … ✗` 有 cue 遺漏

輸出掉了內容，這是硬錯誤。常見原因：

- 字幕檔本身格式異常（手動開 `.vtt` 看一眼）
- 繁簡轉換把字改掉，導致比對失敗 —— 檢查 `[字體]` 那行的判斷是否合理

OpenCC 的 `s2*` 設定假設輸入是簡體。餵給它本來就是繁體的文字，
像 了／才／吃／台 這種兩邊都合法的字會被推成錯誤異體字。
腳本因此先比較繁簡標記字數再決定要不要轉；若判斷錯了，根因在那裡。

## 6. Whisper 跑太慢或記憶體不足

CPU 上約 1.3 倍實時，10 分鐘影片要 20–30 分鐘，正常。

記憶體不足才降級：`--model medium`。要明確告知使用者你降級了、品質會略差。
非 `large-v3` 的尺寸不在本地快取，會需要下載 1–3 GB，腳本會先問。

## 7. `invalid value encountered in matmul` 警告

來自 Whisper 的 mel 頻譜計算，通常是音訊開頭或結尾有靜音段。
已知無害 —— 實測輸出正常。只有在同時出現大量亂碼文字時才需要追查。

## 8. 環境版本（2026-11-02 已升級）

目前環境：

| 項目 | 版本 |
|---|---|
| Python | 3.12.16（Homebrew，`/opt/homebrew/bin/python3.12`） |
| ffmpeg | 9.0.2（已安裝，但管線不依賴它） |
| yt-dlp | 2026.10.29 以後 |
| tokenizers | 0.23.x（有預編譯 wheel，無需鎖版本） |

這次升級解決了三個先前必須繞路的問題，記錄在此以免日後誤判：

1. **`web` extractor 失效**。Python 3.9 把 yt-dlp 鎖在 2025.10 版，導致所有
   影片都回 `The page needs to be reloaded`，必須靠 `player_client` 計分繞過。
   升級後預設 client 正常工作。`CLIENTS` 的計分邏輯保留**當保險**，不是必要繞路。
2. **沒有純音訊格式**。舊版只看得到 format 18，為了 10 分鐘的音訊要下載
   32 MB 視訊。升級後 `bestaudio` 解到約 3.6 MB 的 m4a。
3. **`tokenizers` 無 wheel**。py3.9 沒有新版的預編譯 wheel，必須鎖版本。
   3.12 有，依賴可自由升級。

若日後重建 venv：

```bash
rm -rf ~/.local/share/yt2script/venv
sh "${CLAUDE_PLUGIN_ROOT}/cli/install.sh"
```

Don't hand-build it with `python3 -m venv`: on macOS `python3` is still 3.9,
and `faster-whisper` needs 3.11 or newer. `install.sh` finds a usable
interpreter (or has `uv` fetch one) and reads the pinned-on-purpose `av<19`
cap from `requirements.txt`.

模型在 `~/.local/share/yt2script/models/`，重建 venv 不影響它。
用 `--clear` 而非 `rm -rf`，可就地清空重建。

驗收基準：對 `F7WEN5wOGZs` 跑 `yt2script`，應得 368/368 cue 無損，
且輸出 md5 為 `8cccf3bdfe642bbd9659668d5f84465a`。環境改動後這個值不該變。

## 9. 依賴相容性陷阱（2026-11-02 踩過，已修）

升級到 Python 3.12 後，依賴不鎖版本而暴露出兩個上游問題。症狀看起來像
「模型壞了」或「音訊壞了」，實際都不是。

### `TypeError: open() got an unexpected keyword argument 'metadata_errors'`

`faster-whisper 1.2.1`（截至目前的最新版）在 `faster_whisper/audio.py`
呼叫 `av.open(..., metadata_errors="ignore")`，而 **`av` 19.0.x 移除了這個參數**。
`faster-whisper` 宣告依賴是裸的 `av`，沒有上限，所以 `pip install` 會裝到 19。

實測 `av 18.1.0` 仍相容，因此鎖在那裡：

```bash
~/.local/share/yt2script/venv/bin/pip install "av==18.1.0"
```

等 `faster-whisper` 發布修正後可以解鎖再測。這個鎖是因為上游缺上限，
不是我們這邊的設計問題。

### `IncompleteSnapshotError: 2 file(s) are missing (.gitattributes, README.md)`

`huggingface_hub` 2.4 以後，`snapshot_download(local_files_only=True)` 會因為
快取缺少 `.gitattributes` / `README.md` 這類**不影響推論**的檔案而判定不完整。

模型本身完好 —— `WhisperModel('large-v3')` 在 `HF_HUB_OFFLINE=1` 下 3 秒載入成功，
因為 `faster-whisper` 內部用 `allow_patterns` 只取權重與 tokenizer。

所以不要用 `snapshot_download` 判斷「模型在不在」。`driver.py` 的
`model_is_cached()` 改成直接檢查 `model.bin` / `config.json` / `tokenizer.json`
是否存在，那才是推論真正的需求。

### 哨兵值與有效值不可共用

`CLIENTS` 裡 `None` 代表「yt-dlp 預設 client」，所以它**不能**同時當
「還沒找到」的哨兵 —— 否則預設 client 永遠會被後面的 client 覆蓋，
導致抓到較差的格式（實際發生過：下載 33 MB 的 mp4 而非 10 MB 的 opus）。
程式改用 `UNSET = object()` 當哨兵。

## 10. 等待背景程序時不要用 `pgrep -f`

`pgrep -f <pattern>` 比對的是**完整命令列**，所以等待迴圈會匹配到自己：

```bash
# 錯：這個迴圈的命令列本身就含有 "whisper_vtt.py"，條件永遠為真
while pgrep -f whisper_vtt.py >/dev/null; do sleep 10; done
```

被等待的程序早就結束了，等待器還在空轉。本專案開發期間因此留下兩個
空轉一小時以上的孤兒程序。

正確做法是先取得 PID，再用 `kill -0` 檢查該 PID 是否存活：

```bash
"$VENV/bin/python" driver.py "$URL" & PID=$!
while kill -0 "$PID" 2>/dev/null; do sleep 10; done
```

`kill -0` 不送出訊號，只檢查程序是否存在，不會有自我匹配的問題。
