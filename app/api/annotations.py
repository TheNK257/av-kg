import math
from fastapi import APIRouter, HTTPException
from app.core.nuscenes_loader import get_nusc

router = APIRouter()

DANGER_DIST = 10.0
MEDIUM_DIST = 25.0

# Only these broad categories shown in the knowledge graph
ALLOWED_CATEGORIES = {"pedestrian", "vehicle", "barrier"}

def get_direction(tx: float, ty: float) -> str:
    angle = math.degrees(math.atan2(ty, tx))
    if -45 <= angle < 45:
        return "right"
    elif 45 <= angle < 135:
        return "ahead"
    elif angle >= 135 or angle < -135:
        return "left"
    else:
        return "behind"

def get_risk(dist: float) -> str:
    if dist <= DANGER_DIST:
        return "danger"
    elif dist <= MEDIUM_DIST:
        return "medium"
    return "safe"

def get_node_type(category: str) -> str | None:
    if "pedestrian" in category or "animal" in category:
        return "pedestrian"
    elif "vehicle" in category:
        return "vehicle"
    elif "barrier" in category:
        return "barrier"
    return None  # None = skip this object

def get_annotations(sample_token: str) -> dict:
    try:
        nusc   = get_nusc()
        sample = nusc.get("sample", sample_token)
        anns   = sample["anns"]

        objects = []
        for ann_token in anns:
            ann      = nusc.get("sample_annotation", ann_token)
            category = ann["category_name"]

            node_type = get_node_type(category)
            if node_type is None:
                continue  # skip traffic cones, debris, etc.

            label = category.split(".")[-1].upper()

            tx, ty, tz = ann["translation"]
            dist       = round(math.sqrt(tx * tx + ty * ty), 1)
            direction  = get_direction(tx, ty)
            risk       = get_risk(dist)

            vis_token = ann.get("visibility_token", "")
            vis_map   = {"1": 20, "2": 40, "3": 70, "4": 99, "": 50}
            conf      = vis_map.get(vis_token, 50)

            objects.append({
                "id":        ann_token[:8].upper(),
                "label":     label,
                "dist":      f"{dist}m",
                "dist_m":    dist,
                "conf":      conf,
                "direction": direction,
                "risk":      risk,
                "node_type": node_type,
                "tx":        round(tx, 2),
                "ty":        round(ty, 2),
            })

        # Sort by distance and keep only the 10 closest
        objects.sort(key=lambda o: o["dist_m"])
        objects = objects[:10]

        return {"sample_token": sample_token, "objects": objects}

    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/annotations/{sample_token}")
def annotations_endpoint(sample_token: str):
    return get_annotations(sample_token)