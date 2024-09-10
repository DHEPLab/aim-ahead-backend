import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from src import db


class Task(db.Model):
    __tablename__ = "task"
    id: str = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_email: str = db.Column(db.String)
    case_id: int = db.Column(db.Integer)
    path_config = db.Column(db.JSON, nullable=True)
    completed: bool = db.Column(db.Boolean, default=False)
    review_started_timestamp: datetime = db.Column(db.DateTime, nullable=True)

    created_timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    modified_timestamp: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint("user_email", "case_id", name="uq_user_email_case_id"),
    )
