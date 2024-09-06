import csv
from io import StringIO

import pytest

from src.common.exception.BusinessException import BusinessException
from src.user.utils.csv_parser import parse_csv_stream_to_configurations, is_csv_file


def test_should_parse_csv_stream_correctly_when_all_config_are_set():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    # Headers
    writer.writerow(['Config ID', 'Path', 'Collapse', 'Highlight', 'Top'])
    # Data for multiple users and cases
    writer.writerow(['1', 'Background.abc', 'TRUE', 'True', 1])
    writer.writerow(['1', 'background.xxx', 'true', 'False', 2])
    writer.writerow(['1', 'Background.patient demo', 'FALSE', 'false', 1.5])
    stream.seek(0)

    result = parse_csv_stream_to_configurations(stream)
    result_dicts = [config.to_dict()for config in result]

    # Assert with a simple comparison
    len(result) == 1
    assert result_dicts[0]["id"] == "1"
    assert result_dicts[0]["path_config"] == [
        {'path': 'Background.abc', 'style': {'collapse': True, 'highlight': True, 'top': 1}},
        {'path': 'background.xxx', 'style': {'collapse': True, 'highlight': False, 'top': 2}},
        {'path': 'Background.patient demo', 'style': {'collapse': False, 'highlight': False, "top": 1.5}}
    ]


def test_should_ignore_none_config():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    # Headers
    writer.writerow(['Config ID', 'Path', 'Collapse', 'Highlight', 'Top'])
    # Data for multiple users and cases
    writer.writerow(['1', 'Background.abc', None, True, None])
    writer.writerow(['1', 'background.xxx', True, None, None])
    writer.writerow(['1', 'Background.patient demo', None, None, None])
    stream.seek(0)

    result = parse_csv_stream_to_configurations(stream)

    # Check if the result matches the expected configuration
    assert len(result) == 1
    assert result[0].id == "1"
    assert len(result[0].path_config) == 2

    # Assert the configuration of paths
    expected_path_0 = {
        'path': 'Background.abc',
        'style': {'highlight': True}
    }
    expected_path_1 = {
        'path': 'background.xxx',
        'style': {'collapse': True}
    }

    # Check each path configuration for correctness
    assert result[0].path_config[0] == expected_path_0
    assert result[0].path_config[1] == expected_path_1


def test_should_ignore_none_config_while_keep_user_case_relationship():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    # Headers
    writer.writerow(['Config ID', 'Path', 'Collapse', 'Highlight', 'Top'])
    # Data for multiple users and cases
    writer.writerow(['1', 'Background.patient demo', None, None, None])
    stream.seek(0)

    result = parse_csv_stream_to_configurations(stream)
    assert len(result) == 1
    assert result[0].id == "1"
    assert len(result[0].path_config) == 0


def test_should_merge_config_when_id_is_same_or_none():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    # Headers
    writer.writerow(['Config ID', 'Path', 'Collapse', 'Highlight', 'Top'])
    # Data for multiple users and cases
    writer.writerow(['1', 'Background.patient demo', None, None, None])
    writer.writerow(['1', 'Background.drug', None, None, None])
    writer.writerow(['2', 'Background.patient demo', None, True, None])
    writer.writerow(['', 'Background.patient demo', True, None, None])
    stream.seek(0)

    result = parse_csv_stream_to_configurations(stream)
    assert len(result) == 2
    assert result[0].id == "1"
    assert len(result[0].path_config) == 0

    assert result[1].id == "2"
    assert len(result[1].path_config) == 2


def test_is_csv_file():
    csvs = ['test.csv']
    not_csvs = ['test.numbers', 'test.txt', '', None]

    for x in csvs:
        assert is_csv_file(x) is True
    for x in not_csvs:
        assert is_csv_file(x) is False


def test_invalid_non_number_top_config_should_raises_exception():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(['Config ID', 'Path', 'Collapse', 'Highlight', 'Top'])
    writer.writerow(['1', 'Root', None, None, '1'])
    stream.seek(0)

    with pytest.raises(BusinessException) as excinfo:
        parse_csv_stream_to_configurations(stream)

    assert "Error while processing csv file, please check again." in str(excinfo.value.error.value)


def test_invalid_top_config_on_root_node_should_raises_exception():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(['Config ID', 'Path', 'Collapse', 'Highlight', 'Top'])
    writer.writerow(['1', 'Background', None, None, 1])
    stream.seek(0)

    with pytest.raises(BusinessException) as excinfo:
        parse_csv_stream_to_configurations(stream)

    assert "Error while processing csv file, please check again." in str(excinfo.value.error.value)


def test_config_id_not_unique_should_raises_exception():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(['Config ID', 'Path', 'Collapse', 'Highlight', 'Top'])
    writer.writerow(['1', 'Background.patient demo', None, None, None])
    writer.writerow(['2', 'Background.patient demo', None, True, None])
    writer.writerow(['1', 'Background.drug', True, None, None])
    stream.seek(0)

    with pytest.raises(BusinessException) as excinfo:
        parse_csv_stream_to_configurations(stream)

    assert "Config ID should be unique." in str(excinfo.value.error.value)
