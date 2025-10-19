# Expected Behavior for Example 2

## Assertions

The skill MUST identify the following OCP violations:

### Primary Issues

1. **Lines 17-42**: `AreaCalculator.calculate_area()` method
   - if-elif chain checking `shape_type` string
   - Must be modified every time a new shape is added
   - Violates OCP: not closed for modification

2. **Lines 51-58**: `ShapeProcessor.process_shape()` method
   - isinstance() checks to determine behavior
   - Must be modified for new shape types
   - Violates OCP

### Impact Statement
- Should mention: adding new shapes requires modifying existing methods
- Should mention: risk of breaking existing functionality when adding features
- Should mention: not closed for modification

### Suggested Refactoring
- Use abstract base class with `calculate_area()` method
- Each shape implements its own area calculation
- Use Strategy pattern or polymorphism
- Consider using Protocol for structural subtyping

### Should NOT Flag
- Business logic conditionals (none in this example)
- Simple validation checks

## Success Criteria

✅ PASS if the skill:
- Identifies both type-checking patterns (string-based and isinstance-based)
- Explains why these require modification for new types
- Suggests polymorphism/inheritance/Protocol solution
- Distinguishes type-checking from business logic conditionals

❌ FAIL if the skill:
- Misses the OCP violations
- Flags business logic conditionals as OCP violations
- Doesn't suggest extensible alternative approaches
