from ingestion.nuscenes_loader import get_nusc, iter_scene
from ingestion.neo4j_writer import Neo4jWriter


def ingest_scene(scene_index=0):
    print(f"Loading nuScenes...")
    nusc = get_nusc()

    print(f"Ingesting scene {scene_index}: "
          f"{nusc.scene[scene_index]['name']}\n")

    writer = Neo4jWriter()

    try:
        frames = list(iter_scene(nusc, scene_index))
        print(f"Total frames to ingest: {len(frames)}\n")
        writer.write_scene(frames)
    finally:
        writer.close()

    print(f"\nDone. Scene {scene_index} ingested.")


if __name__ == "__main__":
    ingest_scene(scene_index=0)