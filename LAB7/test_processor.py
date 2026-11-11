from hypothesis import given, strategies as st
from processor import parse_walk_schedule, compute_pace_per_pet, lookup_temperament_surcharge

@given(st.text() | st.none())
def test_parse_walk_schedule_no_crash(s):
    # To-Do:Using try and except complete this function.
    pass

@given(st.text() | st.none())
def test_compute_pace_per_pet_safe(s):
    # To-Do:Using try and except complete this function.
    pass

@given(st.text() | st.none())
def test_lookup_temperament_surcharge_safe(s):
    # To-Do:Using try and except complete this function.
    pass