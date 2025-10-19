---
name: Test-Driven Development
description: Write tests first, then implement code to pass them - the RED-GREEN-REFACTOR cycle. Use when implementing new features, fixing bugs, or adding functionality to existing code.
---

# Test-Driven Development

## Overview

Test-Driven Development (TDD) is a development approach where you write tests before writing implementation code. This ensures code is testable, reduces bugs, and provides living documentation of expected behavior.

## When to Use

- Implementing a new feature or function
- Fixing a bug (write a failing test that reproduces it)
- Refactoring existing code (tests ensure behavior doesn't change)
- Working on critical business logic
- When you want high confidence in code correctness

## The TDD Cycle: RED-GREEN-REFACTOR

### 1. RED: Write a Failing Test

```python
# test_calculator.py
def test_add_two_numbers():
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5  # This will fail - Calculator doesn't exist yet
```

**Why it fails**: The implementation doesn't exist or doesn't handle the case yet.

### 2. GREEN: Write Minimal Code to Pass

```python
# calculator.py
class Calculator:
    def add(self, a, b):
        return a + b  # Simplest implementation that passes
```

**Goal**: Make the test pass with the simplest code possible. Don't over-engineer.

### 3. REFACTOR: Improve the Code

```python
# calculator.py (refactored)
class Calculator:
    """A simple calculator for basic arithmetic operations."""

    def add(self, a: float, b: float) -> float:
        """Add two numbers and return the result."""
        return a + b
```

**Improvements**: Add type hints, documentation, error handling - while tests still pass.

## Process

1. **Write a test** that describes the desired behavior
2. **Run the test** and verify it fails (RED)
3. **Write minimal code** to make the test pass (GREEN)
4. **Run all tests** to ensure nothing broke
5. **Refactor** the code for clarity and efficiency
6. **Run tests again** to ensure refactoring didn't break anything
7. **Repeat** for the next piece of functionality

## Examples

### Example 1: Adding Input Validation

**RED - Write the test**:
```python
def test_add_rejects_non_numeric():
    calc = Calculator()
    with pytest.raises(TypeError):
        calc.add("2", 3)
```

**GREEN - Make it pass**:
```python
def add(self, a: float, b: float) -> float:
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be numeric")
    return a + b
```

**REFACTOR - Improve**:
```python
def add(self, a: float, b: float) -> float:
    """Add two numbers with type validation."""
    self._validate_numeric(a, b)
    return a + b

def _validate_numeric(self, *args):
    """Validate all arguments are numeric."""
    for arg in args:
        if not isinstance(arg, (int, float)):
            raise TypeError(f"Expected numeric type, got {type(arg).__name__}")
```

### Example 2: Bug Fix with TDD

**Problem**: Function crashes with empty list

**RED - Test that reproduces the bug**:
```python
def test_average_empty_list():
    result = calculate_average([])
    assert result == 0  # Or raise ValueError, depending on requirements
```

**GREEN - Fix the bug**:
```python
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

**REFACTOR - Make it robust**:
```python
def calculate_average(numbers: list[float]) -> float:
    """Calculate average of numbers, returning 0 for empty lists."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

## Benefits of TDD

- **Fewer bugs**: Issues caught early in development
- **Better design**: Writing tests first forces you to think about interfaces
- **Living documentation**: Tests show how code should be used
- **Confidence to refactor**: Tests catch regressions
- **Faster debugging**: Failing tests pinpoint issues

## Anti-patterns

- ❌ **Don't**: Write all tests first, then all implementation
  - ✅ **Do**: One test → one implementation → refactor → repeat

- ❌ **Don't**: Write tests after the implementation
  - ✅ **Do**: Write tests first to drive the design

- ❌ **Don't**: Skip the refactor step
  - ✅ **Do**: Clean up code while tests keep you safe

- ❌ **Don't**: Write tests that test implementation details
  - ✅ **Do**: Test behavior and public interfaces

- ❌ **Don't**: Make big leaps in implementation
  - ✅ **Do**: Take small steps, one test at a time

## Testing This Skill

To validate you're doing TDD correctly:

1. **Check**: Did you write the test before the implementation?
2. **Verify**: Did the test fail initially (RED)?
3. **Confirm**: Did you write minimal code to pass (GREEN)?
4. **Review**: Did you refactor while keeping tests green?
5. **Ensure**: Are all tests passing after refactoring?

## Common TDD Patterns

### Test Naming Convention

```python
def test_<function>_<scenario>_<expected_outcome>():
    # e.g., test_add_negative_numbers_returns_correct_sum()
    pass
```

### Arrange-Act-Assert Pattern

```python
def test_calculator_add():
    # Arrange: Set up test data
    calc = Calculator()
    a, b = 5, 3

    # Act: Execute the behavior
    result = calc.add(a, b)

    # Assert: Verify the outcome
    assert result == 8
```

### Test Fixtures

```python
@pytest.fixture
def calculator():
    """Reusable calculator instance for tests."""
    return Calculator()

def test_add(calculator):
    assert calculator.add(2, 3) == 5

def test_subtract(calculator):
    assert calculator.subtract(5, 3) == 2
```

## Integration with Claude Code

When implementing features:
1. Ask Claude to write tests first
2. Review test coverage before implementation
3. Reference this skill when you need TDD guidance

## Related Skills

- `writing-good-tests` - Best practices for test quality
- `debugging-failing-tests` - How to diagnose test failures
- `test-coverage-analysis` - Ensuring adequate test coverage

---

**Remember**: RED → GREEN → REFACTOR. Write the test, make it pass, clean it up. Repeat.
