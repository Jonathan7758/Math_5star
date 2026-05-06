from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.agents.motivation_agent import MotivationAgent
from backend.store import store

router = APIRouter()


class RewardStatusResponse(BaseModel):
    success: bool = True
    student_id: int
    level: int
    xp_current: int
    xp_next: int
    star_coins: int
    streak_days: int
    daily_goal_progress: float
    daily_goal_minutes: int
    sprite_stage: int
    sprite_name: str


@router.get("/api/rewards/status", response_model=RewardStatusResponse)
async def rewards_status(student_id: int):
    student = store.get_or_create_student(student_id)
    level = student.level or 1
    total_xp = student.total_xp or 0
    xp_current = total_xp % (level * MotivationAgent.XP_PER_LEVEL)
    xp_next = level * MotivationAgent.XP_PER_LEVEL

    sprite_info = store.get_sprite_stage_info(student_id)
    daily_minutes = student.daily_goal_minutes or 10

    daily_stats_records = store.get_weekly_stats(student_id)
    today = str(date.today())
    today_stat = next((r for r in daily_stats_records if r["date"] == today), None)
    today_minutes = today_stat["minutes"] if today_stat else 0
    progress = min(today_minutes / daily_minutes, 1.0) if daily_minutes > 0 else 0

    return RewardStatusResponse(
        student_id=student_id,
        level=level,
        xp_current=xp_current,
        xp_next=xp_next,
        star_coins=student.star_coins or 0,
        streak_days=student.current_streak_days or 0,
        daily_goal_progress=round(progress, 2),
        daily_goal_minutes=daily_minutes,
        sprite_stage=sprite_info["stage"],
        sprite_name=sprite_info["stage_name"],
    )


@router.post("/api/rewards/process")
async def process_reward(student_id: int, is_correct: bool, combo: int = 0, time_spent: float = 0):
    student = store.get_or_create_student(student_id)
    unlocked = store.get_unlocked_achievements(student_id)

    today_str = str(date.today())
    is_first = False
    last_active = student.last_active_date
    if not last_active or str(last_active) != today_str:
        is_first = True
        store.mark_daily_active(student_id)

    student_dict = {
        "total_xp": student.total_xp or 0,
        "level": student.level or 1,
        "current_streak_days": student.current_streak_days or 0,
        "last_active_date": str(last_active) if last_active else None,
        "daily_goal_minutes": student.daily_goal_minutes or 10,
        "today_minutes": 0,
    }

    result = MotivationAgent.process_answer(
        student_dict, is_correct, combo, time_spent,
        is_first_today=is_first,
        unlocked_achievements=unlocked,
    )

    store.update_xp(student_id, result.xp_earned)
    store.update_coins(student_id, result.star_coins_earned)
    if result.level_up:
        store.update_xp(student_id, 0, result.new_level)
    if result.streak_updated:
        store.update_streak(student_id, result.new_streak)
    if result.achievement_unlocked:
        store.unlock_achievement(student_id, result.achievement_unlocked)
        ach_info = MotivationAgent.ACHIEVEMENTS.get(result.achievement_unlocked, {})
        xp_bonus = ach_info.get("xp_bonus", 0)
        if xp_bonus:
            store.update_xp(student_id, xp_bonus)
        store.update_coins(student_id, 10)

    student2 = store.get_or_create_student(student_id)

    return {
        "success": True,
        "xp_earned": result.xp_earned,
        "total_xp": student2.total_xp or 0,
        "level": student2.level or 1,
        "level_up": result.level_up,
        "star_coins": student2.star_coins or 0,
        "streak_days": student2.current_streak_days or 0,
        "combo_milestone": result.combo_milestone,
        "achievement_unlocked": result.achievement_unlocked,
        "sprite_reaction": result.sprite_reaction,
        "daily_goal_progress": result.daily_goal_progress,
    }
