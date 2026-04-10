from fastapi import APIRouter, HTTPException
from app.core.nuscenes_loader import get_sample_tokens

router = APIRouter()

@router.get("/api/samples/{scene_token}")
def list_samples(scene_token: str):
    try:
        tokens = get_sample_tokens(scene_token)
        return {
            "scene_token":   scene_token,
            "sample_count":  len(tokens),
            "sample_tokens": tokens,
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Scene '{scene_token}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))