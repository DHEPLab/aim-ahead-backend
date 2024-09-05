import csv
from io import StringIO

import pytest
from werkzeug.exceptions import InternalServerError

from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.user.repository.display_config_repository import DisplayConfigRepository
from src.user.service.configuration_service import ConfigurationService


@pytest.fixture
def mock_repo(mocker):
    return mocker.Mock(DisplayConfigRepository)


@pytest.fixture
def valid_csv_file():
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    # Headers
    writer.writerow(['Config ID', 'Path', 'Collapse', 'Highlight', 'Top'])
    # Add some dummy data
    writer.writerow(['1', 'Background.abc', 'TRUE', 'TRUE', 1])
    writer.writerow(['2', 'Background.xyz', 'FALSE', 'TRUE', None])
    stream.seek(0)  # Rewind the stream to the beginning
    return stream


@pytest.fixture
def config_data():
    return [
        {"id": 1, "path_config": [
            {"path": "Background.abc", "style": {"Collapse": True, "Highlight": True, "top": 1.0}}
        ]},
        {"id": 2, "path_config": [
            {"path": "Background.xyz", "style": {"Collapse": False, "Highlight": True}}
        ]}
    ]


def test_process_csv_file_success(mocker, mock_repo, valid_csv_file, config_data):
    # Setup the mock to return our prepared config data
    mocker.patch('src.user.utils.csv_parser.parse_csv_stream_to_configurations', return_value=config_data)
    service = ConfigurationService(repository=mock_repo)

    response = service.process_csv_file(valid_csv_file)
    # Assertions to check if the response is as expected
    assert len(response) == len(config_data)
    assert response[0]["status"] == "added"
    assert response[0]["config"] is not None
    assert response[1]["status"] == "added"
    assert response[1]["config"] is not None
    mock_repo.clean_configurations.assert_called_once()
    assert mock_repo.save_configuration.call_count == len(config_data)


def test_parser_error(mocker, mock_repo, valid_csv_file):
    mocker.patch('src.user.service.configuration_service.parse_csv_stream_to_configurations',
                 side_effect=BusinessException(BusinessExceptionEnum.InvalidCaseId))
    service = ConfigurationService(repository=mock_repo)

    with pytest.raises(BusinessException) as exc_info:
        service.process_csv_file(valid_csv_file)

    assert exc_info.value.error == BusinessExceptionEnum.InvalidCaseId


def test_database_cleaning_error(mocker, mock_repo, valid_csv_file):
    mocker.patch('src.user.utils.csv_parser.parse_csv_stream_to_configurations', return_value=[])
    mock_repo.clean_configurations.side_effect = Exception("Database cleanup failed")
    service = ConfigurationService(repository=mock_repo)

    with pytest.raises(InternalServerError):
        service.process_csv_file(valid_csv_file)


def test_database_save_error(mocker, mock_repo, valid_csv_file):
    config_data = [{"id": 1, "path_config": []}]
    mocker.patch('src.user.utils.csv_parser.parse_csv_stream_to_configurations', return_value=config_data)
    mock_repo.clean_configurations.return_value = None
    mock_repo.save_configuration.side_effect = Exception("Save failed")
    service = ConfigurationService(repository=mock_repo)

    with pytest.raises(InternalServerError):
        service.process_csv_file(valid_csv_file)

    # assert response[0]["user_case_key"] == 'usera@example.com-1'
    # assert response[0]["status"] == 'failed'
    # mock_repo.clean_configurations.assert_called_once()
