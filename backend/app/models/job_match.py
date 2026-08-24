import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id"),
        nullable=False,
    )

    job_title = Column(
        String(255),
        nullable=True,
    )

    company = Column(
        String(255),
        nullable=True,
    )

    job_description = Column(
        Text,
        nullable=False,
    )

    match_score = Column(
        Integer,
        nullable=True,
    )

    analysis = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )