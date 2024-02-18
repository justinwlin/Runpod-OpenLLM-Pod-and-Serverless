import requests
import json
import time
import os
import sys

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

def submit_job_and_stream_output(api_key, endpoint_id, prompt):
    """
    Submits a job to the specified endpoint and streams the output as it becomes available.

    Args:
        api_key (str): The API key for authentication.
        endpoint_id (str): The endpoint ID for the Runpod function.
        prompt (str): The text prompt for the serverless function to process.
    Returns:
        None: Directly prints streamed outputs to the console.
    """
    # Submit job
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": {
            "prompt": prompt,
            "answerType": "stream"
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error submitting job: {response.text}")
        return

    response_json = response.json()
    task_id = response_json.get('id')
    if not task_id:
        print("Failed to get a job ID from the response.")
        return

    print(f"Job ID: {task_id}")

    # Stream output
    status_url = f"https://api.runpod.ai/v2/{endpoint_id}/stream/{task_id}"

    try:
        while True:  # Adjust the range or use a while loop for continuous polling
            time.sleep(1)  # Polling interval
            get_status = requests.get(status_url, headers=headers)
            if get_status.status_code == 200:
                status_response = get_status.json()
                if 'stream' in status_response and len(status_response['stream']) > 0:
                    for item in status_response['stream']:
                        print(item['output']['text'], end='')  # Adjust based on the actual structure
                if status_response.get('status') == 'COMPLETED':
                    print("\nJob completed.")
                    break
            else:
                print(f"Error streaming job output: {get_status.text}")
                break
    except Exception as e:
        print(f"An error occurred while streaming output: {e}")

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
# api_key = "XXX"
# server_endpoint_id = "XXX"
# prompt = "Describe the process of photosynthesis."

# # Submit a job to Runpod by using "normal" which will return it all at once
# response = submit_job_to_runpod(api_key, server_endpoint_id, prompt, "normal")
# if 'id' in response:
#     # If the response includes a job ID, it implies an asynchronous task.
#     job_id = response['id']
#     print(f"Job ID: {job_id}")
#     # Stream the output of the job
#     stream_output(api_key, server_endpoint_id, job_id)
#     print(check_job_status(api_key, server_endpoint_id, job_id, True))
# else:
#     # For synchronous tasks, print the output directly.
#     print("Response:", response)


# Streaming example

# api_key = "X"
# server_endpoint_id = "X"
# prompt = "Describe the process of photosynthesis."

# # Submit a job to Runpod
# response = submit_job_and_stream_output(api_key, server_endpoint_id, prompt)
