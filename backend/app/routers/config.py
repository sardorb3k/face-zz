"""
System configuration router (admin only)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import SystemConfig
from ..routers.auth import get_current_admin
from pydantic import BaseModel
import json

router = APIRouter()


class ConfigItem(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class ConfigResponse(BaseModel):
    id: int
    key: str
    value: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[ConfigResponse])
async def get_configs(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get all system configs (admin only)"""
    configs = db.query(SystemConfig).all()
    return configs


@router.get("/{key}")
async def get_config(
    key: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get specific config (admin only)"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config


@router.post("/", response_model=ConfigResponse)
async def create_config(
    config: ConfigItem,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create or update config (admin only)"""
    existing = db.query(SystemConfig).filter(SystemConfig.key == config.key).first()
    
    if existing:
        existing.value = config.value
        if config.description:
            existing.description = config.description
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_config = SystemConfig(
            key=config.key,
            value=config.value,
            description=config.description
        )
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config


@router.put("/{key}", response_model=ConfigResponse)
async def update_config(
    key: str,
    value: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update config (admin only)"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    config.value = value
    if description is not None:
        config.description = description
    
    db.commit()
    db.refresh(config)
    return config


@router.delete("/{key}")
async def delete_config(
    key: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete config (admin only)"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    db.delete(config)
    db.commit()
    return {"message": "Config deleted successfully"}


# RTSP Camera Config Helpers
@router.get("/rtsp/cameras")
async def get_rtsp_configs(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get RTSP camera configs (admin only)"""
    config = db.query(SystemConfig).filter(SystemConfig.key == "rtsp_cameras").first()
    if config:
        try:
            cameras = json.loads(config.value) if config.value else []
            return {"cameras": cameras}
        except:
            return {"cameras": []}
    return {"cameras": []}


@router.post("/rtsp/cameras")
async def set_rtsp_configs(
    cameras: List[dict],
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Set RTSP camera configs (admin only)"""
    config = db.query(SystemConfig).filter(SystemConfig.key == "rtsp_cameras").first()
    
    cameras_json = json.dumps(cameras)
    
    if config:
        config.value = cameras_json
    else:
        config = SystemConfig(
            key="rtsp_cameras",
            value=cameras_json,
            description="RTSP camera configurations"
        )
        db.add(config)
    
    db.commit()
    
    return {"message": "RTSP cameras configured", "cameras": cameras}

