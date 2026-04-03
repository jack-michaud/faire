---
name: writing-python-services
description: "Python service class patterns for encapsulated logic interfacing with external systems. Use when writing new Python services, API clients, or classes that wrap logging, database access, or third-party integrations — enforces constructor purity, dataclass arguments, and modern type syntax."
---

# Writing Python Services

Guidelines for writing Python service classes that encapsulate logic interfacing with external systems (APIs, databases, logging, etc.).

## Type Conventions

- Use Python 3.12+ syntax for all type annotations
- Use `|` for unions instead of `Union[]`: `str | int`
- Use `| None` for optional types instead of `Optional[]`: `str | None`

## Constructor Rules

- **No side effects in `__init__`** — constructors must be pure and fast
- Use `@cached_property` for lazily evaluating properties that require IO (database connections, API clients, config fetches)

```python
from functools import cached_property

class PaymentService:
    def __init__(self, api_key: str, base_url: str) -> None:
        self._api_key = api_key
        self._base_url = base_url

    @cached_property
    def client(self) -> httpx.Client:
        return httpx.Client(base_url=self._base_url, headers={"Authorization": f"Bearer {self._api_key}"})
```

## Method Signatures

- Use `dataclasses` for method arguments and responses when a method takes or returns more than two related values

```python
from dataclasses import dataclass

@dataclass
class CreateOrderRequest:
    product_id: str
    quantity: int
    customer_email: str | None = None

@dataclass
class CreateOrderResponse:
    order_id: str
    status: str
    created_at: str

class OrderService:
    def create_order(self, request: CreateOrderRequest) -> CreateOrderResponse:
        ...
```
