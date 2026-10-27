import unittest

from supply_chain import investigate_supply_chain


class TestSupplyChain(unittest.TestCase):

    def test_delayed_shipment(self):
        result = investigate_supply_chain(
            {
                "shipment_id": "SHIP-001",
                "expected_days": 5,
                "actual_days": 8,
                "supplier_status": "delayed",
            }
        )

        self.assertEqual(result["delay_days"], 3)
        self.assertIn("delayed by 3 day(s)", result["finding"])

    def test_on_time_shipment(self):
        result = investigate_supply_chain(
            {
                "shipment_id": "SHIP-002",
                "expected_days": 4,
                "actual_days": 4,
            }
        )

        self.assertEqual(result["delay_days"], 0)
        self.assertIn("No transit delay", result["finding"])

    def test_missing_expected_days(self):
        result = investigate_supply_chain(
            {
                "shipment_id": "SHIP-003",
                "expected_days": None,
                "actual_days": 7,
            }
        )

        self.assertIsNone(result["delay_days"])
        self.assertIn("Insufficient", result["finding"])

    def test_early_shipment(self):
        result = investigate_supply_chain(
            {
                "shipment_id": "SHIP-004",
                "expected_days": 6,
                "actual_days": 4,
            }
        )

        self.assertEqual(result["delay_days"], -2)
        self.assertIn("No transit delay", result["finding"])

    def test_evidence_is_recorded(self):
        result = investigate_supply_chain(
            {
                "shipment_id": "SHIP-005",
                "expected_days": 2,
                "actual_days": 3,
                "supplier_status": "awaiting confirmation",
            }
        )

        self.assertTrue(result["evidence"])
        self.assertIn("SHIP-005", result["evidence"][0])
        self.assertTrue(result["recommendation"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
