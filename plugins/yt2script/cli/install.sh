#!/bin/sh
# One-time setup for the yt2script CLI.
#
# Everything this installs lives under $DATA (default ~/.local/share/yt2script),
# never in the plugin directory: a plugin update moves the plugin root, and
# re-downloading a 3 GB model because of a version bump is not acceptable.
set -eu

ROOT=$(cd "$(dirname "$0")" && pwd)
DATA=${YT2SCRIPT_HOME:-$HOME/.local/share/yt2script}
VENV=$DATA/venv

echo "yt2script：安裝到 $DATA"
mkdir -p "$DATA"

if [ -x "$VENV/bin/python" ]; then
    echo "  venv 已存在，只更新套件"
elif command -v uv >/dev/null 2>&1; then
    echo "  用 uv 建 venv（必要時它會自己抓一套 Python 3.12）"
    uv venv --python 3.12 "$VENV"
else
    # faster-whisper pulls in numpy >= 2, which needs Python >= 3.11. macOS
    # still ships 3.9 as `python3`, so a bare `python3 -m venv` is a trap.
    PY=
    for c in python3.13 python3.12 python3.11; do
        if command -v "$c" >/dev/null 2>&1; then PY=$c; break; fi
    done
    if [ -z "$PY" ]; then
        cat >&2 <<'MSG'
找不到 Python 3.11 或更新的版本。選一條：
  1. 裝 uv（最省事）  curl -LsSf https://astral.sh/uv/install.sh | sh
  2. 自己裝 Python    brew install python@3.12
裝好再跑一次這個腳本。
MSG
        exit 1
    fi
    echo "  用 $PY 建 venv"
    "$PY" -m venv "$VENV"
fi

echo "  安裝相依套件"
if command -v uv >/dev/null 2>&1; then
    # A uv-created venv has no pip, and uv can install into any venv anyway.
    uv pip install --quiet --python "$VENV/bin/python" -r "$ROOT/requirements.txt"
else
    "$VENV/bin/python" -m pip install --quiet --upgrade pip
    "$VENV/bin/python" -m pip install --quiet -r "$ROOT/requirements.txt"
fi

# ffmpeg is not a pip package, and Whisper needs it to decode the audio.
# The subtitle paths work without it, so this is a warning, not a failure.
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo
    echo "注意：找不到 ffmpeg。字幕那兩條路不受影響，但 Whisper 轉錄會失敗。"
    echo "      裝法： brew install ffmpeg"
fi

echo
echo "好了。用法： yt2script <YouTube 網址>"
echo "第一次走到 Whisper 時會下載約 3 GB 模型到 $DATA/models/。"
