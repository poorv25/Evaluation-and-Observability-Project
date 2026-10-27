# Evaluation & Observability Capstone

## Project Overview

This project demonstrates evaluation and observability practices across three rule-based systems: policy routing, mortgage document extraction, and supply chain investigation.

The project evaluates functional behavior, structured outputs, edge cases, robustness, and evidence generation.

## Systems Implemented

### 1. Policy Pipeline

- Routes requests to policy, mortgage extraction, supply chain, or clarification.
- Runs representative routing test cases.
- Saves routing decisions as JSON.
- Produces a calibration report and static-check results.

### 2. Mortgage Extraction

- Extracts borrower name, loan amount, and property address from formatted text.
- Handles missing fields.
- Compares extracted values with expected outputs.
- Saves document-run results and test evidence.

### 3. Supply Chain Investigation

- Compares expected and actual shipment transit times.
- Identifies indicated delays and missing transit-time information.
- Records evidence and recommendations for each scenario.
- Saves investigation results as text and JSON.

## Project Structure

```text
Evaluation-and-Observability-Project/
├── policy_pipeline.py
├── mortgage_extraction.py
├── supply_chain.py
├── calibration_report.py
├── static_checks.py
├── static_checks_mortgage.py
├── static_checks_supply_chain.py
├── test_policy_pipeline.py
├── test_mortgage_extraction.py
├── test_supply_chain.py
├── test_robustness.py
├── perturbation-log.md
├── reflection-brief.md
├── README.md
└── capstone-submission/
    ├── environment.txt
    ├── robustness-tests.txt
    ├── 01-policy-pipeline/
    ├── 02-mortgage-extraction/
    └── 03-supply-chain/
```

## Running the Systems

Run each workflow from the project root:

```powershell
python policy_pipeline.py
python mortgage_extraction.py
python supply_chain.py
```

Generate the policy calibration report:

```powershell
python calibration_report.py
```

Run the static checks:

```powershell
python static_checks.py
python static_checks_mortgage.py
python static_checks_supply_chain.py
```

Run the automated test suites:

```powershell
python -m unittest test_policy_pipeline -v
python -m unittest test_mortgage_extraction -v
python -m unittest test_supply_chain -v
python -m unittest test_robustness -v
```

## Evaluation and Evidence

The `capstone-submission` directory stores routing decisions, document extraction runs, investigation runs, static-check results, automated test outputs, calibration findings, robustness results, and environment information.

The perturbation log records tested input variations, observed behavior, interpretations, and limitations.

## Limitations

- The systems use deterministic keyword rules, regular expressions, and supplied scenario data.
- Mortgage extraction is designed for consistently formatted text, not arbitrary scanned documents.
- Supply chain investigations do not access live logistics systems.
- Evaluation results cover the test cases included in this project and do not establish general real-world accuracy.

## Security

No API keys, passwords, tokens, or other credentials should be committed to this repository.

## Submission

The project is intended to be version-controlled with Git and published to GitHub after final validation of its source code, tests, documentation, and evidence files.
