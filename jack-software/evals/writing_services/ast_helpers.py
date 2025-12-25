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


def check_methods_use_dataclasses(file_path: Path) -> bool:
    """Check if a Python file uses dataclasses for complex method parameters and returns.

    Returns True if:
    - No method parameters use bare 'dict' or 'Dict' (without type parameters)
    - No method return types use 'dict' or 'Dict' (even with type parameters)

    Returns False if any method uses dict types instead of dataclasses.
    """
    if not file_path.exists():
        return False

    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return False

    class MethodTypeVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_dict_violation = False
            self.in_dataclass = False

        def _is_dataclass(self, node: ast.ClassDef) -> bool:
            """Check if a class has a @dataclass decorator."""
            for decorator in node.decorator_list:
                # Handle simple decorator: @dataclass
                if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                    return True
                # Handle qualified decorator: @dataclasses.dataclass
                if isinstance(decorator, ast.Attribute) and decorator.attr == "dataclass":
                    return True
            return False

        def _is_dict_type(self, node: ast.expr) -> bool:
            """Check if a node represents a dict or Dict type."""
            if isinstance(node, ast.Name) and node.id in ("dict", "Dict"):
                return True
            if isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name) and node.value.id in (
                    "dict",
                    "Dict",
                ):
                    return True
            return False

        def _check_annotation(self, node: ast.expr | None, allow_subscripted_dict: bool = False) -> None:
            """Check if an annotation uses dict types inappropriately."""
            if node is None:
                return

            # Handle BinOp for union types (e.g., X | None)
            if isinstance(node, ast.BinOp):
                self._check_annotation(node.left, allow_subscripted_dict)
                self._check_annotation(node.right, allow_subscripted_dict)
                return

            # Check for bare dict or Dict (always bad)
            if isinstance(node, ast.Name) and node.id in ("dict", "Dict"):
                self.has_dict_violation = True
                return

            # Check for subscripted dict/Dict (bad for return types)
            if isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name) and node.value.id in ("dict", "Dict"):
                    if not allow_subscripted_dict:
                        self.has_dict_violation = True
                    return

        def visit_ClassDef(self, node):
            """Track when we're inside a dataclass."""
            old_in_dataclass = self.in_dataclass
            if self._is_dataclass(node):
                self.in_dataclass = True
            self.generic_visit(node)
            self.in_dataclass = old_in_dataclass

        def visit_FunctionDef(self, node):
            """Check function signatures for dict usage."""
            # Check parameters (allow subscripted dict like dict[str, Any])
            for arg in node.args.args:
                if arg.arg == "self" or arg.arg == "cls":
                    continue
                self._check_annotation(arg.annotation, allow_subscripted_dict=True)

            # Check return type (allow dict returns from dataclass methods)
            allow_dict_return = self.in_dataclass
            self._check_annotation(node.returns, allow_subscripted_dict=allow_dict_return)

            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            """Check async function signatures for dict usage."""
            # Check parameters (allow subscripted dict like dict[str, Any])
            for arg in node.args.args:
                if arg.arg == "self" or arg.arg == "cls":
                    continue
                self._check_annotation(arg.annotation, allow_subscripted_dict=True)

            # Check return type (allow dict returns from dataclass methods)
            allow_dict_return = self.in_dataclass
            self._check_annotation(node.returns, allow_subscripted_dict=allow_dict_return)

            self.generic_visit(node)

    visitor = MethodTypeVisitor()
    visitor.visit(tree)

    # Return True if no violations found
    return not visitor.has_dict_violation
