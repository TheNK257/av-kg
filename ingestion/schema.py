from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

CONSTRAINTS = [
    "CREATE CONSTRAINT object_token IF NOT EXISTS FOR (o:Object) REQUIRE o.token IS UNIQUE",
    "CREATE CONSTRAINT frame_token IF NOT EXISTS FOR (f:Frame) REQUIRE f.token IS UNIQUE",
    "CREATE CONSTRAINT ego_id IF NOT EXISTS FOR (e:EgoVehicle) REQUIRE e.id IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX object_category IF NOT EXISTS FOR (o:Object) ON (o.category)",
    "CREATE INDEX object_last_seen IF NOT EXISTS FOR (o:Object) ON (o.last_seen)",
]

def run_schema():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        for stmt in CONSTRAINTS:
            session.run(stmt)
            print(f"OK: {stmt[:60]}...")

        for stmt in INDEXES:
            session.run(stmt)
            print(f"OK: {stmt[:60]}...")

    driver.close()
    print("\nSchema setup complete.")

if __name__ == "__main__":
    run_schema()