# Expected Behavior for Example 4

## Assertions

This is a **control test** - the code follows SOLID principles correctly.

### Expected Result

The skill should find **ZERO major violations** or **only very minor suggestions**.

### What Should NOT Be Flagged

1. **SRP**: Each class has a single responsibility
   - `Product`, `OrderItem`, `Order`: Data structures only
   - `StandardPriceCalculator`: Only calculates prices
   - `EmailNotificationService`: Only sends emails
   - `OrderService`: Only coordinates workflow

2. **OCP**: System is extensible without modification
   - Can add new `DiscountStrategy` subclasses
   - Can add new implementations of protocols
   - No type-checking conditionals

3. **LSP**: All implementations are substitutable
   - Any `DiscountStrategy` subclass works
   - Any protocol implementation works

4. **ISP**: Small, focused interfaces
   - `PriceCalculator`: One method
   - `NotificationService`: One method
   - No fat interfaces

5. **DIP**: Depends on abstractions
   - `OrderService` depends on protocols
   - Dependencies injected via constructor
   - Easy to test with mocks

### Acceptable Minor Suggestions

The skill MAY suggest (but these are NOT violations):
- Additional abstractions for future extensibility
- Alternative Protocol vs ABC choices
- Documentation improvements
- Type hint refinements

### Should NOT Suggest

- Breaking apart classes that have single responsibilities
- Adding abstractions where none are needed
- Changing the dependency injection pattern
- Modifying the protocol definitions

## Success Criteria

✅ PASS if the skill:
- Finds zero SOLID violations
- OR suggests only very minor, optional improvements
- Recognizes this as well-designed code
- Doesn't force unnecessary abstractions

❌ FAIL if the skill:
- Flags any major SOLID violations
- Suggests breaking apart single-responsibility classes
- Misidentifies business logic conditionals as OCP violations
- Suggests removing dependency injection
- Recommends changes that would make code worse
