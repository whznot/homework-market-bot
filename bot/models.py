from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    photo_id = Column(String, nullable=True)
