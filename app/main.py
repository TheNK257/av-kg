import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from neo4j import GraphDatabase

from app.api import scenes, samples, meta, annotations
from app.api.websocket import graph_ws_endpoint, get_current_graph
from app.websockets.stream import stream_handler
from app.config import settings

# ── Controller created lazily inside lifespan ──
controller = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global controller
    from streamer.stream_controller import StreamController
    controller = StreamController(scene_index=0, hz=2, loop=True)
    controller.start()
    print("Streamer background thread started")
    yield
    controller.updater.close()


app = FastAPI(title="AV Knowledge Graph – KDTMS", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Neo4j driver (shared) ──
driver = GraphDatabase.driver(
    settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
)

# ── REST routes ──
app.include_router(scenes.router)
app.include_router(samples.router)
app.include_router(meta.router)
app.include_router(annotations.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-health")
def db_health():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS val")
            result.single()
        return {"status": "ok", "neo4j": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/graph/current")
def get_graph():
    return get_current_graph(driver)


# ── WebSocket routes ──
@app.websocket("/ws/stream")
async def websocket_stream(ws: WebSocket):
    await stream_handler(ws)


@app.websocket("/ws/graph")
async def websocket_graph(websocket: WebSocket):
    await graph_ws_endpoint(websocket, driver, controller)


# ── Serve Knowledge Graph frontend ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(BASE_DIR, "frontend")
static_dir = os.path.join(BASE_DIR, "static")

# Mount frontend assets at /static (for graph.js, style.css)
app.mount("/static", StaticFiles(directory=frontend_dir), name="frontend-static")


@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(frontend_dir, "index.html"))


# Mount the KDTMS dashboard at /dashboard
app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="dashboard")