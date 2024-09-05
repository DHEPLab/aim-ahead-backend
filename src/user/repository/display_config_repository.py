from typing import List

from src.user.model.display_config import DisplayConfig


class DisplayConfigRepository:

    def __init__(self, session):
        self.session = session

    def clean_configurations(self):
        self.session.query(DisplayConfig).delete()
        self.session.flush()

    def save_configuration(self, config: DisplayConfig) -> DisplayConfig:
        self.session.add(config)
        self.session.flush()
        return config

    def get_all_configurations(self) -> List[DisplayConfig]:
        return self.session.query(DisplayConfig).all()

    def get_configuration_by_id(self, config_id) -> DisplayConfig:
        return self.session.get(DisplayConfig, config_id)
