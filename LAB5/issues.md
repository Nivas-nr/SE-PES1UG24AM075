# Lab 5: Static Code Analysis - Issues

- **Name:** Nivas Reddy Dandu
- **SRN:** PES1UG24AM075
- **Program:** Pharmacy Prescription & Stock Tracker (`pharmacy_system.py`)

Line numbers refer to the original starter file. Raw tool output is in
`reports/before/` and `reports/after/`.

## Results

| Check | Before | After |
|-------|--------|-------|
| Pylint | 6.90/10 (22 messages) | 10.00/10 |
| Bandit | 2 issues (1 medium, 1 low) | No issues |
| Flake8 | 15 findings | 0 findings |
| Unit tests | None | 26 passing |

## Issues found by the tools

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| SQL injection | Security: Bandit B608 (medium), Pylint C0209 | 21-22 | The patient name is formatted into the SQL. The input `' OR 1=1 --` returns all three patients and their allergies. | Pass the name as a `?` query parameter so it is treated as data. |
| Silent `except: pass` | Security: Bandit B110 (low), Pylint W0702, Flake8 E722 | 58-59 | Every stock loading failure is hidden, including a corrupt file. | Catch only `FileNotFoundError` and print a message. Other errors now reach the caller. |
| Mutable default argument | Bug: Pylint W0102 | 24 | `batch_log=[]` is one list shared by every call, so the returned count keeps growing. | Default to `None` and create a new list inside the function. |
| Bare `except` in `dispense` | Bug: Pylint W0702, Flake8 E722 | 38 | Hides all errors, including programming mistakes. | Replace it with explicit checks for an unknown patient and unknown drug. |
| Files not safely closed | Bug: Pylint R1732, W1514 | 50, 57 | Files can stay open after an error, and the encoding depends on the platform. | Use `with open(..., encoding="utf-8")`. |
| `global` reassignment | Quality: Pylint W0603 | 55, 57 | Replacing the global dictionary breaks other references to it. | Update the existing dictionary with `clear()` and `update()`. |
| Unused import | Quality: Pylint W0611, Flake8 F401 | 3 | `os` is never used. | Remove the import. |
| Function naming | Style: Pylint C0103 | 61 | `printStock` is not snake_case. | Rename to `print_stock`. |
| Missing docstrings | Style: Pylint C0114, C0116 | 1 and every function | The module and functions have no documentation. | Add docstrings. |
| Formatting | Style: Flake8 E302, E305, E501, Pylint C0301 | 11-66, 25, 36, 83 | Missing blank lines between functions and lines that are too long. | Add blank lines and wrap the long lines. |

## Bugs found by running the program (not flagged by any tool)

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Allergy check bypass | Patient safety | 32 | The check is case-sensitive and looks for the drug inside the allergy, so Kavya, who is allergic to penicillin, was given Penicillin. | Compare case-insensitively and warn when an allergy appears in the drug name, so "Penicillin V" is also caught. Ignore the `none` marker. |
| Dispensing more than is in stock | Logic | 35, 73 | Arjun received 30 Amoxicillin when only 20 existed, leaving -10 units. | Check availability first, and change nothing if the request is refused. |
| Expired stock dispensed | Patient safety | 35, 70 | Amoxicillin that expired on 2025-12-31 could still be dispensed. | Refuse a drug after its expiry date. It stays usable on the expiry day itself. |
| Negative quantities accepted | Logic | 25, 35, 72 | `add_stock` accepted -15 Ibuprofen, and a negative dispense would increase stock. | Require positive whole units. `add_stock` raises `ValueError`, and `dispense` refuses the request. |
| Expired drugs listed as "expiring soon" | Logic | 45 | Already expired drugs matched the check, and partial days were rounded away. | Compare calendar dates, and list expired drugs separately with `expired_stock()`. |
| Restock overwrites the expiry date | Logic | 25 | A later date could hide older units that expire sooner. | Keep the earlier of the two dates. |
| Drug names are case-sensitive in stock | Logic | 25, 35 | "ibuprofen" does not find the "Ibuprofen" entry. | Look up stock entries ignoring case. |
| Program runs on import | Testability | 83 | Importing the file starts the program and waits for input, so it cannot be tested. | Add an `if __name__ == "__main__":` guard. |

## Known limitation

The allergy check matches names only. It does not know drug families, so
Amoxicillin, which is a penicillin, is still not flagged for a penicillin
allergy. Fixing that would need drug class data that this program does not have.
