"""RIPARIA -- a coordinator screen for low-barrier citizen stream reporting.

OneAquaHealth IEEE Global Hackathon 2026, Track 3 (AI-Supported Assessment).
Design decisions and their reasoning are in ../AUDIT.md.

This file is a composition root and nothing else: it builds the app, wires the
routers, and mounts static files. All behaviour lives in the layers below.

    domain/     what an observation means. Pure; no I/O, no framework.
    adapters/   everything touching the outside world: persistence, model providers.
    api/        HTTP shape only. No domain knowledge.

The contract the whole system keeps (AUDIT.md D-012):
  - Nothing is auto-accepted and nothing is auto-rejected.
  - The citizen's original answers are immutable and always shown.
  - Nothing is called "validated" until a named reviewer says so.
  - A model outage degrades the service; it never drops an observation.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from adapters import store
from api import observations, protocol, review, sites
from api.shared import UPLOADS

app = FastAPI(
    title="RIPARIA",
    description=(
        "A coordinator screen for citizen stream reports. Describes observations "
        "across four separate dimensions and raises field questions for the person "
        "who filed them. It does not score, validate, accept or reject anything -- "
        "only a named reviewer does that."
    ),
    version="0.4.0",
)

# Dev-wide CORS. In production the SPA is served from this same origin, so this
# matters only when Vite runs on its own port.
# ponytail: open CORS, lock to an origin list if this is ever more than a prototype.
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.middleware("http")
async def cache_headers(request, call_next):
    """Tell browsers what may be cached. Without this they guess, and they guess badly.

    Vite fingerprints every asset (index-CESah9ib.js), so those files are immutable
    and can be cached forever. index.html must NOT be: it is the shell that names
    which fingerprinted bundle to load, so a cached shell keeps pointing at a bundle
    that no longer exists and the user sees a stale app -- or a blank one -- until
    they hard-refresh. That is a deploy-day failure and a demo-day failure, so it is
    fixed at the server rather than explained to each viewer.
    """
    resp = await call_next(request)
    path = request.url.path
    if path.startswith("/assets/"):
        resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    else:
        # index.html, and the uploads a reviewer may re-fetch
        resp.headers["Cache-Control"] = "no-cache"
    return resp


app.include_router(protocol.router)
app.include_router(observations.router)
app.include_router(review.router)
app.include_router(sites.router)
app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")


@app.on_event("startup")
def _startup() -> None:
    store.init()


@app.get("/api/health", tags=["ops"])
def health() -> dict[str, object]:
    from adapters import vision
    return {"ok": True, "service": "riparia", "vision": vision.active_provider()}


# --- static frontend -----------------------------------------------------------
# Mounted LAST so every /api route above wins. Absent in development, where Vite
# serves the frontend on its own port.
_HERE = Path(__file__).parent
DIST = next((d for d in (_HERE.parent / "frontend" / "dist", _HERE / "static")
             if d.is_dir()), _HERE / "static")

if DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str) -> FileResponse:
        """Serve the SPA, falling back to index.html for client-side routes."""
        candidate = (DIST / full_path).resolve()
        if not candidate.is_relative_to(DIST.resolve()):
            raise HTTPException(404, "not found")
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")
