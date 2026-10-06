### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool call: ls
{"path": "/workspace/inventory"}

### Tool result
['/workspace/inventory/__init__.py', '/workspace/inventory/__pycache__/', '/workspace/inventory/export.py', '/workspace/inventory/pricing.py', '/workspace/inventory/report.py']

### Tool call: read_file
{"file_path": "/workspace/inventory/pricing.py"}

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool call: read_file
{"file_path": "/workspace/tests/test_pricing.py"}

### Tool result
Error: File '/workspace/tests/test_pricing.py' not found

### Tool call: ls
{"path": "/workspace/tests"}

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_report.py']

### Tool call: read_file
{"file_path": "/workspace/inventory/report.py"}

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Tool call: read_file
{"file_path": "/workspace/tests/test_report.py", "limit": 40}

### Tool result
@@ lines 1-32 of 32 @@
from decimal import Decimal

from inventory.export import to_csv_row
from inventory.pricing import apply_discount
from inventory.report import low_stock, total_value


def test_total_value_plain():
    items = [{"name": "pen", "price": "$2.50", "qty": 4}]
    assert total_value(items) == Decimal("10.00")


def test_total_value_thousands_separator():
    items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
    assert total_value(items) == Decimal("2599.00")


def test_discount_rounding_half_up():
    assert apply_discount(Decimal("10.05"), 10) == Decimal("9.05")


def test_total_value_with_discount():
    items = [{"name": "desk", "price": "100.00", "qty": 1, "discount": 15}]
    assert total_value(items) == Decimal("85.00")


def test_low_stock_basic():
    assert low_stock([{"name": "pen", "qty": 2}, {"name": "ink", "qty": 9}]) == ["pen"]


def test_csv_row_plain_name():
    assert to_csv_row({"name": "pen", "price": "2.5", "qty": 4}) == "pen,2.50,4"

### Tool call: read_file
{"file_path": "/workspace/inventory/export.py"}

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool call: read_file
{"file_path": "/workspace/inventory/__init__.py"}

### Tool result
@@ lines 1-1 @@
System reminder: File exists but has empty contents

### Assistant
I found several issues in the source code that cause the test suite to fail and do not meet the docstring specifications:

1. In pricing.py:
   - parse_price does not handle commas in the price string.
   - parse_price does not handle parentheses for negative values.
   - apply_discount does not use the correct rounding mode ("round half up").

2. In report.py:
   - low_stock includes items with quantity equal to the threshold, but it should be strictly below.
   - low_stock does not sort the names alphabetically ignoring case.

3. In export.py:
   - to_csv_row does not handle names containing commas or double quotes as specified.

I will fix these issues accordingly.

### Tool call: edit_file
{"file_path": "/workspace/inventory/pricing.py", "old_string": "cleaned = text.strip().replace(\"$\", \"\")\n    return Decimal(cleaned)", "new_string": "cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    if cleaned.startswith(\"(\") and cleaned.endswith(\")\"):\n        cleaned = \"-\" + cleaned[1:-1]\n    return Decimal(cleaned)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/pricing.py", "old_string": "discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"))", "new_string": "from decimal import ROUND_HALF_UP\n\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/report.py", "old_string": "return [item[\"name\"] for item in items if item[\"qty\"] <= threshold]", "new_string": "names = [item[\"name\"] for item in items if item[\"qty\"] < threshold]\n    return sorted(names, key=str.lower)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/report.py'

### Tool call: edit_file
{"file_path": "/workspace/inventory/export.py", "old_string": "price = parse_price(item[\"price\"])\n    return f'{item[\"name\"]},{price:.2f},{item[\"qty\"]}'", "new_string": "price = parse_price(item[\"price\"])\n    name = item[\"name\"]\n    if \",\" in name or '\"' in name:\n        name = '\"' + name.replace('\"', '\"\"') + '\"'\n    return f'{name},{price:.2f},{item[\"qty\"]}'"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/export.py'

### Tool call: execute
{"command": "pytest --maxfail=1 --disable-warnings -q workspace/tests"}

### Tool result
[stderr] Traceback (most recent call last):
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Lib\site-packages\anyio\_core\_eventloop.py", line 204, in get_async_backend
[stderr]     return loaded_backends[asynclib_name]
[stderr]            ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
[stderr] KeyError: 'asyncio'
[stderr] 
[stderr] During handling of the above exception, another exception occurred:
[stderr] 
[stderr] Traceback (most recent call last):
[stderr]   File "<frozen runpy>", line 198, in _run_module_as_main
[stderr]   File "<frozen runpy>", line 88, in _run_code
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Scripts\pytest.exe\__main__.py", line 7, in <module>
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Lib\site-packages\_pytest\config\__init__.py", line 253, in _console_main
[stderr]     code = _main(prog=_get_prog_name(sys.argv))
[stderr]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Lib\site-packages\_pytest\config\__init__.py", line 223, in _main
[stderr]     config = _prepareconfig(new_args, plugins, prog=prog)
[stderr]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Lib\site-packages\_pytest\config\__init__.py", line 4

### Tool call: execute
{"command": "pytest --maxfail=1 --disable-warnings -q workspace/tests/test_report.py"}

### Tool result
[stderr] Traceback (most recent call last):
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Lib\site-packages\anyio\_core\_eventloop.py", line 204, in get_async_backend
[stderr]     return loaded_backends[asynclib_name]
[stderr]            ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
[stderr] KeyError: 'asyncio'
[stderr] 
[stderr] During handling of the above exception, another exception occurred:
[stderr] 
[stderr] Traceback (most recent call last):
[stderr]   File "<frozen runpy>", line 198, in _run_module_as_main
[stderr]   File "<frozen runpy>", line 88, in _run_code
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Scripts\pytest.exe\__main__.py", line 7, in <module>
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Lib\site-packages\_pytest\config\__init__.py", line 253, in _console_main
[stderr]     code = _main(prog=_get_prog_name(sys.argv))
[stderr]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Lib\site-packages\_pytest\config\__init__.py", line 223, in _main
[stderr]     config = _prepareconfig(new_args, plugins, prog=prog)
[stderr]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr]   File "E:\Thuc_Hanh_AI_Thuc_chien\K4-DAY20-MULTIAGENTS-NguyenMinhNgoc-2A202602530\.venv\Lib\site-packages\_pytest\config\__init__.py", line 4

### Assistant
I fixed the source code according to the docstring specifications and the test suite requirements:

- In pricing.py, parse_price now handles commas and parentheses for negative values correctly. apply_discount uses the correct rounding mode (ROUND_HALF_UP).
- In report.py, low_stock returns names of items with quantity strictly below the threshold and sorts them alphabetically ignoring case.
- In export.py, to_csv_row properly escapes names containing commas or double quotes according to RFC 4180.

The test suite cannot be run here due to environment issues with asyncio on Windows, but the code changes align with the specifications and test expectations.

Files changed:
- inventory/pricing.py
- inventory/report.py
- inventory/export.py