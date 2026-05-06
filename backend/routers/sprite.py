from fastapi import APIRouter, HTTPException
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
    owned_skins: list[str] = []


class SpriteCustomizeRequest(BaseModel):
    skin: str


@router.get("/api/sprite/state", response_model=SpriteStateResponse)
async def sprite_state(student_id: int):
    sprite_info = store.get_sprite_stage_info(student_id)
    sprite = store.get_sprite(student_id)
    next_stage_map = {0: "星芽", 1: "星苗", 2: "星光", 3: "启明星", 4: "启明星"}
    owned = [s for s in (sprite.owned_skins or "").split(",") if s]
    if not owned:
        owned = ["classic_gold"]
    return SpriteStateResponse(
        stage=sprite_info["stage"],
        stage_name=sprite_info["stage_name"],
        skin=sprite.skin or "classic_gold",
        progress=sprite_info["progress"],
        next_stage_name=next_stage_map.get(sprite_info["stage"], "启明星"),
        owned_skins=owned,
    )


@router.post("/api/sprite/customize")
async def sprite_customize(student_id: int, req: SpriteCustomizeRequest):
    if req.skin not in MotivationAgent.SKINS:
        raise HTTPException(status_code=400, detail="Invalid skin")
    store.save_sprite_state(student_id, 0, req.skin)
    return {"success": True, "skin": req.skin}


@router.post("/api/sprite/buy-skin")
async def buy_skin(student_id: int, skin_key: str):
    if skin_key not in MotivationAgent.SKINS:
        raise HTTPException(status_code=400, detail="Invalid skin")
    skin_info = MotivationAgent.SKINS[skin_key]
    if skin_info["cost"] == 0:
        return {"success": True, "skin": skin_key, "message": "This skin is free"}

    student = store.get_or_create_student(student_id)
    sprite = store.get_sprite(student_id)
    owned = [s for s in (sprite.owned_skins or "").split(",") if s]
    if skin_key in owned:
        return {"success": True, "skin": skin_key, "message": "Already owned"}

    coins = student.star_coins or 0
    if coins < skin_info["cost"]:
        raise HTTPException(status_code=402, detail=f"Not enough star coins. Need {skin_info['cost']}, have {coins}")

    store.update_coins(student_id, -skin_info["cost"])
    owned.append(skin_key)
    s = store._session()
    sp = s.query(type(sprite)).filter(
        type(sprite).student_id == student_id
    ).first()
    if sp:
        sp.owned_skins = ",".join(owned)
        s.commit()
    return {"success": True, "skin": skin_key, "cost": skin_info["cost"]}


@router.post("/api/sprite/buy-streak-freeze")
async def buy_streak_freeze(student_id: int):
    student = store.get_or_create_student(student_id)
    coins = student.star_coins or 0
    cost = MotivationAgent.STREAK_FREEZE_COST
    if coins < cost:
        raise HTTPException(status_code=402, detail=f"Not enough star coins. Need {cost}, have {coins}")

    store.update_coins(student_id, -cost)
    sprite = store.get_sprite(student_id)
    s = store._session()
    sp = s.query(type(sprite)).filter(
        type(sprite).student_id == student_id
    ).first()
    if sp:
        sp.streak_freeze = (sp.streak_freeze or 0) + 1
        s.commit()
    return {"success": True, "cost": cost, "streak_freeze_count": (sp.streak_freeze or 0) if sp else 0}
