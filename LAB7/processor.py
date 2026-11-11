def parse_walk_schedule(schedule_spec):
    pets_str, mins_str, weekend_str = schedule_spec.strip().split('-')
    pets = int(pets_str)
    mins = int(mins_str)
    weekend_map = {"YES": 15.0, "NO": 0.0}
    weekend_fee = weekend_map[weekend_str.strip().upper()]
    base_fee = 20.0 if mins <= 30 else 35.0
    total = base_fee + (pets * 5.0) + weekend_fee
    return f"Walk: {pets} pets, {mins} mins - Total ${total:.2f}"

def compute_pace_per_pet(walk_metrics_str):
    mins_str, pets_str = walk_metrics_str.split('/')
    mins = float(mins_str)
    pets = float(pets_str)
    pace = mins / pets
    return round(pace, 2)

def lookup_temperament_surcharge(temperament_code):
    prefix = temperament_code.strip().upper()[:3]
    surcharges = {
        "CAL": 0.0,
        "PLY": 5.0,
        "REA": 12.0,
        "AGG": 20.0
    }
    return surcharges[prefix]

def main():
    print("==== Running parse_walk_schedule ====")
    s_input = input("Enter schedule (e.g. 2-30-YES): ")
    print(parse_walk_schedule(s_input))

    print("\n==== Running compute_pace_per_pet ====")
    p_input = input("Enter minutes/pets (e.g. 45/3): ")
    print("Pace (min/pet):", compute_pace_per_pet(p_input))

    print("\n==== Running lookup_temperament_surcharge ====")
    t_input = input("Enter temperament code (e.g. CALM, PLAYFUL, AGGRESSIVE): ")
    print("Surcharge: $", lookup_temperament_surcharge(t_input))

if __name__ == "__main__":
    main()