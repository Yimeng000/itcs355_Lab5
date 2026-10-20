from src import config
from cloudlayer.factory import get_adapter

cfg = config.load()
adapter = get_adapter(cfg)

job_id = adapter.submit_training(
    cfg.training_image_uri,
    {
        "checkpoint": True,
        "metrics_out": "/app/reports/metrics.json",
    },
)

result = adapter.wait_training(job_id)

if result["state"] != "PIPELINE_STATE_SUCCEEDED":
    raise RuntimeError(f"Training failed: {result['state']}")

print("Spot training completed successfully")
