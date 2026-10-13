import time
import requests

BASE = "http://127.0.0.1:8000"

def test_api():
    print("Testing GET /api/status...")
    r = requests.get(f"{BASE}/api/status")
    print("Status:", r.status_code, r.json())

    print("\nStarting Harvester via POST /api/start...")
    r = requests.post(f"{BASE}/api/start")
    print("Start Response:", r.status_code, r.json())

    print("\nWaiting 12 seconds for live candles to stream into Neon PostgreSQL...")
    time.sleep(12)

    print("\nChecking updated status / metrics...")
    r = requests.get(f"{BASE}/api/status")
    print("Status:", r.status_code, r.json())

    print("\nFetching recent candles from Neon PostgreSQL via GET /api/candles...")
    r = requests.get(f"{BASE}/api/candles?limit=5")
    data = r.json()
    print(f"Candles retrieved ({len(data.get('candles', []))}):")
    for c in data.get("candles", []):
        print(f"  {c['symbol']:<12} | ts={c['timestamp']} | O={c['open']} | H={c['high']} | L={c['low']} | C={c['close']} | V={c['volume']}")

if __name__ == "__main__":
    test_api()
