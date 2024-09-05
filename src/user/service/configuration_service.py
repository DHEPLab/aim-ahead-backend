from io import StringIO

from werkzeug.exceptions import InternalServerError

from src.common.exception.BusinessException import BusinessException
from src.common.exception.db_transaction import db_transaction
from src.user.repository.display_config_repository import \
    DisplayConfigRepository
from src.user.utils.csv_parser import parse_csv_stream_to_configurations


class ConfigurationService:
    def __init__(self, repository: DisplayConfigRepository):
        self.repository = repository

    @db_transaction()
    def process_csv_file(self, file_stream: StringIO) -> list[dict[str, str]]:
        try:
            # Step 1: parse csv
            configurations = parse_csv_stream_to_configurations(file_stream)

            # Step 2: clean db
            self.repository.clean_configurations()

            # Step 3: Save each configuration from the parsed data
            responses = []
            for config in configurations:
                result = {}
                self.repository.save_configuration(config)
                result["config"] = config.to_dict()
                result["status"] = "added"
                responses.append(result)

            return responses
        except BusinessException as e:
            raise e
        except Exception as e:
            raise InternalServerError from e
