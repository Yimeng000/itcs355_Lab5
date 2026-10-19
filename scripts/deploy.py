import argparse
from pathlib import Path

from src import config
from cloudlayer.factory import get_adapter

parser = argparse.ArgumentParser()
parser.add_argument("--target", default="staging")
args = parser.parse_args()

cfg = config.load()
adapter = get_adapter(cfg)

version_file = Path("/tmp/lab5-model-version.txt")
version_uri = f"{cfg.blob_uri.rstrip('/')}/lab5/model-version.txt"

adapter.download(version_uri, str(version_file))
version = version_file.read_text().strip()

if not version:
    raise ValueError("Model version is empty")

print(f"Deploying model version {version} to {args.target}")

endpoint = adapter.deploy(
    version,
    f"itcs355-lab5-{args.target}",
    "n1-standard-2",
)

print(f"Endpoint: {endpoint}")
