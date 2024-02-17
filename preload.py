import os
import openllm

# Use the MODEL environment variable; fallback to a default if not set
model_name = os.getenv('MODEL', 'mistralai/Mistral-7B-Instruct-v0.1')

llm = openllm.LLM(model_name, backend="vllm")
