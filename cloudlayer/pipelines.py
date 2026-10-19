"""Lab 5 — compile pipeline/pipeline.yaml into your provider's pipeline service.

This module is Layer 3, so provider SDKs are allowed here and nowhere else. The DAG stays
in YAML; only the translation lives here. That separation is what you argue for or against
in Lab 5 Task 4.

Implement ONE compile function, for your provider.
"""
# from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from kfp import compiler, dsl

from src import config

SPEC = Path(__file__).resolve().parents[1] / "pipeline" / "pipeline.yaml"


def load_spec(path: Path = SPEC) -> dict[str, Any]:
    """Read the neutral DAG and expand ${VAR} references from the environment."""
    raw = path.read_text()
    for key, value in os.environ.items():
        raw = raw.replace(f"${{{key}}}", value)
    return yaml.safe_load(raw)


def compile_aws(spec: dict[str, Any]):
    """SageMaker Pipelines.

    Each step becomes a ProcessingStep or TrainingStep; `condition` becomes a
    ConditionStep. Note that SageMaker's condition steps branch rather than abort, so
    `on_failure: abort` needs a FailStep on the else branch — an asymmetry worth
    mentioning in your Lab 5 write-up.
    """
    raise NotImplementedError("TODO Lab 5: build a sagemaker.workflow.pipeline.Pipeline")


def compile_azure(spec: dict[str, Any]):
    """Azure ML Pipelines.

    Each step becomes a command component; the DAG is expressed as a @pipeline function.
    Conditions use azure.ai.ml.dsl.condition, which is closer to this YAML than the other
    two providers' equivalents.
    """
    raise NotImplementedError("TODO Lab 5: build an azure.ai.ml pipeline job")

def make_gcp_gate_component(step: dict[str, Any]):
    @dsl.container_component
    def gate(decision: dsl.OutputPath(str)):
        return dsl.ContainerSpec(
            image=step["image"],
            command=[
                "python", "scripts/evaluation_gate.py",
                "--metrics", "/outputs/metrics.json",
                "--decision-out", decision,
            ],
        )

    return gate

def make_gcp_component(step: dict[str, Any]):
    @dsl.container_component
    def run_step():
        return dsl.ContainerSpec(
            image=step["image"],
            command=step["command"],
        )

    return run_step

def compile_gcp(spec: dict[str, Any]):
    """Vertex AI Pipelines.

    Kubeflow Pipelines underneath: steps become container components, conditions become
    dsl.If blocks. The compiled artifact is a JSON file you submit, so your build step
    produces a file rather than an object — different from the other two.
    """

    """Compile the neutral DAG into a KFP pipeline JSON."""

    cfg = config.load()
    env_vars = {
        "CLOUD_PROVIDER": cfg.provider,
        "PROJECT_ID": cfg.project_id,
        "REGION": cfg.region,
        "BLOB_URI": cfg.blob_uri,
        "CONTAINER_REGISTRY": cfg.container_registry,
        "MLFLOW_TRACKING_URI": cfg.mlflow_tracking_uri,
        "MODEL_REGISTRY_NAME": cfg.model_registry_name,
        "IDENTITY_REF": cfg.identity_ref,
    }

    def configure_task(task):
        for key, value in env_vars.items():
            task.set_env_variable(key, value)
        return task

    components = {
        step["name"]: make_gcp_component(step)
        for step in spec["steps"]
    }

    components["evaluate"] = make_gcp_gate_component(
        next(s for s in spec["steps"] if s["name"] == "evaluate")
    )

    @dsl.pipeline(name=spec["name"])
    def training_pipeline():
        tasks = {}

        for step in spec["steps"]:
            name = step["name"]

            if name == "register":
                with dsl.If(tasks["evaluate"].outputs["decision"] == "pass"):
                    register = configure_task(components["register"]())
                    register.after(tasks["evaluate"])

                    deploy = configure_task(components["deploy_staging"]())
                    deploy.after(register)
                break

            task = configure_task(components[name]())

            for dependency in step.get("depends_on", []):
                task.after(tasks[dependency])

            tasks[name] = task

    output = "pipeline/lab5-pipeline.json"

    compiler.Compiler().compile(
        pipeline_func=training_pipeline,
        package_path=output,
    )

    print(f"Pipeline compiled: {output}")
    return output

COMPILERS = {"aws": compile_aws, "azure": compile_azure, "gcp": compile_gcp}


def compile_for(provider: str, spec: dict[str, Any] | None = None):
    spec = spec or load_spec()
    try:
        return COMPILERS[provider.lower()](spec)
    except KeyError:
        raise ValueError(f"No pipeline compiler for {provider!r}") from None
