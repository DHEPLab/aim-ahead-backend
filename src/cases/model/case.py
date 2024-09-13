from dataclasses import dataclass
from typing import Self


@dataclass
class TreeNode:
    key: str
    values: str | list[str] | list[Self] | None
    style: dict | None = None

    def add_node(self, children):
        self.values.append(children)


@dataclass
class Case:
    personName: str
    caseNumber: str
    details: list[TreeNode]
    importantInfos: list[TreeNode]
