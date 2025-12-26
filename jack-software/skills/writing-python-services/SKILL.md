---
name: Writing python services
description: Writing a class with encapsulated logic that interfaces with an external system. Logging, APIs, etc.
---

- Use python 3.12+ syntax for types
  - e.g. `|` for unions, ` | None` for optional
  - Don't use `Optional`!

- No side effects in constructor
  - Use `@cached_property` and lazily evaluate properties needing IO. Only evaluate inside methods, not initializers.

- Methods use `dataclasses` for arguments and responses
  - Do not return a dict; if you need a dict, add a method on the dataclass to transform it into a dictionary.
