"""AWS adapter. Implement upload/download/push_image for Lab 1.

SDK:  pip install boto3
Docs: S3 -> boto3 client("s3"); ECR -> boto3 client("ecr") for the auth token,
      then `docker push` through subprocess.

Hints for Lab 1:
  * BLOB_URI looks like s3://bucket/prefix — parse it here, never in src/.
  * ECR login expires. If a push that worked yesterday fails today, re-authenticate:
        aws ecr get-login-password --region $REGION | docker login --username AWS \
            --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
  * Return the DIGEST reference from push_image, not the tag. `docker inspect` or the
    push output gives you the sha256.
  * Tag the bucket objects and the ECR repository with cfg.tags(1).
"""
from __future__ import annotations


from cloudlayer.base import CloudAdapter


class AwsAdapter(CloudAdapter):
    def upload(self, local_path: str, key: str) -> str:
        import boto3
        from urllib.parse import urlsplit

        parsed = urlsplit(self.cfg.blob_uri)
        if parsed.scheme != "s3" or not parsed.netloc:
            raise ValueError("AWS BLOB_URI must use s3://bucket/prefix")

        bucket = parsed.netloc
        prefix = parsed.path.strip("/")
        object_key = "/".join(
            part for part in (prefix, key.lstrip("/")) if part
        )
        if not object_key:
            raise ValueError("S3 object key must not be empty")

        boto3.client("s3", region_name=self.cfg.region).upload_file(
            local_path, bucket, object_key
        )
        return f"s3://{bucket}/{object_key}"

    def download(self, uri: str, local_path: str) -> None:
        import boto3
        from pathlib import Path
        from urllib.parse import urlsplit

        parsed = urlsplit(uri)
        if parsed.scheme != "s3" or not parsed.netloc or not parsed.path.strip("/"):
            raise ValueError("AWS download URI must use s3://bucket/object")

        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        boto3.client("s3", region_name=self.cfg.region).download_file(
            parsed.netloc, parsed.path.lstrip("/"), local_path
        )

    def push_image(self, local_tag: str) -> str:
        raise NotImplementedError("TODO Lab 1: authenticate to ECR, push, return repo@sha256:...")

    def invoke(self, endpoint: str, payload: dict) -> dict:
        import json
        import boto3

        client = boto3.client(
            "sagemaker-runtime",
            region_name=self.cfg.region,
        )

        response = client.invoke_endpoint(
            EndpointName=endpoint,
            ContentType="application/json",
            Accept="application/json",
            Body=json.dumps(payload).encode("utf-8"),
        )

        result = json.loads(response["Body"].read().decode("utf-8"))
        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object from SageMaker endpoint")

        return result

    # submit_training / register_model  -> Lab 2 (SageMaker training job + model package group)
    # deploy / invoke                   -> Lab 3 (SageMaker real-time endpoint)
    # emit_metric                       -> Lab 4 (CloudWatch put_metric_data)
    # generate                          -> Lab 5 (managed LLM endpoint; read the usage block for tokens)
    # teardown                          -> Lab 5 (resourcegroupstaggingapi to find by tag)
