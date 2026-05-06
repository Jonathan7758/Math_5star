import json
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.store import store

router = APIRouter()


class PushRegisterRequest(BaseModel):
    endpoint: str
    keys: dict


@router.post("/api/push/register")
async def register_push_subscription(student_id: int, req: PushRegisterRequest):
    """Store a push notification subscription for this student."""
    from backend.models.student import PushSubscription

    s = store._session()
    existing = s.query(PushSubscription).filter(
        PushSubscription.student_id == student_id,
        PushSubscription.endpoint == req.endpoint,
    ).first()
    if existing:
        existing.is_active = True
        s.commit()
        return {"success": True, "status": "updated"}

    sub = PushSubscription(
        student_id=student_id,
        endpoint=req.endpoint,
        p256dh=req.keys.get("p256dh", ""),
        auth=req.keys.get("auth", ""),
    )
    s.add(sub)
    s.commit()
    return {"success": True, "status": "created"}


@router.post("/api/push/unregister")
async def unregister_push_subscription(student_id: int, req: PushRegisterRequest):
    """Deactivate a push notification subscription."""
    from backend.models.student import PushSubscription

    s = store._session()
    sub = s.query(PushSubscription).filter(
        PushSubscription.student_id == student_id,
        PushSubscription.endpoint == req.endpoint,
    ).first()
    if sub:
        sub.is_active = False
        s.commit()
    return {"success": True}


@router.get("/api/push/subscriptions/{student_id}")
async def get_push_subscriptions(student_id: int):
    """Get active push subscriptions for a student (for debugging)."""
    from backend.models.student import PushSubscription

    s = store._session()
    subs = s.query(PushSubscription).filter(
        PushSubscription.student_id == student_id,
        PushSubscription.is_active == True,
    ).all()
    return {
        "count": len(subs),
        "subscriptions": [{"endpoint": sub.endpoint, "created_at": str(sub.created_at)} for sub in subs],
    }
