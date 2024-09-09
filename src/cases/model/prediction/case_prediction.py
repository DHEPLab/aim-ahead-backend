from datetime import datetime

from src import db


class CasePrediction(db.Model):
    __tablename__ = "case_prediction"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visit_occurrence_id: int = db.Column(
        db.Integer, db.ForeignKey("visit_occurrence.visit_occurrence_id")
    )
    important_note: str = db.Column(db.Text)

    created_timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)
