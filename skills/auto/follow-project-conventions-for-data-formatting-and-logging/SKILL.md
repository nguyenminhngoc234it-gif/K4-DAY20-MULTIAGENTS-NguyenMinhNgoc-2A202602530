---
name: follow-project-conventions-for-data-formatting-and-logging
description: Use this skill when producing output files or logs to ensure they conform to project-specific formatting, naming, and sorting rules.
---
1. Before writing output files (e.g., JSON, CSV), review the project’s formatting rules and naming conventions.
2. For monetary values, convert and store amounts as integer cents rather than floats or decimals.
3. Normalize categorical data fields (e.g., region names) to canonical forms with consistent capitalization and spelling.
4. Format timestamps in UTC using the exact required ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).
5. Remove duplicate data rows based on unique keys before analysis or output.
6. When parsing logs, convert all timestamps to UTC and format consistently.
7. Use lowercase service names with underscores instead of dashes in output data.
8. Sort output collections (e.g., error lists) by specified keys such as service name and timestamp ascending.
9. Include all required metadata fields in output files with accurate counts and source references.
10. Validate output files against schema or linting tools if available before submission.
11. When escaping CSV fields, follow RFC 4180 rules for quoting and doubling quotes.
12. Document any assumptions or transformations applied to input data in comments or metadata.
