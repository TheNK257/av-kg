import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from app.config import settings
from app.core.nuscenes_loader import get_sample_tokens
from app.core.frame_encoder import encode_frame
from app.core.radar_parser import get_radar_points
from app.core.imu_parser import get_imu_data
from app.api.annotations import get_annotations

async def stream_handler(ws: WebSocket):
    await ws.accept()

    try:
        # First message from client: { "scene_token": "...", "start_index": 0 }
        init        = await ws.receive_json()
        scene_token = init.get("scene_token")
        start_index = int(init.get("start_index", 0))

        tokens = get_sample_tokens(scene_token)
        if not tokens:
            await ws.close(code=1003, reason="No samples found for scene")
            return

        start_index = max(0, min(start_index, len(tokens) - 1))
        interval    = 1.0 / settings.stream_fps

        for idx in range(start_index, len(tokens)):
            sample_token = tokens[idx]

            # 1. Send camera frame as binary
            frame = encode_frame(sample_token)
            await ws.send_bytes(frame)

            # 2. Send radar + IMU + annotations as JSON
            meta = {
                "index":        idx,
                "total":        len(tokens),
                "sample_token": sample_token,
                "imu":          get_imu_data(sample_token),
                "radar":        get_radar_points(sample_token),
                "annotations":  get_annotations(sample_token)["objects"],
            }
            await ws.send_text(json.dumps(meta))

            # 3. Check for control messages (pause / seek)
            try:
                msg    = await asyncio.wait_for(ws.receive_json(), timeout=interval)
                action = msg.get("action")

                if action == "pause":
                    while True:
                        ctrl = await ws.receive_json()
                        if ctrl.get("action") == "resume":
                            break
                        if ctrl.get("action") == "seek":
                            idx = int(ctrl.get("index", idx))
                            break

                elif action == "seek":
                    idx = int(msg.get("index", idx))
                    tokens_from = tokens[idx:]
                    for sample_token in tokens_from:
                        frame = encode_frame(sample_token)
                        await ws.send_bytes(frame)
                        meta = {
                            "index":        idx,
                            "total":        len(tokens),
                            "sample_token": sample_token,
                            "imu":          get_imu_data(sample_token),
                            "radar":        get_radar_points(sample_token),
                            "annotations":  get_annotations(sample_token)["objects"],
                        }
                        await ws.send_text(json.dumps(meta))
                        idx += 1
                        try:
                            msg2 = await asyncio.wait_for(ws.receive_json(), timeout=interval)
                            if msg2.get("action") in ("pause", "seek"):
                                break
                        except asyncio.TimeoutError:
                            pass
                    break

            except asyncio.TimeoutError:
                pass

        await ws.send_text(json.dumps({"action": "end"}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_text(json.dumps({"error": str(e)}))
        except Exception:
            pass