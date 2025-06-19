FROM python:3.13-slim

ARG DEV

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# POETRY_VERSION can be set if you intend to use it with pip install poetry==<version>
# ENV POETRY_VERSION=2.1.3 

# Install prerequisites for building some Python packages and pip, then install Poetry using pip
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip build-essential \
    && pip install poetry \
    && poetry config virtualenvs.create false

WORKDIR /src

# Copy dependency definition files
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry.
# If DEV is true, install all dependencies including dev, otherwise only main.
# --no-root is used because we are installing dependencies before copying the actual src code,
# and we don't want Poetry to try to install the 'src' package itself at this stage.
RUN if [ "$DEV" = "true" ]; then poetry install --no-root; else poetry install --no-root --only main; fi

# Copy the application source code
# This copies the content of ./src from the host to /src in the container
COPY ./src/. ./

EXPOSE 8008

# CMD is expected to be in docker-compose.yml
