"""Tests for the fixes made to pharmacy_system.py. Run: python -m unittest"""

import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import pharmacy_system as pharmacy


def in_days(days):
    """Return the ISO date that is the given number of days from today."""
    return (date.today() + timedelta(days=days)).isoformat()


class PharmacyTests(unittest.TestCase):
    """Reset shared state before each test."""

    def setUp(self):
        pharmacy.conn.execute("DROP TABLE IF EXISTS patients")
        pharmacy.setup_database()
        pharmacy.stock.clear()
        pharmacy.prescriptions.clear()

    def assert_refused(self, patient, drug, units=1):
        """Check a request is refused and changes no stored state."""
        stock_before = json.dumps(pharmacy.stock)
        self.assertFalse(pharmacy.dispense(patient, drug, units))
        self.assertEqual(json.dumps(pharmacy.stock), stock_before)
        self.assertEqual(pharmacy.prescriptions, [])

    # SQL injection
    def test_injection_input_finds_nobody(self):
        self.assertEqual(pharmacy.find_patient("' OR 1=1 --"), [])

    def test_name_with_apostrophe_is_safe(self):
        self.assertEqual(pharmacy.find_patient("O'Brien"), [])

    def test_exact_name_is_found(self):
        self.assertEqual(pharmacy.find_patient("Arjun"), [("P2", "none")])

    # Allergies
    def test_allergy_ignores_case(self):
        pharmacy.add_stock("Penicillin", 5, in_days(90))
        self.assert_refused("Kavya", "Penicillin")

    def test_allergy_catches_name_variants(self):
        for drug in ["Penicillin V", "Benzyl Penicillin", "PENICILLIN-G"]:
            pharmacy.add_stock(drug, 5, in_days(90))
            self.assert_refused("Kavya", drug)

    def test_allergy_does_not_block_shorter_name(self):
        pharmacy.add_stock("Pen", 5, in_days(90))
        self.assertTrue(pharmacy.dispense("Kavya", "Pen", 1))

    def test_none_marker_blocks_nothing(self):
        pharmacy.add_stock("Nonesuch", 5, in_days(90))
        self.assertTrue(pharmacy.dispense("Arjun", "Nonesuch", 1))

    # Dispensing
    def test_successful_dispense_updates_state(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(90))
        self.assertTrue(pharmacy.dispense("Arjun", "Paracetamol", 3))
        self.assertEqual(pharmacy.stock["Paracetamol"]["units"], 7)
        self.assertEqual(pharmacy.prescriptions[0]["patient"], "P2")

    def test_all_remaining_units_can_be_dispensed(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(90))
        self.assertTrue(pharmacy.dispense("Arjun", "Paracetamol", 10))
        self.assertEqual(pharmacy.stock["Paracetamol"]["units"], 0)

    def test_too_many_units_refused(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(90))
        self.assert_refused("Arjun", "Paracetamol", 11)

    def test_invalid_quantities_refused(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(90))
        for units in [0, -1, 1.5]:
            self.assert_refused("Arjun", "Paracetamol", units)

    def test_unknown_patient_refused(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(90))
        self.assert_refused("Ghost", "Paracetamol")

    def test_unknown_drug_refused(self):
        self.assert_refused("Arjun", "Unknown")

    def test_drug_name_ignores_case(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(90))
        self.assertTrue(pharmacy.dispense("Arjun", "PARACETAMOL", 1))
        self.assertEqual(pharmacy.stock["Paracetamol"]["units"], 9)

    # Expiry
    def test_expired_drug_refused(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(-1))
        self.assert_refused("Arjun", "Paracetamol")

    def test_drug_usable_on_expiry_day(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(0))
        self.assertTrue(pharmacy.dispense("Arjun", "Paracetamol", 1))

    def test_expiry_lists_use_correct_boundaries(self):
        for drug, days in [("Old", -1), ("Today", 0), ("Edge", 30),
                           ("Later", 31)]:
            pharmacy.add_stock(drug, 1, in_days(days))
        self.assertEqual(pharmacy.expiring_soon(), ["Today", "Edge"])
        self.assertEqual(pharmacy.expired_stock(), ["Old"])

    # Adding stock
    def test_invalid_units_rejected(self):
        for units in [-15, 0, 1.5]:
            with self.assertRaises(ValueError):
                pharmacy.add_stock("Ibuprofen", units, in_days(90))
        self.assertEqual(pharmacy.stock, {})

    def test_invalid_expiry_rejected(self):
        with self.assertRaises(ValueError):
            pharmacy.add_stock("Ibuprofen", 5, "not-a-date")
        self.assertEqual(pharmacy.stock, {})

    def test_restock_adds_units_and_keeps_earlier_expiry(self):
        pharmacy.add_stock("Paracetamol", 5, in_days(10))
        pharmacy.add_stock("paracetamol", 5, in_days(90))
        self.assertEqual(pharmacy.stock, {
            "Paracetamol": {"units": 10, "expiry": in_days(10)}
        })

    def test_default_batch_log_is_not_shared(self):
        self.assertEqual(pharmacy.add_stock("First", 1, in_days(90)), 1)
        self.assertEqual(pharmacy.add_stock("Second", 1, in_days(90)), 1)

    def test_batch_log_records_units_added_not_total(self):
        batch_log = []
        pharmacy.add_stock("Paracetamol", 5, in_days(90), batch_log)
        pharmacy.add_stock("Paracetamol", 3, in_days(90), batch_log)
        self.assertEqual(batch_log, [("Paracetamol", 5), ("Paracetamol", 3)])

    # Files
    def test_export_writes_prescriptions(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(90))
        pharmacy.dispense("Arjun", "Paracetamol", 1)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "out.json"
            pharmacy.export_prescriptions(path)
            saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved, pharmacy.prescriptions)

    def test_missing_stock_file_keeps_stock(self):
        pharmacy.add_stock("Paracetamol", 10, in_days(90))
        with tempfile.TemporaryDirectory() as folder:
            pharmacy.load_stock(Path(folder) / "missing.json")
        self.assertIn("Paracetamol", pharmacy.stock)

    def test_corrupt_stock_file_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                pharmacy.load_stock(path)

    def test_load_updates_the_same_stock_dictionary(self):
        original = pharmacy.stock
        data = {"Paracetamol": {"units": 2, "expiry": in_days(90)}}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "stock.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            pharmacy.load_stock(path)
        self.assertIs(pharmacy.stock, original)
        self.assertEqual(pharmacy.stock, data)


if __name__ == "__main__":
    unittest.main()
