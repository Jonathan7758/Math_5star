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

    SKINS = {
        "classic_gold": {"name": "经典金", "desc": "最初的伙伴", "cost": 0, "color": "#fbbf24"},
        "deep_blue": {"name": "深海蓝", "desc": "深邃如知识海洋", "cost": 100, "color": "#3b82f6"},
        "flame_red": {"name": "火焰红", "desc": "燃烧的学习热情", "cost": 150, "color": "#ef4444"},
        "emerald_green": {"name": "翡翠绿", "desc": "智慧的精灵之绿", "cost": 150, "color": "#10b981"},
        "rainbow": {"name": "彩虹", "desc": "七彩光芒，限量珍品", "cost": 500, "color": "#a855f7"},
        "galaxy": {"name": "银河", "desc": "星空下的数学之光", "cost": 1000, "color": "#6366f1"},
        "holiday": {"name": "节日限定", "desc": "仅在节日期间可购买", "cost": 800, "color": "#f472b6"},
    }

    COMBO_MILESTONES = {
        3: "3连击！干得漂亮！",
        5: "5连击！势不可挡！",
        10: "10连击！你是数学大师！",
    }

    ACHIEVEMENTS = {
        "first_correct": {"key": "first_correct", "name": "初试锋芒", "desc": "答对第一道题", "xp_bonus": 20, "category": "milestone", "icon": "⭐"},
        "perfect_5": {"key": "perfect_5", "name": "五连胜", "desc": "连续答对5题", "xp_bonus": 25, "category": "combo", "icon": "🔥"},
        "perfect_10": {"key": "perfect_10", "name": "十全十美", "desc": "连续答对10题", "xp_bonus": 50, "category": "combo", "icon": "💎"},
        "perfect_20": {"key": "perfect_20", "name": "二十不惑", "desc": "连续答对20题", "xp_bonus": 100, "category": "combo", "icon": "👑"},
        "streak_3_days": {"key": "streak_3_days", "name": "三天打鱼", "desc": "连续学习3天", "xp_bonus": 30, "category": "streak", "icon": "🔥"},
        "streak_7_days": {"key": "streak_7_days", "name": "七日之约", "desc": "连续学习7天", "xp_bonus": 80, "category": "streak", "icon": "🏆"},
        "streak_14_days": {"key": "streak_14_days", "name": "半月坚持", "desc": "连续学习14天", "xp_bonus": 120, "category": "streak", "icon": "🌟"},
        "streak_21_days": {"key": "streak_21_days", "name": "习惯养成", "desc": "连续学习21天", "xp_bonus": 200, "category": "streak", "icon": "🎯"},
        "streak_30_days": {"key": "streak_30_days", "name": "月月红", "desc": "连续学习30天", "xp_bonus": 300, "category": "streak", "icon": "🏅"},
        "speed_demon": {"key": "speed_demon", "name": "闪电侠", "desc": "5秒内答对", "xp_bonus": 30, "category": "speed", "icon": "⚡"},
        "speed_light": {"key": "speed_light", "name": "光速答题", "desc": "3秒内答对", "xp_bonus": 50, "category": "speed", "icon": "💨"},
        "total_10": {"key": "total_10", "name": "初出茅庐", "desc": "累计答对10题", "xp_bonus": 25, "category": "milestone", "icon": "📝"},
        "total_25": {"key": "total_25", "name": "小有成就", "desc": "累计答对25题", "xp_bonus": 40, "category": "milestone", "icon": "📊"},
        "total_50": {"key": "total_50", "name": "半百题王", "desc": "累计答对50题", "xp_bonus": 60, "category": "milestone", "icon": "📚"},
        "total_100": {"key": "total_100", "name": "百题斩", "desc": "累计答对100题", "xp_bonus": 100, "category": "milestone", "icon": "🗡️"},
        "total_200": {"key": "total_200", "name": "双百标兵", "desc": "累计答对200题", "xp_bonus": 200, "category": "milestone", "icon": "🛡️"},
        "total_500": {"key": "total_500", "name": "五百罗汉", "desc": "累计答对500题", "xp_bonus": 500, "category": "milestone", "icon": "🏰"},
        "master_5": {"key": "master_5", "name": "掌握五人", "desc": "掌握5个知识点", "xp_bonus": 40, "category": "knowledge", "icon": "🧩"},
        "master_10": {"key": "master_10", "name": "十全武功", "desc": "掌握10个知识点", "xp_bonus": 80, "category": "knowledge", "icon": "🎓"},
        "master_15": {"key": "master_15", "name": "学霸之路", "desc": "掌握15个知识点", "xp_bonus": 150, "category": "knowledge", "icon": "📖"},
        "master_20": {"key": "master_20", "name": "全能冠军", "desc": "掌握全部20个知识点", "xp_bonus": 300, "category": "knowledge", "icon": "👨‍🎓"},
        "daily_goal_met": {"key": "daily_goal_met", "name": "今日事今日毕", "desc": "每日目标达成", "xp_bonus": 40, "category": "special", "icon": "✅"},
        "level_5": {"key": "level_5", "name": "小升初", "desc": "达到等级5", "xp_bonus": 50, "category": "special", "icon": "⬆️"},
        "level_10": {"key": "level_10", "name": "中级学者", "desc": "达到等级10", "xp_bonus": 100, "category": "special", "icon": "🎖️"},
        "level_20": {"key": "level_20", "name": "高级学者", "desc": "达到等级20", "xp_bonus": 200, "category": "special", "icon": "👑"},
        "perfect_all": {"key": "perfect_all", "name": "完美一天", "desc": "一天内所有题全对", "xp_bonus": 80, "category": "special", "icon": "✨"},
        "heartbreaker": {"key": "heartbreaker", "name": "心碎时刻", "desc": "一天内用完所有3颗心", "xp_bonus": 15, "category": "special", "icon": "💔"},
        "xp_100": {"key": "xp_100", "name": "XP新秀", "desc": "累计获得100 XP", "xp_bonus": 20, "category": "special", "icon": "🆙"},
        "xp_500": {"key": "xp_500", "name": "XP达人", "desc": "累计获得500 XP", "xp_bonus": 50, "category": "special", "icon": "⭐"},
        "xp_1000": {"key": "xp_1000", "name": "XP王者", "desc": "累计获得1000 XP", "xp_bonus": 100, "category": "special", "icon": "🌟"},
    }

    COMBO_ACHIEVEMENTS = {
        5: "perfect_5",
        10: "perfect_10",
        20: "perfect_20",
    }

    STREAK_ACHIEVEMENTS = {
        3: "streak_3_days",
        7: "streak_7_days",
        14: "streak_14_days",
        21: "streak_21_days",
        30: "streak_30_days",
    }

    TOTAL_ACHIEVEMENTS = {
        10: "total_10",
        25: "total_25",
        50: "total_50",
        100: "total_100",
        200: "total_200",
        500: "total_500",
    }

    MASTERY_ACHIEVEMENTS = {
        5: "master_5",
        10: "master_10",
        15: "master_15",
        20: "master_20",
    }

    XP_ACHIEVEMENTS = {
        100: "xp_100",
        500: "xp_500",
        1000: "xp_1000",
    }

    LEVEL_ACHIEVEMENTS = {
        5: "level_5",
        10: "level_10",
        20: "level_20",
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
        total_correct: int = 0,
        mastered_count: int = 0,
        daily_goal_met: bool = False,
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
        elif is_correct and current_session_combo in cls.COMBO_ACHIEVEMENTS:
            ach_key = cls.COMBO_ACHIEVEMENTS[current_session_combo]
            if ach_key not in unlocked:
                achievement = ach_key
        elif streak_updated and streak in cls.STREAK_ACHIEVEMENTS:
            ach_key = cls.STREAK_ACHIEVEMENTS[streak]
            if ach_key not in unlocked:
                achievement = ach_key

        if not achievement and is_correct and time_spent > 0 and time_spent < 5:
            if "speed_demon" not in unlocked:
                achievement = "speed_demon"
        if not achievement and is_correct and time_spent > 0 and time_spent < 3:
            if "speed_light" not in unlocked:
                achievement = "speed_light"

        if not achievement and is_correct:
            for threshold, ach_key in sorted(cls.TOTAL_ACHIEVEMENTS.items()):
                if total_correct >= threshold and ach_key not in unlocked:
                    achievement = ach_key

        if not achievement and mastered_count > 0:
            for threshold, ach_key in sorted(cls.MASTERY_ACHIEVEMENTS.items()):
                if mastered_count >= threshold and ach_key not in unlocked:
                    achievement = ach_key

        if not achievement and total_xp >= 100:
            for threshold, ach_key in sorted(cls.XP_ACHIEVEMENTS.items()):
                if total_xp >= threshold and ach_key not in unlocked:
                    achievement = ach_key

        if not achievement and level_up:
            new_lvl = level
            for threshold, ach_key in sorted(cls.LEVEL_ACHIEVEMENTS.items()):
                if new_lvl >= threshold and ach_key not in unlocked:
                    achievement = ach_key

        if not achievement and is_correct and daily_goal_met:
            if "daily_goal_met" not in unlocked:
                achievement = "daily_goal_met"

        sprite_reaction = "idle"
        if achievement:
            sprite_reaction = "celebrate"
        elif is_correct and current_session_combo >= 5:
            sprite_reaction = "excited"
        elif is_correct:
            sprite_reaction = "happy"
        elif not is_correct and current_session_combo == 0:
            sprite_reaction = "thinking"
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
