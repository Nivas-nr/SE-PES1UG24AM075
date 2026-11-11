def process_walking_routes(routes, base_transport_fee):
    if not isinstance(routes, list) or base_transport_fee < 0:
        raise ValueError("Invalid routes list or transport fee")

    total_revenue = 0.0
    incident_count = 0

    for route in routes:
        if not route.get("route_confirmed", False):
            continue

        session_type = route.get("session_type", "standard_30")
        walks = route.get("walks", [])

        if session_type == "standard_60":
            base_fee = 35.0
        elif session_type == "standard_30":
            base_fee = 22.0
        elif session_type == "express_15":
            base_fee = 14.0
        else:
            incident_count += 1
            continue

        route_earnings = 0.0

        for walk in walks:
            num_pets = walk.get("num_pets", 0)
            aggression_alert = walk.get("aggression_alert", False)
            needs_medication = walk.get("needs_meds", False)

            if num_pets <= 0:
                incident_count += 1
                continue

            if aggression_alert:
                incident_count += 1
                if session_type == "standard_60":
                    route_earnings = 0.0
                    break
                route_earnings += 0.0
            elif num_pets > 3:
                route_earnings += (base_fee + (num_pets * 8.0)) * 0.90
            else:
                route_earnings += base_fee + (num_pets * 5.0)

            if needs_medication:
                route_earnings += 6.0

        if route.get("is_weekend", False):
            route_earnings += base_transport_fee

        total_revenue += route_earnings

    if incident_count > 4:
        return {"total_revenue": round(total_revenue, 2), "status": "INCIDENT_AUDIT"}
    if total_revenue == 0.0:
        return {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}
    return {"total_revenue": round(total_revenue, 2), "status": "COMPLETED"}


def inspect_gps_collars(collar_matrix):
    if not collar_matrix:
        return "NO_DATA"

    for collar_logs in collar_matrix:
        signal_lost_streak = 0
        for signal_strength in collar_logs:
            if signal_strength < 20:
                signal_lost_streak += 1
                if signal_lost_streak >= 2:
                    return "LOST_SIGNAL_ALERT"
            else:
                signal_lost_streak = 0
    return "ONLINE"