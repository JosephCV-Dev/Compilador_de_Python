"""Modelo de datos para tokens."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Token:
    type: str
    lexeme: str
    pattern: str
    line: int
    column: int
    start: int
    end: int

    def to_dict(self):
        return asdict(self)
