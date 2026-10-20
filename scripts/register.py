from src import config, seeds
from cloudlayer.factory import get_adapter
from pathlib import Path
from google.cloud import aiplatform

cfg = config.load()
adapter = get_adapter(cfg)

model_uri = (
    f"{cfg.blob_uri.rstrip('/')}/"
    f"lab5/models/seed-{seeds.DEFAULT_SEED}"
)

aiplatform.init(project=cfg.project_id, location=cfg.region)

models = aiplatform.Model.list(
    filter=f'display_name="{cfg.model_registry_name}"'
)

version = None

if models:
    from google.cloud import aiplatform_v1

    client = aiplatform_v1.ModelServiceClient(
        client_options={
            "api_endpoint": f"{cfg.region}-aiplatform.googleapis.com"
        }
    )

    for model in client.list_model_versions(
        name=models[0].resource_name
    ):
        if model.artifact_uri.rstrip("/") == model_uri.rstrip("/"):
            version = model.version_id
            print(f"Reusing registered model version: {version}")
            break

if version is None:
    version = adapter.register_model(
        model_uri,
        cfg.model_registry_name,
    )

print(f"Registered model version: {version}")

version_file = Path("/tmp/lab5-model-version.txt")
version_file.write_text(str(version))

uri = adapter.upload(
    str(version_file),
    "lab5/model-version.txt",
)

print(f"Version saved: {uri}")
