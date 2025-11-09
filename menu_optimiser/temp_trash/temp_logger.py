#!/usr/bin/env python3
import pathlib, time, subprocess, re, os

# ===== CONFIG =====
BASE = pathlib.Path("/home/mahima/dev/Team_Ultra_UBH-2025")
LOG_DIR = BASE / "menu_optimiser" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Your working temp reader + env (keeps grove in temp-test)
# TEMP_CMD = [
#    "conda","run","-n","temp-test","bash","-lc",
#    "export GROVE_I2C_BUS=1; python /home/mahima/dev/Team_Ultra_UBH-2025/temp_test/read_temp_grove.py"
#]
TEMP_CMD = [
	"/home/mahima/miniconda3/envs/temp-test/bin/python",
        "/home/mahima/dev/Team_Ultra_UBH-2025/temp_test/read_temp_grove.py"
]


POLL_SEC = 30
TIMEOUT  = 8
# ================

NUM = re.compile(r"[-+]?\d+(?:\.\d+)?")

def run(cmd, timeout):
    env = os.environ.copy()
    env["GROVE_I2C_BUS"] = "1"

    try:
        r = subprocess.run(cmd, env=env,capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "") + ("\n"+r.stderr if r.stderr else "")
    except Exception as e:
        print(e)
        return ""

def last_number(text: str):
    m = list(NUM.finditer(text or ""))
    return float(m[-1].group(0)) if m else None

def write_atomic(path: pathlib.Path, content: str):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    os.replace(tmp, path)

def main():
    print(f"[temp_logger] writing every {POLL_SEC}s → {LOG_DIR/'temp_c.txt'}")
    while True:
        text = run(TEMP_CMD, TIMEOUT)
        print('LINE', text)
        v = last_number(text)
        temp_c = None
        if v is not None:
            if "°F" in text or "F" in text:
                temp_c = (v - 32.0) * (5.0/9.0)
            else:
                temp_c = v
        if temp_c is not None:
            temp_f = temp_c * (9.0/5.0) + 32.0
            print('Here', temp_c, temp_f)
            write_atomic(LOG_DIR/"temp_c.txt", f"{temp_c:.2f}\n")
            write_atomic(LOG_DIR/"temp_f.txt", f"{temp_f:.2f}\n")
            print(f"[temp_logger] {temp_c:.2f} °C")
        else:
            write_atomic(LOG_DIR/"temp_c.txt", "NA\n")
            print("[temp_logger] NA")
        time.sleep(POLL_SEC)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[temp_logger] stopped.")
