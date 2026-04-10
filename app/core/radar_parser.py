import os
import numpy as np
from nuscenes.utils.data_classes import RadarPointCloud
from app.config import settings
from app.core.nuscenes_loader import get_nusc, get_sample_data

def get_radar_points(sample_token: str) -> list[dict]:
    nusc     = get_nusc()
    sample   = nusc.get("sample", sample_token)
    sd_token = sample["data"][settings.radar_channel]
    sd       = get_sample_data(sd_token)
    pcd_path = os.path.join(settings.nuscenes_dataroot, sd["filename"])

    pc = RadarPointCloud.from_file(pcd_path)
    # pc.points shape: (18, N) — rows 0,1 are x,y; rows 6,7 are vx,vy compensated
    points = []
    for i in range(pc.points.shape[1]):
        points.append({
            "x":  round(float(pc.points[0, i]), 3),
            "y":  round(float(pc.points[1, i]), 3),
            "vx": round(float(pc.points[6, i]), 3),
            "vy": round(float(pc.points[7, i]), 3),
        })
    return points