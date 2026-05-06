from datetime import date, datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

engine = create_engine("sqlite:///data.db", echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    star_coins = Column(Integer, default=0)
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    last_active_date = Column(Date, nullable=True)
    daily_goal_minutes = Column(Integer, default=10)
    locale = Column(String, default="zh")

    sprite = relationship("SpriteState", back_populates="student", uselist=False)
    answer_records = relationship("AnswerRecord", back_populates="student")
    mastery_records = relationship("Mastery", back_populates="student")
    achievements = relationship("Achievement", back_populates="student")
    daily_stats = relationship("DailyStats", back_populates="student")
    learning_paths = relationship("LearningPath", back_populates="student")


class AnswerRecord(Base):
    __tablename__ = "answer_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    question_id = Column(String, nullable=False)
    knowledge_point_id = Column(String, nullable=False)
    student_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent_seconds = Column(Float, nullable=True)
    hint_level_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="answer_records")


class Mastery(Base):
    __tablename__ = "mastery"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    knowledge_point_id = Column(String, nullable=False)
    mastery_score = Column(Float, default=0.0)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_practiced_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("student_id", "knowledge_point_id", name="uq_student_kp"),
    )

    student = relationship("Student", back_populates="mastery_records")


class DailyStats(Base):
    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    date = Column(Date, nullable=False)
    questions_answered = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    total_time_minutes = Column(Float, default=0.0)
    xp_earned = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_student_date"),
    )

    student = relationship("Student", back_populates="daily_stats")
