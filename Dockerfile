# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Ensure that Python outputs all logs to the terminal without buffering them
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libc-dev \
        && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run gunicorn with a few workers to handle requests
# Bind to 0.0.0.0:8000 so that it is accessible outside the container
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "boom.wsgi:application"]
