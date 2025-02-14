# Dockerfile for FastAPI application (with Telegram bot and Redis) deployed on Hugging Face Spaces
FROM python:3.11-slim

# Install Redis server (requires root privileges)
USER root
RUN apt-get update && \
    apt-get install -y redis-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and switch to a non-root user for security
RUN useradd -m -u 1000 user
USER user

# Ensure local binaries are in PATH and disable output buffering
ENV PATH="/home/user/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all application code into the container
COPY --chown=user . /app

# Copy the entrypoint script into the container and make it executable
COPY --chown=user entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the port used by the FastAPI app (Hugging Face Spaces expects this)
EXPOSE 7860

# Start everything via the entrypoint script
CMD ["/app/entrypoint.sh"]
