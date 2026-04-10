import cv2
import os
from app.config import settings
from app.core.nuscenes_loader import get_nusc, get_sample_data

def encode_frame(sample_token: str) -> bytes:
    nusc     = get_nusc()
    sample   = nusc.get("sample", sample_token)
    sd_token = sample["data"][settings.camera_channel]
    sd       = get_sample_data(sd_token)
    img_path = os.path.join(settings.nuscenes_dataroot, sd["filename"])

    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Camera image not found: {img_path}")

    # Fix: convert BGR to RGB so colors render correctly in browser
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Resize to fit viewport while keeping aspect ratio
    img = cv2.resize(img, (1600, 900), interpolation=cv2.INTER_AREA)

    _, buf = cv2.imencode(
        ".jpg", img,
        [cv2.IMWRITE_JPEG_QUALITY, settings.jpeg_quality]
    )
    return buf.tobytes()