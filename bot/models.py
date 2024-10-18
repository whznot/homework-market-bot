import pytz
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    deadline = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    photo_id = Column(String, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.utc))
