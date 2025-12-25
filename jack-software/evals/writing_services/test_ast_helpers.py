"""Unit tests for AST helper functions."""

import tempfile
import unittest
from pathlib import Path

from .ast_helpers import check_uses_union_none_syntax


class TestCheckUsesUnionNoneSyntax(unittest.TestCase):
    """Tests for check_uses_union_none_syntax function."""

    def test_file_with_union_none_only(self):
        """Should return True when file uses | None syntax without Optional."""
        content = '''
def foo(x: str | None) -> int | None:
    return None

class MyClass:
    value: dict | None = None
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_file_with_optional_only(self):
        """Should return False when file uses Optional syntax."""
        content = '''
from typing import Optional

def foo(x: Optional[str]) -> Optional[int]:
    return None

class MyClass:
    value: Optional[dict] = None
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_file_with_both_union_and_optional(self):
        """Should return False when file uses both | None and Optional."""
        content = '''
from typing import Optional

def foo(x: str | None) -> Optional[int]:
    return None
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_file_with_no_type_annotations(self):
        """Should return True when file has no type annotations (no Optional used)."""
        content = '''
def foo(x):
    return None

class MyClass:
    value = None
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_file_with_reversed_union_none(self):
        """Should return True when file uses None | X syntax."""
        content = '''
def foo(x: None | str) -> int:
    return 1
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_file_with_union_but_not_none(self):
        """Should return True when file uses | but not with None (no Optional used)."""
        content = '''
def foo(x: str | int) -> list | dict:
    return []
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_nonexistent_file(self):
        """Should return False when file doesn't exist."""
        path = Path("/nonexistent/file.py")
        self.assertFalse(check_uses_union_none_syntax(path))

    def test_file_with_syntax_error(self):
        """Should return False when file has syntax errors."""
        content = '''
def foo(x: str | None
    return None
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_file_with_union_none_in_multiple_locations(self):
        """Should return True when | None appears in various contexts."""
        content = '''
from dataclasses import dataclass

@dataclass
class MyClass:
    name: str | None
    value: int | None
    data: dict[str, str] | None

def process(
    x: str | None,
    y: list[int] | None = None,
) -> tuple[str, int] | None:
    if x is None:
        return None
    return (x, 1)
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_file_with_optional_string_in_comment(self):
        """Should return True if Optional appears only in comments."""
        content = '''
# This used to use Optional[str] but now uses | None
def foo(x: str | None) -> int | None:
    # Optional is mentioned here but not used
    return None
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            # This should return True because Optional isn't used in actual code
            self.assertTrue(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_empty_file(self):
        """Should return True for empty file (no Optional used)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('')
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_uses_union_none_syntax(path))
        finally:
            path.unlink()

    def test_file_with_type_annotations_but_no_optional_types(self):
        """Should return True when file has type annotations but neither | None nor Optional."""
        content = '''
def foo(x: str, y: int) -> list[str]:
    return [x] * y

class MyClass:
    name: str
    count: int
    data: dict[str, int]

def process(items: list[dict[str, str]]) -> tuple[int, str]:
    return (len(items), "done")
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            # Should pass because it doesn't use Optional (no optional types at all)
            self.assertTrue(check_uses_union_none_syntax(path))
        finally:
            path.unlink()


if __name__ == '__main__':
    unittest.main()
