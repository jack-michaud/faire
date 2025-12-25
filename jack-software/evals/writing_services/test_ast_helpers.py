"""Unit tests for AST helper functions."""

import tempfile
import unittest
from pathlib import Path

from .ast_helpers import check_methods_use_dataclasses, check_uses_union_none_syntax


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


class TestCheckMethodsUseDataclasses(unittest.TestCase):
    """Tests for check_methods_use_dataclasses function."""

    def test_file_with_dataclass_params_and_returns(self):
        """Should return True when methods use dataclasses for params and returns."""
        content = '''
from dataclasses import dataclass

@dataclass
class UserRequest:
    name: str
    age: int

@dataclass
class UserResponse:
    id: int
    status: str

class UserService:
    def create_user(self, request: UserRequest) -> UserResponse:
        return UserResponse(id=1, status="created")

    def get_user(self, user_id: int) -> UserResponse | None:
        return None
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_bare_dict_param(self):
        """Should return False when method parameter uses bare dict."""
        content = '''
class UserService:
    def create_user(self, data: dict) -> str:
        return "created"
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_subscripted_dict_param(self):
        """Should return True when method parameter uses dict[str, Any]."""
        content = '''
from typing import Any

class UserService:
    def create_user(self, data: dict[str, Any]) -> str:
        return "created"
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_dict_return_type(self):
        """Should return False when method returns dict (even with generics)."""
        content = '''
from typing import Any

class UserService:
    def get_user(self, user_id: int) -> dict[str, Any]:
        return {"id": user_id, "name": "John"}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_bare_dict_return(self):
        """Should return False when method returns bare dict."""
        content = '''
class UserService:
    def get_user(self, user_id: int) -> dict:
        return {"id": user_id}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_primitive_types(self):
        """Should return True when methods use primitive types."""
        content = '''
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

    def concat(self, a: str, b: str) -> str:
        return a + b

    def is_valid(self, value: float) -> bool:
        return value > 0
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_private_methods_using_dict(self):
        """Should return False when private methods use dict (private methods are also checked)."""
        content = '''
from dataclasses import dataclass

@dataclass
class UserResponse:
    id: int
    name: str

class UserService:
    def get_user(self, user_id: int) -> UserResponse:
        data = self._fetch_data(user_id)
        return UserResponse(id=data["id"], name=data["name"])

    def _fetch_data(self, user_id: int) -> dict[str, str]:
        # Private methods are also checked
        return {"id": str(user_id), "name": "John"}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_typing_dict(self):
        """Should return False when method uses typing.Dict."""
        content = '''
from typing import Dict

class UserService:
    def get_user(self, user_id: int) -> Dict[str, str]:
        return {"id": str(user_id)}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_union_dict_return(self):
        """Should return False when return type is dataclass | dict."""
        content = '''
from dataclasses import dataclass

@dataclass
class UserResponse:
    id: int

class UserService:
    def get_user(self, user_id: int) -> UserResponse | dict[str, str]:
        if user_id > 0:
            return UserResponse(id=user_id)
        return {"error": "invalid"}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_no_type_annotations(self):
        """Should return True when methods have no type annotations."""
        content = '''
class UserService:
    def create_user(self, name, age):
        return {"id": 1}

    def get_user(self, user_id):
        return None
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_file_with_list_and_tuple_types(self):
        """Should return True when methods use list and tuple types."""
        content = '''
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str

class UserService:
    def get_all_users(self) -> list[User]:
        return []

    def get_user_tuple(self, user_id: int) -> tuple[int, str]:
        return (user_id, "John")
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_nonexistent_file(self):
        """Should return False when file doesn't exist."""
        path = Path("/nonexistent/file.py")
        self.assertFalse(check_methods_use_dataclasses(path))

    def test_file_with_syntax_error(self):
        """Should return False when file has syntax errors."""
        content = '''
def foo(x: dict[str, Any]
    return x
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_empty_file(self):
        """Should return True for empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('')
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_standalone_functions_with_dict(self):
        """Should return False when standalone functions return dict."""
        content = '''
def get_config() -> dict[str, str]:
    return {"key": "value"}

def process_data(data: dict) -> str:
    return "processed"
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_async_functions_with_dataclasses(self):
        """Should return True when async methods use dataclasses."""
        content = '''
from dataclasses import dataclass

@dataclass
class AsyncRequest:
    url: str

@dataclass
class AsyncResponse:
    status: int
    body: str

class AsyncService:
    async def fetch(self, request: AsyncRequest) -> AsyncResponse:
        return AsyncResponse(status=200, body="OK")
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_async_functions_with_dict_return(self):
        """Should return False when async methods return dict."""
        content = '''
class AsyncService:
    async def fetch(self, url: str) -> dict[str, str]:
        return {"status": "ok"}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_dataclass_methods_can_return_dict(self):
        """Should return True when dataclass methods return dict."""
        content = '''
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str

    def to_dict(self) -> dict[str, str | int]:
        return {"id": self.id, "name": self.name}

    def get_metadata(self) -> dict[str, str]:
        return {"type": "user"}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_dataclass_with_dataclasses_module(self):
        """Should return True when using @dataclasses.dataclass decorator."""
        content = '''
import dataclasses

@dataclasses.dataclass
class Config:
    key: str
    value: str

    def to_dict(self) -> dict[str, str]:
        return {"key": self.key, "value": self.value}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertTrue(check_methods_use_dataclasses(path))
        finally:
            path.unlink()

    def test_non_dataclass_methods_cannot_return_dict(self):
        """Should return False when regular class methods return dict."""
        content = '''
class UserService:
    def get_user_data(self, user_id: int) -> dict[str, str]:
        return {"id": str(user_id)}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            self.assertFalse(check_methods_use_dataclasses(path))
        finally:
            path.unlink()


if __name__ == '__main__':
    unittest.main()
