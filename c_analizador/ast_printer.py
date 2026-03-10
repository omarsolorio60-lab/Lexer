
import io
from contextlib import redirect_stdout

from ast_nodes import (
    Program, FunctionDeclaration, Block, VariableDeclaration, Assignment,
    ReturnStatement, IfStatement, WhileStatement, ForStatement, ExpressionStatement,
    BinaryOperation, UnaryOperation, Literal, Identifier, FunctionCall
)


def mostrar_ast(node, indent=""):
    if isinstance(node, Program):
        print(f"{indent}Programa:")
        for d in node.declarations:
            mostrar_ast(d, indent + "  ")

    elif isinstance(node, FunctionDeclaration):
        print(f"{indent}Funcion: {node.return_type} {node.name}")
        if node.parameters:
            print(f"{indent}  Parametros:")
            for p in node.parameters:
                print(f"{indent}    - {p.param_type} {p.name}")
        print(f"{indent}  Cuerpo:")
        mostrar_ast(node.body, indent + "    ")

    elif isinstance(node, Block):
        print(f"{indent}Bloque:")
        for s in node.statements:
            mostrar_ast(s, indent + "  ")

    elif isinstance(node, VariableDeclaration):
        print(f"{indent}Declaracion: {node.var_type} {node.name}")
        if node.initializer:
            print(f"{indent}  Inicializador:")
            mostrar_ast(node.initializer, indent + "    ")

    elif isinstance(node, Assignment):
        print(f"{indent}Asignacion: {node.target}")
        mostrar_ast(node.value, indent + "  ")

    elif isinstance(node, ReturnStatement):
        print(f"{indent}Return:")
        if node.expression:
            mostrar_ast(node.expression, indent + "  ")

    elif isinstance(node, IfStatement):
        print(f"{indent}If:")
        print(f"{indent}  Condicion:")
        mostrar_ast(node.condition, indent + "    ")
        print(f"{indent}  Then:")
        mostrar_ast(node.then_body, indent + "    ")
        if node.else_body:
            print(f"{indent}  Else:")
            mostrar_ast(node.else_body, indent + "    ")

    elif isinstance(node, WhileStatement):
        print(f"{indent}While:")
        print(f"{indent}  Condicion:")
        mostrar_ast(node.condition, indent + "    ")
        print(f"{indent}  Cuerpo:")
        mostrar_ast(node.body, indent + "    ")

    elif isinstance(node, ExpressionStatement):
        print(f"{indent}ExprStmt:")
        mostrar_ast(node.expression, indent + "  ")

    elif isinstance(node, BinaryOperation):
        print(f"{indent}BinOp: {node.operator}")
        print(f"{indent}  Izquierda:")
        mostrar_ast(node.left, indent + "    ")
        print(f"{indent}  Derecha:")
        mostrar_ast(node.right, indent + "    ")

    elif isinstance(node, UnaryOperation):
        print(f"{indent}UnaryOp: {node.operator}")
        mostrar_ast(node.operand, indent + "  ")

    elif isinstance(node, Literal):
        print(f"{indent}Literal: {node.value}")

    elif isinstance(node, Identifier):
        print(f"{indent}Identificador: {node.name}")

    elif isinstance(node, FunctionCall):
        print(f"{indent}Llamada: {node.name}")
        for arg in node.arguments:
            mostrar_ast(arg, indent + "  ")

    elif isinstance(node, ForStatement):
        print(f"{indent}For:")
        print(f"{indent}  Inicializador:")
        if node.initializer:
            mostrar_ast(node.initializer, indent + "    ")
        else:
            print(f"{indent}    None")

        print(f"{indent}  Condicion:")
        if node.condition:
            mostrar_ast(node.condition, indent + "    ")
        else:
            print(f"{indent}    None")

        print(f"{indent}  Incremento:")
        if node.increment:
            mostrar_ast(node.increment, indent + "    ")
        else:
            print(f"{indent}    None")

        print(f"{indent}  Cuerpo:")
        mostrar_ast(node.body, indent + "    ")

def obtener_ast_como_texto(ast):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        mostrar_ast(ast)
    return buffer.getvalue()