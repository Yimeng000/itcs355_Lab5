# Lab 5 — Teardown Report

## Project Information

- GCP Project: itcs355-6688176
- Region: asia-southeast1
- Scope: Lab 5 resources only
- Evidence directory: reports/lab5/teardown-evidence/

## Resource Cleanup Results

| Resource | Result |
|---|---|
| Lab 5 Vertex AI Endpoint | Deleted and verified |
| Lab 5 Pipeline Schedule | Deleted and verified |
| Four Lab 5 Model Registry resources | Deleted and verified |
| Lab 5 Pipeline Jobs | 1 succeeded, 3 failed; all terminated |
| Active Custom Training Jobs | No RUNNING, PENDING, or QUEUED jobs returned |
| Lab 5 GCS live objects | Deleted and verified |
| Lab 5 training Docker images | Deleted and verified |
| Three identified Lab 5 serving images | Deleted and verified |
| Compute Engine VMs | No instances found |
| Cloud Run Services | No services found in asia-southeast1 |
| Vertex AI Persistent Resources | No resources found |

## Shared Resources Preserved

- Vertex AI Endpoint: itcs355-lab4-staging
- Cloud Scheduler: itcs355-drift-schedule (PAUSED)
- Cloud Run Job: itcs355-drift-job
- Artifact Registry packages for Lab 1, Drift Monitoring, and Capstone
- Other Model Registry resources unrelated to the identified Lab 5 models

## Cloud Storage Backup and Retention

Eight live GCS files were backed up locally before deletion:

reports/lab5/gcs-backup/lab5/

The Lab 5 GCS prefix has no remaining live objects.

The bucket has a seven-day Soft Delete policy. A subsequent
query returned 29 soft-deleted object generations. These may
continue to incur storage charges during their retention period.

The shared bucket and its retention settings were preserved.

## Evidence

Resource inspection results are stored under:

reports/lab5/teardown-evidence/

## Remaining Verification

- Capture screenshots showing the absence of Lab 5 resources.
- Review Cloud Billing at least 24 hours after teardown.
- Account for billing reporting delays and retained GCS storage.
- Confirm that no new Lab 5 resources have been created.

## Conclusion

The identified Lab 5 deployment, training schedule, models,
container images, and live storage objects have been removed.

No active Lab 5 compute resources were identified in the
checks performed. Complete billing cessation has not yet
been independently verified.
