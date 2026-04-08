import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER     = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "avkgpassword")
NUSCENES_DATAROOT = os.getenv("NUSCENES_DATAROOT", "data/nuscenes")
NUSCENES_VERSION  = os.getenv("NUSCENES_VERSION", "v1.0-mini")