from typing import List, Optional
from token_types import TokenType
from token_model import Token
from ast_nodes import (
    Program, Literal, Identifier, BinaryOperation, UnaryOperation, FunctionCall,
    VariableDeclaration, Assignment, ReturnStatement, IfStatement, WhileStatement,
    ExpressionStatement, Block, Parameter, FunctionDeclaration, Expression, Statement
)


class SyntaxError(Exception):
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        super().__init__(self.format_error())

    def format_error(self) -> str:
        if self.token:
            return f"Error de sintaxis en línea {self.token.line}, columna {self.token.column}: {self.message}"
        return f"Error de sintaxis: {self.message}"


class SyntaxAnalyzer:
    def __init__(self, tokens: List[Token]):
        self.tokens = [
            token for token in tokens
            if token.type not in {
                TokenType.WHITESPACE,
                TokenType.NEWLINE,
                TokenType.COMMENT,
                TokenType.PREPROCESSOR,
            }
        ]
        self.position = 0

    def current_token(self) -> Optional[Token]:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def peek_token(self, offset: int = 1) -> Optional[Token]:
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def match(self, *types: TokenType) -> bool:
        token = self.current_token()
        return token is not None and token.type in types

    def consume(self, expected_type: TokenType) -> Token:
        token = self.current_token()
        if token is None:
            raise SyntaxError(f"Se esperaba {expected_type.value}, pero se llegó al final")
        if token.type != expected_type:
            raise SyntaxError(f"Se esperaba {expected_type.value}, se encontró {token.type.value}", token)
        self.position += 1
        return token

    def parse(self) -> Program:
        declarations = []
        while not self.match(TokenType.EOF):
            declarations.append(self.parse_top_level())
        return Program(declarations)

    def parse_top_level(self):
        type_token = self.parse_type_specifier()
        name = self.consume(TokenType.IDENTIFIER).value

        if self.match(TokenType.LPAREN):
            return self.parse_function_declaration(type_token.value, name)
        raise SyntaxError("Solo se soportan funciones en el nivel superior por ahora")

    def parse_type_specifier(self) -> Token:
        token = self.current_token()
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.VOID):
            self.position += 1
            return token
        raise SyntaxError("Se esperaba un tipo", token)

    def parse_function_declaration(self, return_type: str, name: str) -> FunctionDeclaration:
        self.consume(TokenType.LPAREN)
        parameters = []

        if not self.match(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            while self.match(TokenType.COMMA):
                self.consume(TokenType.COMMA)
                parameters.append(self.parse_parameter())

        self.consume(TokenType.RPAREN)
        body = self.parse_block()
        return FunctionDeclaration(return_type, name, parameters, body)

    def parse_parameter(self) -> Parameter:
        param_type = self.parse_type_specifier().value
        name = self.consume(TokenType.IDENTIFIER).value
        return Parameter(param_type, name)

    def parse_block(self) -> Block:
        self.consume(TokenType.LBRACE)
        statements = []

        while not self.match(TokenType.RBRACE):
            statements.append(self.parse_statement())

        self.consume(TokenType.RBRACE)
        return Block(statements)

    def parse_statement(self) -> Statement:
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.CHAR):
            return self.parse_variable_declaration()

        if self.match(TokenType.IF):
            return self.parse_if_statement()

        if self.match(TokenType.WHILE):
            return self.parse_while_statement()

        if self.match(TokenType.RETURN):
            return self.parse_return_statement()

        if self.match(TokenType.LBRACE):
            return self.parse_block()

        if self.match(TokenType.IDENTIFIER) and self.peek_token() and self.peek_token().type == TokenType.ASSIGN:
            return self.parse_assignment()

        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return ExpressionStatement(expr)

    def parse_variable_declaration(self) -> VariableDeclaration:
        var_type = self.parse_type_specifier().value
        name = self.consume(TokenType.IDENTIFIER).value
        initializer = None

        if self.match(TokenType.ASSIGN):
            self.consume(TokenType.ASSIGN)
            initializer = self.parse_expression()

        self.consume(TokenType.SEMICOLON)
        return VariableDeclaration(var_type, name, initializer)

    def parse_assignment(self) -> Assignment:
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.ASSIGN)
        value = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return Assignment(name, value)

    def parse_if_statement(self) -> IfStatement:
        self.consume(TokenType.IF)
        self.consume(TokenType.LPAREN)
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN)
        then_body = self.parse_statement()
        else_body = None

        if self.match(TokenType.ELSE):
            self.consume(TokenType.ELSE)
            else_body = self.parse_statement()

        if not isinstance(then_body, Block):
            then_body = Block([then_body])
        if else_body is not None and not isinstance(else_body, Block):
            else_body = Block([else_body])

        return IfStatement(condition, then_body, else_body)

    def parse_while_statement(self) -> WhileStatement:
        self.consume(TokenType.WHILE)
        self.consume(TokenType.LPAREN)
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN)
        body = self.parse_statement()

        if not isinstance(body, Block):
            body = Block([body])

        return WhileStatement(condition, body)

    def parse_return_statement(self) -> ReturnStatement:
        self.consume(TokenType.RETURN)

        if self.match(TokenType.SEMICOLON):
            self.consume(TokenType.SEMICOLON)
            return ReturnStatement(None)

        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return ReturnStatement(expr)

    def parse_expression(self) -> Expression:
        return self.parse_logical_or()

    def parse_logical_or(self) -> Expression:
        left = self.parse_logical_and()
        while self.match(TokenType.OR):
            op = self.consume(TokenType.OR).value
            right = self.parse_logical_and()
            left = BinaryOperation(left, op, right)
        return left

    def parse_logical_and(self) -> Expression:
        left = self.parse_equality()
        while self.match(TokenType.AND):
            op = self.consume(TokenType.AND).value
            right = self.parse_equality()
            left = BinaryOperation(left, op, right)
        return left

    def parse_equality(self) -> Expression:
        left = self.parse_relational()
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self.current_token().value
            self.position += 1
            right = self.parse_relational()
            left = BinaryOperation(left, op, right)
        return left

    def parse_relational(self) -> Expression:
        left = self.parse_additive()
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op = self.current_token().value
            self.position += 1
            right = self.parse_additive()
            left = BinaryOperation(left, op, right)
        return left

    def parse_additive(self) -> Expression:
        left = self.parse_term()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.current_token().value
            self.position += 1
            right = self.parse_term()
            left = BinaryOperation(left, op, right)
        return left

    def parse_term(self) -> Expression:
        left = self.parse_unary()
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.current_token().value
            self.position += 1
            right = self.parse_unary()
            left = BinaryOperation(left, op, right)
        return left

    def parse_unary(self) -> Expression:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.current_token().value
            self.position += 1
            operand = self.parse_unary()
            return UnaryOperation(op, operand)
        return self.parse_primary()

    def parse_primary(self) -> Expression:
        if self.match(TokenType.NUMBER):
            token = self.consume(TokenType.NUMBER)
            value = float(token.value) if '.' in token.value else int(token.value)
            return Literal(value, "NUMBER")

        if self.match(TokenType.STRING):
            token = self.consume(TokenType.STRING)
            return Literal(token.value[1:-1], "STRING")

        if self.match(TokenType.CHAR_LITERAL):
            token = self.consume(TokenType.CHAR_LITERAL)
            return Literal(token.value[1:-1], "CHAR")

        if self.match(TokenType.IDENTIFIER):
            name = self.consume(TokenType.IDENTIFIER).value
            if self.match(TokenType.LPAREN):
                return self.parse_function_call(name)
            return Identifier(name)

        if self.match(TokenType.LPAREN):
            self.consume(TokenType.LPAREN)
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return expr

        token = self.current_token()
        raise SyntaxError("Expresión inesperada", token)

    def parse_function_call(self, name: str) -> FunctionCall:
        self.consume(TokenType.LPAREN)
        arguments = []

        if not self.match(TokenType.RPAREN):
            arguments.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.consume(TokenType.COMMA)
                arguments.append(self.parse_expression())

        self.consume(TokenType.RPAREN)
        return FunctionCall(name, arguments)