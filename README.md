# Docker Configuration for OpenLLM with Runpod

## Summary

This Docker configuration utilizes OpenLLM for both GPU and Serverless deployments on Runpod. It employs an environment variable, `MODE_TO_RUN`, to dictate the startup behavior. Depending on the `MODE_TO_RUN` value, the configuration may launch `handler.py` for serverless operations or initiate OpenSSH and Jupyter Lab for GPU pods. This adaptable setup allows for straightforward modifications to meet various deployment requirements.

## Environment Variables

Below is a table of the environment variables that can be passed to the Docker container. These variables enable customization of the deployment's behavior, offering flexibility for different scenarios.

| Variable               | Description                                                                                                                  | Expected Values              | Default Value                   |
|------------------------|------------------------------------------------------------------------------------------------------------------------------|------------------------------|---------------------------------|
| `MODE_TO_RUN`          | Determines the container's operational mode, affecting the execution of `handler.py` and the initiation of services.         | `serverless`, `pod`, `both` | None                            |
| `MODEL`                | Identifier for the OpenLLM model to be used. Specifies which AI model your applications will utilize.                        | Model Identifier (string)   | None                            |
| `CONCURRENCY_MODIFIER` | A factor used to adjust the concurrency level for handling requests, allowing for tuning based on workload.                  | Integer                     | `1`                             |

### Note on Model Identifiers

To find specific model identifiers for use with OpenLLM, visit the [OpenLLM GitHub repository](https://github.com/bentoml/OpenLLM). This resource offers a comprehensive list of available models and their identifiers, which can be utilized to set the `MODEL` environment variable.

### Mode Descriptions

- `serverless`: Executes `handler.py` for serverless request handling, optimal for scalable, efficient deployments.
- `pod`: Initiates essential services like OpenSSH and Jupyter Lab, bypassing `handler.py`, suitable for development or tasks requiring GPU resources.
- `both`: Combines the functionalities of both modes by executing `handler.py` and initiating essential services, ideal for debugging serverless deployments with additional tool access b/c you can set a minimum active worker to 1 and then essentially just use jupyter notebook / ssh to debug the worker.

## Getting Started

1. **Build the Docker Image**: Create your image using the Dockerfile, optionally specifying the `MODEL` and `CONCURRENCY_MODIFIER` variables as needed.

    ```sh
    docker build --build-arg MODEL_ARG=<your_model_identifier> -t your_image_name .
    ```

2. **Run the Container**: Start your container with the desired `MODE_TO_RUN` and any other environment variables.

    ```sh
    docker run -e MODE_TO_RUN=serverless -e CONCURRENCY_MODIFIER=2 your_image_name
    ```

3. **Accessing Services**: Depending on the chosen mode,
    - In `serverless` and `both`, interact with the deployed model through the specified handler.
    - In `pod` and `both`, access Jupyter Lab and SSH services as provided.