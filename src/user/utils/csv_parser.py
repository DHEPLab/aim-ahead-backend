import csv
import os
from io import StringIO
from typing import List

from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.user.model.display_config import DisplayConfig

H_ID = "Config ID"
H_PATH = "Path"
H_COLLAPSE = "Collapse"
H_HIGHLIGHT = "Highlight"
H_TOP = "Top"


def is_empty(value: str):
    return value is None or value.strip() == ""


def str_to_bool(value):
    return True if value.lower() == "true" else False


def string_to_num(value: str):
    try:
        return int(value)
    except ValueError:
        return float(value)


def validate_top(row):
    path, top = row[H_PATH], row[H_TOP]

    if not is_empty(top):
        # The top config can not set on root node.
        if len(path.split(".")) < 2:
            raise BusinessException(BusinessExceptionEnum.ConfigFileIncorrect)


def build_style_dict(collapse, highlight, top) -> dict:
    style = {}
    if not is_empty(collapse):
        style["collapse"] = str_to_bool(collapse)
    if not is_empty(highlight):
        style["highlight"] = str_to_bool(highlight)
    if not is_empty(top):
        style["top"] = string_to_num(top)
    return style


class CsvConfigurationParser:
    def __init__(self, csv_stream: StringIO):
        csv_reader = csv.DictReader(csv_stream, delimiter=",")
        self.csv_data = []
        for row in csv_reader:
            self.csv_data.append(row)
        self.current_config = None

    def parse(self) -> List[DisplayConfig]:
        configurations = []
        p_id = None

        for row in self.csv_data:
            validate_top(row)

            id = row[H_ID]
            if self._should_create_new_config(p_id, id):
                p_id = id
                self.current_config = DisplayConfig(id=id, path_config=[])
                configurations.append(self.current_config)

            self._process_path_config(row)

        return configurations

    def _should_create_new_config(self, p_id, id):
        return not is_empty(id) and p_id != id

    def _process_path_config(self, row):
        path, collapse, highlight, top = (
            row[H_PATH],
            row[H_COLLAPSE],
            row[H_HIGHLIGHT],
            row[H_TOP],
        )

        if not is_empty(path):
            style = build_style_dict(collapse, highlight, top)
            if style:
                self.current_config.path_config.append({"path": path, "style": style})


def parse_csv_stream_to_configurations(csv_stream: StringIO) -> List[DisplayConfig]:
    parser = CsvConfigurationParser(csv_stream)
    return parser.parse()


def is_csv_file(filename: str | None):
    if filename is None:
        return False

    _, extension = os.path.splitext(filename)
    return extension == ".csv"
