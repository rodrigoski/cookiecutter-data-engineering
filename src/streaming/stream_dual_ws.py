# src/streaming/stream_dual_ws.py  (solo Binance)
import asyncio, json, os, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import websockets
    from websockets.exceptions import ConnectionClosed, InvalidStatusCode
except ImportError:
    raise SystemExit("Falta 'websockets'. Instala con: pip install websockets")

# Rutas relativas al raíz del proyecto
# Este archivo está en: <root>/src/streaming/stream_dual_ws.py
ROOT_DIR = Path(__file__).resolve().parents[2]   # streaming/ -> src/ -> root
OUT_DIR = ROOT_DIR / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BINANCE_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

def out_path_for_today() -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    return OUT_DIR / f"stream_ws_{today}.jsonl"

async def consume_binance(ws):
    """
    Lee un mensaje del stream de trades de Binance y lo normaliza.
    Esquema del WS (trade): https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams
    """
    msg = await asyncio.wait_for(ws.recv(), timeout=25)
    d = json.loads(msg)
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": "binance",
        "instrument": d["s"],               # BTCUSDT
        "price": float(d["p"]),
        "currency": "USDT",
        "qty": float(d["q"]),
        "trade_id": d["t"]
    }

async def run_stream(max_events=None, max_seconds=None):
    """
    Parámetros opcionales (también por variables de entorno):
      - WS_MAX_EVENTS  (int)
      - WS_MAX_SECONDS (int)
    """
    try:
        if max_events is None and "WS_MAX_EVENTS" in os.environ:
            max_events = int(os.environ["WS_MAX_EVENTS"])
        if max_seconds is None and "WS_MAX_SECONDS" in os.environ:
            max_seconds = int(os.environ["WS_MAX_SECONDS"])
    except Exception:
        pass

    deadline = datetime.now() + timedelta(seconds=max_seconds) if max_seconds else None
    written = 0
    backoff = 1

    # Línea de prueba para validar permisos/ruta
    with out_path_for_today().open("a", encoding="utf-8") as f:
        f.write(json.dumps({"_probe": True, "ts": datetime.now(timezone.utc).isoformat()}) + "\n")

    while True:
        # Criterios de parada
        if max_events is not None and written >= max_events:
            print(f"[DONE] Eventos: {written}")
            print(out_path_for_today().resolve())
            return
        if deadline is not None and datetime.now() >= deadline:
            print(f"[DONE] Tiempo agotado. Eventos: {written}")
            print(out_path_for_today().resolve())
            return

        try:
            async with websockets.connect(BINANCE_URL, ping_interval=20, ping_timeout=20) as ws:
                backoff = 1
                while True:
                    if deadline is not None and datetime.now() >= deadline:
                        break
                    rec = await consume_binance(ws)
                    with out_path_for_today().open("a", encoding="utf-8") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    written += 1
                    if max_events is not None and written >= max_events:
                        break

        except asyncio.TimeoutError:
            # Reinicia el bucle para evitar bloqueos largos si no llegan mensajes
            continue
        except (InvalidStatusCode, ConnectionClosed, OSError) as e:
            # Desconexión o rechazo: espera exponencial y reintenta
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)
        except KeyboardInterrupt:
            print("\n[STOP] Cancelado por el usuario.")
            sys.exit(0)
        except Exception:
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)

if __name__ == "__main__":
    try:
        asyncio.run(run_stream())
    except KeyboardInterrupt:
        print("\n[STOP] Cancelado por el usuario.")