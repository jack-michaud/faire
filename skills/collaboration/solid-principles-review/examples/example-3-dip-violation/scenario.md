# Example 3: Dependency Inversion Principle Violation

## Scenario

Service class that directly instantiates concrete dependencies, making it impossible to test without real database and email service.

## Difficulty

Easy - Common real-world violation that directly impacts testability

## Test Objective

Verify the skill correctly identifies hard-coded dependencies and suggests dependency injection.
