from enum import Enum


class TokenType(Enum):
    # Identificadores y literales
    IDENTIFIER = "IDENTIFICADOR"
    NUMBER = "NUMERO"
    STRING = "CADENA"
    CHAR_LITERAL = "CARACTER"

    # Tipos
    INT = "INT"
    FLOAT = "FLOAT"
    CHAR = "CHAR"
    VOID = "VOID"

    # Palabras reservadas
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    RETURN = "RETURN"

    # Operadores aritméticos
    PLUS = "SUMA"
    MINUS = "RESTA"
    MULTIPLY = "MULTIPLICACION"
    DIVIDE = "DIVISION"
    MODULO = "MODULO"

    # Asignación
    ASSIGN = "ASIGNACION"

    # Comparación
    EQUAL = "IGUAL"
    NOT_EQUAL = "NO_IGUAL"
    LESS_THAN = "MENOR_QUE"
    GREATER_THAN = "MAYOR_QUE"
    LESS_EQUAL = "MENOR_IGUAL"
    GREATER_EQUAL = "MAYOR_IGUAL"

    # Lógicos
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    # Delimitadores
    LPAREN = "PARENTESIS_IZQ"
    RPAREN = "PARENTESIS_DER"
    LBRACE = "LLAVE_IZQ"
    RBRACE = "LLAVE_DER"
    COMMA = "COMA"
    SEMICOLON = "PUNTO_Y_COMA"

    # Otros
    COMMENT = "COMENTARIO"
    PREPROCESSOR = "PREPROCESADOR"
    WHITESPACE = "ESPACIO"
    NEWLINE = "NUEVA_LINEA"
    UNKNOWN = "DESCONOCIDO"
    EOF = "EOF"