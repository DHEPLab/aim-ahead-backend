from dataclasses import dataclass
from enum import Enum


@dataclass
class ErrorCode(Enum):
    code: str
    message: str

    UNKNOWN = ("AA-001", "unknown exception")
