from fastapi import APIRouter

from backend.agents.motivation_agent import MotivationAgent

router = APIRouter()


@router.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


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
