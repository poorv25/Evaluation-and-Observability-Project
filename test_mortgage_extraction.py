import unittest

from mortgage_extraction import extract_mortgage_fields


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
