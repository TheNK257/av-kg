from streamer.frame_producer import FrameProducer
from streamer.graph_updater import GraphUpdater


def run(scene_index=0, hz=2, loop=False):
    producer = FrameProducer(scene_index=scene_index, hz=hz)
    updater  = GraphUpdater()

    print(f"Live graph stream started — scene {scene_index} at {hz} Hz")
    print("Watch Neo4j Browser at http://localhost:7474\n")

    try:
        for frame in producer.stream(loop=loop):
            stats = updater.update(frame)
            print(f"Frame {stats['frame_token'][:8]}... | "
                  f"active: {stats['active']} | "
                  f"removed: {stats['removed']} | "
                  f"ts: {stats['timestamp']}")
    except KeyboardInterrupt:
        print("\nStream stopped.")
    finally:
        updater.close()


if __name__ == "__main__":
    run(scene_index=0, hz=2, loop=True)