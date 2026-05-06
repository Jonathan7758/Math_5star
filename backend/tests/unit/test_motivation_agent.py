import pytest
from datetime import date, timedelta
from backend.agents.motivation_agent import MotivationAgent, RewardResult


class TestMotivationAgent:
    def test_xp_correct_answer(self):
        xp = MotivationAgent.calculate_xp(True, 0)
        assert xp == 10

    def test_xp_wrong_answer(self):
        xp = MotivationAgent.calculate_xp(False, 5)
        assert xp == 0

    def test_xp_combo_bonus_3(self):
        xp = MotivationAgent.calculate_xp(True, 3)
        assert xp > 10

    def test_xp_combo_bonus_5(self):
        xp3 = MotivationAgent.calculate_xp(True, 3)
        xp5 = MotivationAgent.calculate_xp(True, 5)
        assert xp5 > xp3

    def test_xp_speed_bonus(self):
        xp_normal = MotivationAgent.calculate_xp(True, 0, 10)
        xp_fast = MotivationAgent.calculate_xp(True, 0, 3)
        assert xp_fast > xp_normal

    def test_process_answer_level_up(self):
        student = {"total_xp": 95, "level": 1, "current_streak_days": 0, "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, True, 5, time_spent=2, is_first_today=False)
        assert result.level_up is True
        assert result.new_level == 2
        assert result.star_coins_earned >= 20

    def test_level_up_animation_trigger(self):
        student = {"total_xp": 90, "level": 1, "current_streak_days": 0, "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, True, 1, time_spent=5, is_first_today=False)
        assert result.level_up is True

    def test_first_correct_achievement(self):
        student = {"total_xp": 0, "level": 1, "current_streak_days": 0, "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, True, 1, is_first_today=False, unlocked_achievements=set())
        assert result.achievement_unlocked == "first_correct"

    def test_achievement_no_duplicate(self):
        student = {"total_xp": 0, "level": 1, "current_streak_days": 0, "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, True, 1, is_first_today=False, unlocked_achievements={"first_correct"})
        assert result.achievement_unlocked is None

    def test_streak_increment_first_today(self):
        student = {"total_xp": 0, "level": 1, "current_streak_days": 2, "last_active_date": str(date.today() - timedelta(days=1)), "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, True, 1, is_first_today=True)
        assert result.streak_updated is True
        assert result.new_streak == 3

    def test_streak_break(self):
        student = {"total_xp": 0, "level": 1, "current_streak_days": 5, "last_active_date": str(date.today() - timedelta(days=3)), "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, False, 0, is_first_today=True)
        assert result.new_streak == 1

    def test_daily_goal_progress(self):
        student = {"total_xp": 0, "level": 1, "current_streak_days": 0, "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, True, 1, time_spent=600, is_first_today=False)
        assert result.daily_goal_progress >= 0.9

    def test_combo_milestone_3(self):
        student = {"total_xp": 0, "level": 1, "current_streak_days": 0, "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, True, 3, is_first_today=False)
        assert result.combo_milestone is not None
        assert "3" in result.combo_milestone

    def test_sprite_reaction_correct(self):
        student = {"total_xp": 0, "level": 1, "current_streak_days": 0, "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, True, 1, is_first_today=False, unlocked_achievements={"first_correct"})
        assert result.sprite_reaction == "happy"

    def test_sprite_reaction_wrong(self):
        student = {"total_xp": 0, "level": 1, "current_streak_days": 0, "daily_goal_minutes": 10, "today_minutes": 0}
        result = MotivationAgent.process_answer(student, False, 0, is_first_today=False)
        assert result.sprite_reaction == "encourage"

    def test_sprite_stage_0(self):
        result = MotivationAgent.get_sprite_stage(3, 2, 0, 50)
        assert result["stage"] == 0
        assert result["stage_name"] == "星尘"

    def test_sprite_stage_1(self):
        result = MotivationAgent.get_sprite_stage(10, 5, 3, 200)
        assert result["stage"] == 1
        assert result["stage_name"] == "星芽"

    def test_sprite_evolution_progress(self):
        result = MotivationAgent.get_sprite_stage(0, 0, 0, 0)
        assert 0 <= result["progress"] <= 1
