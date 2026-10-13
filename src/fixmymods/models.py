from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Diagnostic:
    rule_id: str
    title: str
    description: str
    severity: Literal["info", "warning", "error"]
    suggestions: tuple[str, ...]
    evidence: tuple[str, ...]