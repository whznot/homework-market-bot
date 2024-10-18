<<<<<<< HEAD
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
=======
import pytz
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
>>>>>>> 8a44031 (migrated to a new stable folder)

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"
<<<<<<< HEAD

=======
>>>>>>> 8a44031 (migrated to a new stable folder)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    deadline = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    photo_id = Column(String, nullable=True)
<<<<<<< HEAD
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
=======
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.utc))
>>>>>>> 8a44031 (migrated to a new stable folder)
