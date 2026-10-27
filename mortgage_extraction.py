import json
import re
from pathlib import Path

OUTPUT_DIR = Path("capstone-submission/02-mortgage-extraction")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Expected fields for a mortgage document.
REQUIRED_FIELDS = [
    "borrower_name",
    "loan_amount",
    "property_address",
]


def extract_mortgage_fields(document: str) -> dict:
    """Extract selected fields from a consistently formatted text document."""
    patterns = {
        "borrower_name": r"Borrower:\s*(.+)",
        "loan_amount": r"Loan Amount:\s*\$?([\d,]+(?:\.\d{2})?)",
        "property_address": r"Property Address:\s*(.+)",
    }

    extracted = {}

    for field, pattern in patterns.items():
        match = re.search(pattern, document, re.IGNORECASE)
        if match:
            value = match.group(1).strip()

            if field == "loan_amount":
                value = float(value.replace(",", ""))

            extracted[field] = value
        else:
            extracted[field] = None

    return extracted


def main():
    cases = [
        {
            "name": "complete_document",
            "document": (
                "Borrower: Alex Morgan\n"
                "Loan Amount: $250,000\n"
                "Property Address: 10 Oak Street\n"
            ),
            "expected": {
                "borrower_name": "Alex Morgan",
                "loan_amount": 250000.0,
                "property_address": "10 Oak Street",
            },
        },
        {
            "name": "missing_property_address",
            "document": ("Borrower: Jamie Lee\n" "Loan Amount: $180,500\n"),
            "expected": {
                "borrower_name": "Jamie Lee",
                "loan_amount": 180500.0,
                "property_address": None,
            },
        },
    ]

    results = []

    for case in cases:
        extracted = extract_mortgage_fields(case["document"])
        passed = extracted == case["expected"]

        results.append(
            {
                "case": case["name"],
                "expected": case["expected"],
                "extracted": extracted,
                "passed": passed,
            }
        )

    report = [
        "MORTGAGE EXTRACTION DOCUMENT RUNS",
        "=" * 34,
    ]

    for result in results:
        report.extend(
            [
                "",
                f"Case: {result['case']}",
                f"Expected: {json.dumps(result['expected'])}",
                f"Extracted: {json.dumps(result['extracted'])}",
                f"Result: {'PASS' if result['passed'] else 'FAIL'}",
            ]
        )

    passed_count = sum(result["passed"] for result in results)
    report.extend(
        [
            "",
            f"Passed: {passed_count}/{len(results)}",
        ]
    )

    (OUTPUT_DIR / "document-runs.txt").write_text(
        "\n".join(report) + "\n",
        encoding="utf-8",
    )

    (OUTPUT_DIR / "document_decisions.json").write_text(
        json.dumps(results, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\n".join(report))

    if passed_count != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
