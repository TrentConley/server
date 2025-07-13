# --- Stage 1: Build Stage ---
# Use an official Python image that includes build tools.
FROM python:3.11-slim-bullseye as builder

# Set the working directory
WORKDIR /app

# Install poetry for dependency management
# Using poetry helps in creating a lock file for deterministic builds
RUN pip install poetry

# Copy only the files needed for dependency installation
COPY pyproject.toml poetry.lock* ./

# Install dependencies into a virtual environment
# This isolates dependencies and keeps the final image clean
RUN poetry config virtualenvs.in-project true && \
    poetry install --only=main --no-root


# --- Stage 2: Final Stage ---
# Use a slim, non-root base image for the final application
FROM python:3.11-slim-bullseye

# Set the working directory
WORKDIR /app

# Create a non-root user for security
# Running as a non-root user is a security best practice
RUN useradd --create-home appuser

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Copy the application source code
COPY . .

# Activate the virtual environment for subsequent commands
ENV PATH="/app/.venv/bin:$PATH"

# Set the owner of the files to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
# The default is 8000, but it can be overridden by the PORT env var
EXPOSE 8000

# The command to run the application
# This uses the production runner script
CMD ["python", "run_prod.py"]

