from fastapi import APIRouter, HTTPException
from app.core.nuscenes_loader import get_scenes
from app.config import settings
import os

router = APIRouter()

@router.get("/api/debug")
def debug():
    return {
        "dataroot":        settings.nuscenes_dataroot,
        "version":         settings.nuscenes_version,
        "path_exists":     os.path.exists(settings.nuscenes_dataroot),
        "version_exists":  os.path.exists(os.path.join(settings.nuscenes_dataroot, settings.nuscenes_version)),
    }

@router.get("/api/scenes")
def list_scenes():
    try:
        return {"scenes": get_scenes()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))