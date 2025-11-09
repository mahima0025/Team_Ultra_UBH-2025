#!/usr/bin/env python3
import time, sys, subprocess, threading, pathlib, datetime as dt, importlib.util, re
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Paths to your existing scripts
BASE = pathlib.Path("/home/mahima/dev/Team_Ultra_UBH-2025")
TEMP_PY = BASE/"temp_test/read_temp_grove2.py"   # prints Fahrenheit line(s)
LIGHT_PY = BASE/"lightsensor/grovelight.py"      # has read_light_intensity()
CAM_PY = BASE/"cam_test/cam.py"                  # grabs frame0.jpg

MENU_CSV = pathlib.Path("menu.csv")              # your menu file
MODEL_PKL = pathlib.Path("models/model.joblib")  # optional trained model
PEOPLE_TXT = pathlib.Path("people.txt")          # manual crowd value (no cam edits)
POLL_SEC = 30
TIMEOUT_SEC = 6

_num = re.compile(r"[-+]?\d+(?:\.\d+)?")

def _parse_first_number(s: str) -> Optional[float]:
    m = _num.search(s or "")
    return float(m.group(0)) if m else None

# ---------- TEMP (spawn once, read one line, kill) ----------
def read_temp_c() -> Optional[float]:
    try:
        p = subprocess.Popen(
            ["python3", str(TEMP_PY)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )
        line = None
        def _readline():
            nonlocal line
            try:
                line = p.stdout.readline()
            except Exception:
                line = None
        t = threading.Thread(target=_readline, daemon=True); t.start()
        t.join(TIMEOUT_SEC)
        p.terminate()
        if line:
            # your script prints something like: "ADC=... V=... R=... T=xx.xxF"
            f = _parse_first_number(line)
            if f is None: return None
            return (f - 32) * 5/9
        return None
    except Exception:
        return None

# ---------- LIGHT (import your module and call function once) ----------
def _import_module_from_path(py_path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(py_path.stem, str(py_path))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def read_lux() -> Optional[float]:
    try:
        gl = _import_module_from_path(LIGHT_PY)
        # Your grovelight.py exposes read_light_intensity()
        return float(gl.read_light_intensity())
    except Exception:
        # fallback: run once and parse the printed number
        try:
            out = subprocess.run(["python3", str(LIGHT_PY)],
                                 capture_output=True, text=True, timeout=TIMEOUT_SEC).stdout
            # lines like: "Approximate Light Intensity: 123.45 lux"
            return float(_parse_first_number(out))
        except Exception:
            return None

# ---------- CAMERA (refresh an image; doesn't return people) ----------
def refresh_camera_image() -> bool:
    try:
        r = subprocess.run(["python3", str(CAM_PY)],
                           capture_output=True, text=True, timeout=TIMEOUT_SEC)
        return r.returncode == 0
    except Exception:
        return False

# ---------- PEOPLE (no change to your camera code) ----------
def read_people() -> Optional[int]:
    try:
        return int(float(PEOPLE_TXT.read_text().strip()))
    except Exception:
        return None

# ---------- Integrator: model if present, else rules ----------
def integrate_and_decide(people: Optional[int], temp_c: Optional[float], lux: Optional[float], top_k=5):
    people = people or 0
    temp_c = temp_c if temp_c is not None else 0.0
    lux    = lux if lux is not None else 0.0
    hour = dt.datetime.now().hour
    is_weekend = int(dt.datetime.now().weekday() >= 5)

    if MODEL_PKL.exists():
        import pandas as pd, numpy as np
        from joblib import load
        pack = load(MODEL_PKL)
        pipe, feats_num, feats_cat, menu = pack["pipe"], pack["feats_num"], pack["feats_cat"], pack["menu"]
        X = menu.copy()
        X["people"] = people; X["temp_c"] = temp_c; X["lux"] = lux
        X["hour"] = hour; X["is_weekend"] = is_weekend
        X["crowd_temp"] = people * temp_c; X["crowd_lux"] = people * lux
        yhat = pipe.predict(X[feats_num+feats_cat])
        per_min = (X["prep_time_min"]).clip(lower=1)
        score = yhat / per_min if people >= 15 else yhat
        order = score.argsort()[::-1][:top_k]
        recs = X.iloc[order][["name","price","cost","prep_time_min","category"]].assign(
            expected_profit=yhat[order], score=score[order]
        ).to_dict(orient="records")
        mode = "model"
    else:
        import csv
        rows = []
        with MENU_CSV.open() as f:
            r = csv.DictReader(f)
            for row in r:
                row["price"]=float(row["price"]); row["cost"]=float(row["cost"])
                row["prep_time_min"]=float(row["prep_time_min"])
                rows.append(row)
        # quick, interpretable scoring
        items=[]
        for row in rows:
            margin = row["price"]-row["cost"]
            cat = (row.get("category") or "").lower()
            hot = "hot" in cat; cold = "cold" in cat
            score = 0.02*people*margin
            score += (0.03*temp_c*margin) if cold else 0.0
            score += (0.03*(30-temp_c)*margin) if hot else 0.0
            score += (0.01*(lux/200.0)*margin) if cold else 0.0
            if people >= 15: score /= max(row["prep_time_min"],1.0)
            items.append({
                "name": row["name"], "price": row["price"], "cost": row["cost"],
                "prep_time_min": row["prep_time_min"], "category": row.get("category"),
                "expected_profit": margin*max(0.0, people/50.0), "score": score
            })
        items.sort(key=lambda d: d["score"], reverse=True)
        recs = items[:top_k]; mode = "rules"

    return {
        "context": {"people": people, "temp_c": temp_c, "lux": lux, "hour": hour, "is_weekend": is_weekend},
        "mode": mode,
        "items": recs
    }

# ---------- main loop ----------
def main():
    print("[orchestrator] sampling every", POLL_SEC, "sec; Ctrl+C to stop.")
    while True:
        ts = dt.datetime.now().isoformat(timespec="seconds")
        # 1) collect
        people = read_people()
        temp_c = read_temp_c()
        lux    = read_lux()
        _ = refresh_camera_image()  # optional: update frame0.jpg for your UI

        # 2) integrate to deliverables
        res = integrate_and_decide(people, temp_c, lux, top_k=5)

        # 3) print (or save to JSON / send to UI)
        ctx = res["context"]
        print(f"{ts}  people={ctx['people']}  temp={ctx['temp_c']:.1f}°C  lux={ctx['lux']:.0f}  mode={res['mode']}")
        for i, it in enumerate(res["items"], 1):
            print(f"  {i}. {it['name']}  ₹{it['price']:.0f}  ({it['category']})  score={it['score']:.2f}")
        sys.stdout.flush()
        time.sleep(POLL_SEC)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[orchestrator] stopped.")
