FROM python:3.11

# Setting environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off
ENV ALEMBIC_CONFIG=/app/src/alembic/alembic.ini

# Installing dependencies
RUN apt update && apt install -y \
    gcc \
    netcat-openbsd \
    dos2unix \
    && apt clean

# Install Poetry
RUN python -m pip install --upgrade pip && \
    pip install poetry

# Copy dependency files
COPY ./poetry.lock /app/src/poetry/poetry.lock
COPY ./pyproject.toml /app/src/poetry/pyproject.toml
COPY ./alembic.ini /app/src/alembic/alembic.ini

# Configure Poetry to avoid creating a virtual environment
RUN poetry config virtualenvs.create false

# Selecting a working directory
WORKDIR /app/src/poetry

# Install dependencies with Poetry
RUN poetry install --no-root --only main

# Selecting a working directory
WORKDIR /app/src/cinema

# Copy the source code
COPY ./src .

# Copy commands
COPY ./commands /commands

# Ensure Unix-style line endings for scripts
RUN dos2unix /commands/*.sh

# Add execute bit to commands files
RUN chmod +x /commands/*.sh
