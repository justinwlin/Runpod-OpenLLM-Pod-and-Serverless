import os
import openllm
import runpod
import asyncio
import torch
import numpy as np
import random
import uuid

# Use the MODEL environment variable; fallback to a default if not set
model_name = os.getenv("MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
concurrency_modifier = int(os.getenv("CONCURRENCY_MODIFIER", 1))
mode_to_run = os.getenv("MODE_TO_RUN", "pod")
model_length_default = 25000

print("------- ENVIRONMENT VARIABLES -------")
print("Model name: ", model_name)
print("Concurrency: ", concurrency_modifier)
print("Mode running: ", mode_to_run)
print("Model Length: ", os.getenv("MAX_MODEL_LEN"))
print("------- -------------------- -------")

try: 
    max_model_len = int(os.getenv("MAX_MODEL_LEN", model_length_default))
    llm = openllm.LLM(model_name, backend="vllm", max_model_len=max_model_len)
except: 
    llm = openllm.LLM(model_name, backend="vllm", max_model_len=model_length_default)


async def handler(event):
    inputReq = event.get("input", {})
    user_prompt = inputReq.get("prompt")
    answerType = inputReq.get("answerType", "normal").lower()
    # Retrieve temperature from the event, defaulting to 0.7 if not provided.
    options = inputReq.get("options", {})

    if answerType not in ["stream", "normal"]:
        print("answerType not correctly set, defaulting to stream")
        answerType = "stream"

    if not user_prompt:
        yield {"error": "No user prompt provided"}
        return
    print("LLM: ", llm)
    print("Options: ", options)

    try:
        if answerType == "stream":
            async for generation in llm.generate_iterator(user_prompt, **options):
                yield {"text": generation.outputs[0].text}
        elif answerType == "normal":
            print("Generating response:...")
            response = await llm.generate(user_prompt, **options)  # Pass temperature and other options here.
            yield {"text": response.outputs[0].text}
    except Exception as e:
        yield {"error": str(e)}

def adjust_concurrency(current_concurrency):
    return concurrency_modifier

if mode_to_run in ["both", "serverless"]:
    runpod.serverless.start({
        "handler": handler,
        "concurrency_modifier": adjust_concurrency,
        "return_aggregate_stream": True,
    })

if mode_to_run == "pod":
    async def main():
        randomness = str(uuid.uuid4())
        prompt = f"[INST] You are a helpful code assistant. Your task is to generate a valid JSON object. The JSON object will contain only a single key 'idea [/INST]"
        requestObject = {"input": {"prompt": prompt, "answerType": "normal", "options": { "temperature": 0.8, "top_k": 1000}}}
        
        async for response in handler(requestObject):
            print(response)

    asyncio.run(main())
