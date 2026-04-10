import threading
import time
from streamer.frame_producer import FrameProducer
from streamer.graph_updater import GraphUpdater


class StreamController:
    def __init__(self, scene_index=0, hz=2, loop=True):
        self.hz = hz
        self.producer = FrameProducer(scene_index=scene_index, hz=hz)
        self.updater = GraphUpdater()

        self.frames = []          # all produced frames stored here
        self.current_index = -1
        self.paused = False
        self._step_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = None
        self.loop = loop

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        print(f"StreamController started — {self.producer.scene_name} at {self.hz} Hz")
        for frame in self.producer.stream(loop=self.loop):
            # store frame
            with self._lock:
                self.frames.append(frame)

            # wait if paused
            while self.paused:
                self._step_event.wait(timeout=0.1)
                if self._step_event.is_set():
                    self._step_event.clear()
                    break
                continue

            if self.paused:
                # stepped once, don't advance further
                continue

            # update neo4j and advance index
            self.updater.update(frame)
            with self._lock:
                self.current_index = len(self.frames) - 1

            time.sleep(1 / self.hz)

    def pause(self):
        self.paused = True

    def play(self):
        # jump to latest frame and resume
        with self._lock:
            # replay from current_index to latest so neo4j catches up
            for i in range(self.current_index + 1, len(self.frames)):
                self.updater.update(self.frames[i])
            self.current_index = len(self.frames) - 1
        self.paused = False

    def step(self, delta):
        if not self.paused:
            return
        with self._lock:
            new_idx = self.current_index + delta
            if new_idx < 0 or new_idx >= len(self.frames):
                return
            self.current_index = new_idx
            self.updater.update(self.frames[self.current_index])

    def get_current_frame_index(self):
        with self._lock:
            return self.current_index, len(self.frames)