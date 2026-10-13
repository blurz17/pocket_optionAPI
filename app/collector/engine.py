import asyncio
import json
import logging
import ssl
import time
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Set, Callable
import websockets

from app.config import config
from app.database import db
from app.alerts.telegram import notifier
from app.collector.normalizer import CandleNormalizer

logger = logging.getLogger("collector.engine")

class EngineStatus(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    RECONNECTING = "RECONNECTING"
    AUTH_ERROR = "AUTH_ERROR"

class CollectorEngine:
    def __init__(self):
        self.status: EngineStatus = EngineStatus.STOPPED
        self.symbols: List[str] = list(config.DEFAULT_SYMBOLS)
        self.timeframe: int = config.DEFAULT_TIMEFRAME
        self.is_demo: int = config.PO_IS_DEMO

        self.session_token: str = config.PO_SESSION
        self.uid: int = config.PO_UID
        self.platform: int = config.PO_PLATFORM

        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._pause_event = asyncio.Event()
        self._pause_event.set() # Not paused initially

        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.reconnect_count: int = 0
        self.server_name: Optional[str] = None

        # Telemetry & Metrics
        self.metrics = {
            "status": self.status.value,
            "candles_total": 0,
            "candles_per_min": 0,
            "ticks_total": 0,
            "uptime_seconds": 0,
            "latency_ms": 0,
            "start_time": None,
            "active_symbols": len(self.symbols),
            "db_type": "PostgreSQL (Neon)" if not config.USE_SQLITE_FALLBACK else "SQLite",
            "last_tick_time": None,
        }

        # In-memory tick buffers for constructing candles: {symbol: [(ts, price)]}
        self._tick_buffers: Dict[str, List[tuple]] = {}
        # Recent raw log queue for Web UI streaming
        self._log_listeners: Set[asyncio.Queue] = set()
        self._candles_minute_counter: int = 0
        self._last_minute_calc_time = time.time()

    def add_log_listener(self, queue: asyncio.Queue):
        self._log_listeners.add(queue)

    def remove_log_listener(self, queue: asyncio.Queue):
        self._log_listeners.discard(queue)

    def log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {"time": timestamp, "level": level, "message": message}
        if level == "INFO":
            logger.info(message)
        elif level == "WARN":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
        else:
            logger.debug(message)

        # Broadcast to all connected web dashboards
        for q in list(self._log_listeners):
            try:
                q.put_nowait(entry)
            except asyncio.QueueFull:
                pass

    def get_status(self) -> Dict[str, Any]:
        uptime = int(time.time() - self.metrics["start_time"]) if self.metrics["start_time"] else 0
        self.metrics["uptime_seconds"] = uptime
        self.metrics["status"] = self.status.value
        self.metrics["active_symbols"] = len(self.symbols)
        return dict(self.metrics)

    async def update_session(self, session: str, uid: Optional[int] = None, is_demo: Optional[int] = None):
        self.session_token = session.strip()
        if uid is not None:
            self.uid = uid
        if is_demo is not None:
            self.is_demo = is_demo
        self.log("INFO", f"Updated session token (uid={self.uid}, isDemo={self.is_demo}).")
        # If currently in auth error, restart collector
        if self.status == EngineStatus.AUTH_ERROR:
            await self.start()

    async def start(self):
        if self.status in (EngineStatus.RUNNING, EngineStatus.STARTING):
            self.log("WARN", "Collector is already running.")
            return

        self.status = EngineStatus.STARTING
        self._stop_event.clear()
        self._pause_event.set()
        self.metrics["start_time"] = time.time()
        self.reconnect_count = 0

        self.log("INFO", f"Starting Collector Engine on {len(self.symbols)} symbols (timeframe={self.timeframe}s)...")
        notifier.notify_background(
            f"🚀 *Pocket Option Harvester STARTED*\n\n"
            f"• *Database:* {self.metrics['db_type']}\n"
            f"• *Symbols:* {len(self.symbols)}\n"
            f"• *Timeframe:* {self.timeframe}s"
        )

        self._task = asyncio.create_task(self._run_loop())

    async def pause(self):
        if self.status == EngineStatus.RUNNING:
            self.status = EngineStatus.PAUSED
            self._pause_event.clear()
            self.log("INFO", "Collector PAUSED.")
            notifier.notify_background("⏸️ *Pocket Option Harvester PAUSED*")

    async def resume(self):
        if self.status == EngineStatus.PAUSED:
            self.status = EngineStatus.RUNNING
            self._pause_event.set()
            self.log("INFO", "Collector RESUMED.")
            notifier.notify_background("▶️ *Pocket Option Harvester RESUMED*")

    async def stop(self):
        if self.status == EngineStatus.STOPPED:
            return

        self.log("INFO", "Stopping Collector Engine...")
        self.status = EngineStatus.STOPPED
        self._stop_event.set()
        self._pause_event.set() # Unblock if paused

        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
            self.ws = None

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        self.log("INFO", "Collector Engine stopped.")
        notifier.notify_background("🛑 *Pocket Option Harvester STOPPED*")

    async def _run_loop(self):
        base_delay = 2.0
        max_delay = 30.0

        while not self._stop_event.is_set():
            await self._pause_event.wait()
            try:
                ws_url = config.DEMO_WS_URL if self.is_demo == 1 else config.REAL_WS_URL
                self.log("INFO", f"Connecting to WebSocket: {ws_url} (Mode: {'DEMO' if self.is_demo == 1 else 'REAL'})...")

                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                headers = {
                    "Origin": "https://pocketoption.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8,fa;q=0.7,ay;q=0.6",
                }

                t0 = time.time()
                async with websockets.connect(
                    ws_url,
                    ssl=ssl_context,
                    additional_headers=headers,
                    open_timeout=10,
                    close_timeout=5,
                ) as ws:
                    self.ws = ws
                    self.metrics["latency_ms"] = round((time.time() - t0) * 1000, 1)

                    # Handshake
                    m0 = await ws.recv()
                    if m0.startswith("0"):
                        await ws.send("40")
                        m1 = await ws.recv()

                    # Send Auth
                    auth_payload = {
                        "session": self.session_token,
                        "isDemo": self.is_demo,
                        "uid": self.uid,
                        "platform": self.platform,
                        "isFastHistory": True,
                        "isOptimized": True
                    }
                    await ws.send(f'42{json.dumps(["auth", auth_payload])}')
                    self.log("INFO", "Sent authentication frame. Waiting for server confirmation...")

                    auth_ok = False
                    auth_deadline = time.time() + 8
                    while time.time() < auth_deadline:
                        frame = await asyncio.wait_for(ws.recv(), timeout=3.0)
                        if isinstance(frame, str):
                            if frame == "41" or "NotAuthorized" in frame:
                                self.status = EngineStatus.AUTH_ERROR
                                self.log("ERROR", "Authentication REJECTED by server (`41 Unauthorized`). Token may be expired.")
                                notifier.notify_background("🚨 *Session Expired:* Pocket Option rejected credentials (`41 Unauthorized`).")
                                return
                            elif frame.startswith("451-["):
                                meta = json.loads(frame.split("-", 1)[1])
                                b = await asyncio.wait_for(ws.recv(), timeout=3.0)
                                if isinstance(b, bytes):
                                    data = json.loads(b.decode("utf-8"))
                                    if meta[0] == "successauth":
                                        auth_ok = True
                                        self.server_name = data.get("serverName", "Connected")
                                        self.log("INFO", f"Authenticated successfully: {self.server_name}")
                                        break
                                    elif meta[0] == "updateAssets":
                                        self.log("INFO", f"Loaded asset catalog ({len(data)} assets).")

                    if not auth_ok:
                        raise ConnectionError("Server did not confirm authentication (timeout).")

                    # Authenticated!
                    self.status = EngineStatus.RUNNING
                    self.reconnect_count = 0
                    base_delay = 2.0

                    # Subscribe to symbols & request history
                    await self._subscribe_all(ws)

                    # Run listener tasks
                    listener_task = asyncio.create_task(self._listen_frames(ws))
                    ping_task = asyncio.create_task(self._ping_loop(ws))
                    calc_task = asyncio.create_task(self._metrics_loop())

                    done, pending = await asyncio.wait(
                        [listener_task, ping_task, calc_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    for t in pending:
                        t.cancel()
                    for t in done:
                        exc = t.exception()
                        if exc:
                            raise exc

            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.status == EngineStatus.AUTH_ERROR:
                    break
                self.reconnect_count += 1
                self.status = EngineStatus.RECONNECTING
                delay = min(base_delay * (1.5 ** self.reconnect_count), max_delay)
                self.log("WARN", f"Connection dropped: {e}. Reconnecting attempt #{self.reconnect_count} in {delay:.1f}s...")
                notifier.notify_background(f"⚠️ *Harvester Disconnected:* {e}\nAttempting reconnect #{self.reconnect_count} in {delay:.1f}s...")
                await asyncio.sleep(delay)

    async def _subscribe_all(self, ws):
        """Staggers subscriptions across all configured symbols."""
        self.log("INFO", f"Subscribing to {len(self.symbols)} instruments...")
        now_ts = int(time.time())
        for idx, sym in enumerate(self.symbols):
            try:
                await ws.send(f'42["changeSymbol",{{"asset":"{sym}","period":{self.timeframe}}}]')
                await ws.send(f'42["subfor","{sym}"]')
                # Request 100 historical bars to bridge gaps
                hist_req = f'42["loadHistoryPeriod",{{"asset":"{sym}","index":{now_ts + idx},"offset":100,"period":{self.timeframe},"time":{now_ts}}}]'
                await ws.send(hist_req)
                await asyncio.sleep(0.08) # 80ms stagger
            except Exception as e:
                self.log("WARN", f"Error subscribing to {sym}: {e}")

    async def _ping_loop(self, ws):
        while not self._stop_event.is_set():
            await asyncio.sleep(20)
            if self.status == EngineStatus.RUNNING:
                try:
                    await ws.send('42["ps"]')
                except Exception as e:
                    self.log("WARN", f"Ping error: {e}")
                    break

    async def _metrics_loop(self):
        """Calculates rolling candles/min."""
        while not self._stop_event.is_set():
            await asyncio.sleep(10)
            now = time.time()
            elapsed = now - self._last_minute_calc_time
            if elapsed >= 60:
                self.metrics["candles_per_min"] = int(self._candles_minute_counter * (60.0 / elapsed))
                self._candles_minute_counter = 0
                self._last_minute_calc_time = now

    async def _listen_frames(self, ws):
        while not self._stop_event.is_set():
            await self._pause_event.wait()
            frame = await ws.recv()

            if isinstance(frame, str):
                if frame == "2":
                    await ws.send("3")
                elif frame.startswith("451-["):
                    meta = json.loads(frame.split("-", 1)[1])
                    msg_type = meta[0]
                    bin_frame = await asyncio.wait_for(ws.recv(), timeout=3.0)
                    if isinstance(bin_frame, bytes):
                        data = json.loads(bin_frame.decode("utf-8"))
                        await self._handle_data_message(msg_type, data)

    async def _handle_data_message(self, msg_type: str, data: Any):
        if msg_type == "updateStream":
            # Real-time ticks: [[sym, ts, price]]
            for item in data:
                if len(item) >= 3:
                    sym, ts, price = item[0], item[1], item[2]
                    self.metrics["ticks_total"] += 1
                    self.metrics["last_tick_time"] = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

                    if sym not in self._tick_buffers:
                        self._tick_buffers[sym] = []
                    self._tick_buffers[sym].append((ts, price))

                    # Process tick buffers into closed candles if period passed
                    if len(self._tick_buffers[sym]) > 50:
                        norm = CandleNormalizer.ticks_to_candles(self._tick_buffers[sym], self.timeframe)
                        closed = CandleNormalizer.normalize_closed_candles(norm, self.timeframe, int(ts))
                        if closed:
                            saved = await db.save_candles(sym, self.timeframe, closed)
                            if saved > 0:
                                self.metrics["candles_total"] += saved
                                self._candles_minute_counter += saved
                        # Retain only the newest ticks
                        self._tick_buffers[sym] = self._tick_buffers[sym][-20:]

        elif msg_type == "loadHistoryPeriodFast":
            # Historical batch bars
            candles = data.get("data", [])
            asset = data.get("asset") or "unknown"
            if candles:
                closed = CandleNormalizer.normalize_closed_candles(candles, self.timeframe)
                if closed:
                    saved = await db.save_candles(asset, self.timeframe, closed)
                    if saved > 0:
                        self.metrics["candles_total"] += saved
                        self._candles_minute_counter += saved
                        self.log("INFO", f"Ingested {saved} historical candles for `{asset}`.")

engine = CollectorEngine()
