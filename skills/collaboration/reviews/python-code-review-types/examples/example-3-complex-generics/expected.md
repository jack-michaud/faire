# Expected Findings

The skill should distinguish between deprecated and legitimate typing imports:

## Issues to Flag

1. **Line 1: Deprecated imports**
   - `List`, `Dict`, `Type` should not be imported from `typing`
   - Should use built-in `list`, `dict`, `type`

2. **Line 12: Old Type usage**
   - `item_type: Type[T]` uses old syntax
   - Should be `item_type: type[T]`

3. **Line 14: Old List usage**
   - `self._items: List[T] = []` uses old syntax
   - Should be `self._items: list[T] = []`

4. **Line 16: Missing return type**
   - `def add(self, item: T):` is missing `-> None`

5. **Line 19: Old List return type**
   - `-> List[T]` uses old syntax
   - Should be `-> list[T]`

6. **Line 22: Old List return type**
   - `-> List[T]` uses old syntax
   - Should be `-> list[T]`

7. **Line 25: Old Dict usage throughout**
   - Parameter `-> Dict[K, T]` uses old syntax
   - Variable `result: Dict[K, T]` uses old syntax
   - Should be `dict[K, T]`

## Should NOT Flag (Correct Usage)

1. **Line 1: TypeVar, Generic, Protocol, override**
   - ✅ These MUST be imported from `typing` - they're not deprecated
   - These are legitimate typing constructs

2. **Line 2: Callable from collections.abc**
   - ✅ Correct import location

3. **Lines 4-6: TypeVar definitions**
   - ✅ Correct usage

4. **Line 8: Protocol class**
   - ✅ Correct usage

5. **Line 11: Generic[T] base class**
   - ✅ Correct usage

## Correct Version

```python
from typing import TypeVar, Generic, Protocol, override
from collections.abc import Callable

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Comparable(Protocol):
    def compare(self, other: 'Comparable') -> int: ...

class Repository(Generic[T]):
    def __init__(self, item_type: type[T]) -> None:
        self._item_type = item_type
        self._items: list[T] = []

    def add(self, item: T) -> None:
        self._items.append(item)

    def get_all(self) -> list[T]:
        return self._items

    def filter(self, predicate: Callable[[T], bool]) -> list[T]:
        return [item for item in self._items if predicate(item)]

    def map_to_dict(self, key_fn: Callable[[T], K]) -> dict[K, T]:
        result: dict[K, T] = {}
        for item in self._items:
            result[key_fn(item)] = item
        return result

class InMemoryRepository(Repository[T]):
    @override
    def add(self, item: T) -> None:
        print(f"Adding {item}")
        super().add(item)
```

## Critical Test

The skill MUST understand that:
- `TypeVar`, `Generic`, `Protocol`, `override` are NOT deprecated
- Only `List`, `Dict`, `Set`, `Tuple`, `Type` are deprecated
- This is a nuanced distinction that tests skill accuracy
