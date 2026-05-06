from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from backend.models.student import Base
from sqlalchemy.orm import relationship


class LearningPath(Base):
    __tablename__ = "learning_path"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    path_json = Column(Text, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="learning_paths")
