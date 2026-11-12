
import ast
import operator
import math
import re

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "pi": math.pi,
    "e": math.e,
}


def safe_calculate(expression):
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent too large")

            return OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](evaluate(node.operand))

        if isinstance(node, ast.Name) and node.id in FUNCTIONS:
            value = FUNCTIONS[node.id]
            if isinstance(value, (int, float)):
                return value

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS:
                function = FUNCTIONS[node.func.id]
                if callable(function) and len(node.args) == 1:
                    return function(evaluate(node.args[0]))

        raise ValueError("Unsupported expression")

    return evaluate(tree)


def calculate(expression):
    try:
        expression = expression.lower().strip()

        # Handle percentage questions
        percent_match = re.search(
            r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)",
            expression
        )

        if percent_match:
            percentage = float(percent_match.group(1))
            number = float(percent_match.group(2))
            result = percentage / 100 * number
        else:
            # Remove common question words
            expression = re.sub(
                r"^(what is|calculate|compute|solve|please calculate)\s+",
                "",
                expression
            )
            expression = expression.rstrip("? ")
            result = safe_calculate(expression)

        return str(result)

    except Exception:
        return "Sorry, I couldn't calculate that expression."
