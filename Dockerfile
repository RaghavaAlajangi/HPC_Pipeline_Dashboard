# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements and code to the working directory
COPY requirements.txt /app
COPY dashboard /app/dashboard

# Install requirements
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Set the environment variables (hpc_pipeline_requests repo access token)
ENV REPO_URL = None
ENV REPO_TOKEN = None
ENV PROJECT_NUM = None

#VOLUME /app/SECRETS.txt

# Once a Docker image is built, its contents are fixed and cannot be
# changed. If we need to update the contents of a directory in a running
# Docker container, we will need to mount a volume to that directory using
# the '-v' option when you start the container. This will allow you to
# update the files on the host machine, and those changes will be reflected
# in the container.
VOLUME /app/HSMFS_drive.csv

# Run the dashboard
CMD ["python3", "-m", "dashboard"]
