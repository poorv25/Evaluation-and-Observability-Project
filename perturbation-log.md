# Perturbation Log

## Purpose

Record controlled input changes used to evaluate the robustness of the Policy Pipeline, Mortgage Extraction, and Supply Chain Investigation systems.

## Results

| System              | Perturbation                             | Why it was tested                      | Observed result | Interpretation                                                         |
| ------------------- | ---------------------------------------- | -------------------------------------- | --------------- | ---------------------------------------------------------------------- |
| Policy Pipeline     | Uppercase `MORTGAGE`                     | Test case-insensitive routing          | Passed          | Routing normalizes input to lowercase.                                 |
| Policy Pipeline     | Whitespace-only input                    | Test boundary input                    | Passed          | Empty normalized input routes to clarification.                        |
| Policy Pipeline     | Unknown request wording                  | Test unsupported intent                | Passed          | Unknown requests route to clarification.                               |
| Mortgage Extraction | Missing loan amount and property address | Test incomplete documents              | Passed          | Missing fields are returned as `None`.                                 |
| Mortgage Extraction | Fields reordered in the document         | Test field-order assumptions           | Passed          | Each field is extracted independently by its label.                    |
| Supply Chain        | Missing expected transit time            | Test incomplete investigation evidence | Passed          | The workflow reports insufficient transit-time data.                   |
| Supply Chain        | Actual transit time lower than expected  | Test negative delay values             | Passed          | The calculation records a negative delay and reports no transit delay. |

## Evidence

The robustness tests were executed using:

`python -m unittest test_robustness -v`

The captured output is stored in `capstone-submission/robustness-tests.txt`.

Observed result: 7 tests passed.

## Limitations

- These tests cover only the selected synthetic scenarios.
- Mortgage extraction relies on specific text labels and regular expressions.
- Policy routing uses keyword rules and may misclassify unfamiliar or conflicting requests.
- Supply Chain findings depend on the accuracy and completeness of supplied data.
- Passing these tests does not establish general reliability for real-world documents or workflows.

## Next Steps

Expand the test set with additional ambiguous inputs, malformed documents, conflicting evidence, and unexpected data types. Review any failures and preserve the actual test output.
