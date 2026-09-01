import ast
import operator

from langchain_core.tools import tool

_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _evaluate(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 10_000:
            raise ValueError("Exponent is too large")
        return _BINARY_OPERATORS[type(node.op)](left, right)
    raise ValueError("Only basic arithmetic is supported")


@tool
def calculator(expression: str) -> str:
    """Evaluate a bounded basic arithmetic expression."""
    if not expression or len(expression) > 200:
        return "Invalid arithmetic expression."

    try:
        result = _evaluate(ast.parse(expression, mode="eval").body)
    except (ArithmeticError, SyntaxError, ValueError) as exc:
        return f"Could not calculate expression: {exc}"

    return str(result)
