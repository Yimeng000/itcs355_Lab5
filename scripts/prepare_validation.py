from src import config
from cloudlayer.factory import get_adapter

cfg = config.load()
adapter = get_adapter(cfg)

uri = cfg.blob_uri.rstrip("/") + "/lab5/raw/sensors.csv"
adapter.download(uri, "data/raw/sensors.csv")

print("Dataset downloaded successfully")
