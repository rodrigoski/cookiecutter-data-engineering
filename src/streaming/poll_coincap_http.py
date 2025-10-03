# src/streaming/poll_binance_http.py
import json, time, os
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Falta 'requests'. Instala con: pip install requests")

# Rutas relativas al raíz del proyecto (<root>/src/streaming/poll_binance_http.py)
ROOT_DIR = Path(__file__).resolve().parents[2]   # streaming/ -> src/ -> root
OUT_DIR = ROOT_DIR / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Parámetros (override por variables de entorno)
SYMBOL       = os.getenv("POLL_SYMBOL", "BTCUSDT").upper()   # p.ej. BTCUSDT, ETHUSDT
INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC", "5"))      # segundos entre lecturas
ITERATIONS   = int(os.getenv("POLL_ITERATIONS", "20"))       # número de lecturas

URL = f"https://api.binance.com/api/v3/ticker/price?symbol={SYMBOL}"
DST = OUT_DIR / f"poll_binance_{SYMBOL}_{datetime.now().strftime('%Y-%m-%d')}.jsonl"

for i in range(ITERATIONS):
    r = requests.get(URL, timeout=10)
    r.raise_for_status()
    j = r.json()

    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": "binance",
        "instrument": j["symbol"],
        "price_usd": float(j["price"])
    }

    with DST.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

    print(f"[POLL] {i+1}/{ITERATIONS} -> {rec}")
    time.sleep(INTERVAL_SEC)

print("[DONE] Archivo:", DST.resolve())