import re
from typing import List
from token_types import TokenType
from token_model import Token


class LexicalAnalyzer:
    def __init__(self):
        raw_patterns = [
            (r'\#[^\n]*', TokenType.PREPROCESSOR),

            (r'//[^\n]*', TokenType.COMMENT),
            (r'/\*.*?\*/', TokenType.COMMENT),

            (r'"([^"\\]|\\.)*"', TokenType.STRING),
            (r"'([^'\\]|\\.)'", TokenType.CHAR_LITERAL),

            (r'\d+\.\d+', TokenType.NUMBER),
            (r'\d+', TokenType.NUMBER),

            (r'&&', TokenType.AND),
            (r'\|\|', TokenType.OR),

            (r'==', TokenType.EQUAL),
            (r'!=', TokenType.NOT_EQUAL),
            (r'<=', TokenType.LESS_EQUAL),
            (r'>=', TokenType.GREATER_EQUAL),
            (r'<', TokenType.LESS_THAN),
            (r'>', TokenType.GREATER_THAN),

            (r'=', TokenType.ASSIGN),

            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'%', TokenType.MODULO),
            (r'!', TokenType.NOT),

            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r',', TokenType.COMMA),
            (r';', TokenType.SEMICOLON),

            (r'\b(int|float|char|void|if|else|while|for|return)\b', None),

            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),

            (r'\n', TokenType.NEWLINE),
            (r'[ \t\r]+', TokenType.WHITESPACE),
        ]

        self.token_patterns = [
            (re.compile(pattern, re.DOTALL), token_type)
            for pattern, token_type in raw_patterns
        ]

        self.keywords = {
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'char': TokenType.CHAR,
            'void': TokenType.VOID,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for' : TokenType.FOR,
            'return': TokenType.RETURN,
        }

    def tokenize(self, code: str, include_whitespace: bool = False) -> List[Token]:
        tokens = []
        pos = 0
        line = 1
        column = 1

        while pos < len(code):
            matched = False

            for regex, token_type in self.token_patterns:
                match = regex.match(code, pos)

                if match:
                    value = match.group(0)
                    current_type = token_type

                    if current_type is None:
                        current_type = self.keywords.get(value, TokenType.IDENTIFIER)

                    if include_whitespace or current_type not in {
                        TokenType.WHITESPACE, TokenType.NEWLINE
                    }:
                        tokens.append(Token(current_type, value, line, column))

                    line_breaks = value.count('\n')
                    if line_breaks > 0:
                        line += line_breaks
                        column = len(value.split('\n')[-1]) + 1
                    else:
                        column += len(value)

                    pos = match.end()
                    matched = True
                    break

            if not matched:
                tokens.append(Token(TokenType.UNKNOWN, code[pos], line, column))
                if code[pos] == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                pos += 1

        tokens.append(Token(TokenType.EOF, "", line, column))
        return tokens