import unittest

from mortgage_extraction import extract_mortgage_fields
from policy_pipeline import route_request
from supply_chain import investigate_supply_chain


class TestRobustness(unittest.TestCase):

    def test_policy_routing_ignores_case(self):
        self.assertEqual(route_request("MORTGAGE"), "mortgage_extraction")

    def test_policy_routing_handles_surrounding_spaces(self):
        self.assertEqual(route_request("   "), "clarification")

    def test_policy_routing_unknown_phrase(self):
        self.assertEqual(route_request("What is the weather?"), "clarification")

    def test_mortgage_missing_fields(self):
        result = extract_mortgage_fields("Borrower: Sam Lee")
        self.assertEqual(result["borrower_name"], "Sam Lee")
        self.assertIsNone(result["loan_amount"])
        self.assertIsNone(result["property_address"])

    def test_mortgage_reordered_fields(self):
        document = (
            "Property Address: 8 Lake Road\n"
            "Borrower: Sam Lee\n"
            "Loan Amount: $120,000\n"
        )
        result = extract_mortgage_fields(document)
        self.assertEqual(result["borrower_name"], "Sam Lee")
        self.assertEqual(result["loan_amount"], 120000.0)
        self.assertEqual(result["property_address"], "8 Lake Road")

    def test_supply_chain_missing_transit_time(self):
        result = investigate_supply_chain(
            {
                "shipment_id": "ROBUST-001",
                "expected_days": None,
                "actual_days": 6,
            }
        )
        self.assertIsNone(result["delay_days"])
        self.assertIn("Insufficient", result["finding"])

    def test_supply_chain_negative_transit_time(self):
        result = investigate_supply_chain(
            {
                "shipment_id": "ROBUST-002",
                "expected_days": 5,
                "actual_days": 3,
            }
        )
        self.assertEqual(result["delay_days"], -2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
