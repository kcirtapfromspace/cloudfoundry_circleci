ARG PYTHON_VERSION=3.9
# Python build stage
FROM python:${PYTHON_VERSION}-slim-bullseye as python_build
WORKDIR /opt/venv
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
COPY  ./src/requirements.txt .
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python3 -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/python3 -m pip install -U --upgrade pip && \
    $VIRTUAL_ENV/bin/pip install --upgrade pip setuptools wheel psutil
# Python install stage
FROM  python_build as python_install
# Use buildkit to cache pip dependencies
# https://pythonspeed.com/articles/docker-cache-pip-downloads/
RUN --mount=type=cache,target=/root/.cache \ 
    $VIRTUAL_ENV/bin/pip install torch==1.9.1+cpu torchvision==0.10.1+cpu torchaudio===0.9.1 -f https://download.pytorch.org/whl/torch_stable.html && \
    $VIRTUAL_ENV/bin/pip install -U sentence-transformers psycopg2-binary && \
    apt-get purge -y --auto-remove gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    # find /opt/venv/ -name '*.pyc' -delete
    # python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('bert-base-nli-mean-tokens')" && \


# Final stage 
# FROM gcr.io/distroless/python3-debian11:debug
FROM gcr.io/distroless/python3-debian11:debug
ENV PYTHON_VERSION=3.9
COPY  ./src/*.py /opt/venv/
COPY --from=python_install /opt/venv/ /opt/venv/
COPY --from=python_install /usr/lib/ /usr/lib/
ENV SPARK_HOME=/opt
ENV PATH=$PATH:/opt/bin
ENV PATH /opt/venv/bin:$PATH
WORKDIR /opt/venv
CMD ["python3", "/app.py"]