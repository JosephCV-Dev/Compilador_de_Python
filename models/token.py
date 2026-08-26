"""Modelo de datos para tokens."""

from dataclasses import dataclass, asdict

@dataclass
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

