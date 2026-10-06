"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when the task first requires inspecting README files, docstrings, "
                "sample data, or existing code to identify requirements and report facts "
                "without changing files."
            ),
            "system_prompt": (
                "You are an exploration specialist. Read the relevant instructions, code, "
                "and data carefully, then return a concise, evidence-based report to the main "
                "agent. Do not create, edit, or delete files. You see only the delegation "
                "message, so work strictly from the rules and paths it provides."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when a well-scoped change must be implemented in specified files and "
                "verified by running the supplied tests or scripts."
            ),
            "system_prompt": (
                "You are an implementation specialist. Follow every rule and file path in the "
                "delegation message, inspect the relevant files before editing, make only the "
                "requested changes, and run the stated tests or scripts. Return a concise report "
                "of files actually changed and verification results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use after implementation when the result needs an independent check against "
                "the task specification, tests, and likely edge cases."
            ),
            "system_prompt": (
                "You are an independent reviewer. Inspect the completed work against every rule "
                "in the delegation message, run relevant checks when useful, and report concrete "
                "defects or confirm the observed results. Do not modify any files."
            ),
        },
    ]
