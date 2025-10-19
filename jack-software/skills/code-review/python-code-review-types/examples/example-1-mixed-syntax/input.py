from typing import List, Dict, Optional
from collections.abc import Callable


class DataProcessor:
    def __init__(self, config: Dict[str, str]) -> None:
        self.config = config
        self._cache: dict[str, int] = {}

    def process_items(self, items: List[str]) -> list[dict[str, int]]:
        results = []
        for item in items:
            result = self._process_single(item)
            if result is not None:
                results.append(result)
        return results

    def _process_single(self, item: str) -> Optional[dict[str, int]]:
        if item in self._cache:
            return {"value": self._cache[item]}
        return None

    def register_callback(self, callback: Callable[[str], None]) -> None:
        self.callback = callback
