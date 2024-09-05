from datetime import datetime

from src import db


class DisplayConfig(db.Model):
    __tablename__ = "display_config"
    id = db.Column(db.String, primary_key=True)
    path_config = db.Column(db.JSON, nullable=True)
    created_timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, id, path_config):
        self.id = id
        self.path_config = path_config

    def to_dict(self):
        return {
            "id": self.id,
            "path_config": self.path_config,
            "created_timestamp": self.created_timestamp,
        }
