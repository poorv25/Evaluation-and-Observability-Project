import json
from pathlib import Path

EVIDENCE_DIR = Path("capstone-submission/01-policy-pipeline")
DECISIONS_FILE = EVIDENCE_DIR / "routing_decisions.json"
REPORT_FILE = EVIDENCE_DIR / "calibration-report.txt"


def main():
    decisions = json.loads(DECISIONS_FILE.read_text(encoding="utf-8"))

    total = len(decisions)
    passed = sum(item["passed"] for item in decisions)
    failed = total - passed
    accuracy = (passed / total * 100) if total else 0.0

    lines = [
        "POLICY PIPELINE CALIBRATION REPORT",
        "=" * 35,
        "",
        "Measured results",
        f"Total routing cases: {total}",
        f"Correct routing decisions: {passed}",
        f"Incorrect routing decisions: {failed}",
        f"Observed accuracy: {accuracy:.1f}%",
        "",
        "Observed routing decisions",
    ]

    for item in decisions:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"{status}: input={item['input']!r}; "
            f"expected={item['expected']}; actual={item['route']}"
        )

    lines.extend(
        [
            "",
            "Calibration findings",
            "- Results reflect only the saved routing test cases.",
            "- Keyword rules are deterministic but may be brittle.",
            "- Overlapping keywords can make routing dependent on rule order.",
            "- Unknown and empty inputs are routed to clarification.",
            "- Passing these cases does not establish general routing accuracy.",
            "",
            "Recommended next steps",
            "- Expand tests with more boundary and ambiguous inputs.",
            "- Measure performance on a larger representative test set.",
            "- Refine overlapping rules based on observed failures.",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
