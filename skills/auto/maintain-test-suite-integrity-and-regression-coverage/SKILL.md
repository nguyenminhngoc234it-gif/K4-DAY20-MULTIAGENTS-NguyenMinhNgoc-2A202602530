---
name: maintain-test-suite-integrity-and-regression-coverage
description: Use this skill when fixing bugs or adding features to ensure tests are properly added without modifying existing test files.
---
1. Never modify existing test files under the tests/ directory; create new test files if additional tests are needed.
2. For each bug fix, add a dedicated regression test function in a designated regression test file (e.g., tests/test_regressions.py).
3. Ensure the regression test function clearly reproduces the bug scenario and asserts the correct fixed behavior.
4. Add at least one regression test per bug fix; if multiple bugs are fixed, add multiple tests.
5. Run the full test suite to verify no existing tests fail and all new tests pass.
6. Confirm that the regression test file itself passes without errors or warnings.
7. Avoid duplicating tests already covered by existing test files.
8. Document the purpose of each regression test clearly in the test function’s docstring or comments.
