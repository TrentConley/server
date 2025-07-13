# Use an official Python runtime as the base image
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Create a non-root user for security
RUN useradd --create-home appuser

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set the owner of the files to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Run the application using Uvicorn, binding to a hardcoded port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

