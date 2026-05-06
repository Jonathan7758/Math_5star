from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from backend.models.student import Base
from sqlalchemy.orm import relationship


class SpriteState(Base):
    __tablename__ = "sprite_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False, unique=True)
    stage = Column(Integer, default=0)
    skin = Column(String, default="classic_gold")
    accessory = Column(String, nullable=True)
    total_learning_days = Column(Integer, default=0)
    owned_skins = Column(String, nullable=True, default="classic_gold")
    streak_freeze = Column(Integer, default=0)

    student = relationship("Student", back_populates="sprite")


class Achievement(Base):
    __tablename__ = "achievement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    achievement_key = Column(String, nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "achievement_key", name="uq_student_achievement"),
    )

    student = relationship("Student", back_populates="achievements")
