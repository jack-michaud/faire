# Expected Findings

The skill should identify:

1. **Line 1: Deprecated imports**
   - `List`, `Dict`, `Optional` should not be imported from `typing`
   - Should use built-in `list`, `dict`, and union syntax instead

2. **Line 5: Inconsistent Dict usage**
   - `config: Dict[str, str]` uses old syntax
   - Should be `config: dict[str, str]`

3. **Line 9: Inconsistent List usage**
   - `items: List[str]` uses old syntax
   - Should be `items: list[str]`

4. **Line 16: Inconsistent Optional usage**
   - `Optional[dict[str, int]]` mixes old Optional with new dict syntax
   - Should be `dict[str, int] | None`

5. **Line 21: Correct Callable import**
   - `Callable` from `collections.abc` is correct (not deprecated)
   - This should NOT be flagged

6. **Overall: Inconsistency warning**
   - Code mixes old and new syntax inconsistently
   - All should be migrated to Python 3.12+ syntax

## Correct Version

```python
from collections.abc import Callable

class DataProcessor:
    def __init__(self, config: dict[str, str]) -> None:
        self.config = config
        self._cache: dict[str, int] = {}

    def process_items(self, items: list[str]) -> list[dict[str, int]]:
        results: list[dict[str, int]] = []
        for item in items:
            result = self._process_single(item)
            if result is not None:
                results.append(result)
        return results

    def _process_single(self, item: str) -> dict[str, int] | None:
        if item in self._cache:
            return {"value": self._cache[item]}
        return None

    def register_callback(self, callback: Callable[[str], None]) -> None:
        self.callback = callback
```
