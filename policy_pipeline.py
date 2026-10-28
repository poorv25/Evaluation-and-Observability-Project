import json
from pathlib import Path

OUTPUT_DIR = Path("capstone-submission/01-policy-pipeline")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VALID_ROUTES = {
    "mortgage_extraction",
    "supply_chain",
    "policy_pipeline",
    "clarification",
}


def route_request(text: str) -> str:
    """Route clear requests and clarify conflicting domain intents."""
    normalized = text.lower().strip()

    if not normalized:
        return "clarification"

    mortgage_words = ["mortgage", "loan application", "borrower"]
    supply_chain_words = [
        "shipment",
        "supplier",
        "supply chain",
        "delivery delay",
        "delayed shipment",
    ]
    policy_words = ["policy", "compliance", "routing"]

    has_mortgage = any(word in normalized for word in mortgage_words)
    has_supply_chain = any(word in normalized for word in supply_chain_words)
    has_policy = any(word in normalized for word in policy_words)

    if has_mortgage and has_supply_chain:
        return "clarification"

    if has_mortgage:
        return "mortgage_extraction"

    if has_supply_chain:
        return "supply_chain"

    if has_policy:
        return "policy_pipeline"

    return "clarification"


def validate_route(route: str) -> tuple[bool, str]:
    """Validate a routing decision and explain any failure."""
    if not isinstance(route, str):
        return False, "Route must be a string."

    if route not in VALID_ROUTES:
        return False, f"Unsupported route: {route!r}."

    return True, "Route is valid."


def route_request_with_retry(
    text: str,
    max_attempts: int = 3,
) -> dict:
    """Validate routing decisions and retry within a bounded attempt limit."""
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool):
        raise TypeError("max_attempts must be a positive integer.")

    if max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer.")

    attempt_history = []
    last_route = "clarification"

    for attempt in range(1, max_attempts + 1):
        route = route_request(text)
        is_valid, feedback = validate_route(route)

        attempt_history.append(
            {
                "attempt": attempt,
                "route": route,
                "valid": is_valid,
                "feedback": feedback,
            }
        )

        last_route = route

        if is_valid:
            return {
                "input": text,
                "route": route,
                "valid": True,
                "attempts_used": attempt,
                "attempt_history": attempt_history,
            }

    return {
        "input": text,
        "route": "clarification",
        "valid": False,
        "attempts_used": max_attempts,
        "attempt_history": attempt_history,
        "error": f"Routing validation failed; last route was {last_route!r}.",
    }


def run_routing_tests():
    """Evaluate routing against a fixed set of labeled examples."""
    cases = [
        # Standard routing
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
            "input": "MORTGAGE",
            "expected": "mortgage_extraction",
        },
        {
            "input": "Supplier delivery delay",
            "expected": "supply_chain",
        },
        {
            "input": "Please check the routing policy",
            "expected": "policy_pipeline",
        },
        # Empty and whitespace inputs
        {
            "input": "",
            "expected": "clarification",
        },
        {
            "input": "   ",
            "expected": "clarification",
        },
        # Ambiguous or overlapping keywords
        {
            "input": "Review the policy for a delayed shipment",
            "expected": "supply_chain",
        },
        {
            "input": "Check mortgage policy compliance",
            "expected": "mortgage_extraction",
        },
        {
            "input": "Mortgage loan for a supplier shipment policy",
            "expected": "clarification",
        },
        {
            "input": "Review policy for supplier delivery delay",
            "expected": "supply_chain",
        },
        {
            "input": "Mortgage borrower and shipment delay",
            "expected": "clarification",
        },
        # Unknown and unusual inputs
        {
            "input": "Tell me something interesting",
            "expected": "clarification",
        },
        {
            "input": "Please review this request",
            "expected": "clarification",
        },
        {
            "input": "!!! ???",
            "expected": "clarification",
        },
        # Repeated keywords and casing
        {
            "input": "Mortgage mortgage borrower",
            "expected": "mortgage_extraction",
        },
        {
            "input": "SHIPMENT shipment delay",
            "expected": "supply_chain",
        },
        {
            "input": "CoMpLiAnCe PoLiCy",
            "expected": "policy_pipeline",
        },
        {
            "input": "Supplier shipment mortgage application",
            "expected": "clarification",
        },
    ]

    results = []

    for case in cases:
        retry_result = route_request_with_retry(case["input"])
        actual = retry_result["route"]

        results.append(
            {
                **case,
                "actual": actual,
                "passed": (actual == case["expected"] and retry_result["valid"]),
                "attempts_used": retry_result["attempts_used"],
                "attempt_history": retry_result["attempt_history"],
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
            "attempts_used": result["attempts_used"],
            "attempt_history": result["attempt_history"],
        }
        for result in results
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUTPUT_DIR / "routing_decisions.json").write_text(
        json.dumps(decisions, indent=2),
        encoding="utf-8",
    )

    report = "\n".join(
        f"{'PASS' if result['passed'] else 'FAIL'}: "
        f"{result['input']!r} "
        f"(expected={result['expected']}, "
        f"actual={result['actual']}, "
        f"attempts={result['attempts_used']})"
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
