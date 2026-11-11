"""Lab 6 - branch coverage tests for pet_walking_service.py.

Every decision is tested in both directions, grouped by the line it is on.
coverage.py only checks that each if/loop goes both ways, so this file also
tests each half of compound conditions, boundary values and missing keys.
Run:  coverage run --branch -m pytest BranchCoverageTest_PES1UG24AM075_pet_walking_service.py
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


def completed(total):
    """Expected result for a normal billing run."""
    return {"total_revenue": total, "status": "COMPLETED"}


ZERO = {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


# ---- process_walking_routes ----------------------------------------------

# Line 2: not a list OR negative fee -> error; otherwise continue
@pytest.mark.parametrize("routes, fee", [
    ("not a list", 5.0),           # first condition true
    ([], -0.01),                   # first false, second true
    ({"walks": []}, 5.0),          # dict is not a list
])
def test_invalid_input_raises(routes, fee):
    with pytest.raises(ValueError):
        process_walking_routes(routes, fee)


def test_zero_transport_fee_is_allowed():
    routes = [route("standard_30", [], weekend=True)]
    assert process_walking_routes(routes, 0.0) == ZERO


# Line 8: no routes at all
def test_empty_route_list_earns_nothing():
    assert process_walking_routes([], 5.0) == ZERO


# Line 9: route not confirmed (False or key missing) -> skipped
def test_unconfirmed_routes_are_skipped():
    routes = [
        route("standard_30", [walk(1)], confirmed=False),
        {"session_type": "standard_30", "walks": [walk(1)]},
        route("overnight", [walk(1)], confirmed=False),  # no incident
    ]
    assert process_walking_routes(routes, 5.0) == ZERO


# Lines 15-21: each session type, the default type and an unknown type
@pytest.mark.parametrize("session_type, expected", [
    ("standard_60", 40.0),   # 35 + 1 pet * 5
    ("standard_30", 27.0),   # 22 + 5
    ("express_15", 19.0),    # 14 + 5
])
def test_session_type_base_fees(session_type, expected):
    routes = [route(session_type, [walk(1)])]
    assert process_walking_routes(routes, 5.0) == completed(expected)


def test_missing_session_type_defaults_to_standard_30():
    routes = [{"route_confirmed": True, "walks": [walk(1)]}]
    assert process_walking_routes(routes, 5.0) == completed(27.0)


def test_unknown_session_type_is_an_incident_and_skipped():
    routes = [route("overnight", [walk(1)])] * 5
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 0.0, "status": "INCIDENT_AUDIT"}


# Line 27: route with no walks (empty or key missing) only gets the
# weekend fee
def test_route_without_walks_earns_only_weekend_fee():
    routes = [
        route("standard_30", [], weekend=True),
        {"route_confirmed": True, "is_weekend": True},
    ]
    assert process_walking_routes(routes, 5.0) == completed(10.0)


# Line 32: zero, negative or missing pet count is an incident
@pytest.mark.parametrize("bad_walk", [walk(0), walk(-2), {}])
def test_walk_without_pets_is_an_incident(bad_walk):
    routes = [route("standard_30", [bad_walk] * 5)]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 0.0, "status": "INCIDENT_AUDIT"}


# Lines 36-41: aggression, on standard_60 and on other session types
def test_aggression_on_standard_60_cancels_route_and_later_walks():
    walks = [walk(1), walk(1, aggression=True), walk(2)]
    routes = [route("standard_60", walks)]
    assert process_walking_routes(routes, 5.0) == ZERO


def test_aggression_cancel_still_adds_weekend_fee():
    walks = [walk(1), walk(1, aggression=True)]
    routes = [route("standard_60", walks, weekend=True)]
    assert process_walking_routes(routes, 5.0) == completed(5.0)


@pytest.mark.parametrize("session_type", ["standard_30", "express_15"])
def test_aggression_on_shorter_walks_only_loses_that_walk(session_type):
    walks = [walk(2, aggression=True), walk(1)]
    expected = process_walking_routes([route(session_type, [walk(1)])], 0)
    result = process_walking_routes([route(session_type, walks)], 5.0)
    assert result == expected


# Line 42: more than three pets gets the discounted rate; exactly three
# does not
@pytest.mark.parametrize("pets, expected", [
    (3, 37.0),    # 22 + 3 * 5
    (4, 48.6),    # (22 + 4 * 8) * 0.90
])
def test_group_size_boundary(pets, expected):
    routes = [route("standard_30", [walk(pets)])]
    assert process_walking_routes(routes, 5.0) == completed(expected)


# Line 47: medication fee, including on an aggressive walk
@pytest.mark.parametrize("walk_data, expected", [
    (walk(1, meds=True), 33.0),                     # 27 + 6
    (walk(1, meds=False), 27.0),
    (walk(1, aggression=True, meds=True), 6.0),     # only the meds fee
])
def test_medication_fee(walk_data, expected):
    routes = [route("standard_30", [walk_data])]
    assert process_walking_routes(routes, 5.0) == completed(expected)


# Line 50: weekend fee applies only on weekends
@pytest.mark.parametrize("weekend, expected", [(True, 34.5), (False, 27.0)])
def test_weekend_fee(weekend, expected):
    routes = [route("standard_30", [walk(1)], weekend=weekend)]
    assert process_walking_routes(routes, 7.5) == completed(expected)


# Line 55: more than four incidents -> audit (exactly four is not enough)
def test_exactly_four_incidents_is_not_an_audit():
    routes = [route("standard_30", [walk(0)] * 4 + [walk(1)])]
    assert process_walking_routes(routes, 5.0) == completed(27.0)


def test_audit_keeps_revenue_earned():
    routes = [route("standard_30", [walk(0)] * 5 + [walk(1)])]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 27.0, "status": "INCIDENT_AUDIT"}


# Lines 57-59: zero earnings versus earnings, across several routes
def test_revenue_is_summed_and_rounded_across_routes():
    routes = [
        route("standard_30", [walk(4)]),                 # 48.6
        route("express_15", [walk(1)], weekend=True),    # 19 + 2.25
    ]
    assert process_walking_routes(routes, 2.25) == completed(69.85)


# ---- inspect_gps_collars -------------------------------------------------

# Line 63: no data at all
@pytest.mark.parametrize("matrix", [[], None])
def test_no_collar_data(matrix):
    assert inspect_gps_collars(matrix) == "NO_DATA"


# Lines 66-75: signal strength, streaks and multiple collars
@pytest.mark.parametrize("matrix, expected", [
    ([[20, 20, 20]], "ONLINE"),                 # 20 is not weak
    ([[19, 19]], "LOST_SIGNAL_ALERT"),          # 19 is weak
    ([[50, 10, 50, 10]], "ONLINE"),             # streak resets
    ([[50, 60], [70, 10, 5]], "LOST_SIGNAL_ALERT"),  # second collar
    ([[50, 10], [10, 50]], "ONLINE"),           # streak is per collar
    ([[]], "ONLINE"),                           # collar with no logs
    ([[10]], "ONLINE"),                         # one weak signal only
])
def test_gps_signal_patterns(matrix, expected):
    assert inspect_gps_collars(matrix) == expected
