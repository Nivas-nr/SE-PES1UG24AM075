import json
import sqlite3
import os
from datetime import datetime

# Global state
conn = sqlite3.connect(":memory:")
stock = {}
prescriptions = []

def setup_database():
    cur = conn.cursor()
    cur.execute("CREATE TABLE patients (id TEXT, name TEXT, allergy TEXT)")
    cur.execute("INSERT INTO patients VALUES ('P1', 'Kavya', 'penicillin')")
    cur.execute("INSERT INTO patients VALUES ('P2', 'Arjun', 'none')")
    cur.execute("INSERT INTO patients VALUES ('P3', 'Meena', 'ibuprofen')")
    conn.commit()

def find_patient(name):
    cur = conn.cursor()
    query = "SELECT id, allergy FROM patients WHERE name = '%s'" % name
    return cur.execute(query).fetchall()

def add_stock(drug, units, expiry, batch_log=[]):
    stock[drug] = {"units": stock.get(drug, {}).get("units", 0) + units, "expiry": expiry}
    batch_log.append((drug, units))
    return len(batch_log)

def dispense(patient_name, drug, units):
    try:
        patient = find_patient(patient_name)[0]
        if drug in patient[1]:
            print("Allergy warning for", patient_name)
            return False
        stock[drug]["units"] -= units
        prescriptions.append({"patient": patient[0], "drug": drug, "units": units, "time": str(datetime.now())})
        return True
    except:
        return False

def expiring_soon(days=30):
    soon = []
    for d in stock:
        exp = datetime.strptime(stock[d]["expiry"], "%Y-%m-%d")
        if (exp - datetime.now()).days < days:
            soon.append(d)
    return soon

def export_prescriptions(file="prescriptions.json"):
    f = open(file, "w")
    f.write(json.dumps(prescriptions))
    f.close()

def load_stock(file="stock.json"):
    global stock
    try:
        stock = json.load(open(file))
    except:
        pass

def printStock():
    print("Pharmacy Stock")
    for d in stock:
        print(d, "->", stock[d]["units"], "units, expires", stock[d]["expiry"])

def main():
    setup_database()
    load_stock()
    add_stock("Paracetamol", 100, "2027-03-01")
    add_stock("Amoxicillin", 20, "2025-12-31")
    add_stock("Penicillin", 50, "2027-01-15")
    add_stock("Ibuprofen", -15, "2026-11-30")
    print("Arjun gets Amoxicillin:", dispense("Arjun", "Amoxicillin", 30))
    print("Kavya gets Penicillin:", dispense("Kavya", "Penicillin", 10))
    print("Meena gets ibuprofen:", dispense("Meena", "ibuprofen", 2))
    print("Unknown patient:", dispense("Ghost", "Paracetamol", 5))
    name = input("Patient name to look up (Enter for Arjun): ") or "Arjun"
    print("Lookup result:", find_patient(name))
    print("Expiring within 30 days:", expiring_soon())
    export_prescriptions()
    printStock()

main()
