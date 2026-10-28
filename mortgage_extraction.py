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


def classify_mortgage_document(document: str) -> dict[str, str | bool]:
    """Classify a document before attempting field extraction."""
    labels = {
        "borrower_name": r"Borrower\s*:",
        "loan_amount": r"Loan Amount\s*:",
        "property_address": r"Property Address\s*:",
    }

    found_fields = [
        field
        for field, pattern in labels.items()
        if re.search(pattern, document, re.IGNORECASE)
    ]

    is_mortgage = bool(found_fields) and (
        "loan_amount" in found_fields or "borrower_name" in found_fields
    )

    return {
        "document_type": "mortgage" if is_mortgage else "unknown",
        "is_mortgage": is_mortgage,
        "fields_detected": len(found_fields) > 0,
    }


def extract_mortgage_fields(document: str) -> dict:
    """Extract mortgage fields and reject invalid loan amounts."""
    patterns = {
        "borrower_name": r"Borrower:\s*(.+)",
        "loan_amount": r"Loan Amount:\s*\$?([\d,]+(?:\.\d{2})?)",
        "property_address": r"Property Address:\s*(.+)",
    }

    extracted: dict[str, str | float | None] = {}

    for field, pattern in patterns.items():
        match = re.search(pattern, document, re.IGNORECASE)

        if not match:
            extracted[field] = None
            continue

        value = match.group(1).strip()

        if field == "loan_amount":
            try:
                amount = float(value.replace(",", ""))
            except ValueError:
                extracted[field] = None
                continue

            extracted[field] = amount if amount > 0 else None
        else:
            extracted[field] = value or None

    return extracted


def validate_monthly_income(
    income: dict[str, float],
    tolerance: float = 1.0,
) -> dict[str, float | bool | None]:
    """Check whether reported monthly income matches its components."""
    components = [
        value
        for key, value in income.items()
        if key.endswith("_monthly") and key != "reported_monthly_total"
    ]

    if not components:
        return {
            "calculated_total": None,
            "valid": False,
        }

    calculated_total = sum(components)
    reported_total = income.get("reported_monthly_total")

    valid = (
        isinstance(reported_total, (int, float))
        and abs(calculated_total - reported_total) <= tolerance
    )

    return {
        "calculated_total": calculated_total,
        "valid": valid,
    }


def process_mortgage_document(document: str) -> dict:
    """Classify a document, then extract and validate its fields."""
    classification = classify_mortgage_document(document)

    if not classification["is_mortgage"]:
        return {
            "classification": classification,
            "extracted_fields": {},
            "missing_fields": REQUIRED_FIELDS.copy(),
            "status": "rejected_non_mortgage",
        }

    extracted = extract_mortgage_fields(document)

    missing_fields = [
        field for field in REQUIRED_FIELDS if extracted.get(field) is None
    ]

    status = "complete" if not missing_fields else "incomplete"

    return {
        "classification": classification,
        "extracted_fields": extracted,
        "missing_fields": missing_fields,
        "status": status,
    }


def process_mortgage_document_with_retry(
    document: str,
    max_attempts: int = 3,
) -> dict:
    """Retry validation up to a limit and record feedback for each attempt."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    attempt_history = []
    result = {}

    for attempt in range(1, max_attempts + 1):
        result = process_mortgage_document(document)

        attempt_record = {
            "attempt": attempt,
            "status": result["status"],
            "missing_fields": result["missing_fields"],
            "validation_feedback": (
                "All required fields are present."
                if result["status"] == "complete"
                else (
                    "Document is not recognized as a mortgage document."
                    if result["status"] == "rejected_non_mortgage"
                    else "Missing required fields: "
                    + ", ".join(result["missing_fields"])
                )
            ),
        }
        attempt_history.append(attempt_record)

        if result["status"] != "incomplete":
            break

    result["attempts"] = len(attempt_history)
    result["attempt_history"] = attempt_history
    return result


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
