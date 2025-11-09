#!/usr/bin/env python3
import pathlib, time, subprocess, re, os, argparse

# === CONFIG (edit if needed) ===
# If your grovelight.py needs the "temp-test" env, use the conda-run command below.
GROVELIGHT_CMD = [
    "conda","run","-n","temp-test","bash","-lc",
    "export GROVE_I2C_BUS=1; python /home/mahima/dev/Team_Ultra_UBH-2025/lightsensor/grovelight.py"
]
# If grovelight.py works in your current env, replace with:
# GROVELIGHT_CMD = ["python3", "/home/mahima/dev/Team_Ultra_UBH-2025/lightsensor/grovelight.py"]

BASE = pathlib.Path("/home/mahima/dev/Team_Ultra_UBH-2025/menu_optimiser")
OUT_FILE = BASE / "logs" / "lux.txt"
POLL_SEC = 30
TIMEOUT  = 6
# ===============================

NUM = re.compile(r"[-+]?\d+(?:\.\d+)?")

def run(cmd, timeout):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "") + ("\n"+r.stderr if r.stderr else "")
    except Exception:
        return ""

def last_number(text: str):
    ms = list(NUM.finditer(text or ""))
    return float(ms[-1].group(0)) if ms else None

def write_atomic(path: pathlib.Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    os.replace(tmp, path)

def sample_once() -> float | None:
    text = run(GROVELIGHT_CMD, TIMEOUT)
    val = last_number(text)
    return float(val) if val is not None else None

def loop(poll: int):
    print(f"[light_logger] writing every {poll}s → {OUT_FILE}")
    while True:
        lux = sample_once()
        if lux is not None:
            write_atomic(OUT_FILE, f"{lux:.0f}\n")
            print(f"[light_logger] {lux:.0f} lux")
        else:
            write_atomic(OUT_FILE, "NA\n")
            print("[light_logger] NA")
        time.sleep(poll)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Log lux from grovelight.py to a file.")
    ap.add_argument("--once", action="store_true", help="Take one sample and exit.")
    ap.add_argument("--poll", type=int, default=POLL_SEC, help="Polling interval seconds.")
    args = ap.parse_args()

    if args.once:
        lux = sample_once()
        if lux is not None:
            write_atomic(OUT_FILE, f"{lux:.0f}\n")
            print(f"[light_logger] wrote {lux:.0f} lux to {OUT_FILE}")
        else:
            write_atomic(OUT_FILE, "NA\n")
            print(f"[light_logger] wrote NA to {OUT_FILE}")
    else:
        loop(args.poll)
