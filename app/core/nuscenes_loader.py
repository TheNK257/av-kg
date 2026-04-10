import os
import re
from functools import lru_cache
from nuscenes.nuscenes import NuScenes
from app.config import settings

DUMMY_PNG = bytes([
    0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,
    0x00,0x00,0x00,0x0D,0x49,0x48,0x44,0x52,
    0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,
    0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,
    0xDE,0x00,0x00,0x00,0x0C,0x49,0x44,0x41,
    0x54,0x08,0xD7,0x63,0xF8,0xCF,0xC0,0x00,
    0x00,0x00,0x02,0x00,0x01,0xE2,0x21,0xBC,
    0x33,0x00,0x00,0x00,0x00,0x49,0x45,0x4E,
    0x44,0xAE,0x42,0x60,0x82
])

def _ensure_map_pngs():
    maps_dir = os.path.join(settings.nuscenes_dataroot, "maps")
    os.makedirs(maps_dir, exist_ok=True)

    # Read map.json and create a dummy PNG for every map token listed
    import json
    map_json = os.path.join(settings.nuscenes_dataroot, settings.nuscenes_version, "map.json")
    if os.path.exists(map_json):
        with open(map_json, "r") as f:
            maps = json.load(f)
        for m in maps:
            filename = m.get("filename", "")
            png_path = os.path.join(settings.nuscenes_dataroot, filename)
            os.makedirs(os.path.dirname(png_path), exist_ok=True)
            if not os.path.exists(png_path):
                with open(png_path, "wb") as f:
                    f.write(DUMMY_PNG)

@lru_cache(maxsize=1)
def get_nusc() -> NuScenes:
    _ensure_map_pngs()
    return NuScenes(
        version=settings.nuscenes_version,
        dataroot=settings.nuscenes_dataroot,
        verbose=False,
    )

def get_scenes() -> list[dict]:
    nusc = get_nusc()
    return [
        {
            "token":        s["token"],
            "name":         s["name"],
            "description":  s["description"],
            "sample_count": s["nbr_samples"],
        }
        for s in nusc.scene
    ]

def get_sample_tokens(scene_token: str) -> list[str]:
    nusc  = get_nusc()
    scene = nusc.get("scene", scene_token)
    tokens = []
    token  = scene["first_sample_token"]
    while token:
        sample = nusc.get("sample", token)
        tokens.append(token)
        token  = sample["next"]
    return tokens

def get_sample(sample_token: str) -> dict:
    return get_nusc().get("sample", sample_token)

def get_sample_data(sample_data_token: str) -> dict:
    return get_nusc().get("sample_data", sample_data_token)

def get_ego_pose(ego_pose_token: str) -> dict:
    return get_nusc().get("ego_pose", ego_pose_token)