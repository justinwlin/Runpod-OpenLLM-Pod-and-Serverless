import os
import openllm
import runpod

# Use the MODEL environment variable; fallback to a default if not set
model_name = os.getenv("MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
concurrency_modifier = os.getenv("CONCURRENCY_MODIFIER", 1)
mode_to_run = os.getenv("MODE_TO_RUN", "pod")

llm = openllm.LLM(model_name, backend="vllm")


def handler(event):
    input = event["input"]
    return input


def adjust_concurrency():
    """
    Adjusts the concurrency level based on the current request rate.
    """
    return concurrency_modifier


# Only if we are in the correct mode should we run this
if mode_to_run == "both" or mode_to_run == "serverless":
    runpod.start({"handler": handler, "concurrency_modifier": adjust_concurrency})

if mode_to_run == "pod":
    handler({input: {"prompt": "This is a test prompt."}})
