import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


def get_current_graph(driver):
    with driver.session() as session:
        result = session.run("""
            MATCH (e:EgoVehicle {id: 'ego'})-[r:IS_NEAR]->(o:Object)
            WHERE o.stale = false
            RETURN o.token     AS token,
                   o.category  AS category,
                   o.rel_x     AS rel_x,
                   o.rel_y     AS rel_y,
                   o.vel_x     AS vel_x,
                   o.vel_y     AS vel_y,
                   r.distance  AS distance,
                   r.zone      AS zone,
                   r.direction AS direction,
                   e.x         AS ego_x,
                   e.y         AS ego_y,
                   e.timestamp AS timestamp
        """)

        records = list(result)

        if not records:
            return {"nodes": [], "edges": [], "ego": {}}

        first = records[0]
        ego = {
            "x":         first["ego_x"],
            "y":         first["ego_y"],
            "timestamp": first["timestamp"],
        }

        nodes, edges = [], []
        for record in records:
            nodes.append({
                "id":       record["token"],
                "category": record["category"],
                "rel_x":    record["rel_x"],
                "rel_y":    record["rel_y"],
                "vel_x":    record["vel_x"],
                "vel_y":    record["vel_y"],
            })
            edges.append({
                "from":      "ego",
                "to":        record["token"],
                "distance":  round(record["distance"], 2),
                "zone":      record["zone"],
                "direction": record["direction"],
            })

        return {"nodes": nodes, "edges": edges, "ego": ego}


async def graph_ws_endpoint(websocket: WebSocket, driver):
    await websocket.accept()
    print("Client connected to WebSocket")

    try:
        while True:
            data = get_current_graph(driver)
            await websocket.send_json(data)
            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")