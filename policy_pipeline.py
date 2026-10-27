import json
from pathlib import Path

OUTPUT_DIR = Path("capstone-submission/01-policy-pipeline")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def route_request(text: str) -> str:
    """Route a request using explicit keyword rules."""
    normalized = text.lower().strip()

    if not normalized:
        return "clarification"

    if any(word in normalized for word in ["mortgage", "loan application", "borrower"]):
        return "mortgage_extraction"

    if any(
        word in normalized
        for word in ["shipment", "supplier", "supply chain", "delivery delay"]
    ):
        return "supply_chain"

    if any(word in normalized for word in ["policy", "compliance", "routing"]):
        return "policy_pipeline"

    return "clarification"


def run_routing_tests():
    cases = [
        # Normal cases
        {
            "input": "Check mortgage borrower details",
            "expected": "mortgage_extraction",
        },
        {
            "input": "Investigate a shipment delay",
            "expected": "supply_chain",
        },
        {
            "input": "Review compliance policy",
            "expected": "policy_pipeline",
        },
        # Boundary cases
        {
            "input": "",
            "expected": "clarification",
        },
        {
            "input": "   ",
            "expected": "clarification",
        },
        {
            "input": "MORTGAGE",
            "expected": "mortgage_extraction",
        },
        # Ambiguous cases
        {
            "input": "Review the policy for a delayed shipment",
            "expected": "supply_chain",
        },
        {
            "input": "Check mortgage policy compliance",
            "expected": "mortgage_extraction",
        },
        # Unknown input
        {
            "input": "Tell me something interesting",
            "expected": "clarification",
        },
    ]

    results = []

    for case in cases:
        actual = route_request(case["input"])
        results.append(
            {
                **case,
                "actual": actual,
                "passed": actual == case["expected"],
            }
        )

    return results

    cases = [
        {
            "input": "Check mortgage borrower details",
            "expected": "mortgage_extraction",
        },
        {
            "input": "Investigate a shipment delay",
            "expected": "supply_chain",
        },
        {
            "input": "Review compliance policy",
            "expected": "policy_pipeline",
        },
        {
            "input": "",
            "expected": "clarification",
        },
        {
            "input": "Tell me something interesting",
            "expected": "clarification",
        },
    ]

    results = []

    for case in cases:
        actual = route_request(case["input"])
        results.append(
            {
                **case,
                "actual": actual,
                "passed": actual == case["expected"],
            }
        )

    return results


def main():
    results = run_routing_tests()
    total = len(results)
    passed = sum(result["passed"] for result in results)

    decisions = [
        {
            "input": result["input"],
            "route": result["actual"],
            "expected": result["expected"],
            "passed": result["passed"],
        }
        for result in results
    ]

    (OUTPUT_DIR / "routing_decisions.json").write_text(
        json.dumps(decisions, indent=2),
        encoding="utf-8",
    )

    report = "\n".join(
        f"{'PASS' if result['passed'] else 'FAIL'}: "
        f"{result['input']!r} "
        f"(expected={result['expected']}, "
        f"actual={result['actual']})"
        for result in results
    )

    report += f"\n\nPassed: {passed}/{total}\n"

    (OUTPUT_DIR / "routing-tests.txt").write_text(
        report,
        encoding="utf-8",
    )

    print(report)


if __name__ == "__main__":
    main()
