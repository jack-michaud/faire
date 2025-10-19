# Expected Behavior for Example 3

## Assertions

The skill MUST identify the following DIP violations:

### Primary Issues

1. **Lines 10-13**: `UserService.__init__()` method
   - Hard-coded `sqlite3.connect()` instantiation
   - Hard-coded `smtplib.SMTP()` instantiation
   - High-level service depends directly on low-level implementations
   - Violates DIP

2. **Lines 16-40**: `register_user()` method
   - Cannot test without real database connection
   - Cannot test without real SMTP server
   - Business logic tightly coupled to infrastructure

3. **Lines 56-59**: `OrderService.__init__()` method
   - Same pattern: hard-coded database and email dependencies
   - Violates DIP

4. **Lines 61-83**: `create_order()` method
   - Cannot test in isolation
   - Mixed business logic with database queries

### Impact Statement
- Should mention: impossible to write unit tests without real database and email server
- Should mention: cannot swap implementations (e.g., from SQLite to PostgreSQL)
- Should mention: high-level business logic coupled to low-level infrastructure

### Suggested Refactoring
- Introduce repository abstraction (e.g., `UserRepository` protocol or ABC)
- Introduce email service abstraction (e.g., `EmailService` protocol or ABC)
- Use constructor injection to pass dependencies
- Suggest Protocol or ABC for abstractions
- Show example of injected dependencies

### Should NOT Flag
- The `_hash_password` method (this is properly separated)
- Business logic conditionals (email validation, etc.)

## Success Criteria

✅ PASS if the skill:
- Identifies hard-coded dependencies in `__init__` methods
- Explains testability impact clearly
- Suggests repository pattern or similar abstraction
- Recommends dependency injection via constructor
- Mentions both UserService and OrderService violations

❌ FAIL if the skill:
- Misses the DIP violations
- Doesn't explain testability problems
- Fails to suggest constructor injection
- Focuses on other issues instead of DIP
