import json
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("capstone-submission/03-supply-chain")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def investigate_supply_chain(scenario: dict[str, Any]) -> dict[str, Any]:
    """Investigate shipment status using traceable, multi-source evidence."""
    shipment_id = scenario.get("shipment_id")
    expected_days = scenario.get("expected_days")
    actual_days = scenario.get("actual_days")
    supplier_status = scenario.get("supplier_status", "unknown")

    evidence: list[str] = []
    source_failures: list[str] = []
    conflicts: list[str] = []

    evidence.append(f"Shipment ID: {shipment_id}")

    # Preserve compatibility with the original scenario format while
    # supporting optional independent sources.
    sources = scenario.get("sources")

    if not isinstance(sources, list) or not sources:
        sources = [
            {
                "source": "scenario_input",
                "status": "available",
                "expected_days": expected_days,
                "actual_days": actual_days,
                "supplier_status": supplier_status,
            }
        ]

    available_sources: list[dict[str, Any]] = []

    for source in sources:
        if not isinstance(source, dict):
            source_failures.append("A source entry was not a valid object.")
            continue

        source_name = str(source.get("source", "unnamed_source"))
        source_status = str(source.get("status", "available")).lower()

        if source_status != "available":
            failure_reason = source.get("error", source_status)
            source_failures.append(
                f"{source_name}: source unavailable ({failure_reason})"
            )
            continue

        available_sources.append(source)
        evidence.append(
            f"Source {source_name}: "
            f"expected_days={source.get('expected_days')}, "
            f"actual_days={source.get('actual_days')}, "
            f"supplier_status={source.get('supplier_status', 'unknown')}"
        )

    expected_values = {
        source["expected_days"]
        for source in available_sources
        if isinstance(source.get("expected_days"), (int, float))
        and not isinstance(source.get("expected_days"), bool)
    }
    actual_values = {
        source["actual_days"]
        for source in available_sources
        if isinstance(source.get("actual_days"), (int, float))
        and not isinstance(source.get("actual_days"), bool)
    }

    if len(expected_values) > 1:
        conflicts.append(
            f"Sources disagree on expected transit time: " f"{sorted(expected_values)}"
        )

    if len(actual_values) > 1:
        conflicts.append(
            f"Sources disagree on actual transit time: " f"{sorted(actual_values)}"
        )

    expected_days = next(iter(expected_values)) if len(expected_values) == 1 else None
    actual_days = next(iter(actual_values)) if len(actual_values) == 1 else None

    supplier_statuses = {
        str(source["supplier_status"])
        for source in available_sources
        if source.get("supplier_status") not in (None, "")
    }

    if len(supplier_statuses) > 1:
        conflicts.append(
            f"Sources disagree on supplier status: " f"{sorted(supplier_statuses)}"
        )

    if len(supplier_statuses) == 1:
        supplier_status = next(iter(supplier_statuses))
    elif len(supplier_statuses) > 1:
        supplier_status = "conflicting"

    delay_days = None

    if conflicts:
        finding = "Conflicting source evidence; delay conclusion is unverified"
        recommendation = (
            "Reconcile the conflicting sources before making an operational " "decision"
        )
    elif (
        not isinstance(expected_days, (int, float))
        or isinstance(expected_days, bool)
        or not isinstance(actual_days, (int, float))
        or isinstance(actual_days, bool)
    ):
        finding = "Insufficient transit-time data to determine delay"
        recommendation = "Obtain and verify expected and actual transit times"
    else:
        delay_days = actual_days - expected_days

        if delay_days < 0:
            finding = (
                f"No transit delay indicated; shipment arrived "
                f"{abs(delay_days):g} day(s) earlier"
            )
            recommendation = "Confirm receipt and update shipment records"
        elif delay_days > 0:
            finding = f"Shipment delayed by {delay_days:g} day(s)"
            recommendation = "Confirm revised ETA with the supplier"
        else:
            finding = "No transit delay indicated by the supplied data"
            recommendation = "Continue monitoring shipment status"

    if source_failures:
        recommendation += (
            ". Verify unavailable sources before relying on this assessment"
        )

    if not available_sources:
        finding = "No available sources; shipment status cannot be verified"
        delay_days = None

    evidence.extend(f"Source failure: {failure}" for failure in source_failures)
    evidence.extend(f"Conflict: {conflict}" for conflict in conflicts)

    return {
        "shipment_id": shipment_id,
        "finding": finding,
        "delay_days": delay_days,
        "supplier_status": supplier_status,
        "evidence": evidence,
        "source_failures": source_failures,
        "conflicts": conflicts,
        "sources_available": len(available_sources),
        "recommendation": recommendation,
    }


def main():
    scenarios = [
        {
            "shipment_id": "SHIP-001",
            "expected_days": 5,
            "actual_days": 8,
            "supplier_status": "awaiting dispatch confirmation",
        },
        {
            "shipment_id": "SHIP-002",
            "expected_days": 4,
            "actual_days": 4,
            "supplier_status": "dispatched",
        },
        {
            "shipment_id": "SHIP-003",
            "expected_days": None,
            "actual_days": 7,
            "supplier_status": "unknown",
        },
        {
            "shipment_id": "SHIP-004",
            "sources": [
                {
                    "source": "carrier_tracking",
                    "status": "available",
                    "expected_days": 5,
                    "actual_days": 8,
                    "supplier_status": "dispatched",
                },
                {
                    "source": "supplier_portal",
                    "status": "available",
                    "expected_days": 5,
                    "actual_days": 6,
                    "supplier_status": "awaiting confirmation",
                },
            ],
        },
        {
            "shipment_id": "SHIP-005",
            "sources": [
                {
                    "source": "carrier_tracking",
                    "status": "available",
                    "expected_days": 5,
                    "actual_days": 8,
                    "supplier_status": "dispatched",
                },
                {
                    "source": "supplier_portal",
                    "status": "unavailable",
                    "error": "connection timeout",
                },
            ],
        },
    ]

    results = [investigate_supply_chain(scenario) for scenario in scenarios]

    report = ["SUPPLY CHAIN INVESTIGATION RUNS", "=" * 32]

    for result in results:
        report.extend(
            [
                "",
                f"Shipment: {result['shipment_id']}",
                f"Finding: {result['finding']}",
                f"Delay days: {result['delay_days']}",
                f"Supplier status: {result['supplier_status']}",
                f"Sources available: {result['sources_available']}",
                f"Conflicts: {json.dumps(result['conflicts'])}",
                f"Source failures: {json.dumps(result['source_failures'])}",
                f"Evidence: {json.dumps(result['evidence'])}",
                f"Recommendation: {result['recommendation']}",
            ]
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUTPUT_DIR / "investigation-runs.txt").write_text(
        "\n".join(report) + "\n",
        encoding="utf-8",
    )

    (OUTPUT_DIR / "investigation_decisions.json").write_text(
        json.dumps(results, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\n".join(report))


if __name__ == "__main__":
    main()
