from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from api.websocket import graph_ws_endpoint

app = FastAPI(title="AV Knowledge Graph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

driver = GraphDatabase.driver(
    NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
)


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
def get_current_graph():
    from api.websocket import get_current_graph as _get
    return _get(driver)


@app.websocket("/ws/graph")
async def websocket_endpoint(websocket: WebSocket):
    await graph_ws_endpoint(websocket, driver)