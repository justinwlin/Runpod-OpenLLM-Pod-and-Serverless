import os
import openllm
import runpod
import asyncio

# Use the MODEL environment variable; fallback to a default if not set
model_name = os.getenv("MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
concurrency_modifier = int(os.getenv("CONCURRENCY_MODIFIER", 1))
mode_to_run = os.getenv("MODE_TO_RUN", "pod")
max_model_len = int(os.getenv("MAX_MODEL_LEN", 25000))

llm = openllm.LLM(model_name, backend="vllm", max_model_len=max_model_len)

async def handler(event):
    inputReq = event.get("input", {})
    user_prompt = inputReq.get("prompt")
    answerType = inputReq.get("answerType", "normal").lower()  # Ensure lowercase for comparison

    if answerType not in ["stream", "normal"]:
        print("answerType not correctly set, defaulting to stream")
        answerType = "stream"

    if not user_prompt:
        yield {"error": "No user prompt provided"}
        return

    try:
        if answerType == "stream":
            async for generation in llm.generate_iterator(user_prompt):
                yield {"text": generation.outputs[0].text}
        elif answerType == "normal":
            response = await llm.generate(user_prompt)
            yield {"text": response.outputs[0].text}  # Ensure consistent response format
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
        async for response in handler({"input": {"prompt": "Hello world", "answerType": "normal"}}):
            print(response)

    asyncio.run(main())
