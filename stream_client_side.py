import requests
import json
import time

'''
Client-side code that you can use to make requests to your deployed runpod API.
'''

def submit_job_to_runpod(api_key, server_endpoint_id, prompt, answer_type="normal"):
    """
    Submits a job to a specific Runpod serverless endpoint.

    Args:
        api_key (str): Runpod API key for authentication.
        server_endpoint_id (str): The specific endpoint ID for the serverless function on Runpod.
        prompt (str): The text prompt for the serverless function to process.
        answer_type (str): Specifies how the answer should be returned ('normal' or 'stream').

    Returns:
        dict: Direct response from the serverless function or job ID if asynchronous.
    """
    endpoint_url = f"https://api.runpod.ai/v2/{server_endpoint_id}/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "input": {
            "prompt": prompt,
            "answerType": answer_type.lower()
        }
    }
    response = requests.post(endpoint_url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        # For synchronous response, return the output directly.
        return response.json()
    else:
        raise Exception(f"Runpod job submission failed: {response.text}")

def stream_runpod_job_output(api_key, server_endpoint_id, job_id):
    """
    Streams the output of a Runpod job in real-time.

    Args:
        api_key (str): Runpod API key for authentication.
        server_endpoint_id (str): The specific endpoint ID for the serverless function on Runpod.
        job_id (str): The job ID to stream output for.

    Returns:
        None: Directly prints streamed outputs to the console.
    """
    stream_url = f"https://api.runpod.ai/v2/{server_endpoint_id}/stream/{job_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(stream_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'stream' in data and len(data['stream']) > 0:
            for item in data['stream']:
                print(item['output'], end='')
            if data.get('status') == 'COMPLETED':
                print("\nJob completed.")
        else:
            print("No output available yet.")
    else:
        raise Exception(f"Error streaming job output: {response.text}")

def check_job_status(api_key, server_endpoint_id, job_id, poll=False, polling_interval=20):
    """
    Checks the status of a job on Runpod.

    Args:
        api_key (str): Runpod API key for authentication.
        server_endpoint_id (str): The specific endpoint ID for the serverless function on Runpod.
        job_id (str): The job ID to check the status for.
        poll (bool, optional): If True, continue to check the status at intervals until the job is completed. Defaults to False.
        polling_interval (int, optional): Time in seconds to wait between status checks if polling. Defaults to 20 seconds.

    Returns:
        dict: The latest status response from Runpod. If polling is enabled, returns the final status once completed.
    """
    url = f"https://api.runpod.ai/v2/{server_endpoint_id}/status/{job_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            status_response = response.json()
            status = status_response.get("status", "UNKNOWN")
            print(f"Current job status: {status}")

            if not poll or status in ["COMPLETED", "FAILED", "CANCELLED"]:
                return status_response
            else:
                time.sleep(polling_interval)
        else:
            raise Exception(f"Failed to check job status: {response.text}")
            break

# Example usage
api_key = "your_runpod_api_key"
server_endpoint_id = "your_server_endpoint_id"
prompt = "Describe the process of photosynthesis."

# Submit a job to Runpod
response = submit_job_to_runpod(api_key, server_endpoint_id, prompt, "normal")
if 'id' in response:
    # If the response includes a job ID, it implies an asynchronous task.
    job_id = response['id']
    print(f"Job ID: {job_id}")
    # Stream the output of the job
    stream_runpod_job_output(api_key, server_endpoint_id, job_id)
else:
    # For synchronous tasks, print the output directly.
    print("Response:", response)
