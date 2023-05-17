ARG PYTHON_VERSION=3.9
# Python build stage
FROM python:${PYTHON_VERSION}-slim-bullseye as python_base
WORKDIR /opt/venv
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev apt-utils  && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
COPY  ./src/bert/requirements.txt .

ENV TORCH_VERSION=2.0.1
ENV TORCHVISION_VERSION=0.15.2
ENV TORCHAUDIO_VERSION=2.0.2
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/python3 -m pip install -U --upgrade pip --no-cache-dir && \
    $VIRTUAL_ENV/bin/pip install --upgrade setuptools wheel psutil cleanpy --no-cache-dir && \
    $VIRTUAL_ENV/bin/pip install --upgrade torch==${TORCH_VERSION}+cpu torchvision==${TORCHVISION_VERSION}+cpu torchaudio==${TORCHAUDIO_VERSION} --index-url https://download.pytorch.org/whl/cpu --no-cache-dir && \
    $VIRTUAL_ENV/bin/pip install -r requirements.txt --no-cache-dir  && \
    apt-get purge -y --auto-remove gcc python3-dev apt-utils && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    cleanpy -v -f -a /opt/venv/
    # Remove any weight that we can to keep under the 2048MB limit of Cloud Foundry
    # rm -rf /root/.cache/pip && \
    # rm -rf /usr/local/lib/python3.9/distutils && \
    # rm -rf /usr/local/lib/python3.9/site-packages/pip/_vendor/ && \
    # find /opt/venv/ -type d \(-name '__pycache__' -name 'tests' -o -name 'test' -o -name 'testing' \) -exec rm -rf {} + && \
    # find /opt/venv/ -type f \( -name '.pyc' -name '.pyo' -name '*_test.py' -o -name 'test.py' \) -delete

# Python artifact stage
# FROM python_base as artifact_build
# WORKDIR /vendor
# COPY  ./src/bert/requirements.txt .
# ENV VIRTUAL_ENV=/opt/venv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# RUN  --mount=type=cache,target=/root/.cache \ 
#     $VIRTUAL_ENV/bin/pip download -r requirements.txt --no-binary=:none: --no-cache-dir

# Final stage
FROM gcr.io/distroless/python3-debian11:debug as final
# FROM python:${PYTHON_VERSION}-slim-bullseye as final
ENV PYTHON_VERSION=3.9
ENV PYTHONPATH "${PYTHONPATH}:/opt/venv/lib/python${PYTHON_VERSION}/site-packages"
COPY  ./src/**/*.py /opt/venv/
COPY --from=python_base /opt/venv/ /opt/venv/
COPY --from=python_base /usr/lib/ /usr/lib/
COPY --from=python_base /usr/local/lib/ /usr/local/lib/
ENV SPARK_HOME=/opt
ENV PATH=$PATH:/opt/bin
ENV PATH /opt/venv/bin:$PATH
WORKDIR /opt/venv
CMD ["python3", "/app.py"]