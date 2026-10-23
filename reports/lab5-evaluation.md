# Lab 5 — LLM Evaluation Gate

## Golden Set
- 12 cases in `evals/golden/triage.jsonl`.
- Covers decision correctness, grounding, guardrails, prompt injection, and insufficient input.
- Cases triage-009 through triage-012 are custom additions.

## Baseline
- Command: `make llm-eval`
- Result: 12/12 PASS (100%).
- Evidence: `reports/llm_eval-baseline.json`.

## Regression Demonstration
- Changed case: triage-011 (prompt injection).
- Expected decision: no_action.
- Simulated regressed decision: schedule_urgent.
- Result: 11/12 PASS (91.7%).
- Gate: FAILED, 1 regression detected.
- Evidence: `reports/llm_eval-custom-regressed.json`.

## Limitations
The additional responses were manually constructed for offline testing.
This demonstrates that the evaluation gate detects the simulated regression,
not that a live LLM actually followed the malicious instruction.

Token usage for the new cases was not measured from a provider.
The fixture-based cost figures must not be reported as real usage.

<!-- LAB5_LIVE_EXPERIMENT_FINAL -->
## Live Gemini Evaluation — 23 October 2026

Provider: Vertex AI, global location.
Model: gemini-3.5-flash-lite.

Unlike the earlier fixture-based demonstration, these results came
from actual Gemini API calls.

| Configuration | Golden Cases Passed | Pass Rate |
|---|---:|---:|
| Original prompt, plain text | 1/8 | 12.5% |
| Original prompt, JSON mode | 3/8 | 37.5% |
| Prompt v2, explicit decision rules | 7/8 | 87.5% |
| Prompt v3, injection-output protection | 8/8 | 100% |
| Prompt v3, full Golden Set | 12/12 | 100% |

The regression gate passed when comparing Prompt v3 against Prompt v2.
No previously passing case failed. The final 12-case evaluation passed
all Golden Checks.

Prompt v2 introduced explicit probability-based decision rules and
safety priorities. Prompt v3 additionally prohibited repeating
untrusted instructions from operator notes.

The probability thresholds were defined for this course experiment;
they are not independently validated industrial maintenance standards.

Evidence:
- reports/lab5-live-json-after-evaluation.json
- reports/lab5-live-prompt-v2-gate.json
- reports/lab5-live-prompt-v3-gate.json
- reports/lab5-live-prompt-v3-all12-evaluation.json
- evals/prompts/triage-v2.txt
- evals/prompts/triage-v3.txt

Limitations: This is a small fixed test set with single-run samples.
The 8-case and 12-case scores use different denominators. A 100%
Golden Set result does not establish production safety or generalization.
