from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base
from datetime import datetime, timezone


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    title = Column(
        Text,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    is_important = Column(
        Boolean,
        nullable=False,
        default=False
    )

    is_urgent = Column(
        Boolean,
        nullable=False,
        default=False
    )

    quadrant = Column(
        String(2),
        nullable=False
    )

    completed = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # Новый столбец: плановый дедлайн
    deadline_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    @property
    def days_left(self) -> int | None:
        """
        Сколько дней осталось до дедлайна от сегодняшней даты (UTC).
        """
        if not self.deadline_at:
            return None

        today = datetime.now(timezone.utc).date()
        deadline_date = self.deadline_at.astimezone(timezone.utc).date()
        return (deadline_date - today).days

    def __repr__(self) -> str:
        return (
            f"<Task(id={self.id}, title='{self.title}', "
            f"quadrant='{self.quadrant}', is_urgent={self.is_urgent}, "
            f"deadline_at='{self.deadline_at}')>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_important": self.is_important,
            "is_urgent": self.is_urgent,
            "quadrant": self.quadrant,
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "deadline_at": self.deadline_at,
            "days_left": self.days_left,
        }
