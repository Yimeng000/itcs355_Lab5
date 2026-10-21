# ITCS355 Lab 1 — Reproducible Training

> **Course materials live in [`course/`](course/README.md)** — syllabus, slides, the faculty
> specification, all five lab handouts, and the project brief. Every document is Markdown and
> renders on GitHub, diagrams included. New to the repo? Start with the
> [portability reference](course/reference/cloud-portability-reference.md).
> Keep this block when you edit the rest of this file; it is not part of the Lab 1 deliverable.

Predicting machine failure within 7 days from sensor readings. The model is not the point;
whether a stranger can reproduce it is.

> **This README is graded.** A grader with Docker and nothing else from your setup runs one
> command and compares the result against the claim below.

## Reproduce

```bash
make reproduce
```

expected test_roc_auc: 0.848 ± 0.010

Runtime: about 35 seconds on 4 cores. No cloud account or credentials needed for this command —
that is deliberate, and it is why a grader can run it.

---

## The problem

240 machines, 25 readings each, 6 sensor features, binary target `failed_within_7d` with a
positive rate near 12%.

Machines have persistent characteristics — a hot-running machine reads hot in every row. So the
train/validation/test split is **grouped by `machine_id`**: every reading from one machine lands
in exactly one partition. Splitting row-wise instead lets the model memorise the machine and
reports a validation score that will never survive production. `tests/test_data.py` asserts this
property holds, and Lab 4 turns it into a CI gate.

Bringing your own dataset is allowed. Replace `scripts/make_dataset.py`, update the schema in
`src/data.py`, and keep every test passing.

---

## Layout

```
src/          Layer 1 — provider-neutral. No SDKs, no bucket names, no absolute paths.
cloudlayer/   Layer 3 — the only place a provider SDK may be imported.
scripts/      Dataset generation, cloud check, portability audit, metric verification.
tests/        Data contract tests and split property tests.
```

`src/config.py` is the single point of environment knowledge. Everything else reads from it.
`make portability-audit` enforces the rule; it fails the build if a provider string appears in
`src/` or `tests/`.

---

## Setup

```bash
cp cloud.env.example cloud.env      # fill in, never commit
make setup
make cloud-check                    # eight slots, all PASS
make data                           # generate the dataset
make test                           # 10 tests, all passing
```

Post your `make cloud-check` output in the course channel before Session 1.

---

## What you must finish

Four `TODO` markers are left in the repo deliberately. Each is a graded decision, not busywork.

| Where | What |
|---|---|
| `requirements.txt` | Regenerate with `pip-compile --generate-hashes` |
| `Dockerfile` | Pin the base image by digest; add `--require-hashes` |
| `cloudlayer/<your provider>.py` | Implement `upload`, `download`, `push_image` |
| This README | The reproducibility trade-off question below |

Then:

```bash
make image-push        # image reaches your registry, digest-pinned
dvc init && dvc remote add -d storage ${BLOB_URI}/dvc
dvc add data/raw && dvc push
```

Run five or more tracked runs varying something meaningful — not five identical runs with
different seeds.

---

## Reproducibility trade-off

Three things pin your build: hashed dependencies, a digest-pinned base image, and controlled
seeds. Under real time pressure you would keep some and drop others.

Which would you drop first, and what specifically breaks when you do? There is a defensible
answer, and we compare answers in Session 2. An answer that refuses to choose scores zero.

**My Answer:**
If I had limited time, I would drop the digest-pinned base image first. I would keep the hashed dependencies and fixed seeds because they directly affect the training environment and results. Without the digest, the same Docker base image tag could change in the future, so the environment might be slightly different. However, the training can still run. Without fixed dependencies or seeds, the package versions or training results could change more easily. Therefore, I think keeping the dependencies and seeds is more important for reproducing the reported metric.

---

## Notes for the grader

`make reproduce` does not require a cloud account, cloud credentials, or the local `cloud.env`
file. It generates the deterministic dataset, builds the Docker image for `linux/amd64`, and runs
the training container. The reproduced test ROC-AUC is expected to be approximately 0.848, within
the stated ±0.010 tolerance.

The command writes `reports/metrics.json` and the MLflow tracking database under `reports/`.
The container is run with the current user's UID/GID so that the mounted output directory remains
writable without elevated permissions.

---

## Checklist before you submit

- [ ] `make reproduce` works from a fresh clone, on a machine that is not yours
- [ ] `make verify` passes against your claim line
- [ ] `make test` — all tests pass
- [ ] `make portability-audit` — clean
- [ ] Image builds for `linux/amd64` and is pushed, digest-pinned
- [ ] `dvc push` completed; a grader can `dvc pull`
- [ ] Five or more tracked runs with params, metrics, data fingerprint, and commit SHA
- [ ] No placeholder or instruction blocks remain
- [ ] `git log -p | grep -i -E "secret|password|AKIA|BEGIN PRIVATE"` returns nothing

That last check is not optional. A credential in Git history is an automatic deduction in this
course, and rotating it is your responsibility, not the grader's.

## Lab 2 — Model promotion

In a real organisation, promotion to the `staging` stage should be restricted to an authorised ML engineer, MLOps engineer, or designated model owner rather than every developer.

Before promotion, they should check the model lineage, including the Git commit, data version, MLflow run ID, training job ID, container image digest, seed, validation metric, and test metric. They should also verify that the training job completed successfully and that the selected model passed the required validation and test checks.

---

## Lab 4 — Data contract tests

The Lab 4 CI pipeline includes data contract tests that are designed to catch realistic production data failures.

- `test_schema_columns_present_and_typed`: This would catch an upstream pipeline change where a required sensor column is removed, renamed, or produced with the wrong data type. Without this test, the model could receive an unexpected schema and fail or produce invalid predictions.

- `test_features_within_plausible_ranges`: This would catch a sensor or ETL unit-conversion error that produces values outside realistic limits, such as `load_pct` being scaled incorrectly. The data may still have the correct columns and types, but the values would no longer represent valid production inputs.

### Lab 4 — Drift detection threshold

The drift detector uses a PSI threshold of 0.25. Values below 0.10 are treated as normal variation, while 0.25 is used as the alert boundary so that the scheduled detector reacts to a substantial distribution shift rather than small sampling noise. When any monitored feature reaches PSI >= 0.25, the detector reports an alert and emits the feature PSI score to Cloud Monitoring.

### Lab 4 — Drift injection evidence

Injected drift into `temp_c` by shifting the feature mean from 79.58 to 85.58. The detector reported `temp_c PSI = 0.38333`, exceeding the alert threshold of 0.25. The first alert was recorded about 109 seconds after injection, and the configured email notification channel received the alert.

Postmortem:
1. A deliberate +6 shift was applied to `temp_c`.
2. The scheduled drift detector detected PSI 0.38333, above the 0.25 threshold.
3. Detection latency was approximately 109 seconds from injection to the first alert.
4. Cloud Monitoring triggered the configured email notification successfully.
5. Before retraining, the team should confirm whether the shift is genuine production drift or an upstream data-quality problem.

## Lab 5 Task 2 — Least Privilege IAM

Three service accounts separate training, serving, and CI/CD responsibilities.

| Identity | Service Account | IAM Roles | Purpose |
|---|---|---|---|
| Training | `lab5-pipeline@itcs355-6688176.iam.gserviceaccount.com` | `roles/aiplatform.user`, `roles/monitoring.metricWriter`, bucket-level `roles/storage.objectUser` | Run training operations, read training data, save model artifacts and checkpoints, and publish metrics. |
| Serving | `lab5-serving@itcs355-6688176.iam.gserviceaccount.com` | Bucket-level `roles/storage.objectViewer` | Read model artifacts without object modification or deletion permissions. |
| CI/CD | `github-actions@itcs355-6688176.iam.gserviceaccount.com` | `roles/aiplatform.user`, `roles/artifactregistry.writer`, `roles/monitoring.metricWriter`, `roles/iam.serviceAccountUser` on `lab5-serving` | Push container images, perform Vertex AI operations, and deploy with the dedicated serving identity. |

### Permission Removal Experiment

**Objective:** Verify that removing the serving identity's object-read permission prevents access to model artifacts.

**Test object:** `gs://itcs355-6688176/itcs355/lab5/model-version.txt`

**Procedure and results:**

1. Temporarily granted the test operator `roles/iam.serviceAccountTokenCreator` on `lab5-serving` to enable service account impersonation.
2. Read the test object as `lab5-serving`. The command succeeded with exit code `0`.
3. Removed `roles/storage.objectViewer` from `lab5-serving` at the bucket level.
4. Repeated the object-read operation using the same serving identity.
5. Observed `HTTPError 403`, with `Permission 'storage.objects.get' denied`.
6. Restored the original bucket-level `roles/storage.objectViewer` permission.
7. Removed the test operator's temporary `roles/iam.serviceAccountTokenCreator` permission.

**Conclusion:** Removing the serving identity's object-read permission caused the artifact access operation to fail. The experiment demonstrates an enforced IAM permission boundary. The original serving permission was restored after testing.

**Scope note:** The IAM roles above are the observed configuration. Further privilege reduction may be possible, particularly for the broad `roles/aiplatform.user` role. The serving identity's object-read permission is scoped to the project bucket rather than exclusively to the Lab 5 object prefix.
