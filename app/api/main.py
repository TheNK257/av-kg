# ─────────────────────────────────────────────────────────────
# LEGACY STANDALONE APP — Now integrated into app/main.py
# This file is kept for reference only.
# To run the unified app, use:  python run.py
# ─────────────────────────────────────────────────────────────

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from app.api.websocket import graph_ws_endpoint, get_current_graph
from streamer.stream_controller import StreamController

controller = StreamController(scene_index=0, hz=2, loop=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    controller.start()
    print("Streamer background thread started")
    yield
    controller.updater.close()


app = FastAPI(title="AV Knowledge Graph API (Legacy)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

driver = GraphDatabase.driver(
    NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
)


@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(frontend_dir, "index.html"))


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


@app.websocket("/ws/graph")
async def websocket_endpoint(websocket: WebSocket):
    await graph_ws_endpoint(websocket, driver, controller)