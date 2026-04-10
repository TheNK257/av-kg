import time
from ingestion.nuscenes_loader import get_nusc, iter_scene


class FrameProducer:
    def __init__(self, scene_index=0, hz=2):
        self.scene_index = scene_index
        self.hz = hz
        self.nusc = get_nusc()
        self.scene_name = self.nusc.scene[scene_index]['name']

    def stream(self, loop=False):
        while True:
            print(f"\nStreaming scene: {self.scene_name} at {self.hz} Hz")

            for frame in iter_scene(self.nusc, self.scene_index):
                yield frame
                time.sleep(1 / self.hz)

            if not loop:
                print("Scene complete.")
                break

            print("Looping back to start...")


if __name__ == "__main__":
    producer = FrameProducer(scene_index=0, hz=2)

    for i, frame in enumerate(producer.stream()):
        print(f"Frame {i+1:02d} | "
              f"timestamp: {frame['timestamp']} | "
              f"objects: {len(frame['objects'])}")