# recommend_from_text_v2.py
import os, argparse, json
import google.generativeai as genai


SYSTEM = (
"You are a restaurant menu optimizer.\n"
"Return STRICT JSON only (no prose).\n"
'Schema: {"items":[{"name":str,"reason":str}], "notes":str}\n'
"Rules:\n"
"- Temperature readings are Fahrenheit.\n"
"- Light readings are in lux.\n"
"- Menu is text; only pick item names that appear in it. But column names are price, name, temperature\n"
"- If hot/bright, prefer cold/refreshing; if cool/dim, prefer hot/comfort.\n"
"- Also write a funny quote on aww, it's cold outside, have these noodles etc"
"-On backend, calculate the price and precition of getting that profit in total these days"
"- If price is present, lightly prefer higher price as margin proxy.\n"
"- Suggest at most K items. Keep each reason ≤ 10 words."
)


def tail_lines(path: str, n: int) -> list[str]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    return lines[-n:] if lines else []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--temp_file", required=True, help="temp log (°F, one value per line)")
    ap.add_argument("--lux_file",  required=True, help="lux log (lux, one value per line)")
    ap.add_argument("--menu_file", required=True, help="menu text (CSV-like)")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--tail", type=int, default=40, help="use last N lines from each log")
    ap.add_argument("--model", default="gemini-2.5-flash")
    args = ap.parse_args()

    # Read inputs
    temp_lines = tail_lines(args.temp_file, args.tail)
    lux_lines  = tail_lines(args.lux_file,  args.tail)
    menu_lines = tail_lines(args.menu_file, args.tail)

    # Build a small JSON payload (safe—no backticks/braces issues)
    payload = {
        "K": args.k,
        "temperature_f_lines": temp_lines,
        "lux_lines": lux_lines,
        "menu_lines": menu_lines
    }

    print('Fetching recommendations.............')

    # Call Gemini
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(args.model)
    resp = model.generate_content(
        [{"text": SYSTEM}, {"text": json.dumps(payload, ensure_ascii=False)}],
        generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
    )

    # Print STRICT JSON from the model
    print(resp.text)

if __name__ == "__main__":
    main()
