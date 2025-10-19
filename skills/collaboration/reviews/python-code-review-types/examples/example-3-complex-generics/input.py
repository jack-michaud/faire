from typing import TypeVar, Generic, Protocol, List, Dict, Type, override
from collections.abc import Callable

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Comparable(Protocol):
    def compare(self, other: 'Comparable') -> int: ...

class Repository(Generic[T]):
    def __init__(self, item_type: Type[T]):
        self._item_type = item_type
        self._items: List[T] = []

    def add(self, item: T):
        self._items.append(item)

    def get_all(self) -> List[T]:
        return self._items

    def filter(self, predicate: Callable[[T], bool]) -> List[T]:
        return [item for item in self._items if predicate(item)]

    def map_to_dict(self, key_fn: Callable[[T], K]) -> Dict[K, T]:
        result: Dict[K, T] = {}
        for item in self._items:
            result[key_fn(item)] = item
        return result

class InMemoryRepository(Repository[T]):
    @override
    def add(self, item: T):
        print(f"Adding {item}")
        super().add(item)
