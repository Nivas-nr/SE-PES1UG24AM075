"""Track pharmacy stock, patient allergies and dispensed prescriptions."""

import json
import sqlite3
from datetime import date, datetime

# Global state
conn = sqlite3.connect(":memory:")
stock = {}
prescriptions = []


def setup_database():
    """Create the patients table and fill it with sample patients."""
    cur = conn.cursor()
    cur.execute("CREATE TABLE patients (id TEXT, name TEXT, allergy TEXT)")
    cur.execute("INSERT INTO patients VALUES ('P1', 'Kavya', 'penicillin')")
    cur.execute("INSERT INTO patients VALUES ('P2', 'Arjun', 'none')")
    cur.execute("INSERT INTO patients VALUES ('P3', 'Meena', 'ibuprofen')")
    conn.commit()


def find_patient(name):
    """Return (id, allergy) rows for patients with exactly this name."""
    cur = conn.cursor()
    query = "SELECT id, allergy FROM patients WHERE name = ?"
    return cur.execute(query, (name,)).fetchall()


def _parse_expiry(expiry):
    """Convert a YYYY-MM-DD string to a date, raising ValueError if invalid."""
    return datetime.strptime(expiry, "%Y-%m-%d").date()


def _is_positive_whole(units):
    """Return whether units is a whole number greater than zero."""
    return isinstance(units, int) and units > 0


def _stock_key(drug):
    """Return the stock entry's name for a drug, ignoring case, or None."""
    for name in stock:
        if name.casefold() == drug.casefold():
            return name
    return None


def add_stock(drug, units, expiry, batch_log=None):
    """Add units of a drug and return the number of entries in batch_log.

    A restock keeps the earlier expiry date, so older units are never hidden
    behind a later date. Raises ValueError for invalid units or dates.
    """
    if not _is_positive_whole(units):
        raise ValueError(f"Units must be a positive whole number: {units}")
    earliest = _parse_expiry(expiry)
    if batch_log is None:
        batch_log = []
    key = _stock_key(drug) or drug
    total = units
    if key in stock:
        earliest = min(earliest, _parse_expiry(stock[key]["expiry"]))
        total += stock[key]["units"]
    stock[key] = {"units": total, "expiry": earliest.isoformat()}
    batch_log.append((key, units))
    return len(batch_log)


def _has_allergy(allergy_field, drug):
    """Return whether any listed allergy appears in the drug's name.

    Partial matches count, so "Penicillin V" matches a penicillin allergy:
    for a safety check a false warning is better than a missed one.
    """
    drug_name = drug.casefold()
    for allergy in allergy_field.split(","):
        allergy = allergy.strip().casefold()
        if allergy not in ("", "none") and allergy in drug_name:
            return True
    return False


def _stock_problem(key, units):
    """Return why units of a stock entry cannot be dispensed, or None."""
    if key is None:
        return "not in stock"
    if not _is_positive_whole(units):
        return f"invalid quantity {units}"
    if _parse_expiry(stock[key]["expiry"]) < date.today():
        return f"expired on {stock[key]['expiry']}"
    if units > stock[key]["units"]:
        return f"only {stock[key]['units']} units available"
    return None


def dispense(patient_name, drug, units):
    """Dispense a drug to a patient and return whether it succeeded.

    A refused request leaves stock and prescriptions unchanged.
    """
    patients = find_patient(patient_name)
    if not patients:
        print("Unknown patient:", patient_name)
        return False
    patient_id, allergy = patients[0]
    if _has_allergy(allergy, drug):
        print("Allergy warning for", patient_name)
        return False
    key = _stock_key(drug)
    problem = _stock_problem(key, units)
    if problem:
        print(f"Cannot dispense {drug}: {problem}")
        return False
    stock[key]["units"] -= units
    prescriptions.append({
        "patient": patient_id,
        "drug": key,
        "units": units,
        "time": str(datetime.now()),
    })
    return True


def _days_left(item):
    """Return the whole calendar days until a stock item expires."""
    return (_parse_expiry(item["expiry"]) - date.today()).days


def expiring_soon(days=30):
    """Return unexpired drugs that expire within the given number of days."""
    return [drug for drug, item in stock.items()
            if 0 <= _days_left(item) <= days]


def expired_stock():
    """Return the drugs whose expiry date has already passed."""
    return [drug for drug, item in stock.items() if _days_left(item) < 0]


def export_prescriptions(file="prescriptions.json"):
    """Write all dispensed prescriptions to a JSON file."""
    with open(file, "w", encoding="utf-8") as output:
        json.dump(prescriptions, output)


def load_stock(file="stock.json"):
    """Replace the current stock with a JSON file's contents, if it exists."""
    try:
        with open(file, encoding="utf-8") as source:
            loaded = json.load(source)
    except FileNotFoundError:
        print("No stock file found at", file)
        return
    stock.clear()
    stock.update(loaded)


def print_stock():
    """Print every drug with its units and expiry date."""
    print("Pharmacy Stock")
    for drug, item in stock.items():
        print(drug, "->", item["units"], "units, expires", item["expiry"])


def main():
    """Run a short demonstration of the stock and dispensing features."""
    setup_database()
    load_stock()
    add_stock("Paracetamol", 100, "2027-03-01")
    add_stock("Amoxicillin", 20, "2025-12-31")
    add_stock("Penicillin", 50, "2027-01-15")
    try:
        add_stock("Ibuprofen", -15, "2026-11-30")
    except ValueError as error:
        print("Stock rejected:", error)
    add_stock("Ibuprofen", 15, "2026-11-30")
    print("Arjun gets Amoxicillin:", dispense("Arjun", "Amoxicillin", 30))
    print("Kavya gets Penicillin:", dispense("Kavya", "Penicillin", 10))
    print("Meena gets ibuprofen:", dispense("Meena", "ibuprofen", 2))
    print("Unknown patient:", dispense("Ghost", "Paracetamol", 5))
    print("Arjun gets Paracetamol:", dispense("Arjun", "Paracetamol", 5))
    name = input("Patient name to look up (Enter for Arjun): ") or "Arjun"
    print("Lookup result:", find_patient(name))
    print("Expiring within 30 days:", expiring_soon())
    print("Already expired:", expired_stock())
    export_prescriptions()
    print_stock()


if __name__ == "__main__":
    main()
