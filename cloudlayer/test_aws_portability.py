"""Lab 5 Task 4: AWS portability tests without real cloud resources."""

import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import boto3
from moto import mock_aws

from cloudlayer.factory import get_adapter


def test_aws_upload_download(tmp_path, monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    with mock_aws():
        boto3.client("s3", region_name="us-east-1").create_bucket(
            Bucket="itcs355-portability-test"
        )

        cfg = SimpleNamespace(
            provider="aws",
            blob_uri="s3://itcs355-portability-test/lab5",
            region="us-east-1",
        )
        adapter = get_adapter(cfg)

        source = tmp_path / "source.txt"
        target = tmp_path / "downloads" / "result.txt"
        source.write_text("AWS portability test", encoding="utf-8")

        uri = adapter.upload(str(source), "probe/source.txt")
        assert uri == "s3://itcs355-portability-test/lab5/probe/source.txt"

        adapter.download(uri, str(target))
        assert target.read_bytes() == source.read_bytes()


def test_aws_invoke():
    cfg = SimpleNamespace(provider="aws", region="us-east-1")
    adapter = get_adapter(cfg)

    payload = {"rows": []}
    expected = {"predictions": [0.87]}

    class FakeSageMaker:
        def invoke_endpoint(self, **kwargs):
            assert kwargs["EndpointName"] == "test-endpoint"
            assert kwargs["ContentType"] == "application/json"
            assert json.loads(kwargs["Body"]) == payload
            return {
                "Body": io.BytesIO(json.dumps(expected).encode("utf-8"))
            }

    with patch("boto3.client", return_value=FakeSageMaker()):
        result = adapter.invoke("test-endpoint", payload)

    assert result == expected


def test_provider_swap():
    aws = get_adapter(SimpleNamespace(provider="aws"))
    gcp = get_adapter(SimpleNamespace(provider="gcp"))

    assert type(aws).__name__ == "AwsAdapter"
    assert type(gcp).__name__ == "GcpAdapter"
