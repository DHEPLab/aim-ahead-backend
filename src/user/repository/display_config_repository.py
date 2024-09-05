import json
import uuid
from typing import List

from src.user.model.display_config import DisplayConfig


class DisplayConfigRepository:

    def __init__(self, session):
        self.session = session

    def clean_configurations(self):
        self.session.query(DisplayConfig).delete()
        self.session.flush()

    def __generate_uuid(self, config: DisplayConfig):
        unique_string = (
            f"{config.user_email}-{config.case_id}-{json.dumps(config.path_config)}"
        )
        return uuid.uuid5(uuid.NAMESPACE_URL, unique_string).hex

    def save_configuration(self, config: DisplayConfig) -> DisplayConfig:
        config.id = self.__generate_uuid(config)
        self.session.add(config)
        self.session.flush()
        return config

    def get_all_configurations(self) -> List[DisplayConfig]:
        return self.session.query(DisplayConfig).all()
