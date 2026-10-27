import json
from pathlib import Path

OUTPUT_DIR = Path("capstone-submission/03-supply-chain")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def investigate_supply_chain(scenario: dict) -> dict:
    """Produce a traceable investigation from supplied scenario evidence."""
    shipment_id = scenario.get("shipment_id")
    expected_days = scenario.get("expected_days")
    actual_days = scenario.get("actual_days")
    supplier_status = scenario.get("supplier_status", "unknown")

    evidence = [
        f"Shipment ID: {shipment_id}",
        f"Expected transit days: {expected_days}",
        f"Actual transit days: {actual_days}",
        f"Supplier status: {supplier_status}",
    ]

    if not isinstance(expected_days, (int, float)) or not isinstance(
        actual_days, (int, float)
    ):
        finding = "Insufficient transit-time data to determine delay"
        delay_days = None
        recommendation = "Obtain and verify expected and actual transit times"
    else:
        delay_days = actual_days - expected_days

        if delay_days > 0:
            finding = f"Shipment delayed by {delay_days:g} day(s)"
            recommendation = "Confirm revised ETA with the supplier"
        else:
            finding = "No transit delay indicated by the supplied data"
            recommendation = "Continue monitoring shipment status"

    return {
        "shipment_id": shipment_id,
        "finding": finding,
        "delay_days": delay_days,
        "supplier_status": supplier_status,
        "evidence": evidence,
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
                f"Evidence: {json.dumps(result['evidence'])}",
                f"Recommendation: {result['recommendation']}",
            ]
        )

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
