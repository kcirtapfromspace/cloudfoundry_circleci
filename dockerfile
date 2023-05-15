ARG PYTHON_VERSION=3.9
# Python build stage
FROM python:${PYTHON_VERSION}-slim-bullseye as python_base
WORKDIR /opt/venv
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/python3 -m pip install -U --upgrade pip --no-cache-dir && \
    $VIRTUAL_ENV/bin/pip install --upgrade pip setuptools wheel psutil --no-cache-dir
# # Python install stage
FROM  python_base as python_install
WORKDIR /opt/venv
# Use buildkit to cache pip dependencies
# https://pythonspeed.com/articles/docker-cache-pip-downloads/
RUN --mount=type=cache,target=/root/.cache \ 
    $VIRTUAL_ENV/bin/pip install \
        -f https://download.pytorch.org/whl/torch_stable.html\
        psycopg2-binary\
        sentence-transformers\ 
        torch \
        torchaudio\
        torchvision\
        --no-cache-dir && \
    apt-get purge -y --auto-remove gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    find /opt/venv/ -name '*.pyc' -delete && \
    # Remove any weight that we can to keep under the 2048MB limit of Cloud Foundry
    rm -rf /root/.cache/pip && \
    rm -rf /usr/local/lib/python3.9/distutils && \
    rm -rf /usr/local/lib/python3.9/site-packages/pip/_vendor/ && \
    find /opt/venv/ -type d \( -name 'tests' -o -name 'test' -o -name 'testing' \) -exec rm -rf {} + && \
    find /opt/venv/ -type f \( -name '*_test.py' -o -name 'test.py' \) -delete

ARG PYTHON_VERSION=3.9
# Python artifact stage
FROM python_base as artifact_build
WORKDIR /vendor
COPY  ./src/buildpack_deploy/bert/requirements.txt .
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN  --mount=type=cache,target=/root/.cache \ 
    $VIRTUAL_ENV/bin/pip download -r requirements.txt --no-cache-dir

# Final stage
FROM gcr.io/distroless/python3-debian11:debug
ENV PYTHON_VERSION=3.9
ENV PYTHONPATH "${PYTHONPATH}:/opt/venv/lib/python${PYTHON_VERSION}/site-packages"
COPY  ./src/**/*.py /opt/venv/
COPY --from=python_install /opt/venv/ /opt/venv/
COPY --from=python_install /usr/lib/ /usr/lib/
COPY --from=python_install /usr/local/lib/ /usr/local/lib/
ENV SPARK_HOME=/opt
ENV PATH=$PATH:/opt/bin
ENV PATH /opt/venv/bin:$PATH
WORKDIR /opt/venv
CMD ["python3", "/app.py"]