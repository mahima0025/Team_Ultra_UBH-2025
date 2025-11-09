#!/usr/bin/env bash
# runner.sh — run both sensor writers together and capture logs

set -Eeuo pipefail

# >>> adjust these two paths if needed
BASE="/home/mahima/dev/Team_Ultra_UBH-2025/menu_optimiser"
LOG_DIR="$BASE/logs"
# <<<

mkdir -p "$LOG_DIR"
cd "$BASE"

STAMP=$(date +%Y%m%d_%H%M%S)
TEMP_LOG="$LOG_DIR/temp_logs_${STAMP}.txt"
LUX_LOG="$LOG_DIR/lux_output_${STAMP}.txt"

echo "[*] Writing for 10s:"
echo "    TEMP -> $TEMP_LOG"
echo "    LUX  -> $LUX_LOG"

# If your writers expect LOG_DIR env, export it:
export LOG_DIR

# If you need conda, set PY like this:
# PY=(conda run -n temp-test --no-capture-output python -u)
PY=(python3 -u)

# Run both in background, piping stdout to log files
"${PY[@]}" temp_writer2.py  | tee -a "$TEMP_LOG" & PID1=$!
"${PY[@]}" light_writer2.py | tee -a "$LUX_LOG"  & PID2=$!

# Let them run
sleep 20

# Stop both (ignore if already exited)
kill -TERM "$PID1" "$PID2" 2>/dev/null || true
wait "$PID1" "$PID2" 2>/dev/null || true

echo "[✓] Collected logs"

# Fetch latest logs (in case other files also exist)
latest_temp=$(ls -t "$LOG_DIR"/temp_logs_* 2>/dev/null | head -1 || true)
latest_lux=$(ls -t "$LOG_DIR"/lux_output_* 2>/dev/null | head -1 || true)

echo "Latest temp: ${latest_temp:-<none>}"
[ -n "$latest_temp" ] && tail -n 10 "$latest_temp"
echo
echo "Latest lux : ${latest_lux:-<none>}"
[ -n "$latest_lux" ] && tail -n 10 "$latest_lux"

echo "Now running our model"

python simp_prompter.py --temp_file $latest_temp --lux_file $latest_lux --menu_file logs/menu4.txt
