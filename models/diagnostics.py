"""Modelos para diagnosticos del compilador."""

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(frozen=True)
class Diagnostic:
    type: str
    message: str
    lexeme: str
    line: int
    column: int
    position: int
    suggestion: Optional[str] = None

    def to_dict(self):
        return asdict(self)
