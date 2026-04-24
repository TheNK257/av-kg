# 🚗 AV-KG — Automotive Live Knowledge Graph

> A real-time knowledge graph pipeline for autonomous vehicle (AV) data, built on nuScenes, Neo4j, FastAPI, and WebSockets.

---

## 📖 Overview

**AV-KG** ingests autonomous vehicle sensor and scene data (from the [nuScenes dataset](https://www.nuscenes.org/)) and constructs a **live, queryable knowledge graph** in [Neo4j](https://neo4j.com/). A FastAPI backend exposes REST and WebSocket endpoints so downstream applications — dashboards, planners, or analytics tools — can stream and query the graph in real time.

The project is structured around four clean concerns:

| Layer | Folder | Responsibility |
|---|---|---|
| Data Ingestion | `ingestion/` | Parse nuScenes scenes, objects, annotations |
| Graph Streaming | `streamer/` | Push live updates into Neo4j |
| API | `api/` | FastAPI REST + WebSocket endpoints |
| Configuration | `config/` | Environment variables, constants |

---

## 🏗️ Architecture

```
nuScenes Dataset
      │
      ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Ingestion  │─────▶│   Streamer   │─────▶│    Neo4j    │
│  (Parser)   │      │ (Live Graph) │      │  Knowledge  │
└─────────────┘      └──────────────┘      │   Graph     │
                                           └──────┬──────┘
                                                  │
                                           ┌──────▼──────┐
                                           │   FastAPI   │
                                           │  REST + WS  │
                                           └─────────────┘
```

- **Ingestion** reads nuScenes scene metadata, sample data, ego poses, and object annotations.
- **Streamer** translates parsed AV data into graph nodes and relationships and writes them to Neo4j in real time.
- **API** exposes the graph over HTTP (query, filter) and WebSocket (live push to clients).
- **Config** centralises environment and connection settings via `.env`.

---

## 📦 Tech Stack

| Technology | Role |
|---|---|
| [nuScenes devkit](https://github.com/nutonomy/nuscenes-devkit) | AV dataset parsing (scenes, objects, ego pose) |
| [Neo4j](https://neo4j.com/) | Graph database backend |
| [FastAPI](https://fastapi.tiangolo.com/) | Async REST & WebSocket API |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server |
| [WebSockets](https://websockets.readthedocs.io/) | Real-time streaming to clients |
| [httpx](https://www.python-httpx.org/) | Async HTTP client (inter-service calls) |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable management |
| [pytest](https://docs.pytest.org/) | Testing |
| [Docker Compose](https://docs.docker.com/compose/) | Multi-service orchestration |

---

## 📁 Project Structure

```
av-kg/
├── api/                  # FastAPI app — REST and WebSocket endpoints
├── config/               # Settings, constants, and env loading
├── ingestion/            # nuScenes dataset parser and data models
├── streamer/             # Graph streaming logic (writes to Neo4j)
├── docker-compose.yml    # Orchestrates Neo4j + API services
├── requirements.txt      # Python dependencies
├── tempTest.py           # Ad-hoc/integration test script
└── README.md
```

---

## ⚙️ Prerequisites

- **Python 3.9+**
- **Docker & Docker Compose** (for Neo4j + service orchestration)
- **nuScenes dataset** — download from [nuscenes.org](https://www.nuscenes.org/nuscenes#download) (mini split recommended for development)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/TheNK257/av-kg.git
cd av-kg
```

### 2. Set Up Environment Variables

Copy or create a `.env` file in the project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

NUSCENES_DATAROOT=/path/to/nuscenes
NUSCENES_VERSION=v1.0-mini
```

### 3. Start Services with Docker Compose

This spins up Neo4j (and any other configured services):

```bash
docker compose up -d
```

Neo4j will be available at:
- **Browser UI:** `http://localhost:7474`
- **Bolt:** `bolt://localhost:7687`

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Ingestion Pipeline

Parse nuScenes data and stream it into the knowledge graph:

```bash
python -m ingestion.main
```

### 6. Start the API Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API docs will be available at `http://localhost:8000/docs` (Swagger UI).

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/scenes` | List all ingested scenes |
| `GET` | `/scenes/{scene_id}` | Get scene graph details |
| `GET` | `/objects` | Query tracked objects/agents |
| `WebSocket` | `/ws/stream` | Subscribe to live graph updates |

> Full interactive documentation is auto-generated at `/docs` when the server is running.

---

## 📊 Knowledge Graph Schema

Nodes and relationships in the Neo4j graph follow the nuScenes scene hierarchy:

```
(Scene)-[:HAS_SAMPLE]->(Sample)
(Sample)-[:HAS_ANNOTATION]->(ObjectAnnotation)
(Sample)-[:HAS_EGO_POSE]->(EgoPose)
(ObjectAnnotation)-[:INSTANCE_OF]->(Category)
(Sample)-[:NEXT]->(Sample)
```

**Node types:**
- `Scene` — A driving scenario / log snippet
- `Sample` — A timestamped keyframe within a scene
- `EgoPose` — Ego vehicle position and orientation at a sample
- `ObjectAnnotation` — Bounding box + attributes for a detected object
- `Category` — Object class label (car, pedestrian, bicycle, etc.)

---

## 🧪 Testing

Run the test suite with:

```bash
pytest
```

For quick ad-hoc integration checks, you can also run:

```bash
python tempTest.py
```

---

## 🐳 Docker Compose Reference

The `docker-compose.yml` at minimum orchestrates:

- **Neo4j** graph database with exposed Bolt and HTTP ports
- *(Optionally)* the FastAPI service if containerised

To bring everything down:

```bash
docker compose down
```

To reset the Neo4j database volume:

```bash
docker compose down -v
```

---

## 🗺️ Roadmap

- [ ] Support full nuScenes dataset (not just mini split)
- [ ] Add Cypher query templates for common AV analytics
- [ ] Real-time dashboard frontend (React + WebSocket)
- [ ] Support additional AV datasets (Waymo Open, Argoverse)
- [ ] Graph-based trajectory prediction queries
- [ ] Authentication for API endpoints

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

Please make sure all tests pass before submitting a PR.

---

## 📄 License

This project does not currently specify a license. Please contact the repository owner for usage permissions.

---

## 🙏 Acknowledgements

- [nuScenes by Motional (nuTonomy)](https://www.nuscenes.org/) for the AV dataset and devkit
- [Neo4j](https://neo4j.com/) for the graph database
- [FastAPI](https://fastapi.tiangolo.com/) for the elegant async API framework
