import json
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.student import Student, AnswerRecord, Mastery, DailyStats, SessionLocal
from backend.models.sprite import SpriteState, Achievement as AchievementModel
from backend.models.parent import LearningPath as LearningPathModel
from backend.agents.motivation_agent import MotivationAgent


class SharedStore:
    """Single source of truth for all student data.

    Writes through to SQLite and caches in memory for speed.
    All routers share this one instance.
    """

    _tables_created = False

    def __init__(self):
        self._db = SessionLocal()
        self._ensure_tables()

    def _ensure_tables(self):
        if not SharedStore._tables_created:
            from backend.models.student import Base
            Base.metadata.create_all(bind=self._db.bind)
            SharedStore._tables_created = True

    def _session(self) -> Session:
        try:
            self._db.execute(Student.__table__.select().limit(1))
        except Exception:
            self._db = SessionLocal()
            self._ensure_tables()
        return self._db

    def get_or_create_student(self, student_id: int) -> Student:
        s = self._session()
        student = s.query(Student).filter(Student.id == student_id).first()
        if student is None:
            student = Student(
                id=student_id,
                name=f"Student {student_id}",
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            s.add(student)
            s.commit()
            s.refresh(student)
        return student

    def get_sprite(self, student_id: int) -> SpriteState:
        s = self._session()
        sprite = s.query(SpriteState).filter(SpriteState.student_id == student_id).first()
        if sprite is None:
            sprite = SpriteState(student_id=student_id)
            s.add(sprite)
            s.commit()
            s.refresh(sprite)
        return sprite

    def get_streak_days(self, student_id: int) -> int:
        student = self.get_or_create_student(student_id)
        return student.current_streak_days or 0

    def update_streak(self, student_id: int, new_streak: int):
        s = self._session()
        student = s.query(Student).filter(Student.id == student_id).first()
        if student:
            student.current_streak_days = new_streak
            if new_streak > (student.longest_streak_days or 0):
                student.longest_streak_days = new_streak
            s.commit()

    def record_answer(self, student_id: int, question_id: str, kp_id: str,
                      is_correct: bool, time_spent: float = 0, hint_level: int = 0):
        s = self._session()
        record = AnswerRecord(
            student_id=student_id,
            question_id=question_id,
            knowledge_point_id=kp_id,
            student_answer="",
            is_correct=is_correct,
            time_spent_seconds=time_spent,
            hint_level_used=hint_level,
        )
        s.add(record)
        s.commit()

        mastery = s.query(Mastery).filter(
            Mastery.student_id == student_id,
            Mastery.knowledge_point_id == kp_id,
        ).first()
        if mastery is None:
            mastery = Mastery(
                student_id=student_id,
                knowledge_point_id=kp_id,
            )
            s.add(mastery)
        mastery.total_attempts = (mastery.total_attempts or 0) + 1
        if is_correct:
            mastery.correct_attempts = (mastery.correct_attempts or 0) + 1
        mastery.mastery_score = (mastery.correct_attempts or 0) / max(mastery.total_attempts, 1)
        mastery.last_practiced_at = datetime.now(timezone.utc).replace(tzinfo=None)
        s.commit()

    def update_xp(self, student_id: int, xp_earned: int, level: int = None):
        s = self._session()
        student = s.query(Student).filter(Student.id == student_id).first()
        if student:
            student.total_xp = (student.total_xp or 0) + xp_earned
            student.total_attempts = (student.total_attempts or 0) + 1
            if level is not None:
                student.level = level
            s.commit()

    def increment_correct(self, student_id: int):
        s = self._session()
        student = s.query(Student).filter(Student.id == student_id).first()
        if student:
            student.total_correct = (student.total_correct or 0) + 1
            s.commit()

    def update_coins(self, student_id: int, coins: int):
        s = self._session()
        student = s.query(Student).filter(Student.id == student_id).first()
        if student:
            student.star_coins = (student.star_coins or 0) + coins
            s.commit()

    def update_daily_stats(self, student_id: int, date_str: str, questions: int,
                           correct: int, minutes: float, xp: int):
        s = self._session()
        stat = s.query(DailyStats).filter(
            DailyStats.student_id == student_id,
            DailyStats.date == date.fromisoformat(date_str),
        ).first()
        if stat is None:
            stat = DailyStats(
                student_id=student_id,
                date=date.fromisoformat(date_str),
            )
            s.add(stat)
        stat.questions_answered = (stat.questions_answered or 0) + questions
        stat.correct_count = (stat.correct_count or 0) + correct
        stat.total_time_minutes = (stat.total_time_minutes or 0) + minutes
        stat.xp_earned = (stat.xp_earned or 0) + xp
        s.commit()

    def update_mastery(self, student_id: int, kp_id: str, is_correct: bool):
        self.record_answer(student_id, "", kp_id, is_correct, 0, 0)

    def set_learning_path(self, student_id: int, path: list[dict]):
        s = self._session()
        existing = s.query(LearningPathModel).filter(
            LearningPathModel.student_id == student_id,
            LearningPathModel.status == "pending",
        ).first()
        if existing:
            existing.path_json = json.dumps(path)
            s.commit()
        else:
            lp = LearningPathModel(
                student_id=student_id,
                path_json=json.dumps(path),
                status="pending",
            )
            s.add(lp)
            s.commit()

    def get_learning_path(self, student_id: int) -> list[dict]:
        s = self._session()
        lp = s.query(LearningPathModel).filter(
            LearningPathModel.student_id == student_id,
        ).order_by(LearningPathModel.created_at.desc()).first()
        if lp:
            try:
                return json.loads(lp.path_json)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def approve_path(self, student_id: int, adjustments: dict[str, int] = None):
        s = self._session()
        lp = s.query(LearningPathModel).filter(
            LearningPathModel.student_id == student_id,
            LearningPathModel.status == "pending",
        ).first()
        if lp is None:
            return None
        if adjustments:
            path = json.loads(lp.path_json)
            def sort_key(pn):
                return adjustments.get(pn["kp_id"], pn["order"])
            path.sort(key=sort_key)
            for i, pn in enumerate(path, 1):
                pn["order"] = i
            lp.path_json = json.dumps(path)
        lp.status = "approved"
        lp.approved_at = datetime.now(timezone.utc).replace(tzinfo=None)
        s.commit()
        return json.loads(lp.path_json)

    def get_mastery_heatmap(self, student_id: int) -> list[dict]:
        s = self._session()
        records = s.query(Mastery).filter(Mastery.student_id == student_id).all()
        result = []
        for m in records:
            result.append({
                "kp_id": m.knowledge_point_id,
                "score": round(m.mastery_score or 0.0, 2),
                "attempts": m.total_attempts or 0,
                "correct": m.correct_attempts or 0,
            })
        return result

    def get_weekly_stats(self, student_id: int) -> list[dict]:
        s = self._session()
        records = s.query(DailyStats).filter(
            DailyStats.student_id == student_id,
        ).order_by(DailyStats.date).all()
        result = []
        for r in records:
            total_q = r.questions_answered or 1
            accuracy = (r.correct_count or 0) / max(total_q, 1)
            result.append({
                "date": str(r.date),
                "minutes": round(r.total_time_minutes or 0, 1),
                "accuracy": round(accuracy, 2),
                "questions": r.questions_answered or 0,
            })
        return result

    def get_unlocked_achievements(self, student_id: int) -> set[str]:
        s = self._session()
        records = s.query(AchievementModel).filter(
            AchievementModel.student_id == student_id,
        ).all()
        return {a.achievement_key for a in records}

    def unlock_achievement(self, student_id: int, achievement_key: str):
        s = self._session()
        existing = s.query(AchievementModel).filter(
            AchievementModel.student_id == student_id,
            AchievementModel.achievement_key == achievement_key,
        ).first()
        if existing is None:
            ach = AchievementModel(
                student_id=student_id,
                achievement_key=achievement_key,
            )
            s.add(ach)
            s.commit()

    def clear_achievements(self, student_id: int):
        s = self._session()
        s.query(AchievementModel).filter(
            AchievementModel.student_id == student_id,
        ).delete()
        s.commit()

    def get_sprite_stage_info(self, student_id: int) -> dict:
        sprite = self.get_sprite(student_id)
        student = self.get_or_create_student(student_id)
        mastered = self._count_mastered(student_id)
        return MotivationAgent.get_sprite_stage(
            sprite.total_learning_days or 0,
            student.current_streak_days or 0,
            mastered,
            student.total_xp or 0,
        )

    def _count_mastered(self, student_id: int) -> int:
        s = self._session()
        records = s.query(Mastery).filter(
            Mastery.student_id == student_id,
            Mastery.mastery_score >= 0.6,
        ).all()
        return len(records)

    def add_weekly_stat(self, student_id: int, date_str: str, minutes: float,
                        accuracy: float, questions: int):
        self.update_daily_stats(student_id, date_str, questions, 0, minutes, 0)

    def get_path_status(self, student_id: int) -> str:
        s = self._session()
        lp = s.query(LearningPathModel).filter(
            LearningPathModel.student_id == student_id,
        ).order_by(LearningPathModel.created_at.desc()).first()
        return lp.status if lp else "none"

    def mark_daily_active(self, student_id: int):
        s = self._session()
        student = s.query(Student).filter(Student.id == student_id).first()
        sprite = s.query(SpriteState).filter(SpriteState.student_id == student_id).first()
        if student:
            today = date.today()
            if student.last_active_date != today:
                student.last_active_date = today
                if sprite:
                    sprite.total_learning_days = (sprite.total_learning_days or 0) + 1
            s.commit()

    def save_sprite_state(self, student_id: int, stage: int, skin: str = None):
        s = self._session()
        sprite = s.query(SpriteState).filter(SpriteState.student_id == student_id).first()
        if sprite:
            sprite.stage = stage
            if skin:
                sprite.skin = skin
            s.commit()


store = SharedStore()
