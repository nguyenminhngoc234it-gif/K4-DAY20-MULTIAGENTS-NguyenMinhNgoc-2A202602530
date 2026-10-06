---
name: enforce-type-annotations-on-public-functions
description: Use this skill when adding or modifying public functions to ensure all parameters and return values have type annotations.
---
1. Identify all public functions in the package (functions whose names do not start with an underscore).
2. For each public function, verify that every parameter has an explicit type annotation.
3. Verify that the function has a return type annotation.
4. If any annotation is missing, add the appropriate type hint based on the function’s logic and expected inputs/outputs.
5. Use consistent and standard typing syntax (e.g., built-in types, typing module generics).
6. Run a static type checker (e.g., mypy) if available to confirm no missing or incorrect annotations.
7. Review changes to ensure no private or internal functions are unnecessarily annotated if not required.
8. Commit changes only after all public functions are fully annotated.
