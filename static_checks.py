import ast
from pathlib import Path

SOURCE_FILE = Path("policy_pipeline.py")
OUTPUT_FILE = Path("capstone-submission/01-policy-pipeline/static-checks.txt")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def main():
    checks = []

    source = SOURCE_FILE.read_text(encoding="utf-8")

    try:
        ast.parse(source)
        checks.append(("Python syntax", True, "Source parses successfully"))
    except SyntaxError as error:
        checks.append(("Python syntax", False, str(error)))

    required_items = [
        "def route_request",
        "def run_routing_tests",
        "routing_decisions.json",
        "routing-tests.txt",
    ]

    for item in required_items:
        found = item in source
        checks.append(
            (
                f"Required item: {item}",
                found,
                "Found" if found else "Missing",
            )
        )

    lines = [
        f"{'PASS' if passed else 'FAIL'}: {name} — {details}"
        for name, passed, details in checks
    ]

    lines.append(
        f"\nPassed: {sum(passed for _, passed, _ in checks)}" f"/{len(checks)}"
    )

    report = "\n".join(lines)
    OUTPUT_FILE.write_text(report + "\n", encoding="utf-8")
    print(report)

    if any(not passed for _, passed, _ in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
