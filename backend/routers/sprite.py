from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.motivation_agent import MotivationAgent
from backend.store import store

router = APIRouter()


class SpriteStateResponse(BaseModel):
    success: bool = True
    stage: int
    stage_name: str
    skin: str
    progress: float
    next_stage_name: str


class SpriteCustomizeRequest(BaseModel):
    skin: str


@router.get("/api/sprite/state", response_model=SpriteStateResponse)
async def sprite_state(student_id: int):
    sprite_info = store.get_sprite_stage_info(student_id)
    sprite = store.get_sprite(student_id)
    next_stage_map = {0: "星芽", 1: "星苗", 2: "星光", 3: "启明星", 4: "启明星"}
    return SpriteStateResponse(
        stage=sprite_info["stage"],
        stage_name=sprite_info["stage_name"],
        skin=sprite.skin or "classic_gold",
        progress=sprite_info["progress"],
        next_stage_name=next_stage_map.get(sprite_info["stage"], "启明星"),
    )


@router.post("/api/sprite/customize")
async def sprite_customize(student_id: int, req: SpriteCustomizeRequest):
    store.save_sprite_state(student_id, 0, req.skin)
    return {"success": True, "skin": req.skin}
