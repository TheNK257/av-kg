import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    nuscenes_dataroot: str = os.getenv("NUSCENES_DATAROOT", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nuscenes"))
    nuscenes_version: str  = os.getenv("NUSCENES_VERSION", "v1.0-mini")
    jpeg_quality: int      = 80
    stream_fps: float      = 2.0
    camera_channel: str    = "CAM_FRONT"
    radar_channel: str     = "RADAR_FRONT"
    host: str              = "0.0.0.0"
    port: int              = 8001

    # Neo4j settings (shared with config/settings.py)
    neo4j_uri: str      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str     = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "avkgpassword")

settings = Settings()