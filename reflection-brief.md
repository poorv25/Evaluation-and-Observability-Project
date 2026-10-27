# Reflection Brief — Evaluation & Observability Capstone

## Project Objective

The objective was to implement and evaluate three workflows while preserving evidence of their behavior, test results, and limitations.

## Systems Implemented

The Policy Pipeline routes requests using explicit keyword rules. Mortgage Extraction retrieves selected fields from formatted text using regular expressions. Supply Chain Investigation compares expected and actual transit times and records evidence-based findings from supplied scenarios.

## Evaluation Approach

Each system was evaluated using representative scenarios and automated tests. Static checks inspect source syntax and the presence of selected implementation elements. Additional robustness tests examine case variation, whitespace, missing fields, reordered document fields, and missing or changed transit-time values.

## Initial Findings

The initial Policy Pipeline evaluation reported 9 correct decisions out of 9 saved cases. Its automated unit test suite passed 10 tests.

Mortgage Extraction passed two initial document scenarios and four automated unit tests. Its static-check script reported seven successful checks.

Supply Chain Investigation produced three initial scenario reports and passed five automated unit tests. Its static-check script was also created to verify source syntax and selected implementation elements.

The robustness suite passed seven tests across the three systems.

These results describe the selected test cases only. They should not be interpreted as proof of general accuracy or production readiness.

## Perturbations and Robustness

The tests examined uppercase routing inputs, whitespace-only and unknown requests, missing mortgage fields, reordered document fields, missing transit-time data, and negative calculated delay values.

The observations are recorded in `perturbation-log.md` and `capstone-submission/robustness-tests.txt`.

## Limitations

The workflows use deterministic rules rather than trained extraction or reasoning models. The mortgage extractor depends on specific field labels and text formatting. The routing rules may misclassify ambiguous or unfamiliar requests. Supply chain findings depend on the correctness of the supplied scenario data.

The test datasets are small and synthetic. Further testing is required before using these workflows for consequential real-world decisions.

## Improvements and Lessons Learned

The project demonstrates the importance of separating implementation from evaluation, recording actual outputs, testing incomplete and ambiguous inputs, and preserving reproducible evidence.

Future improvements include expanding the test datasets, testing malformed inputs and unexpected data types, measuring field-level extraction accuracy, introducing explicit handling for conflicting evidence, and strengthening static checks.

## Conclusion

The three initial workflows and their evidence-generation scripts were implemented locally. The remaining quality gate is to run the complete test suite, inspect the final submission structure, and publish the validated project through Git.
