Pocket Option Market Data Harvester: Comprehensive Technical & Architecture Report (v2.0)

**Project:** Pocket Option 24/7 Market Data Harvester (AI/ML Pipeline)  
**Version:** 2.0.0 (Enterprise Modular Architecture)  
**Target Environment:** Local Residential Client + Cloud Neon PostgreSQL + Telegram Alerting  
**Author:** AI Engineering & Architecture Team  
**Date:** October 2026  

---

## 1. Executive Summary

The **Pocket Option Market Data Harvester** is a high-performance, asynchronous market data collection engine engineered to continuously extract tick-level and candlestick (OHLCV) market data from Pocket Option regular and Over-The-Counter (OTC) financial markets.

The system is designed for quantitative finance and machine learning workflows, ensuring that all collected data has **zero lookahead bias**, is **mathematically validated**, and is **idempotently deduplicated** into **Neon Serverless PostgreSQL (AWS)** in real time.

With the latest **v2.0 Architectural Refactoring**, the system has transitioned from a monolithic script into an **enterprise-grade, modular FastAPI application** backed by dependency injection, asynchronous storage interfaces, domain-driven error handling, and a complete suite of **123 automated tests** passing at 100%.

---

## 2. Refactoring Analysis: What Changed & Why

The codebase was refactored to achieve decoupling, testability, and resilience.

### Before vs. After Architecture

```
┌──────────────────────────────────────────────┐       ┌──────────────────────────────────────────────┐
│             BEFORE (v1.0 Monolith)           │       │             AFTER (v2.0 Modular)             │
├──────────────────────────────────────────────┤       ├──────────────────────────────────────────────┤
│ • Module-level global singletons             │  ──►  │ • Lifespan Dependency Injection (app.state)  │
│ • Monolithic web server file (server.py)     │  ──►  │ • Modular APIRouter per domain (api/)        │
│ • Synchronous blocking sqlite3 calls         │  ──►  │ • Asynchronous aiosqlite integration        │
│ • Manual dict parsing & loose validation     │  ──►  │ • Strict Pydantic v2 schema validation       │
│ • Generic HTTP errors / unhandled crashes    │  ──►  │ • Domain Exception hierarchy & error handlers│
│ • Untested WebSocket & route handlers        │  ──►  │ • 123 automated tests (pytest-asyncio)      │
│ • Hardcoded database switching               │  ──►  │ • Structural DatabaseProtocol interface     │
└──────────────────────────────────────────────┘       └──────────────────────────────────────────────┘
```

### Key Architectural Upgrades:

1. **Lifespan-Managed Dependency Injection (`app/main.py`):**
   - Eliminated global state and circular imports.
   - Database pools, the Telegram notifier, and the WebSocket engine are initialized in a strict, deterministic sequence during FastAPI startup and stored on `app.state`.
   - On shutdown, resources are gracefully terminated in reverse order (Engine stopped $\to$ Database disconnected $\to$ Notifier closed).

2. **Structural Database Interface (`app/database/base.py`):**
   - Introduced `@runtime_checkable` `DatabaseProtocol` using Python's `typing.Protocol`.
   - Both `PostgresManager` and `SQLiteManager` adhere to the identical contract, making storage backends 100% interchangeable without tight coupling.

3. **Asynchronous Local Storage (`app/database/sqlite.py`):**
   - Replaced Python's standard blocking `sqlite3` library with `aiosqlite`.
   - Database operations (candle insertions and metric queries) no longer block the asyncio event loop, eliminating tick-processing latency spikes.

4. **Domain Exception Hierarchy & Error Handling (`app/core/errors.py`):**
   - Implemented domain exceptions (`CollectorAlreadyRunning`, `CollectorNotRunning`, `SessionRequired`, `DatabaseNotConnected`).
   - Mapped directly to standard HTTP status codes (RFC 409 Conflict, 400 Bad Request, 503 Service Unavailable, 422 Unprocessable Content).

5. **Pydantic v2 Request/Response Schemas (`app/schemas/`):**
   - All inbound payloads (`/api/session`, `/api/config`) and outbound responses (`/api/status`, `/api/candles`) are strictly validated with custom field validators (stripping whitespace, enforcing positive timeframes, and rejecting empty symbols).

6. **Automated Test Suite (`tests/`):**
   - **123 automated unit and integration tests** covering collector lifecycle, websocket normalizer, schemas, error handlers, and database operations.
   - 100% passing in 2.3 seconds with complete dependency mocking.

---

## 3. End-to-End System Data Flow

The following sequence diagram details how data moves through the refactored architecture from the WebSocket wire to the AI/ML database:

```mermaid
sequenceDiagram
    autonumber
    actor Client as Residential User / Script
    participant App as FastAPI Lifespan (main.py)
    participant Engine as Collector Engine (engine.py)
    participant Normalizer as AI Normalizer (normalizer.py)
    participant PO as Pocket Option Gateway (Socket.IO)
    participant DB as Neon PostgreSQL (Cloud)
    participant TG as Telegram Bot
    actor ML as AI/ML Model (Colab/PyTorch)

    Client->>App: Launch Application (run_dashboard.py)
    App->>DB: Connect Connection Pool (asyncpg)
    App->>TG: Initialize Async HTTP Session
    App->>Engine: Inject (db, notifier) & Start Engine
    
    Engine->>PO: Handshake (0 -> 40 -> 42["auth", session])
    PO-->>Engine: 451-["updateAssets"] (Handshake Confirmed)
    
    loop Multiplexed Market Stream
        Engine->>PO: 42["changeSymbol", {"asset": sym, "period": 60}]
        Engine->>PO: 42["subfor", sym]
        PO-->>Engine: Raw WebSocket Tick & Candle Frames
        Engine->>Normalizer: Process Frames (Filter forming candles)
        Normalizer-->>Engine: Validated Closed Bars Only
        Engine->>DB: Batch Insert (ON CONFLICT DO NOTHING)
    end

    opt Disconnection / Error
        PO--xEngine: Socket Drop
        Engine->>TG: Send Incident Notification
        Engine->>Engine: Exponential Backoff Reconnect (2s -> 4s -> 8s)
    end

    ML->>DB: SQL Query Closed Candlesticks (Pandas/PyTorch)
```

---

## 4. Comprehensive Feature Catalog

### 1. Market Data Ingestion & Multiplexing
- **Socket.IO v4 Engine:** Full implementation of the binary and JSON-wrapped framing used by Pocket Option servers.
- **Concurrent Asset Harvesting:** Dynamically multiplexes across unlimited symbols simultaneously (Top 8 OTC, All 114 OTC pairs, and Major Forex pairs) over a single persistent socket.
- **Heartbeat Management:** Issues scheduled keep-alive ping frames (`42["ps"]`) every 20 seconds to guarantee connection persistence.

### 2. AI/ML Normalization (Zero Lookahead Bias)
- **Forming-Candle Elimination:** Prevents machine learning models from training on in-progress, moving candles. Only candles whose timeframe window has strictly closed ($\text{timestamp} + \text{timeframe} \le \text{current\_time}$) are committed.
- **Financial Invariant Verification:** Checks and enforces that every OHLC bar satisfies:
  $$\text{High} \ge \max(\text{Open}, \text{Close}), \quad \text{Low} \le \min(\text{Open}, \text{Close})$$
- **Tick Aggregation:** Can synthesize raw high-frequency ticks into custom candlestick timeframes (1s, 5s, 15s, 30s, 60s, 5m, 15m, 1h).

### 3. High-Throughput Cloud Storage
- **Neon Serverless PostgreSQL:** Managed connection pool with auto-reconnect, health checks, and prepared statement caching.
- **Idempotent Inserts:** Powered by composite database constraints:
  ```sql
  CONSTRAINT uq_symbol_tf_ts UNIQUE (symbol, timeframe, timestamp)
  ```
- **Duplicate Prevention:** Executes all writes with `ON CONFLICT (symbol, timeframe, timestamp) DO NOTHING`. Network retries never produce duplicate rows.
- **Zero-Data-Loss SQLite Fallback:** Automatically switches to `aiosqlite` if the cloud connection is interrupted, queuing candles locally until cloud connectivity is restored.

### 4. Interactive Web Dashboard (`app/web/static/index.html`)
- **Real-Time Telemetry:** Live counters showing total database candles, ingestion rate (candles/min), tick counts, latency (ms), and connection health.
- **Live In-Browser Terminal:** WebSocket stream (`/ws/logs`) piping server events, warnings, and errors directly to the UI.
- **Dataset Exporter:** Direct `/api/export` endpoint that streams up to 5,000 recent candles directly into a downloadable CSV file.
- **Instrument Presets:** 1-click preset selector for Top 8 OTC, All 114 OTC assets, and Major Forex currencies.

### 5. Automated Telegram Incident Bot
- **Real-Time Alerts:** Notifies the client on start, manual pause, resume, disconnection events, automatic recovery backfills, and session expiration.
- **Non-Blocking Architecture:** Dispatched as background asynchronous tasks (`notify_background`) without adding latency to the market data loop.

---

## 5. Technical Forensic: Why Cloud Scrapers (Heroku/AWS) Fail

During testing on Heroku, the application encountered:
```text
[ERROR] Authentication REJECTED by server (`41 Unauthorized`). Token may be expired.
```
Running the exact same code on the local residential computer returned:
```text
Status: RUNNING | Candles: 264 | Ticks: 53,865 | DB: PostgreSQL (Neon)
```

### The Root Cause: Cryptographic IP Binding

```
CLIENT MACHINE (Residential IP: 196.141.35.31)
  │
  ├─► Generates Session: a:4:{...;s:10:"ip_address";s:13:"196.141.35.31";...} + HMAC Hash
  │
  ├─► Local Run:  TCP Outbound IP (196.141.35.31) == Session IP (196.141.35.31)  ══► 🟢 200 AUTHORIZED
  │
  └─► Heroku Run: TCP Outbound IP (54.210.x.x)    != Session IP (196.141.35.31)  ══► 🚨 41 UNAUTHORIZED
```

1. **Serialized Session Payload:** The session string generated by Pocket Option's CodeIgniter backend embeds the client's home IP (`s:10:"ip_address";s:13:"196.141.35.31"`).
2. **HMAC Signature:** A cryptographic signature is appended to the payload, calculated using Pocket Option's private server secret. Any modification of the IP string breaks the signature.
3. **Server TCP Inspection:** When Heroku connects, the incoming socket originates from Amazon AWS data centers in Virginia (`54.210.x.x`). Pocket Option compares the socket IP to the session IP. Because they do not match, the connection is instantly rejected to prevent session hijacking.

> [!IMPORTANT]
> **Conclusion:** Cloud-only scraping from Heroku or AWS without residential proxies is fundamentally blocked by the broker's security architecture.

---

## 6. The Winning Solution: Hybrid Residential-Cloud Model

The refactored architecture provides the definitive enterprise solution:

| Component | Location | Why It Wins |
| :--- | :--- | :--- |
| **Ingestion Agent** | Client PC (Residential) | Outbound IP matches session IP 100%. Zero IP blocking, zero `41 Unauthorized` errors. |
| **Market Database** | Cloud (Neon PostgreSQL) | Centralized, secure storage. Models in Google Colab, AWS, or Jupyter query it globally. |
| **Alert System** | Cloud (Telegram Bot) | Real-time push notifications delivered to the client's phone 24/7. |
| **Hosting Cost** | $0.00 / month | Zero server costs for scraping dynos; Neon serverless free tier handles the data volume. |

---

## 7. REST & WebSocket API Specification

The refactored application exposes modular endpoints under the `/api` prefix:

### Collector Control (`/api/collector`)
| Method | Endpoint | Description | Status Codes |
| :---: | :--- | :--- | :---: |
| `GET` | `/api/status` | Returns live engine metrics, DB candle totals, and connection health | `200` |
| `POST` | `/api/start` | Starts the collector engine | `200`, `409` (if already running) |
| `POST` | `/api/pause` | Pauses harvesting without terminating the socket | `200`, `409` (if stopped) |
| `POST` | `/api/resume` | Resumes a paused collector | `200`, `409` (if stopped) |
| `POST` | `/api/stop` | Stops collection and closes the WebSocket connection | `200` |

### Session & Configuration (`/api/session`, `/api/config`)
| Method | Endpoint | Description | Payload |
| :---: | :--- | :--- | :--- |
| `POST` | `/api/session` | Updates session token dynamically | `{"session": "...", "uid": 123, "is_demo": 0}` |
| `POST` | `/api/config` | Updates candle timeframe and asset list | `{"timeframe": 60, "symbols": ["EURUSD_otc"]}` |

### Market Data & Export (`/api/candles`)
| Method | Endpoint | Description | Query Parameters |
| :---: | :--- | :--- | :--- |
| `GET` | `/api/candles` | Returns recent OHLCV bars from DB | `symbol`, `limit` (default: 25) |
| `GET` | `/api/symbols` | Returns candle counts per asset | None |
| `GET` | `/api/export` | Streams recent candles as a CSV file | `symbol`, `limit` (default: 5000) |

### WebSocket Telemetry (`/ws/logs`)
- Persistent bi-directional WebSocket streaming live structured JSON logs and status heartbeats every second:
  ```json
  {"type": "log", "data": {"time": "14:30:00", "level": "INFO", "message": "Saved 4 candles to Neon PostgreSQL."}}
  {"type": "status", "data": {"status": "RUNNING", "candles_total": 264, "latency_ms": 627.7}}
  ```

---

## 8. Automated Test Suite (123 Tests Passing)

The project includes a test suite built on `pytest` and `pytest-asyncio`:

```text
======================= test session starts =======================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
collected 123 items

tests/test_alerts_telegram.py .....................         [ 17%]
tests/test_api_candles.py .................                 [ 30%]
tests/test_api_collector.py ................                [ 43%]
tests/test_api_session.py ...........                       [ 52%]
tests/test_collector_engine.py ...............              [ 65%]
tests/test_config.py .......                                [ 70%]
tests/test_database_sqlite.py ..............                 [ 82%]
tests/test_errors.py ........                               [ 88%]
tests/test_normalizer.py ...........                        [ 97%]
tests/test_schemas.py ...                                   [100%]

================ 123 passed, 7 warnings in 2.36s =================
```

---

## 9. Client Operating Guide

### Running the Harvester (1 Click)
1. Ensure dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the harvester:
   ```bash
   python run_dashboard.py
   ```
3. Open your browser to the Web Dashboard:
   👉 **`http://127.0.0.1:8000`**
4. Click **Start Harvester**. The dashboard will display `RUNNING`, and candles will stream directly into Neon PostgreSQL.

### Connecting AI/ML Training Models
Data scientists can query the Neon cloud database directly in Python:
```python
import pandas as pd
import psycopg2

NEON_URL = "postgresql://user:password@ep-autumn-moon-...aws.neon.tech/neondb?sslmode=require"

query = """
    SELECT timestamp, open, high, low, close, volume
    FROM candles
    WHERE symbol = 'EURUSD_otc' AND timeframe = 60
    ORDER BY timestamp ASC;
"""

df = pd.read_sql(query, NEON_URL)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
print(f"Loaded {len(df)} candles for model training.")
print(df.tail())
```
