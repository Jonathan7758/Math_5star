from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class RewardResult:
    xp_earned: int
    level_up: bool
    new_level: int
    star_coins_earned: int
    streak_updated: bool
    new_streak: int
    combo_milestone: Optional[str]
    achievement_unlocked: Optional[str]
    sprite_reaction: str
    daily_goal_progress: float


class MotivationAgent:
    XP_PER_CORRECT = 10
    XP_PER_LEVEL = 100
    STAR_COINS_PER_LEVEL = 20
    STREAK_FREEZE_COST = 50

    COMBO_MILESTONES = {
        3: "3连击！干得漂亮！",
        5: "5连击！势不可挡！",
        10: "10连击！你是数学大师！",
    }

    ACHIEVEMENTS = {
        "first_correct": {"key": "first_correct", "name": "初试锋芒", "desc": "答对第一道题", "xp_bonus": 20},
        "perfect_10": {"key": "perfect_10", "name": "十全十美", "desc": "连续答对10题", "xp_bonus": 50},
        "streak_3_days": {"key": "streak_3_days", "name": "三天打鱼", "desc": "连续学习3天", "xp_bonus": 30},
        "streak_7_days": {"key": "streak_7_days", "name": "七日之约", "desc": "连续学习7天", "xp_bonus": 80},
        "speed_demon": {"key": "speed_demon", "name": "闪电侠", "desc": "5秒内答对", "xp_bonus": 30},
    }

    COMBO_ACHIEVEMENTS = {
        10: "perfect_10",
    }

    STREAK_ACHIEVEMENTS = {
        3: "streak_3_days",
        7: "streak_7_days",
    }

    @staticmethod
    def calculate_xp(is_correct: bool, current_combo: int, time_spent: float = 0) -> int:
        if not is_correct:
            return 0
        bonus = 0
        if current_combo >= 3:
            bonus = min(current_combo, 10) * 2
        if time_spent > 0 and time_spent < 5:
            bonus += 5
        return MotivationAgent.XP_PER_CORRECT + bonus

    @classmethod
    def process_answer(
        cls,
        student: dict,
        is_correct: bool,
        current_session_combo: int,
        time_spent: float = 0,
        is_first_today: bool = False,
        unlocked_achievements: set[str] | None = None,
    ) -> RewardResult:
        unlocked = unlocked_achievements or set()

        xp = cls.calculate_xp(is_correct, current_session_combo, time_spent)

        total_xp = student.get("total_xp", 0) + xp
        level = student.get("level", 1)
        level_up = False
        star_coins = 0

        while total_xp >= level * cls.XP_PER_LEVEL:
            level_up = True
            level += 1
            star_coins += cls.STAR_COINS_PER_LEVEL

        streak = student.get("current_streak_days", 0)
        streak_updated = False
        if is_first_today:
            today = date.today()
            last_active = student.get("last_active_date")
            if last_active:
                try:
                    last_date = date.fromisoformat(str(last_active))
                    if (today - last_date).days == 1:
                        streak += 1
                        streak_updated = True
                    elif (today - last_date).days > 1:
                        streak = 1
                        streak_updated = True
                except (ValueError, TypeError):
                    streak = 1
                    streak_updated = True
            else:
                streak = 1
                streak_updated = True

        combo_milestone = None
        if current_session_combo in cls.COMBO_MILESTONES:
            combo_milestone = cls.COMBO_MILESTONES[current_session_combo]

        achievement = None
        if "first_correct" not in unlocked and is_correct:
            achievement = "first_correct"
        elif current_session_combo in cls.COMBO_ACHIEVEMENTS:
            ach_key = cls.COMBO_ACHIEVEMENTS[current_session_combo]
            if ach_key not in unlocked:
                achievement = ach_key
        elif streak_updated and streak in cls.STREAK_ACHIEVEMENTS:
            ach_key = cls.STREAK_ACHIEVEMENTS[streak]
            if ach_key not in unlocked:
                achievement = ach_key

        sprite_reaction = "idle"
        if achievement:
            sprite_reaction = "celebrate"
        elif is_correct and current_session_combo >= 5:
            sprite_reaction = "excited"
        elif is_correct:
            sprite_reaction = "happy"
        elif not is_correct:
            sprite_reaction = "encourage"

        daily_goal_minutes = student.get("daily_goal_minutes", 10)
        today_minutes = student.get("today_minutes", 0) + (time_spent / 60 if time_spent > 0 else 0.5)
        daily_progress = min(today_minutes / daily_goal_minutes, 1.0)

        return RewardResult(
            xp_earned=xp,
            level_up=level_up,
            new_level=level,
            star_coins_earned=star_coins,
            streak_updated=streak_updated,
            new_streak=streak,
            combo_milestone=combo_milestone,
            achievement_unlocked=achievement,
            sprite_reaction=sprite_reaction,
            daily_goal_progress=daily_progress,
        )

    @staticmethod
    def get_sprite_stage(
        total_learning_days: int,
        streak_days: int,
        mastered_count: int,
        total_xp: int,
    ) -> dict:
        stage = 0
        progress = 0.0
        stage_name = "星尘"

        if total_learning_days >= 100 and mastered_count >= 80:
            stage = 4
            stage_name = "启明星"
            progress = 1.0
        elif total_learning_days >= 60 and mastered_count >= 30:
            stage = 3
            stage_name = "星光"
            progress = min((total_learning_days - 60) / 40, 1.0)
        elif total_learning_days >= 21 and mastered_count >= 10:
            stage = 2
            stage_name = "星苗"
            progress = min((total_learning_days - 21) / 39, 1.0)
        elif total_learning_days >= 7 and mastered_count >= 1:
            stage = 1
            stage_name = "星芽"
            progress = min((total_learning_days - 7) / 14, 1.0)
        else:
            progress = min(total_learning_days / 7, 1.0)

        return {
            "stage": stage,
            "stage_name": stage_name,
            "progress": round(progress, 3),
            "next_stage_days": 7 if stage == 0 else 21 if stage == 1 else 60 if stage == 2 else 100,
        }

    @staticmethod
    def check_daily_streak(last_active_date: Optional[str]) -> tuple[int, bool]:
        if not last_active_date:
            return 0, False
        today = date.today()
        try:
            last = date.fromisoformat(str(last_active_date))
            diff = (today - last).days
            if diff == 0:
                return 0, False
            elif diff == 1:
                return 1, True
            else:
                return 0, True
        except (ValueError, TypeError):
            return 0, False
