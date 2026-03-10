---
name: Python Code Style
description: Use when writing python code. Can be used for code review.
---

- Avoid None arguments where possible
  - If all usages of a function/method provide non-nullable values, make the arguments required.
  - Ignore test fixtures.

- Always type your arguments and return arguments. PLEASE. 
  - Even in tests and fixtures (`TypedDicts` are your friend!)
