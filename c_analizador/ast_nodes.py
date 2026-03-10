from abc import ABC, abstractmethod
from typing import List, Optional, Union


class ASTNode(ABC):
    @abstractmethod
    def __str__(self):
        pass


class Expression(ASTNode):
    pass


class Statement(ASTNode):
    pass


class Program(ASTNode):
    def __init__(self, declarations: List[ASTNode]):
        self.declarations = declarations

    def __str__(self):
        return "Program([\n  " + ",\n  ".join(str(d) for d in self.declarations) + "\n])"


class Literal(Expression):
    def __init__(self, value: Union[int, float, str], literal_type: str):
        self.value = value
        self.literal_type = literal_type

    def __str__(self):
        return f"Literal({self.value})"


class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"Identifier({self.name})"


class BinaryOperation(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class UnaryOperation(Expression):
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand

    def __str__(self):
        return f"UnaryOp({self.operator}{self.operand})"


class FunctionCall(Expression):
    def __init__(self, name: str, arguments: List[Expression]):
        self.name = name
        self.arguments = arguments

    def __str__(self):
        return f"FunctionCall({self.name}({', '.join(str(a) for a in self.arguments)}))"


class VariableDeclaration(Statement):
    def __init__(self, var_type: str, name: str, initializer: Optional[Expression] = None):
        self.var_type = var_type
        self.name = name
        self.initializer = initializer

    def __str__(self):
        return f"VarDecl({self.var_type} {self.name}" + (f" = {self.initializer}" if self.initializer else "") + ")"


class Assignment(Statement):
    def __init__(self, target: str, value: Expression):
        self.target = target
        self.value = value

    def __str__(self):
        return f"Assignment({self.target} = {self.value})"


class ReturnStatement(Statement):
    def __init__(self, expression: Optional[Expression] = None):
        self.expression = expression

    def __str__(self):
        return f"Return({self.expression})"


class IfStatement(Statement):
    def __init__(self, condition: Expression, then_body: 'Block', else_body: Optional['Block'] = None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def __str__(self):
        return f"If({self.condition}, {self.then_body}, {self.else_body})"


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: 'Block'):
        self.condition = condition
        self.body = body

    def __str__(self):
        return f"While({self.condition}, {self.body})"


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __str__(self):
        return f"ExprStmt({self.expression})"


class Block(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements = statements

    def __str__(self):
        return "Block([" + ", ".join(str(s) for s in self.statements) + "])"


class Parameter(ASTNode):
    def __init__(self, param_type: str, name: str):
        self.param_type = param_type
        self.name = name

    def __str__(self):
        return f"Param({self.param_type} {self.name})"


class FunctionDeclaration(ASTNode):
    def __init__(self, return_type: str, name: str, parameters: List[Parameter], body: Block):
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body

    def __str__(self):
        params = ", ".join(str(p) for p in self.parameters)
        return f"Function({self.return_type} {self.name}({params}) {self.body})"