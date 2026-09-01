from langchain_core.tools import tool


@tool

def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression using Python's numeric operations."""
    allowed = set("0123456789+-*/(). %")
    if not expression or any(char not in allowed for char in expression):
        return "Invalid arithmetic expression."

    try:
        result = eval(expression, {"__builtins__": {}}, {})
    except Exception as exc:
        return f"Could not calculate expression: {exc}"

    return str(result)
