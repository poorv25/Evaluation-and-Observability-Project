import unittest

from policy_pipeline import route_request, run_routing_tests


class TestPolicyPipeline(unittest.TestCase):

    def test_mortgage_routing(self):
        self.assertEqual(
            route_request("Check mortgage borrower details"),
            "mortgage_extraction",
        )

    def test_supply_chain_routing(self):
        self.assertEqual(
            route_request("Investigate a shipment delay"),
            "supply_chain",
        )

    def test_policy_routing(self):
        self.assertEqual(
            route_request("Review compliance policy"),
            "policy_pipeline",
        )

    def test_empty_input(self):
        self.assertEqual(route_request(""), "clarification")

    def test_whitespace_input(self):
        self.assertEqual(route_request("   "), "clarification")

    def test_case_insensitivity(self):
        self.assertEqual(route_request("MORTGAGE"), "mortgage_extraction")

    def test_ambiguous_supply_chain_input(self):
        self.assertEqual(
            route_request("Review the policy for a delayed shipment"),
            "supply_chain",
        )

    def test_ambiguous_mortgage_input(self):
        self.assertEqual(
            route_request("Check mortgage policy compliance"),
            "mortgage_extraction",
        )

    def test_unknown_input(self):
        self.assertEqual(
            route_request("Tell me something interesting"),
            "clarification",
        )

    def test_evaluation_cases_pass(self):
        results = run_routing_tests()
        self.assertTrue(all(result["passed"] for result in results))


if __name__ == "__main__":
    unittest.main(verbosity=2)
