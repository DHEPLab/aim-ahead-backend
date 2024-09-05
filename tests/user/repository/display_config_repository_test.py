import pytest

from src.user.model.display_config import DisplayConfig
from src.user.repository.display_config_repository import DisplayConfigRepository


@pytest.fixture
def config_repository(session):
    repo = DisplayConfigRepository(session)
    session.query(DisplayConfig).delete()
    session.commit()
    return repo


def test_clean_configurations(config_repository):
    config_repository.save_configuration(
        DisplayConfig(id="1", path_config=[{'info': 'initial'}]))
    config_repository.save_configuration(
        DisplayConfig(id="2", path_config=[{'info': 'second'}]))
    assert len(config_repository.get_all_configurations()) == 2

    config_repository.clean_configurations()
    assert len(config_repository.get_all_configurations()) == 0


def test_save_configuration(config_repository):
    # Test saving a single configuration
    new_config = DisplayConfig(id="1", path_config=[{'info': 'details'}])
    config_repository.save_configuration(new_config)
    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 1
    assert all_configs[0].id == "1"
    assert all_configs[0].path_config == [{'info': 'details'}]


def test_save_multiple_configurations(config_repository):
    # Saving multiple configurations
    configs = [
        DisplayConfig(id="1", path_config=[{'info': 'first'}]),
        DisplayConfig(id="2", path_config=[])
    ]
    for config in configs:
        config_repository.save_configuration(config)

    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 2
    # Check details of one of the configurations
    assert any(
        config.id == "1" and config.path_config == [{'info': 'first'}] for
        config in all_configs)
