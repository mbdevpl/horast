"""Idenify docstrings in AST and transform the AST accordingly."""

import inspect

import typed_ast.ast3


def is_docstring(node: typed_ast.ast3.AST) -> bool:
    stack = inspect.stack()
    frame = stack[6].frame
    if 'fundef' not in frame.f_locals:
        return False
    expr = frame.f_locals['fundef'].body[0]
    if not isinstance(expr, typed_ast.ast3.Expr):
        return False
    if expr.value is not node:
        return False
    return True


def convert_docstrings(tree: typed_ast.ast3.AST) -> typed_ast.ast3.AST:
    raise NotImplementedError(tree)
