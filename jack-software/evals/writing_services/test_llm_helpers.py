"""Unit tests for LLM helper functions."""

import tempfile
import unittest
from pathlib import Path

from .llm_helpers import check_no_constructor_side_effects


class TestCheckNoConstructorSideEffects(unittest.IsolatedAsyncioTestCase):
    """Tests for check_no_constructor_side_effects function."""

    async def test_good_example_with_cached_property(self):
        """Should return True when IO is deferred to @cached_property."""
        content = """
import sqlite3
from functools import cached_property
from pathlib import Path

class Logger:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    @cached_property
    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        return conn

    def log(self, message: str) -> None:
        cursor = self._connection.cursor()
        cursor.execute("INSERT INTO logs (message) VALUES (?)", (message,))
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = await check_no_constructor_side_effects(path)
            self.assertTrue(result)
        finally:
            path.unlink()

    async def test_bad_example_with_io_in_init(self):
        """Should return False when __init__ performs IO operations."""
        content = """
import sqlite3
from pathlib import Path

class Logger:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(str(db_path))

    def log(self, message: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO logs (message) VALUES (?)", (message,))
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = await check_no_constructor_side_effects(path)
            self.assertFalse(result)
        finally:
            path.unlink()

    async def test_bad_example_with_file_io_in_init(self):
        """Should return False when __init__ opens files."""
        content = """
class ConfigReader:
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        with open(config_path) as f:
            self.config = f.read()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = await check_no_constructor_side_effects(path)
            self.assertFalse(result)
        finally:
            path.unlink()

    async def test_good_example_simple_attributes(self):
        """Should return True when __init__ only sets simple attributes."""
        content = """
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

class UserService:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.timeout = 30
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = await check_no_constructor_side_effects(path)
            self.assertTrue(result)
        finally:
            path.unlink()

    async def test_nonexistent_file(self):
        """Should return False when file doesn't exist."""
        path = Path("/nonexistent/file.py")
        result = await check_no_constructor_side_effects(path)
        self.assertFalse(result)

    async def test_empty_file(self):
        """Should return True for empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("")
            f.flush()
            path = Path(f.name)

        try:
            result = await check_no_constructor_side_effects(path)
            self.assertTrue(result)
        finally:
            path.unlink()

    async def test_file_with_no_classes(self):
        """Should return True when file has no classes."""
        content = """
def helper_function(x: int) -> int:
    return x * 2

def main():
    print(helper_function(5))
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = await check_no_constructor_side_effects(path)
            self.assertTrue(result)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
