import argparse
from google.cloud import aiplatform
from src import config

parser = argparse.ArgumentParser()
parser.add_argument("--run", action="store_true")
args = parser.parse_args()

cfg = config.load()
service_account = (
    f"lab5-pipeline@{cfg.project_id}.iam.gserviceaccount.com"
)

aiplatform.init(
    project=cfg.project_id,
    location=cfg.region,
)

job = aiplatform.PipelineJob(
    display_name="itcs355-lab5-pipeline",
    template_path="pipeline/lab5-pipeline.json",
    pipeline_root=f"{cfg.blob_uri.rstrip('/')}/lab5/pipeline-root",
    enable_caching=False,
)

if args.run:
    job.submit(service_account=service_account)
    print("Pipeline submitted:", job.resource_name)
else:
    print("Configuration ready. No cloud job submitted.")
