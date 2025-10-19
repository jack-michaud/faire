---
name: Systematic Debugging
description: A methodical approach to finding and fixing bugs through hypothesis testing. Use when encountering unexpected behavior, errors, or bugs in code.
---

# Systematic Debugging

## Overview

Systematic debugging is a scientific approach to finding bugs by forming hypotheses, testing them, and narrowing down the problem space. This prevents the common trap of random code changes and "debugging by coincidence."

## When to Use

- Code produces unexpected output
- Tests are failing
- Application crashes or throws errors
- Performance degrades unexpectedly
- Behavior differs across environments
- Integration between components fails

## The Debugging Cycle

### 1. REPRODUCE

Make the bug consistently repeatable.

**Steps**:
- Create a minimal test case that triggers the bug
- Document exact steps to reproduce
- Identify conditions required (data, environment, timing)
- Note what happens vs. what should happen

### 2. ISOLATE

Narrow down where the problem occurs.

**Strategies**:
- Binary search: Comment out half the code, test, repeat
- Add logging at key points to trace execution
- Use debugger breakpoints to inspect state
- Test components in isolation
- Check assumptions with assertions

### 3. HYPOTHESIZE

Form a testable theory about the cause.

**Questions to ask**:
- What changed recently?
- What assumptions might be wrong?
- What could cause this symptom?
- Are there edge cases not handled?
- Could it be a race condition or timing issue?

### 4. TEST

Verify or refute your hypothesis.

**Methods**:
- Add print statements or logging
- Use debugger to inspect variables
- Write a unit test that demonstrates the issue
- Modify code to test the hypothesis
- Check documentation for API misuse

### 5. FIX

Implement the solution.

**Approach**:
- Make minimal changes to fix the root cause
- Add tests to prevent regression
- Verify the fix doesn't break other functionality
- Document why the bug occurred

### 6. VERIFY

Ensure the bug is actually fixed.

**Checklist**:
- Original reproduction case no longer fails
- All existing tests still pass
- New tests cover the bug scenario
- No new issues introduced
- Works across relevant environments

## Process

1. **Reproduce the bug reliably**
2. **Gather information**: Error messages, logs, stack traces
3. **Form hypothesis** about the cause
4. **Test hypothesis** with minimal experiment
5. **If hypothesis wrong**, form new hypothesis and repeat
6. **If hypothesis correct**, implement fix
7. **Verify fix** solves the problem
8. **Add tests** to prevent regression

## Examples

### Example 1: Unexpected Null Value

**Problem**: Application crashes with "Cannot read property 'name' of null"

**Reproduce**:
```javascript
// Crashes when user has no profile
const userName = user.profile.name;
```

**Isolate**:
```javascript
console.log('user:', user);           // { id: 123, profile: null }
console.log('profile:', user.profile); // null
// Bug located: profile can be null
```

**Hypothesize**: Profile is optional and not all users have it

**Test**:
```javascript
// Check database
SELECT COUNT(*) FROM users WHERE profile_id IS NULL;
// Result: 342 users have no profile
```

**Fix**:
```javascript
const userName = user.profile?.name || 'Anonymous';
```

**Verify**:
```javascript
// Test with null profile
assert.equal(getUserName({ id: 1, profile: null }), 'Anonymous');
// Test with valid profile
assert.equal(getUserName({ id: 1, profile: { name: 'John' } }), 'John');
```

### Example 2: Test Failure After Refactoring

**Problem**: Tests started failing after refactoring a function

**Reproduce**:
```bash
$ npm test
FAIL  calculator.test.js
  ✕ test_divide_by_zero (5ms)
```

**Isolate**:
```javascript
// Old implementation
function divide(a, b) {
  if (b === 0) throw new Error('Division by zero');
  return a / b;
}

// New implementation (refactored)
function divide(a, b) {
  return a / b; // Missing zero check!
}
```

**Hypothesize**: Refactoring removed the zero-division check

**Test**:
```javascript
// Add logging
function divide(a, b) {
  console.log(`dividing ${a} by ${b}`);
  return a / b;
}
// Output: "dividing 10 by 0" → returns Infinity, should throw
```

**Fix**:
```javascript
function divide(a, b) {
  if (b === 0) throw new Error('Division by zero');
  return a / b;
}
```

**Verify**:
```bash
$ npm test
PASS  calculator.test.js
  ✓ test_divide_by_zero (2ms)
```

### Example 3: Race Condition

**Problem**: Intermittent failures in async test

**Reproduce**: Run test 100 times, fails ~20% of the time

**Isolate**:
```javascript
test('user data loads', async () => {
  loadUser(123);                    // Async, no await!
  const user = getUser(123);        // Runs before loadUser completes
  expect(user.name).toBe('John');   // Sometimes fails
});
```

**Hypothesize**: Test doesn't wait for async operation to complete

**Test**:
```javascript
test('user data loads', async () => {
  console.log('before load');
  loadUser(123);
  console.log('after load (but not completed)');
  const user = getUser(123);
  console.log('user:', user); // Sometimes undefined
});
```

**Fix**:
```javascript
test('user data loads', async () => {
  await loadUser(123);              // Wait for completion
  const user = getUser(123);
  expect(user.name).toBe('John');
});
```

**Verify**: Run test 1000 times, 100% success rate

## Debugging Tools and Techniques

### Logging

```javascript
console.log('Variable state:', { a, b, c });
console.trace('Call stack at this point');
console.time('operation');
// ... code ...
console.timeEnd('operation'); // Timing measurement
```

### Debugger

```javascript
debugger; // Breakpoint in code
```

Browser DevTools / IDE debugger:
- Set breakpoints
- Step through code
- Inspect variables
- Watch expressions
- View call stack

### Assertions

```javascript
console.assert(user !== null, 'User should not be null here');
```

### Binary Search Debugging

```bash
# Comment out half the code
# If bug persists, it's in the remaining half
# If bug disappears, it's in the commented half
# Repeat until isolated
```

### Git Bisect

```bash
git bisect start
git bisect bad           # Current commit has the bug
git bisect good abc123   # Known good commit
# Git checks out middle commit
# Test, then mark as good or bad
git bisect good|bad
# Repeat until bug-introducing commit found
```

## Anti-patterns

- ❌ **Don't**: Make random changes hoping to fix the bug
  - ✅ **Do**: Form hypothesis, test it, learn from result

- ❌ **Don't**: Debug by adding features or refactoring
  - ✅ **Do**: Make minimal changes to understand the problem

- ❌ **Don't**: Skip reproducing the bug
  - ✅ **Do**: Always create a reliable reproduction first

- ❌ **Don't**: Fix symptoms without finding root cause
  - ✅ **Do**: Ask "why" until you understand the underlying issue

- ❌ **Don't**: Assume you know what's wrong without testing
  - ✅ **Do**: Test your hypotheses with evidence

- ❌ **Don't**: Debug without version control safety
  - ✅ **Do**: Commit working code before debugging experiments

## Debugging Checklist

- [ ] Can you reproduce the bug reliably?
- [ ] Do you have the exact error message and stack trace?
- [ ] Have you checked recent changes (git log)?
- [ ] Have you isolated the minimal code that causes the issue?
- [ ] Have you formed a specific hypothesis?
- [ ] Have you tested your hypothesis?
- [ ] Have you found the root cause (not just symptoms)?
- [ ] Does your fix solve the problem without side effects?
- [ ] Have you added tests to prevent regression?

## Questions to Ask While Debugging

1. **What changed?** (code, data, environment, dependencies)
2. **What assumptions am I making?** (validate each one)
3. **What does the error message tell me?** (read it carefully)
4. **Where exactly does it fail?** (use debugger/logging)
5. **What's the data state at failure?** (inspect variables)
6. **Can I make a simpler test case?** (reduce complexity)
7. **Does it work in isolation?** (test individual components)
8. **What does the documentation say?** (check API usage)
9. **Has anyone else had this issue?** (search errors/issues)
10. **What would prove my hypothesis wrong?** (test counter-examples)

## Testing This Skill

To validate systematic debugging:

1. **Check**: Did you reproduce the bug before trying to fix it?
2. **Verify**: Did you form hypotheses rather than guessing?
3. **Confirm**: Did you test each hypothesis?
4. **Review**: Did you find the root cause, not just patch symptoms?
5. **Ensure**: Did you add tests to prevent the bug from returning?

## Related Skills

- `reading-stack-traces` - Understanding error messages
- `using-debuggers` - Debugger tools and techniques
- `writing-debug-logs` - Effective logging strategies
- `root-cause-analysis` - Finding underlying issues

---

**Remember**: Debugging is the scientific method applied to code. Form hypotheses, test them, learn from results, and iterate until you understand the problem completely.
