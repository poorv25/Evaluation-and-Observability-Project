import unittest

from mortgage_extraction import (
    classify_mortgage_document,
    extract_mortgage_fields,
    process_mortgage_document,
    process_mortgage_document_with_retry,
    validate_monthly_income,
)


class TestMortgageExtraction(unittest.TestCase):

    def test_complete_document(self):
        document = (
            "Borrower: Alex Morgan\n"
            "Loan Amount: $250,000\n"
            "Property Address: 10 Oak Street\n"
        )

        result = extract_mortgage_fields(document)

        self.assertEqual(result["borrower_name"], "Alex Morgan")
        self.assertEqual(result["loan_amount"], 250000.0)
        self.assertEqual(result["property_address"], "10 Oak Street")

    def test_missing_property_address(self):
        document = "Borrower: Jamie Lee\n" "Loan Amount: $180,500\n"

        result = extract_mortgage_fields(document)

        self.assertEqual(result["borrower_name"], "Jamie Lee")
        self.assertEqual(result["loan_amount"], 180500.0)
        self.assertIsNone(result["property_address"])

    def test_empty_document(self):
        result = extract_mortgage_fields("")

        self.assertIsNone(result["borrower_name"])
        self.assertIsNone(result["loan_amount"])
        self.assertIsNone(result["property_address"])

    def test_case_insensitive_labels(self):
        document = (
            "borrower: Taylor Smith\n"
            "loan amount: $90,000\n"
            "property address: 25 Pine Road\n"
        )

        result = extract_mortgage_fields(document)

        self.assertEqual(result["borrower_name"], "Taylor Smith")
        self.assertEqual(result["loan_amount"], 90000.0)
        self.assertEqual(result["property_address"], "25 Pine Road")

    def test_rejects_negative_loan_amount(self):
        document = (
            "Borrower: Alex Morgan\n"
            "Loan Amount: $-250,000\n"
            "Property Address: 10 Oak Street\n"
        )

        result = extract_mortgage_fields(document)

        self.assertIsNone(result["loan_amount"])

    def test_rejects_malformed_loan_amount(self):
        document = (
            "Borrower: Alex Morgan\n"
            "Loan Amount: $abc\n"
            "Property Address: 10 Oak Street\n"
        )

        result = extract_mortgage_fields(document)

        self.assertIsNone(result["loan_amount"])

    def test_rejects_zero_loan_amount(self):
        document = (
            "Borrower: Alex Morgan\n"
            "Loan Amount: $0\n"
            "Property Address: 10 Oak Street\n"
        )

        result = extract_mortgage_fields(document)

        self.assertIsNone(result["loan_amount"])

    def test_monthly_income_total_is_consistent(self):
        income = {
            "salary_monthly": 5000.0,
            "rental_monthly": 1200.0,
            "reported_monthly_total": 6200.0,
        }

        result = validate_monthly_income(income)

        self.assertTrue(result["valid"])
        self.assertAlmostEqual(result["calculated_total"], 6200.0)

    def test_monthly_income_total_detects_mismatch(self):
        income = {
            "salary_monthly": 5000.0,
            "rental_monthly": 1200.0,
            "reported_monthly_total": 7000.0,
        }

        result = validate_monthly_income(income)

        self.assertFalse(result["valid"])
        self.assertAlmostEqual(result["calculated_total"], 6200.0)

    def test_monthly_income_allows_small_tolerance(self):
        income = {
            "salary_monthly": 5000.0,
            "reported_monthly_total": 5000.50,
        }

        result = validate_monthly_income(income, tolerance=1.0)

        self.assertTrue(result["valid"])

    def test_monthly_income_without_components(self):
        income = {"reported_monthly_total": 0.0}

        result = validate_monthly_income(income)

        self.assertIsNone(result["calculated_total"])
        self.assertFalse(result["valid"])

    def test_classifies_mortgage_document(self):
        document = (
            "Borrower: Alex Morgan\n"
            "Loan Amount: $250,000\n"
            "Property Address: 10 Oak Street\n"
        )

        result = classify_mortgage_document(document)

        self.assertEqual(result["document_type"], "mortgage")
        self.assertTrue(result["is_mortgage"])
        self.assertTrue(result["fields_detected"])

    def test_classifies_unrelated_document(self):
        result = classify_mortgage_document("This is an unrelated letter.")

        self.assertEqual(result["document_type"], "unknown")
        self.assertFalse(result["is_mortgage"])
        self.assertFalse(result["fields_detected"])

    def test_process_complete_mortgage_document(self):
        document = (
            "Borrower: Alex Morgan\n"
            "Loan Amount: $250,000\n"
            "Property Address: 10 Oak Street\n"
        )

        result = process_mortgage_document(document)

        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["extracted_fields"]["loan_amount"], 250000.0)
        self.assertEqual(result["missing_fields"], [])

    def test_process_incomplete_mortgage_document(self):
        document = "Borrower: Jamie Lee\nLoan Amount: $180,500\n"

        result = process_mortgage_document(document)

        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["missing_fields"], ["property_address"])

    def test_process_rejects_unrelated_document(self):
        result = process_mortgage_document("This is an unrelated letter.")

        self.assertEqual(result["status"], "rejected_non_mortgage")
        self.assertEqual(result["extracted_fields"], {})

    def test_retry_stops_when_document_is_complete(self):
        document = (
            "Borrower: Alex Morgan\n"
            "Loan Amount: $250,000\n"
            "Property Address: 10 Oak Street\n"
        )

        result = process_mortgage_document_with_retry(
            document,
            max_attempts=3,
        )

        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(len(result["attempt_history"]), 1)

    def test_retry_stops_at_max_attempts_for_incomplete_document(self):
        document = "Borrower: Jamie Lee\nLoan Amount: $180,500\n"

        result = process_mortgage_document_with_retry(
            document,
            max_attempts=3,
        )

        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["attempts"], 3)
        self.assertEqual(len(result["attempt_history"]), 3)
        self.assertEqual(
            result["attempt_history"][-1]["missing_fields"],
            ["property_address"],
        )

    def test_retry_rejects_invalid_attempt_limit(self):
        with self.assertRaises(ValueError):
            process_mortgage_document_with_retry(
                "Borrower: Alex Morgan",
                max_attempts=0,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
