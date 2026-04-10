from fastapi import APIRouter, HTTPException
from app.core.radar_parser import get_radar_points
from app.core.imu_parser import get_imu_data

router = APIRouter()

@router.get("/api/meta/{sample_token}")
def get_meta(sample_token: str):
    try:
        return {
            "sample_token": sample_token,
            "imu":          get_imu_data(sample_token),
            "radar":        get_radar_points(sample_token),
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_token}' not found")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))