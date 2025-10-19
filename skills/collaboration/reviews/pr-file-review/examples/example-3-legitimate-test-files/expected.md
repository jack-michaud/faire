# Expected Review Output

## Files Approved

### 1. tests/__snapshots__/test_renderer.snap
- **Initial suspicion**: "snap" file could be temporary output
- **Analysis**:
  - Located in __snapshots__/ directory (pytest-snapshot convention)
  - Referenced by test_renderer.py snapshot decorator
  - Part of snapshot testing infrastructure
- **Decision**: Approve (legitimate snapshot test data)

### 2. tests/integration/test_data_scenarios.csv
- **Initial suspicion**: CSV file could be test output
- **Analysis**:
  - Located in tests/integration (appropriate location)
  - Referenced in test_data_processor.py
  - Documented in tests/integration/README.md
  - Defines test scenarios (input, not output)
- **Decision**: Approve (legitimate test scenario data)

### 3. .github/workflows/test-results-template.md
- **Initial suspicion**: "test-results" suggests test artifact
- **Analysis**:
  - Located in .github/workflows (CI/CD infrastructure)
  - Referenced in ci.yml workflow
  - Template file, not actual results
  - Part of CI automation
- **Decision**: Approve (legitimate CI/CD template)

### 4. tests/e2e/outputs/.gitkeep
- **Initial suspicion**: Empty file could be unnecessary
- **Analysis**:
  - .gitkeep is a standard pattern to preserve empty directories
  - Referenced in tests/e2e/conftest.py
  - Documented in tests/e2e/README.md
  - Ensures outputs directory exists for test execution
- **Decision**: Approve (legitimate directory preservation)

### 5. tests/test_renderer.py
- Legitimate test file
- Approved

### 6. tests/integration/test_data_processor.py
- Legitimate integration test
- Approved

## Summary

**Flag for removal**: 0 files
**Approved**: 6 files (all are legitimate test infrastructure)

## Key Insights

This example demonstrates the importance of:
1. Understanding test framework conventions (snapshots, fixtures)
2. Recognizing CI/CD templates vs actual results
3. Knowing standard patterns (.gitkeep for directory preservation)
4. Checking documentation references
5. Distinguishing input data (scenarios) from output data (results)
6. Not flagging files just because they have "test" or "output" in the name

## Critical Test

This is the **hardest** example because it tests whether the skill can avoid false positives. All files look suspicious at first glance but are actually necessary. The skill must perform thorough analysis to avoid incorrectly flagging legitimate infrastructure.
