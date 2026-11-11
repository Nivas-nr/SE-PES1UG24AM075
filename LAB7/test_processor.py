"""Lab 7 - Hypothesis fuzz tests for processor.py.

The first three tests are the starter tests, completed with try/except:
any exception means the function crashed on that input.
The others check that results are correct, not just crash-free, using
generated inputs that look almost valid so the fuzzer reaches deeper code.
Run:  python -m pytest test_processor.py
"""

import math

from hypothesis import given, strategies as st
from processor import (parse_walk_schedule, compute_pace_per_pet,
                       lookup_temperament_surcharge)

SURCHARGES = {"CAL": 0.0, "PLY": 5.0, "REA": 12.0, "AGG": 20.0}

# Inputs built from the expected formats plus junk, so most of them get
# past the first split and test the number and keyword handling.
NUMBERS = st.one_of(st.integers(-5, 600).map(str),
                    st.sampled_from(["", " ", "abc", "1.5", "nan", "inf",
                                     "-0", "1e3", "٣", "²", "9" * 5000]))
SCHEDULES = st.builds("{}-{}-{}".format, NUMBERS, NUMBERS,
                      st.sampled_from(["YES", "no", " Yes ", "MAYBE", ""]))
PACES = st.builds("{}/{}".format, NUMBERS, NUMBERS)


# ---- Starter tests: the functions must never crash ------------------------

@given(st.text() | st.none())
def test_parse_walk_schedule_no_crash(s):
    try:
        parse_walk_schedule(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_walk_schedule crashed on {s!r}: {e!r}"


@given(st.text() | st.none())
def test_compute_pace_per_pet_safe(s):
    try:
        compute_pace_per_pet(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"compute_pace_per_pet crashed on {s!r}: {e!r}"


@given(st.text() | st.none())
def test_lookup_temperament_surcharge_safe(s):
    try:
        lookup_temperament_surcharge(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"lookup_temperament_surcharge crashed on {s!r}: {e!r}"


# ---- Near-valid inputs: no crash, and invalid input gives None ------------

@given(SCHEDULES)
def test_parse_walk_schedule_near_valid_inputs(s):
    try:
        result = parse_walk_schedule(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_walk_schedule crashed on {s!r}: {e!r}"
    assert result is None or result.startswith("Walk: ")


@given(PACES)
def test_compute_pace_per_pet_near_valid_inputs(s):
    try:
        result = compute_pace_per_pet(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"compute_pace_per_pet crashed on {s!r}: {e!r}"
    # A pace must be a real, non-negative number of minutes.
    assert result is None or (math.isfinite(result) and result >= 0)


# ---- Valid inputs: the answer must be correct -----------------------------

@given(st.integers(1, 20), st.integers(1, 480), st.booleans())
def test_parse_walk_schedule_valid_total(pets, mins, weekend):
    spec = f"{pets}-{mins}-{'YES' if weekend else 'NO'}"
    total = (20.0 if mins <= 30 else 35.0) + pets * 5.0 + (15 if weekend else 0)
    expected = f"Walk: {pets} pets, {mins} mins - Total ${total:.2f}"
    assert parse_walk_schedule(spec) == expected


@given(st.integers(1, 20), st.integers(1, 20))
def test_parse_walk_schedule_rejects_non_positive_numbers(pets, mins):
    assert parse_walk_schedule(f"{-pets}-{mins}-YES") is None
    assert parse_walk_schedule(f"0-{mins}-YES") is None
    assert parse_walk_schedule(f"{pets}-0-NO") is None


@given(st.integers(1, 480), st.integers(1, 20))
def test_compute_pace_per_pet_valid(mins, pets):
    assert compute_pace_per_pet(f"{mins}/{pets}") == round(mins / pets, 2)


@given(st.sampled_from(list(SURCHARGES)), st.text(max_size=10),
       st.sampled_from(["", " ", "  "]))
def test_known_temperament_codes(prefix, rest, padding):
    code = padding + prefix.lower() + rest + padding
    assert lookup_temperament_surcharge(code) == SURCHARGES[prefix]


@given(st.text())
def test_surcharge_is_none_or_a_known_amount(s):
    try:
        result = lookup_temperament_surcharge(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"lookup_temperament_surcharge crashed on {s!r}: {e!r}"
    assert result is None or result in SURCHARGES.values()
