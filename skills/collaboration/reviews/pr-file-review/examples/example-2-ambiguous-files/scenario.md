# Example 2: Ambiguous Test-Named Files

**Difficulty**: Medium

**Description**: Files with test-like names that require deeper analysis to determine necessity.

**Test Goals**:
- Correctly identify legitimate test configuration despite "test" in name
- Approve fixture data that's properly referenced
- Catch unreferenced test data even in appropriate locations
- Handle edge case of documented temporary file

**Expected Outcome**: Skill should approve referenced files and flag unreferenced ones, demonstrating context analysis.
