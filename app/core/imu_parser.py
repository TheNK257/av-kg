import math
from app.core.nuscenes_loader import get_nusc, get_sample_data
from app.config import settings

def get_imu_data(sample_token: str) -> dict:
    nusc   = get_nusc()
    sample = nusc.get("sample", sample_token)

    # Get ego pose via the camera sample_data record
    sd_token = sample["data"][settings.camera_channel]
    sd       = get_sample_data(sd_token)
    ego      = nusc.get("ego_pose", sd["ego_pose_token"])

    tx, ty, tz = ego["translation"]

    # Derive heading from quaternion (w, x, y, z)
    w, x, y, z = ego["rotation"]
    heading_rad = math.atan2(2.0 * (w * z + x * y),
                             1.0 - 2.0 * (y * y + z * z))
    heading_deg = round(math.degrees(heading_rad) % 360, 2)

    return {
        "timestamp":   sample["timestamp"],
        "translation": {
            "x": round(tx, 3),
            "y": round(ty, 3),
            "z": round(tz, 3),
        },
        "rotation":    ego["rotation"],
        "heading_deg": heading_deg,
    }