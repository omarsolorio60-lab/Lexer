"""
ANALIZADOR SINTÁCTICO INTEGRADO
===============================
Este módulo extiende el analizador léxico existente para realizar análisis sintáctico
y construcción de Árboles de Sintaxis Abstracta (AST).

Integra directamente con la clase LexicalAnalyzer y los TokenType ya definidos.
"""
import re
from enum import Enum
from dataclasses import dataclass
from typing import List
import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Union
from abc import ABC, abstractmethod

# =======================================================
# DEFINICIÓN DE TIPOS DE TOKENS
# =======================================================

class TokenType(Enum):
    """
    Enumeración que define los diferentes tipos de tokens
    que puede reconocer el analizador léxico.
    Incluye identificadores, literales, operadores, delimitadores,
    separadores y palabras reservadas de Python.
    """

    # Identificadores y literales
    IDENTIFIER = "IDENTIFICADOR"
    NUMBER = "NÚMERO"
    STRING = "CADENA"

    # Operadores aritméticos
    PLUS = "SUMA"
    MINUS = "RESTA"
    MULTIPLY = "MULTIPLICACIÓN"
    DIVIDE = "DIVISIÓN"
    MODULO = "MÓDULO"
    POWER = "POTENCIA"

    # Operadores de asignación
    ASSIGN = "ASIGNACIÓN"
    PLUS_ASSIGN = "SUMA_ASIGNACIÓN"
    MINUS_ASSIGN = "RESTA_ASIGNACIÓN"

    # Operadores de comparación
    EQUAL = "IGUAL"
    NOT_EQUAL = "NO_IGUAL"
    LESS_THAN = "MENOR_QUE"
    GREATER_THAN = "MAYOR_QUE"
    LESS_EQUAL = "MENOR_IGUAL"
    GREATER_EQUAL = "MAYOR_IGUAL"

    # Operadores lógicos
    AND = "Y_LÓGICO"
    OR = "O_LÓGICO"
    NOT = "NO_LÓGICO"

    # Delimitadores
    LPAREN = "PARÉNTESIS_IZQ"
    RPAREN = "PARÉNTESIS_DER"
    LBRACKET = "CORCHETE_IZQ"
    RBRACKET = "CORCHETE_DER"
    LBRACE = "LLAVE_IZQ"
    RBRACE = "LLAVE_DER"

    # Separadores
    COMMA = "COMA"
    SEMICOLON = "PUNTO_COMA"
    DOT = "PUNTO"
    COLON = "DOS_PUNTOS"

    # Palabras reservadas de Python
    IF = "SI"
    ELSE = "SINO"
    ELIF = "SINO_SI"
    WHILE = "MIENTRAS"
    FOR = "PARA"
    DEF = "FUNCIÓN"
    CLASS = "CLASE"
    RETURN = "RETORNO"
    PRINT = "IMPRIMIR"
    IMPORT = "IMPORTAR"
    FROM = "DESDE"
    AS = "COMO"
    TRY = "INTENTAR"
    EXCEPT = "EXCEPCIÓN"
    FINALLY = "FINALMENTE"
    WITH = "CON"
    PASS = "PASAR"
    BREAK = "ROMPER"
    CONTINUE = "CONTINUAR"
    TRUE = "VERDADERO"
    FALSE = "FALSO"
    NONE = "NULO"
    IN = "EN"
    IS = "ES"

    # Otros
    NEWLINE = "NUEVA_LÍNEA"
    WHITESPACE = "ESPACIO"
    COMMENT = "COMENTARIO"
    UNKNOWN = "DESCONOCIDO"


# =======================================================
# DEFINICIÓN DE LA CLASE TOKEN
# =======================================================

@dataclass
class Token:
    """
    Representa un token en el código fuente.

    Atributos:
        type (TokenType): tipo del token (ej. IDENTIFIER, NUMBER, PLUS).
        value (str): valor exacto encontrado en el código.
        line (int): número de línea donde aparece.
        column (int): número de columna donde empieza.
    """
    type: TokenType
    value: str
    line: int
    column: int

    def __str__(self):
        """Devuelve una representación legible del token."""
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"


# =======================================================
# ANALIZADOR LÉXICO
# =======================================================

class LexicalAnalyzer:
    """
    Implementa un analizador léxico básico para código Python.
    Utiliza expresiones regulares para dividir el código fuente en tokens.
    """

    def __init__(self):
        # Lista de patrones regex asociados a tipos de tokens
        # El orden importa: patrones más específicos deben ir primero
        self.token_patterns = [
            # Comentarios
            (r'#.*', TokenType.COMMENT),

            # Números (decimales antes que enteros)
            (r'\d+\.\d+', TokenType.NUMBER),
            (r'\d+', TokenType.NUMBER),

            # Cadenas
            (r'"[^"]*"', TokenType.STRING),
            (r"'[^']*'", TokenType.STRING),

            # Operadores de asignación compuesta
            (r'\+=', TokenType.PLUS_ASSIGN),
            (r'-=', TokenType.MINUS_ASSIGN),

            # Operadores de comparación
            (r'==', TokenType.EQUAL),
            (r'!=', TokenType.NOT_EQUAL),
            (r'<=', TokenType.LESS_EQUAL),
            (r'>=', TokenType.GREATER_EQUAL),
            (r'<', TokenType.LESS_THAN),
            (r'>', TokenType.GREATER_THAN),

            # Operadores aritméticos (** antes que *)
            (r'\*\*', TokenType.POWER),
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'%', TokenType.MODULO),
            (r'=', TokenType.ASSIGN),

            # Delimitadores
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\[', TokenType.LBRACKET),
            (r'\]', TokenType.RBRACKET),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),

            # Separadores
            (r',', TokenType.COMMA),
            (r';', TokenType.SEMICOLON),
            (r'\.', TokenType.DOT),
            (r':', TokenType.COLON),

            # Palabras reservadas (manejo especial con self.keywords)
            (r'\b(if|elif|else|while|for|def|class|return|print|import|from|as|try|except|finally|with|pass|break|continue|True|False|None|in|is|and|or|not)\b', None),

            # Identificadores
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),

            # Espacios y saltos de línea
            (r'\n', TokenType.NEWLINE),
            (r'[ \t]+', TokenType.WHITESPACE),
        ]

        # Diccionario de palabras reservadas → tipo de token
        self.keywords = {
            'if': TokenType.IF, 'elif': TokenType.ELIF, 'else': TokenType.ELSE,
            'while': TokenType.WHILE, 'for': TokenType.FOR, 'def': TokenType.DEF,
            'class': TokenType.CLASS, 'return': TokenType.RETURN, 'print': TokenType.PRINT,
            'import': TokenType.IMPORT, 'from': TokenType.FROM, 'as': TokenType.AS,
            'try': TokenType.TRY, 'except': TokenType.EXCEPT, 'finally': TokenType.FINALLY,
            'with': TokenType.WITH, 'pass': TokenType.PASS, 'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE, 'True': TokenType.TRUE, 'False': TokenType.FALSE,
            'None': TokenType.NONE, 'in': TokenType.IN, 'is': TokenType.IS,
            'and': TokenType.AND, 'or': TokenType.OR, 'not': TokenType.NOT,
        }

    def tokenize(self, code: str, include_whitespace: bool = False) -> List[Token]:
        """
        Convierte el código fuente en una lista de tokens.

        Args:
            code (str): código fuente.
            include_whitespace (bool): si True, incluye espacios y saltos de línea.

        Returns:
            List[Token]: lista de tokens generados.
        """
        tokens = []
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            column = 1
            pos = 0

            while pos < len(line):
                matched = False

                for pattern, token_type in self.token_patterns:
                    regex = re.compile(pattern)
                    match = regex.match(line, pos)

                    if match:
                        value = match.group(0)

                        # Si es palabra reservada, usar token especial
                        if token_type is None and value in self.keywords:
                            token_type = self.keywords[value]
                        elif token_type is None:
                            token_type = TokenType.IDENTIFIER

                        # Ignorar espacios y saltos si no se piden
                        if include_whitespace or token_type not in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                            tokens.append(Token(token_type, value, line_num, column))

                        # Avanzar el cursor
                        pos = match.end()
                        column += len(value)
                        matched = True
                        break

                if not matched:
                    # Si no coincide con ningún patrón, es un token desconocido
                    tokens.append(Token(TokenType.UNKNOWN, line[pos], line_num, column))
                    pos += 1
                    column += 1

        return tokens

    def analyze_and_classify(self, code: str) -> dict:
        """
        Clasifica los tokens generados en categorías: identificadores,
        números, cadenas, operadores, delimitadores, palabras reservadas, etc.

        Returns:
            dict: diccionario de categorías con listas de tokens.
        """
        tokens = self.tokenize(code)

        # Diccionario de clasificación
        classification = {
            'identificadores': [],
            'números': [],
            'cadenas': [],
            'operadores': [],
            'delimitadores': [],
            'palabras_reservadas': [],
            'comentarios': [],
            'otros': []
        }

        # Conjuntos de tipos por categoría
        operator_types = {TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
                         TokenType.MODULO, TokenType.POWER, TokenType.ASSIGN, TokenType.PLUS_ASSIGN,
                         TokenType.MINUS_ASSIGN, TokenType.EQUAL, TokenType.NOT_EQUAL,
                         TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_EQUAL,
                         TokenType.GREATER_EQUAL, TokenType.AND, TokenType.OR, TokenType.NOT}

        delimiter_types = {TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACKET, TokenType.RBRACKET,
                          TokenType.LBRACE, TokenType.RBRACE, TokenType.COMMA, TokenType.SEMICOLON,
                          TokenType.DOT, TokenType.COLON}

        keyword_types = set(self.keywords.values())

        # Clasificar tokens
        for token in tokens:
            if token.type == TokenType.IDENTIFIER:
                classification['identificadores'].append(token)
            elif token.type == TokenType.NUMBER:
                classification['números'].append(token)
            elif token.type == TokenType.STRING:
                classification['cadenas'].append(token)
            elif token.type in operator_types:
                classification['operadores'].append(token)
            elif token.type in delimiter_types:
                classification['delimitadores'].append(token)
            elif token.type in keyword_types:
                classification['palabras_reservadas'].append(token)
            elif token.type == TokenType.COMMENT:
                classification['comentarios'].append(token)
            else:
                classification['otros'].append(token)

        return classification, tokens

# =======================================================
# NODOS DEL ÁRBOL DE SINTAXIS ABSTRACTA (AST)
# =======================================================

class ASTNode(ABC):
    """Clase base abstracta para todos los nodos del AST."""

    @abstractmethod
    def __str__(self) -> str:
        pass

class Expression(ASTNode):
    """Clase base para todas las expresiones."""
    pass

class Statement(ASTNode):
    """Clase base para todas las sentencias."""
    pass

# --- EXPRESIONES ---

class BinaryOperation(Expression):
    """Representa una operación binaria: left operator right"""
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f"BinaryOp({self.left} {self.operator} {self.right})"

class UnaryOperation(Expression):
    """Representa una operación unaria: operator operand"""
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand

    def __str__(self) -> str:
        return f"UnaryOp({self.operator}{self.operand})"

class Literal(Expression):
    """Representa un valor literal (número, cadena, booleano)."""
    def __init__(self, value: Union[int, float, str, bool], token_type: str):
        self.value = value
        self.token_type = token_type

    def __str__(self) -> str:
        return f"Literal({self.value})"

class Identifier(Expression):
    """Representa un identificador (variable)."""
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f"Identifier({self.name})"

class FunctionCall(Expression):
    """Representa una llamada a función: func(args)"""
    def __init__(self, name: str, arguments: List[Expression]):
        self.name = name
        self.arguments = arguments

    def __str__(self) -> str:
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"FunctionCall({self.name}({args_str}))"

# --- SENTENCIAS ---

class Assignment(Statement):
    """Representa una asignación: variable = expression"""
    def __init__(self, target: str, value: Expression):
        self.target = target
        self.value = value

    def __str__(self) -> str:
        return f"Assignment({self.target} = {self.value})"

class IfStatement(Statement):
    """Representa una sentencia if-else."""
    def __init__(self, condition: Expression, then_body: List[Statement], else_body: Optional[List[Statement]] = None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body or []

    def __str__(self) -> str:
        then_str = "; ".join(str(stmt) for stmt in self.then_body)
        else_str = "; ".join(str(stmt) for stmt in self.else_body) if self.else_body else ""
        return f"If({self.condition}) then [{then_str}] else [{else_str}]"

class WhileStatement(Statement):
    """Representa un bucle while."""
    def __init__(self, condition: Expression, body: List[Statement]):
        self.condition = condition
        self.body = body

    def __str__(self) -> str:
        body_str = "; ".join(str(stmt) for stmt in self.body)
        return f"While({self.condition}) [{body_str}]"

class PrintStatement(Statement):
    """Representa una sentencia print."""
    def __init__(self, expression: Expression):
        self.expression = expression

    def __str__(self) -> str:
        return f"Print({self.expression})"

class Program(ASTNode):
    """Representa un programa completo (lista de sentencias)."""
    def __init__(self, statements: List[Statement]):
        self.statements = statements

    def __str__(self) -> str:
        stmt_strs = [str(stmt) for stmt in self.statements]
        return f"Program([\n  " + ",\n  ".join(stmt_strs) + "\n])"


# =======================================================
# ANALIZADOR SINTÁCTICO
# =======================================================

class SyntaxError(Exception):
    """Excepción personalizada para errores de sintaxis."""
    def __init__(self, message: str, token: Optional['Token'] = None):
        self.message = message
        self.token = token
        super().__init__(self.format_error())

    def format_error(self) -> str:
        if self.token:
            return f"Error de sintaxis en línea {self.token.line}, columna {self.token.column}: {self.message}"
        return f"Error de sintaxis: {self.message}"


class SyntaxAnalyzer:
    """
    Analizador sintáctico descendente recursivo.
    Funciona directamente con los tokens generados por LexicalAnalyzer.
    """

    def __init__(self, tokens: List['Token']):
        """
        Inicializa el analizador con la lista de tokens.
        Filtra comentarios y espacios automáticamente.
        """
        # Filtrar tokens irrelevantes para el parsing
        self.tokens = [
            token for token in tokens
            if token.type.value not in ['COMENTARIO', 'ESPACIO', 'NUEVA_LÍNEA']
        ]
        self.position = 0

    def current_token(self) -> Optional['Token']:
        """Devuelve el token actual sin avanzar."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def peek_token(self, offset: int = 1) -> Optional['Token']:
        """Mira hacia adelante sin avanzar."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def consume(self, expected_type: str) -> 'Token':
        """Consume un token del tipo esperado o lanza excepción."""
        token = self.current_token()
        if token is None:
            raise SyntaxError(f"Se esperaba {expected_type} pero se llegó al final del archivo")

        # Comparar con el nombre del enum
        if token.type.value != expected_type:
            raise SyntaxError(f"Se esperaba {expected_type}, se encontró {token.type.value}", token)

        self.position += 1
        return token

    def match(self, *expected_types: str) -> bool:
        """Verifica si el token actual coincide con alguno de los tipos esperados."""
        token = self.current_token()
        if token is None:
            return False
        return token.type.value in expected_types

    # =======================================================
    # GRAMÁTICA IMPLEMENTADA
    # =======================================================
    """
    programa → sentencia*
    sentencia → asignación | if_statement | while_statement | print_statement
    asignación → IDENTIFICADOR ASIGNACIÓN expresión
    if_statement → SI expresión DOS_PUNTOS sentencia (SINO DOS_PUNTOS sentencia)?
    while_statement → MIENTRAS expresión DOS_PUNTOS sentencia
    print_statement → IMPRIMIR PARÉNTESIS_IZQ expresión PARÉNTESIS_DER

    expresión → término ((SUMA | RESTA) término)*
    término → factor ((MULTIPLICACIÓN | DIVISIÓN) factor)*
    factor → PARÉNTESIS_IZQ expresión PARÉNTESIS_DER | IDENTIFICADOR función_call? | literal
    función_call → PARÉNTESIS_IZQ (expresión (COMA expresión)*)? PARÉNTESIS_DER
    literal → NÚMERO | CADENA | VERDADERO | FALSO
    """

    def parse(self) -> Program:
        """Punto de entrada principal del parser."""
        statements = []

        while self.current_token() is not None:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        return Program(statements)

    def parse_statement(self) -> Optional[Statement]:
        """Parse una sentencia individual."""
        if not self.current_token():
            return None

        # Asignación: IDENTIFICADOR = expresión
        if self.match("IDENTIFICADOR") and self.peek_token() and self.peek_token().type.value == "ASIGNACIÓN":
            return self.parse_assignment()

        # If statement
        elif self.match("SI"):
            return self.parse_if_statement()

        # While statement
        elif self.match("MIENTRAS"):
            return self.parse_while_statement()

        # Print statement
        elif self.match("IMPRIMIR"):
            return self.parse_print_statement()

        else:
            token = self.current_token()
            raise SyntaxError(f"Sentencia inesperada comenzando con {token.type.value}", token)

    def parse_assignment(self) -> Assignment:
        """Parse: IDENTIFICADOR = expresión"""
        identifier = self.consume("IDENTIFICADOR")
        self.consume("ASIGNACIÓN")
        expression = self.parse_expression()

        return Assignment(identifier.value, expression)

    def parse_if_statement(self) -> IfStatement:
        """Parse: if expresión : sentencia (else : sentencia)?"""
        self.consume("SI")
        condition = self.parse_expression()
        self.consume("DOS_PUNTOS")
        then_stmt = self.parse_statement()
        then_body = [then_stmt] if then_stmt else []

        else_body = []
        if self.match("SINO"):
            self.consume("SINO")
            self.consume("DOS_PUNTOS")
            else_stmt = self.parse_statement()
            if else_stmt:
                else_body = [else_stmt]

        return IfStatement(condition, then_body, else_body)

    def parse_while_statement(self) -> WhileStatement:
        """Parse: while expresión : sentencia"""
        self.consume("MIENTRAS")
        condition = self.parse_expression()
        self.consume("DOS_PUNTOS")
        body_stmt = self.parse_statement()
        body = [body_stmt] if body_stmt else []

        return WhileStatement(condition, body)

    def parse_print_statement(self) -> PrintStatement:
        """Parse: print(expresión)"""
        self.consume("IMPRIMIR")
        self.consume("PARÉNTESIS_IZQ")
        expression = self.parse_expression()
        self.consume("PARÉNTESIS_DER")

        return PrintStatement(expression)

    def parse_expression(self) -> Expression:
        """Parse: término ((+ | -) término)*"""
        left = self.parse_term()

        while self.match("SUMA", "RESTA"):
            operator = self.current_token().value
            self.position += 1
            right = self.parse_term()
            left = BinaryOperation(left, operator, right)

        return left

    def parse_term(self) -> Expression:
        """Parse: factor ((* | /) factor)*"""
        left = self.parse_factor()

        while self.match("MULTIPLICACIÓN", "DIVISIÓN", "MÓDULO"):
            operator = self.current_token().value
            self.position += 1
            right = self.parse_factor()
            left = BinaryOperation(left, operator, right)

        return left

    def parse_factor(self) -> Expression:
        """Parse: (expresión) | IDENTIFICADOR función_call? | literal"""

        # Expresión entre paréntesis
        if self.match("PARÉNTESIS_IZQ"):
            self.consume("PARÉNTESIS_IZQ")
            expr = self.parse_expression()
            self.consume("PARÉNTESIS_DER")
            return expr

        # Identificador (posible función)
        elif self.match("IDENTIFICADOR"):
            name = self.consume("IDENTIFICADOR").value

            # Verificar si es una llamada a función
            if self.match("PARÉNTESIS_IZQ"):
                return self.parse_function_call(name)
            else:
                return Identifier(name)

        # Literales
        elif self.match("NÚMERO"):
            token = self.consume("NÚMERO")
            # Convertir a int o float según el contenido
            try:
                value = int(token.value) if '.' not in token.value else float(token.value)
            except ValueError:
                value = token.value
            return Literal(value, "NÚMERO")

        elif self.match("CADENA"):
            token = self.consume("CADENA")
            # Remover comillas
            value = token.value[1:-1]
            return Literal(value, "CADENA")

        elif self.match("VERDADERO"):
            self.consume("VERDADERO")
            return Literal(True, "VERDADERO")

        elif self.match("FALSO"):
            self.consume("FALSO")
            return Literal(False, "FALSO")

        else:
            token = self.current_token()
            if token:
                raise SyntaxError(f"Factor inesperado: {token.type.value}", token)
            else:
                raise SyntaxError("Se esperaba una expresión pero se llegó al final")

    def parse_function_call(self, function_name: str) -> FunctionCall:
        """Parse: IDENTIFICADOR(expresión, expresión, ...)"""
        self.consume("PARÉNTESIS_IZQ")

        arguments = []
        if not self.match("PARÉNTESIS_DER"):
            arguments.append(self.parse_expression())

            while self.match("COMA"):
                self.consume("COMA")
                arguments.append(self.parse_expression())

        self.consume("PARÉNTESIS_DER")
        return FunctionCall(function_name, arguments)


# =======================================================
# DEMOSTRACIÓN INTEGRADA
# =======================================================

def demostrar_analisis_completo():
    """
    Demuestra el análisis léxico y sintáctico integrados.
    """

    # Ejemplos de código para parsear
    ejemplos_codigo = [
        # Ejemplo 1: Asignación simple
        "x = 5 + 3",

        # Ejemplo 2: Expresión con paréntesis
        "resultado = (a + b) * 2",

        # Ejemplo 3: If statement
        "if x > 0 : print(x)",

        # Ejemplo 4: Múltiples sentencias
        "x = 10\ny = x + 5\nprint(y)",

        # Ejemplo 5: Función y while
        "contador = 0\nwhile contador < 5 : contador = contador + 1"
    ]

    lexer = LexicalAnalyzer()

    for i, codigo in enumerate(ejemplos_codigo, 1):
        print(f"\n{'='*70}")
        print(f"EJEMPLO {i}: ANÁLISIS LÉXICO + SINTÁCTICO")
        print(f"{'='*70}")

        print(f"Código fuente:")
        print(f"  {repr(codigo)}")

        # FASE 1: Análisis Léxico
        print(f"\n{'-'*50}")
        print("FASE 1: ANÁLISIS LÉXICO")
        print(f"{'-'*50}")

        tokens = lexer.tokenize(codigo)
        tokens_filtrados = [t for t in tokens if t.type.value not in ['ESPACIO', 'NUEVA_LÍNEA']]

        print("Tokens generados:")
        for token in tokens_filtrados:
            print(f"  {token}")

        # FASE 2: Análisis Sintáctico
        print(f"\n{'-'*50}")
        print("FASE 2: ANÁLISIS SINTÁCTICO")
        print(f"{'-'*50}")

        try:
            parser = SyntaxAnalyzer(tokens)
            ast = parser.parse()

            print(" Análisis sintáctico exitoso!")
            print(f"AST generado:")
            print(f"  {ast}")

            # Mostrar estructura detallada
            print(f"\nEstructura del AST:")
            mostrar_ast_detallado(ast, "  ")

        except SyntaxError as e:
            print(f" Error de sintaxis: {e}")
        except Exception as e:
            print(f" Error inesperado: {e}")

def mostrar_ast_detallado(node: ASTNode, indent: str = ""):
    """Muestra la estructura del AST de forma jerárquica."""
    if isinstance(node, Program):
        print(f"{indent}Programa:")
        for stmt in node.statements:
            mostrar_ast_detallado(stmt, indent + "  ")

    elif isinstance(node, Assignment):
        print(f"{indent}Asignación:")
        print(f"{indent}  Variable: {node.target}")
        print(f"{indent}  Valor:")
        mostrar_ast_detallado(node.value, indent + "    ")

    elif isinstance(node, BinaryOperation):
        print(f"{indent}Operación Binaria ({node.operator}):")
        print(f"{indent}  Izquierda:")
        mostrar_ast_detallado(node.left, indent + "    ")
        print(f"{indent}  Derecha:")
        mostrar_ast_detallado(node.right, indent + "    ")

    elif isinstance(node, Literal):
        print(f"{indent}Literal: {node.value} (tipo: {node.token_type})")

    elif isinstance(node, Identifier):
        print(f"{indent}Identificador: {node.name}")

    elif isinstance(node, FunctionCall):
        print(f"{indent}Llamada a función: {node.name}")
        if node.arguments:
            print(f"{indent}  Argumentos:")
            for arg in node.arguments:
                mostrar_ast_detallado(arg, indent + "    ")

    elif isinstance(node, PrintStatement):
        print(f"{indent}Sentencia Print:")
        mostrar_ast_detallado(node.expression, indent + "  ")

    elif isinstance(node, IfStatement):
        print(f"{indent}Sentencia If:")
        print(f"{indent}  Condición:")
        mostrar_ast_detallado(node.condition, indent + "    ")
        if node.then_body:
            print(f"{indent}  Then:")
            for stmt in node.then_body:
                mostrar_ast_detallado(stmt, indent + "    ")
        if node.else_body:
            print(f"{indent}  Else:")
            for stmt in node.else_body:
                mostrar_ast_detallado(stmt, indent + "    ")


if __name__ == "__main__":
    demostrar_analisis_completo()