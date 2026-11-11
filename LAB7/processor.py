"""Pet walking schedule, pace and temperament helpers.

Every function returns None for invalid input instead of crashing.
"""

import math

MAX_PETS = 20        # assumed largest group one walker can take
MAX_MINUTES = 480    # assumed longest walk: 8 hours
WEEKEND_FEES = {"YES": 15.0, "NO": 0.0}
SURCHARGES = {"CAL": 0.0, "PLY": 5.0, "REA": 12.0, "AGG": 20.0}


def _whole_number(text, maximum):
    """Return text as an int from 1 to maximum, or None if it is not one.

    Only plain ASCII digits are accepted. int() alone would also accept
    signs, underscores and non-English digits, and very long strings make it
    raise ValueError.
    """
    text = text.strip()
    if not (text.isascii() and text.isdigit()) or len(text) > 4:
        return None
    value = int(text)
    return value if 1 <= value <= maximum else None


def parse_walk_schedule(schedule_spec):
    """Turn 'pets-minutes-YES/NO' into a price summary, or return None."""
    if not isinstance(schedule_spec, str):
        return None
    parts = schedule_spec.strip().split('-')
    if len(parts) != 3:
        return None
    pets = _whole_number(parts[0], MAX_PETS)
    mins = _whole_number(parts[1], MAX_MINUTES)
    weekend_fee = WEEKEND_FEES.get(parts[2].strip().upper())
    if pets is None or mins is None or weekend_fee is None:
        return None
    base_fee = 20.0 if mins <= 30 else 35.0
    total = base_fee + (pets * 5.0) + weekend_fee
    return f"Walk: {pets} pets, {mins} mins - Total ${total:.2f}"


def compute_pace_per_pet(walk_metrics_str):
    """Turn 'minutes/pets' into minutes per pet, or return None."""
    if not isinstance(walk_metrics_str, str):
        return None
    parts = walk_metrics_str.split('/')
    if len(parts) != 2:
        return None
    try:
        mins = float(parts[0])
    except ValueError:
        return None
    pets = _whole_number(parts[1], MAX_PETS)
    # Rejects nan, infinity, zero/negative minutes and impossible pet counts.
    if not math.isfinite(mins) or not 0 < mins <= MAX_MINUTES or pets is None:
        return None
    return round(mins / pets, 2)


def lookup_temperament_surcharge(temperament_code):
    """Return the surcharge for a temperament code, or None if unknown."""
    if not isinstance(temperament_code, str):
        return None
    prefix = temperament_code.strip().upper()[:3]
    return SURCHARGES.get(prefix)


def main():
    """Ask for one input per function and print the results."""
    print("==== Running parse_walk_schedule ====")
    s_input = input("Enter schedule (e.g. 2-30-YES): ")
    summary = parse_walk_schedule(s_input)
    print(summary if summary is not None else "Invalid schedule")

    print("\n==== Running compute_pace_per_pet ====")
    p_input = input("Enter minutes/pets (e.g. 45/3): ")
    pace = compute_pace_per_pet(p_input)
    if pace is None:
        print("Invalid minutes/pets")
    else:
        print("Pace (min/pet):", pace)

    print("\n==== Running lookup_temperament_surcharge ====")
    t_input = input("Enter temperament code (e.g. CALM, PLAYFUL, AGGRESSIVE): ")
    surcharge = lookup_temperament_surcharge(t_input)
    if surcharge is None:
        print("Unknown temperament code")
    else:
        print("Surcharge: $", surcharge)


if __name__ == "__main__":
    main()
