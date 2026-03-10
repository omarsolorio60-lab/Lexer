import re
from typing import List
from token_types import TokenType
from token_model import Token


class LexicalAnalyzer:
    def __init__(self):
        self.token_patterns = [
            # Preprocesador
            (r'\#[^\n]*', TokenType.PREPROCESSOR),

            # Comentarios
            (r'//[^\n]*', TokenType.COMMENT),
            (r'/\*.*?\*/', TokenType.COMMENT),

            # Literales
            (r'"([^"\\]|\\.)*"', TokenType.STRING),
            (r"'([^'\\]|\\.)'", TokenType.CHAR_LITERAL),

            # Números
            (r'\d+\.\d+', TokenType.NUMBER),
            (r'\d+', TokenType.NUMBER),

            # Operadores lógicos
            (r'&&', TokenType.AND),
            (r'\|\|', TokenType.OR),

            # Comparación
            (r'==', TokenType.EQUAL),
            (r'!=', TokenType.NOT_EQUAL),
            (r'<=', TokenType.LESS_EQUAL),
            (r'>=', TokenType.GREATER_EQUAL),
            (r'<', TokenType.LESS_THAN),
            (r'>', TokenType.GREATER_THAN),

            # Asignación
            (r'=', TokenType.ASSIGN),

            # Operadores aritméticos
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'%', TokenType.MODULO),
            (r'!', TokenType.NOT),

            # Delimitadores
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r',', TokenType.COMMA),
            (r';', TokenType.SEMICOLON),

            # Palabras reservadas
            (r'\b(int|float|char|void|if|else|while|return)\b', None),

            # Identificadores
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),

            # Espacios y saltos
            (r'\n', TokenType.NEWLINE),
            (r'[ \t\r]+', TokenType.WHITESPACE),
        ]

        self.keywords = {
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'char': TokenType.CHAR,
            'void': TokenType.VOID,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'return': TokenType.RETURN,
        }

    def tokenize(self, code: str, include_whitespace: bool = False) -> List[Token]:
        tokens = []
        pos = 0
        line = 1
        column = 1

        while pos < len(code):
            matched = False

            for pattern, token_type in self.token_patterns:
                regex = re.compile(pattern, re.DOTALL)
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