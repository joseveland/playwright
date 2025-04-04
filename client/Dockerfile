## For local testing as it internally uses a runtime-interface-emulator, but `ENTRYPOINT` needs to be commented later
FROM public.ecr.aws/lambda/python:3.12
## Custom image that I prefer, however the `ENTRYPOINT` must be defined next to reach `awslambdaric` module
# FROM python:3.11-slim

LABEL authors="jose.velandia"

## There are a few defaults but those can change with `--build-arg` option when building this Dockerfile (If entered)
ARG AWS_LAMBDA_LOG_FORMAT="TEXT"
ARG AWS_LAMBDA_LOG_LEVEL="DEBUG"

ENV AWS_LAMBDA_LOG_FORMAT=${AWS_LAMBDA_LOG_FORMAT}
ENV AWS_LAMBDA_LOG_LEVEL=${AWS_LAMBDA_LOG_LEVEL}

COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY . ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

## `ENTRYPOINT` won't work if deployed locally as it needs a `AWS_LAMBDA_RUNTIME_API` env-var host (or rie-emulator) to connect to, however it will work remotely deployed with my desired base-image as it will have `AWS_LAMBDA_RUNTIME_API` there.
# RUN pip install awslambdaric
# ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
## CMD having the python nomenclauture pointing to the main method is the way to indicate this image where to look for.
## As stated here https://www.youtube.com/watch?v=wbsbXfkv47A or here https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/deploy-lambda-functions-with-container-images.html
CMD ["main_async.main"]
# CMD ["main_sync.main"]    # Alternative python file/pointer to a handler
