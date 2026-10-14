import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_client_guide_pdf(filename="Pocket_Option_Harvester_Client_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom Palettes
    c_primary = colors.HexColor("#0F172A")    # Deep Slate
    c_accent = colors.HexColor("#2563EB")     # Blue
    c_accent_light = colors.HexColor("#EFF6FF")
    c_success = colors.HexColor("#059669")    # Emerald
    c_card_bg = colors.HexColor("#F8FAFC")    # Light Gray
    c_border = colors.HexColor("#E2E8F0")     # Border
    c_text = colors.HexColor("#1E293B")
    c_text_muted = colors.HexColor("#64748B")

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=c_primary,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=c_accent,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=c_text,
        spaceAfter=6,
    )

    body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    bullet_style = ParagraphStyle(
        "BulletText",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=c_text,
    )

    story = []

    # ── HEADER BLOCK ──────────────────────────────────────────────────────────
    story.append(Paragraph("Pocket Option Market Data Harvester", title_style))
    story.append(Paragraph("Enterprise AI/ML Pipeline & Dashboard Operational Manual", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=c_accent, spaceBefore=4, spaceAfter=12))

    # Meta Info Table
    meta_data = [
        [
            Paragraph("<b>Target Platform:</b> Pocket Option (OTC & Global)", body_style),
            Paragraph("<b>Architecture:</b> FastAPI + WebSocket + Async Engine", body_style),
        ],
        [
            Paragraph("<b>Database Backends:</b> Neon PostgreSQL (Cloud) + SQLite (Local)", body_style),
            Paragraph("<b>Alerting:</b> Automated Telegram Bot Service", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # ── 1. EXECUTIVE SUMMARY & ARCHITECTURE ─────────────────────────────────────
    story.append(Paragraph("1. System Purpose & Core Capabilities", h1_style))
    story.append(Paragraph(
        "This platform is engineered for <b>continuous 24/7 market recording</b> of high-frequency "
        "candlestick and tick movements across all currency pairs, with specialized support for "
        "<b>Over-The-Counter (OTC)</b> weekend markets. The data is rigorously processed for machine "
        "learning pipelines, algorithmic backtesting, and automated strategy training.",
        body_style
    ))

    # Key Pillars Table
    pillars = [
        [
            Paragraph("<b>24/7 Zero-Loss Streaming</b>", table_header_style),
            Paragraph("<b>Automated Gap Recovery</b>", table_header_style),
            Paragraph("<b>Strict ML Integrity</b>", table_header_style),
        ],
        [
            Paragraph("Non-blocking asynchronous WebSocket collector with heartbeat ping keep-alive and exponential reconnect.", table_cell_style),
            Paragraph("Self-heals after network stoppage by calculating missing time offset and backfilling historical bars in &lt;500ms.", table_cell_style),
            Paragraph("Strictly commits only finalized closed candles, eliminating lookahead bias and fixing wick anomalies automatically.", table_cell_style),
        ],
    ]
    p_table = Table(pillars, colWidths=[180, 180, 180])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BACKGROUND', (0,1), (-1,1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 12))

    # ── 2. DASHBOARD USER INTERFACE GUIDE ───────────────────────────────────────
    story.append(Paragraph("2. Web Dashboard Operational Guide", h1_style))
    story.append(Paragraph(
        "The web dashboard (accessible at <code>http://localhost:8000</code>) provides non-technical "
        "operators with full visual control over data harvesting, storage health, and streaming diagnostics.",
        body_style
    ))

    ui_elements = [
        [Paragraph("<b>Component</b>", table_header_style), Paragraph("<b>Function & How to Use</b>", table_header_style)],
        [
            Paragraph("<b>Master Controls</b>", table_cell_style),
            Paragraph("• <b>Start:</b> Boots the engine, connects to WebSocket, and begins recording.<br/>"
                      "• <b>Pause / Resume:</b> Temporarily suspends recording without terminating socket.<br/>"
                      "• <b>Stop:</b> Closes connection cleanly and flushes final bars to database.", table_cell_style),
        ],
        [
            Paragraph("<b>Live Telemetry HUD</b>", table_cell_style),
            Paragraph("• <b>Status Badge:</b> Real-time operational state (<code>RUNNING</code>, <code>PAUSED</code>, <code>RECONNECTING</code>).<br/>"
                      "• <b>Candles Total:</b> Cumulative closed candles stored in the database.<br/>"
                      "• <b>Ingestion Rate:</b> Rolling candles processed per minute (speed gauge).<br/>"
                      "• <b>WebSocket Latency:</b> Ping round-trip time in milliseconds (e.g., <code>25ms</code>).<br/>"
                      "• <b>Database Target:</b> Active storage backend (Neon PostgreSQL or SQLite).", table_cell_style),
        ],
        [
            Paragraph("<b>Instrument & Period Selector</b>", table_cell_style),
            Paragraph("Allows dynamic multi-asset configuration (e.g., <code>EURUSD_otc, USDARS_otc, GBPUSD_otc</code>) "
                      "and timeframe periods (<code>60s</code> for 1-minute, <code>300s</code> for 5-minute). "
                      "Changes take effect immediately without requiring a system restart.", table_cell_style),
        ],
        [
            Paragraph("<b>Live Terminal / Log Stream</b>", table_cell_style),
            Paragraph("Streams raw WebSocket frames, heartbeat confirmations (<code>42[\"ps\"]</code>), "
                      "and backfill events directly to a scrolling dark-mode console window.", table_cell_style),
        ],
        [
            Paragraph("<b>Recent Candlesticks Table</b>", table_cell_style),
            Paragraph("Displays the latest verified closed candles with microsecond timestamps, "
                      "Open, High, Low, Close (OHLC), and tick Volume for instant audit.", table_cell_style),
        ],
    ]
    ui_table = Table(ui_elements, colWidths=[150, 390])
    ui_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(ui_table)
    story.append(Spacer(1, 12))

    # ── 3. AUTOMATED GAP RECOVERY & DATA INTEGRITY ──────────────────────────────
    story.append(Paragraph("3. Self-Healing & Gap Recovery Architecture", h1_style))
    story.append(Paragraph(
        "When an outage occurs (e.g. WiFi interruption, platform maintenance, or machine reboot), "
        "the engine executes an automatic 3-stage self-correction sequence:",
        body_style
    ))

    # Recovery steps callout box
    recovery_text = (
        "<b>Stage 1: Outage Detection</b> — Upon reconnecting, the engine queries the active database: "
        "<code>SELECT MAX(timestamp) FROM candles WHERE symbol = :sym AND timeframe = :tf</code>.<br/>"
        "<b>Stage 2: Delta Calculation</b> — It calculates <code>gap_seconds = current_time - last_saved_time</code>. "
        "If the gap exceeds 60s, it automatically requests missing bars using <code>loadHistoryPeriod</code>.<br/>"
        "<b>Stage 3: Idempotent Insertion</b> — All missing bars (up to 1,440 per 24h block) are received in pre-calculated "
        "binary packages and inserted with <code>ON CONFLICT DO NOTHING</code>, guaranteeing zero duplicate records."
    )
    rec_table = Table([[Paragraph(recovery_text, callout_style)]], colWidths=[540])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_accent_light),
        ('BOX', (0,0), (-1,-1), 1, c_accent),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 14))

    story.append(PageBreak())

    # ── 4. TELEGRAM INTEGRATION ────────────────────────────────────────────────
    story.append(Paragraph("4. Telegram Notification System", h1_style))
    story.append(Paragraph(
        "The harvester connects directly to a dedicated Telegram bot to notify the trading team of all "
        "critical lifecycle events in real-time:",
        body_style
    ))

    tg_data = [
        [Paragraph("<b>Event</b>", table_header_style), Paragraph("<b>Trigger</b>", table_header_style), Paragraph("<b>Alert Sample</b>", table_header_style)],
        [
            Paragraph("🚀 <b>Harvester Started</b>", table_cell_style),
            Paragraph("Engine booted via Web Dashboard or auto-restart.", table_cell_style),
            Paragraph("<code>🚀 Pocket Option Harvester STARTED<br/>• DB: PostgreSQL<br/>• Symbols: 4<br/>• Timeframe: 60s</code>", table_cell_style),
        ],
        [
            Paragraph("⚠️ <b>Reconnection Attempt</b>", table_cell_style),
            Paragraph("Network disconnected; exponential backoff active.", table_cell_style),
            Paragraph("<code>⚠️ Harvester Disconnected<br/>Attempting reconnect #1 in 2.0s...</code>", table_cell_style),
        ],
        [
            Paragraph("✅ <b>Gap Recovered</b>", table_cell_style),
            Paragraph("History backfilled after outage.", table_cell_style),
            Paragraph("<code>✅ Reconnected & Recovered<br/>• EURUSD_otc: 120 bars patched</code>", table_cell_style),
        ],
        [
            Paragraph("🚨 <b>Session Alert</b>", table_cell_style),
            Paragraph("Platform auth rejected (token expired).", table_cell_style),
            Paragraph("<code>🚨 Session Expired (41 Unauthorized)<br/>Please refresh token in Dashboard.</code>", table_cell_style),
        ],
    ]
    tg_table = Table(tg_data, colWidths=[120, 180, 240])
    tg_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tg_table)
    story.append(Spacer(1, 14))

    # ── 5. PROPOSED VALUE-ADD ROADMAP FEATURES ──────────────────────────────────
    story.append(Paragraph("5. Value-Add Roadmap: Suggested Future Features", h1_style))
    story.append(Paragraph(
        "To maximize the commercial and operational impact of the harvester for the client's algorithmic trading, "
        "the following non-intrusive enhancements are recommended for immediate presentation:",
        body_style
    ))

    roadmap_items = [
        [
            Paragraph("<b>1. Live Lightweight Candlestick Chart in Dashboard</b>", h2_style),
        ],
        [
            Paragraph("Embed a TradingView-style interactive HTML5 candlestick canvas directly inside the web dashboard. "
                      "Operators can visually follow candles forming in real-time, inspect OHLC levels, and verify "
                      "data parity against the Pocket Option trading terminal with zero performance overhead.", body_style),
        ],
        [
            Paragraph("<b>2. One-Click AI/ML Dataset Export (CSV / Parquet / JSON)</b>", h2_style),
        ],
        [
            Paragraph("Add an export drawer allowing users to filter by date range, select specific assets, "
                      "and download pre-cleaned data files formatted specifically for Python Pandas, PyTorch, "
                      "TensorFlow, and Backtrader backtesting scripts.", body_style),
        ],
        [
            Paragraph("<b>3. Data Completeness & Quality Scorecard (99.99% Gauge)</b>", h2_style),
        ],
        [
            Paragraph("Display a visual health meter showing data completeness: total expected minutes vs. recorded bars, "
                      "average ping latency, and zero-gap verification. This provides the client with proof of data integrity.", body_style),
        ],
        [
            Paragraph("<b>4. Automated 24-Hour Midnight Telegram Digest</b>", h2_style),
        ],
        [
            Paragraph("A daily automated report card delivered to Telegram at 00:00 UTC summarizing total volume recorded, "
                      "highest volatility pair, network uptime percentage, and cloud storage growth.", body_style),
        ],
        [
            Paragraph("<b>5. Multi-Timeframe Virtual Resampler (Virtual 5m / 15m / 1h)</b>", h2_style),
        ],
        [
            Paragraph("Using the granular 1-minute closed bars, an in-memory aggregation module can generate higher timeframe "
                      "candles on demand without opening additional WebSocket streams to Pocket Option.", body_style),
        ],
    ]
    rm_table = Table(roadmap_items, colWidths=[540])
    rm_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(rm_table)
    story.append(Spacer(1, 14))

    # ── FOOTER / CONCLUSION ────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(
        "<b>Prepared by:</b> AI & Algorithmic Trading Engineering Team &nbsp;|&nbsp; "
        "<b>Platform Version:</b> v2.0 Enterprise &nbsp;|&nbsp; <b>Status:</b> Production Ready",
        ParagraphStyle("FooterNote", parent=styles["Normal"], fontSize=8, textColor=c_text_muted, alignment=1)
    ))

    doc.build(story)
    print(f"[SUCCESS] Generated PDF: {filename} ({os.path.getsize(filename)} bytes)")

if __name__ == "__main__":
    create_client_guide_pdf()
