import unittest

from policy_pipeline import (
    route_request,
    route_request_with_retry,
    run_routing_tests,
    validate_route,
)


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

    def test_conflicting_intents_require_clarification(self):
        self.assertEqual(
            route_request("Mortgage loan for a supplier shipment policy"),
            "clarification",
        )

    def test_policy_routing_requires_clear_intent(self):
        self.assertEqual(
            route_request("Please review this request"),
            "clarification",
        )

    def test_routing_result_is_always_a_valid_route(self):
        valid_routes = {
            "mortgage_extraction",
            "supply_chain",
            "policy_pipeline",
            "clarification",
        }

        inputs = [
            "",
            "Mortgage application",
            "Supplier shipment delay",
            "Compliance policy",
            "Unknown request",
            "MORTGAGE BORROWER",
            "Shipment shipment delay",
            "!!!",
        ]

        for text in inputs:
            with self.subTest(text=text):
                self.assertIn(route_request(text), valid_routes)

    def test_validate_route_accepts_valid_route(self):
        valid, feedback = validate_route("mortgage_extraction")
        self.assertTrue(valid)
        self.assertEqual(feedback, "Route is valid.")

    def test_validate_route_rejects_invalid_route(self):
        valid, feedback = validate_route("unknown_route")
        self.assertFalse(valid)
        self.assertIn("Unsupported route", feedback)

    def test_retry_rejects_invalid_attempt_limit(self):
        with self.assertRaises(ValueError):
            route_request_with_retry("Mortgage application", max_attempts=0)

        with self.assertRaises(TypeError):
            route_request_with_retry("Mortgage application", max_attempts="3")

    def test_retry_returns_valid_route_and_attempt_history(self):
        result = route_request_with_retry("Check mortgage borrower details")

        self.assertTrue(result["valid"])
        self.assertEqual(result["route"], "mortgage_extraction")
        self.assertGreaterEqual(result["attempts_used"], 1)
        self.assertLessEqual(result["attempts_used"], 3)
        self.assertTrue(result["attempt_history"])

    def test_punctuation_only_input_requires_clarification(self):
        self.assertEqual(route_request("!!! ???"), "clarification")

    def test_repeated_mortgage_keywords(self):
        self.assertEqual(
            route_request("Mortgage mortgage borrower"),
            "mortgage_extraction",
        )

    def test_mortgage_and_shipment_conflict(self):
        self.assertEqual(
            route_request("Review the mortgage loan and shipment delay"),
            "clarification",
        )

    def test_supply_chain_with_policy_context(self):
        self.assertEqual(
            route_request("Review policy for supplier delivery delay"),
            "supply_chain",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
