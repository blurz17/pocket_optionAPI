# Pocket Option Data Harvester — Static dashboard route
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

dashboard_router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent.parent / "web" / "static"


def mount_static(app) -> None:
    """Mount the /static directory. Call this once during app creation."""
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@dashboard_router.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main dashboard HTML page."""
    index_file = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
