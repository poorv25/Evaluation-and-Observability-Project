import json
from collections import defaultdict
from pathlib import Path

EVIDENCE_DIR = Path("capstone-submission/01-policy-pipeline")
DECISIONS_FILE = EVIDENCE_DIR / "routing_decisions.json"
REPORT_FILE = EVIDENCE_DIR / "calibration-report.txt"


def classify_slice(item: dict) -> str:
    """Assign a routing case to an interpretable evaluation slice."""
    text = str(item.get("input", "")).strip().lower()
    expected = item.get("expected", "")

    if not text:
        return "empty_input"

    if expected == "clarification":
        return "unknown_or_conflicting"

    if "policy" in text and any(
        word in text
        for word in (
            "mortgage",
            "loan application",
            "borrower",
            "shipment",
            "supplier",
            "supply chain",
            "delivery delay",
            "delayed shipment",
        )
    ):
        return "ambiguous_or_overlapping"

    return "standard_routing"


def calculate_metrics(items: list[dict]) -> dict:
    """Calculate accuracy and counts for a group of routing decisions."""
    total = len(items)
    passed = sum(bool(item.get("passed", False)) for item in items)

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": passed / total * 100 if total else 0.0,
    }


def main():
    if not DECISIONS_FILE.exists():
        raise FileNotFoundError(
            f"Routing decisions not found: {DECISIONS_FILE}. "
            "Run policy_pipeline.py first."
        )

    decisions = json.loads(DECISIONS_FILE.read_text(encoding="utf-8"))

    if not isinstance(decisions, list):
        raise TypeError("Routing decisions must be a JSON list.")

    slices = defaultdict(list)

    for item in decisions:
        if not isinstance(item, dict):
            continue
        category = classify_slice(item)
        slices[category].append(item)

    overall = calculate_metrics(decisions)
    lines = [
        "POLICY PIPELINE CALIBRATION REPORT",
        "=" * 35,
        "",
        "Overall measured results",
        f"Total routing cases: {overall['total']}",
        f"Correct routing decisions: {overall['passed']}",
        f"Incorrect routing decisions: {overall['failed']}",
        f"Observed accuracy: {overall['accuracy']:.1f}%",
        "",
        "SLICED EVALUATION RESULTS",
        "-" * 35,
    ]

    for category in sorted(slices):
        metrics = calculate_metrics(slices[category])
        lines.extend(
            [
                "",
                f"Category: {category}",
                f"  Cases: {metrics['total']}",
                f"  Correct: {metrics['passed']}",
                f"  Incorrect: {metrics['failed']}",
                f"  Accuracy: {metrics['accuracy']:.1f}%",
            ]
        )

    lines.extend(
        [
            "",
            "Observed routing decisions",
        ]
    )

    for item in decisions:
        if not isinstance(item, dict):
            lines.append(f"SKIP: invalid decision record: {item!r}")
            continue

        status = "PASS" if item.get("passed", False) else "FAIL"
        category = classify_slice(item)
        lines.append(
            f"{status}: slice={category}; "
            f"input={item.get('input', '')!r}; "
            f"expected={item.get('expected')}; "
            f"actual={item.get('route')}"
        )

    lines.extend(
        [
            "",
            "Calibration findings",
            "- Metrics describe only the saved routing test cases.",
            "- Slice labels use simple keyword-based heuristics.",
            "- Small slice sizes may make accuracy unstable.",
            "- High accuracy on these cases does not prove general accuracy.",
            "- This report measures observed accuracy, not probabilistic confidence calibration.",
            "",
            "Recommended next steps",
            "- Add more representative cases to every slice.",
            "- Include ambiguous cases with and without overlapping keywords.",
            "- Review failures separately for each category.",
            "- Re-run evaluation after changing routing rules.",
        ]
    )

    report = "\n".join(lines) + "\n"
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
