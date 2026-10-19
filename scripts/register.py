from src import config, seeds
from cloudlayer.factory import get_adapter
from pathlib import Path

cfg = config.load()
adapter = get_adapter(cfg)

model_uri = (
    f"{cfg.blob_uri.rstrip('/')}/"
    f"lab2/models/seed-{seeds.DEFAULT_SEED}"
)

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
