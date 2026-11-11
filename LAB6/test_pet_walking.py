import pytest
from pet_walking_service import process_walking_routes, inspect_gps_collars

# Example test case:
def test_single_standard_30_walk():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_30",
            "is_weekend": False,
            "walks": [{"num_pets": 1, "aggression_alert": False, "needs_meds": False}]
        }
    ]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 27.0
    assert result["status"] == "COMPLETED"

# TODO: Add test cases to achieve 90-100% on both Line and Branch coverage!