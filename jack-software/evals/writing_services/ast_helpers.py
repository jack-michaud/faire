"""AST helpers for analyzing generated Python code in evals."""

import ast
from pathlib import Path


def check_uses_union_none_syntax(file_path: Path) -> bool:
    """Check if a Python file uses | None instead of Optional[T].

    Returns True if the file doesn't use Optional from typing.
    The file can use | None for optional types, or have no optional types at all.
    Returns False if the file uses Optional[T] syntax.
    """
    if not file_path.exists():
        return False

    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return False

    class TypeAnnotationVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_optional = False

        def visit_Subscript(self, node):
            # Check for Optional[X] pattern
            if isinstance(node.value, ast.Name) and node.value.id == "Optional":
                self.has_optional = True
            self.generic_visit(node)

    visitor = TypeAnnotationVisitor()
    visitor.visit(tree)

    # Return True if the file doesn't use Optional
    return not visitor.has_optional
