# Example 1: Obvious Test Artifacts

**Difficulty**: Easy

**Description**: Pull request contains obvious test artifacts that should be flagged for removal.

**Test Goals**:
- Catch test result markdown files in root
- Flag temporary debug scripts
- Identify CSV test output files
- Flag scratch/temporary files

**Expected Outcome**: Skill should flag all 4 files as unnecessary and provide clear reasoning.
