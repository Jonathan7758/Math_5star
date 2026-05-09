from fastapi import APIRouter
from backend.agents.motivation_agent import MotivationAgent
from backend.config import DATA_DIR
import json
import os

router = APIRouter()


@router.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@router.get("/api/health/version")
async def app_version():
    """Return latest app version info for in-app updates."""
    version_path = os.path.join(str(DATA_DIR), "version.json")
    try:
        with open(version_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"version": "0.1.0", "version_code": 1, "apk_url": "", "release_notes": ""}


@router.get("/api/health/achievements")
async def achievements_list():
    return {
        "achievements": [
            {"key": k, **v} for k, v in MotivationAgent.ACHIEVEMENTS.items()
        ],
    }


@router.get("/api/health/skins")
async def skins_list():
    return {
        "skins": [
            {"key": k, **v} for k, v in MotivationAgent.SKINS.items()
        ],
    }
