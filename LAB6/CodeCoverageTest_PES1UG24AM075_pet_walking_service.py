"""Lab 6 - code (line) coverage tests for pet_walking_service.py.

Each test targets lines the starter test never runs.
Run:  coverage run -m pytest CodeCoverageTest_PES1UG24AM075_pet_walking_service.py
      coverage report -m
"""

import pytest

from pet_walking_service import process_walking_routes, inspect_gps_collars


def route(session_type, walks, confirmed=True, weekend=False):
    """Build one route dictionary in the format the service expects."""
    return {
        "route_confirmed": confirmed,
        "session_type": session_type,
        "is_weekend": weekend,
        "walks": walks,
    }


def walk(num_pets, aggression=False, meds=False):
    """Build one walk dictionary."""
    return {"num_pets": num_pets, "aggression_alert": aggression,
            "needs_meds": meds}


# Starter test, kept so the original line coverage is still counted.
def test_single_standard_30_walk():
    result = process_walking_routes([route("standard_30", [walk(1)])], 5.0)
    assert result == {"total_revenue": 27.0, "status": "COMPLETED"}


# Line 3: invalid input
def test_routes_that_are_not_a_list_raise_value_error():
    with pytest.raises(ValueError):
        process_walking_routes("not a list", 5.0)


# Line 10: unconfirmed routes are skipped
# Lines 21-23: unknown session type is an incident
# Line 58: nothing earned
def test_unconfirmed_and_unknown_routes_earn_nothing():
    routes = [
        route("standard_30", [walk(1)], confirmed=False),
        route("overnight", [walk(1)]),
    ]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


# Line 16: standard_60 fee; line 43: large-group discount;
# line 48: medication fee; line 51: weekend transport fee
def test_standard_60_large_group_with_meds_on_weekend():
    routes = [route("standard_60", [walk(4, meds=True)], weekend=True)]
    result = process_walking_routes(routes, 10.0)
    # (35 + 4 * 8) * 0.90 = 60.30, + 6 meds, + 10 weekend fee
    assert result == {"total_revenue": 76.3, "status": "COMPLETED"}


# Line 19: express_15 fee
def test_express_15_walk():
    result = process_walking_routes([route("express_15", [walk(2)])], 5.0)
    assert result == {"total_revenue": 24.0, "status": "COMPLETED"}


# Lines 37-40: aggression on a standard_60 route cancels the whole route
def test_aggression_on_standard_60_cancels_route_earnings():
    routes = [route("standard_60", [walk(1), walk(1, aggression=True)])]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


# Line 41: aggression on other routes only loses that walk's fee
def test_aggression_on_standard_30_skips_only_that_walk():
    routes = [route("standard_30", [walk(2, aggression=True), walk(1)])]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 27.0, "status": "COMPLETED"}


# Lines 33-34: walk with no pets; line 56: more than four incidents
def test_more_than_four_incidents_triggers_audit():
    routes = [route("standard_30", [walk(0)] * 5)]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 0.0, "status": "INCIDENT_AUDIT"}


# Lines 63-64: no collar data
def test_gps_no_data():
    assert inspect_gps_collars([]) == "NO_DATA"


# Lines 70-72: two weak signals in a row
def test_gps_two_weak_signals_in_a_row_raise_alert():
    assert inspect_gps_collars([[50, 10, 15]]) == "LOST_SIGNAL_ALERT"


# Line 74: a strong signal resets the streak; line 75: all online
def test_gps_weak_signals_separated_by_strong_ones_stay_online():
    assert inspect_gps_collars([[10, 50, 10, 50]]) == "ONLINE"
