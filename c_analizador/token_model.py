from dataclasses import dataclass
from token_types import TokenType


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __str__(self):
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"