# Lab 5 — Full Cost Accounting

**Provider:** Google Cloud Platform (GCP)  
**Project:** itcs355-6688176  
**Region:** asia-southeast1  
**Billing period examined:** 20–21 October 2026  
**Currency:** Thai Baht (THB)

## 1. Estimate Before Running

No verifiable Lab 5 pre-run cost estimate committed before Task 1 was found in the repository history.

The earlier Lab 3 cost report contains a serving cost model, but it is not evidence of a Lab 5 pre-run estimate. Therefore, no retrospective calculation is represented as an advance prediction.

**Limitation:** The requirement for a pre-run committed estimate was not satisfied.

## 2. Actual Cost from Billing

The Google Cloud Billing report for 20–21 October 2026 shows approximately **18.99 THB** in resource usage charges, offset by approximately 18.99 THB in credits, leaving approximately **0.00 THB** in net charges.

This billing account is linked to one GCP project, `itcs355-6688176`.

However, the project was used for multiple labs. The reported amount represents project-level usage during the selected period and cannot be conclusively attributed entirely to Lab 5.

The historical Lab 5 training job `554680251590901760` was incorrectly labeled `lab=2`, although its container image and SPOT scheduling confirm that it belongs to Lab 5.

Consequently, filtering the historical billing data by `lab=5` would omit relevant charges, while filtering by `lab=2` could mix costs from different experiments.

The adapter's future resource labels have been corrected to `lab=5`. This correction does not retroactively change historical billing records.

## 3. Estimate vs Actual — The Gap

A numerical estimate-versus-actual difference cannot be established honestly because no committed pre-run estimate was found.

The available billing evidence indicates approximately 18.99 THB of project-level usage charges for the examined period. This is not a verified Lab 5-only total.

Several factors explain why a prediction could differ from actual cloud expenditure: repeated pipeline attempts during debugging, failed training jobs, provisioned online prediction instances, pipeline orchestration overhead, and storage charges.

The inaccurate historical labels created an additional attribution problem: resources belonging to Lab 5 were recorded under earlier lab identifiers.

Credits reduce the amount payable but do not eliminate the underlying resource consumption.

## 4. Breakdown by Component

The following figures are provisional classifications of billing SKU data for 20–21 October 2026, not an independently verified Lab 5-only breakdown.

| Component | Usage cost (THB) | Explanation |
|---|---:|---|
| Training | 7.59 | Compute and training-related disk charges, including provisional classification of Spot compute |
| Storage | 0.75 | Artifact Registry storage charges |
| Serving | 6.55 | Vertex AI online prediction CPU and memory |
| Pipeline | 4.09 | Managed pipeline jobs and management fees |
| Monitoring | 0.00 | No identifiable charged monitoring SKU in the export |
| **Subtotal** | **18.98** | Sum of individually rounded provisional SKU allocations |

The approximately 0.01 THB difference from the reported 18.99 THB project total may result from rounding of displayed SKU amounts.

These categories do not prove that every charge is exclusively attributable to Lab 5. The storage row includes identified Artifact Registry charges and should not be interpreted as a verified total for every storage service.

## 5. Cost per 1,000 Predictions

**Serving instance:** `n1-standard-2`  
**Reference hourly cost:** 3.80 THB/hour  
**Measured throughput:** 23.90 requests/second (Lab 3 load test)

The Lab 5 deployment configuration specifies `n1-standard-2`. Throughput was reused from Lab 3; a separate Lab 5 throughput measurement was not performed.

The course cost model is:

Cost per 1,000 predictions =
(3.80 × 1000) / (23.90 × utilisation × 3600)

| Utilisation | Estimated THB per 1,000 predictions |
|---|---:|
| 5% | 0.8833 |
| 25% | 0.1767 |
| 80% | 0.0552 |

The 25% utilisation case is used as the representative planning assumption, not a measured production utilisation level.

These values are estimates based on course reference rates and exclude additional platform costs.

## 6. Applied Optimisation — Spot Training

A real Vertex AI Custom Job provides evidence of SPOT scheduling:

- **Job ID:** `554680251590901760`
- **Training image:** `itcs355-lab5`
- **Machine type:** `e2-standard-4`
- **Replicas:** 1
- **Scheduling strategy:** `SPOT`
- **State:** `JOB_STATE_SUCCEEDED`
- **Start time:** 2026-10-20 17:16:38 UTC
- **End time:** 2026-10-20 17:17:38 UTC
- **Observed execution duration:** approximately 60 seconds

Using the course reference cost model, the on-demand hourly price is 6.40 THB and the assumed Spot factor is 0.30.

| Metric | Before: On-demand baseline | After: Spot |
|---|---:|---:|
| Machine | e2-standard-4 | e2-standard-4 |
| Reference hourly compute cost | 6.40 THB | 1.92 THB |
| Estimated compute cost for 60 seconds | 0.1067 THB | 0.0320 THB |
| Estimated compute saving | — | 0.0747 THB (70%) |

The before case is a modeled counterfactual, not an executed on-demand job. The after cost is also based on the course reference pricing factor, not a job-level billing measurement.

This comparison excludes disk and orchestration costs. Spot interruptions may also increase elapsed training time or require retries. Checkpointing was enabled to reduce the cost of interruptions.

The available evidence does not establish a before-and-after latency p95 measurement; training scheduling primarily affects cost and completion risk rather than online inference latency.

## Evidence and Limitations

- Google Cloud Billing report and SKU export for 20–21 October 2026.
- Vertex AI Custom Job `554680251590901760`, verified with `gcloud ai custom-jobs describe`.
- `cloudlayer/gcp.py` and `src/costs.py` for configuration and reference pricing.
- `reports/lab3-cost.md` for historical serving throughput assumptions.
- No verified pre-run Lab 5 cost estimate was found.
- Historical billing attribution is limited by inconsistent resource labels.
- Billing data may be delayed and should be checked again after teardown.

<!-- LAB5_LIVE_EXPERIMENT_FINAL -->
## 7. LLM Token Cost and Optimisation — 23 October 2026

### Live Usage

Model: gemini-3.5-flash-lite through Vertex AI global.
Prompt: evals/prompts/triage-v3.txt.

Across 12 real API requests with max_output_tokens=200:

| Metric | Observed |
|---|---:|
| Requests | 12 |
| Input tokens | 5,340 |
| Candidate output tokens | 592 |
| Average input tokens/request | 445 |
| Average output tokens/request | 49.33 |
| Cached input tokens | 0 |
| Golden Set pass rate | 12/12 |
| p95 latency | 2,802 ms |

The original 12 response records did not separately capture thinking
tokens. A subsequent real verification request recorded 450 input,
54 candidate output, 0 thinking and 504 total tokens. This validates
the accounting fields for that request, but does not prove that all
historical requests had zero thinking tokens.

### Output Cap Comparison

| Metric | Cap 200 | Cap 100 |
|---|---:|---:|
| Golden Cases Passed | 12/12 | 12/12 |
| Total candidate output tokens | 592 | 585 |
| p95 latency | 2,802 ms | 2,669 ms |
| Regression gate | Baseline | PASS |

The observed candidate-output reduction was 7 tokens across 12
requests, approximately 1.18%. Halving the cap did not halve actual
token usage. Cap 100 was adequate for this fixed sample, but might
truncate longer outputs on other inputs.

### Prompt Cache Break-even

The course model assumes CACHE_READ_FACTOR=0.10 and
CACHE_WRITE_FACTOR=1.25, giving a mathematical break-even hit rate of
21.74%. This is a course-model assumption, not a measured Google Cloud
caching break-even point.

Actual cached input tokens: 0 of 5,340.
Observed cache hit rate: 0%.
No realized caching savings were demonstrated.

### Preliminary Token Cost Estimate

Illustrative rates applied for this calculation:
- Input: USD 0.30 per million tokens.
- Output: USD 2.50 per million tokens.

Using the recorded candidate input/output tokens:
- Estimated sample cost for 12 requests: USD 0.003082.
- Estimated cost per 1,000 requests: USD 0.256833.

This is a preliminary usage-based calculation, not an actual GCP
billing charge. Final costing requires verification of the applicable
Vertex AI billing SKU, pricing date, tier, currency conversion, and
any historically unrecorded reasoning or other billable usage.
The teacher's gcp/small rates in src/llmcost.py are sample rates,
not independently verified rates for this exact model.

These LLM experiments are not represented in the 20–21 October
project-level billing summary above.

Evidence:
- reports/lab5-live-prompt-v3-all12.jsonl
- reports/lab5-live-prompt-v3-all12-evaluation.json
- reports/lab5-output-cap100-all12.jsonl
- reports/lab5-output-cap100-gate.json
- reports/lab5-thinking-token-check.json
- src/llmcost.py
