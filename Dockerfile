## Use an official Python runtime as a parent image
#FROM python:3.9-slim
#
## Set the working directory to /app
#WORKDIR /app
#
## Copy the requirements and code to the working directory
#COPY requirements.txt /app
#COPY dashboard /app/dashboard
#
## Install requirements
#RUN pip install --trusted-host pypi.python.org -r requirements.txt
#
## Set the environment variables (hpc_pipeline_requests repo access token)
#ENV REPO_URL = None
#ENV REPO_TOKEN = None
#ENV PROJECT_NUM = None
#
##VOLUME /app/SECRETS.txt
#
## Once a Docker image is built, its contents are fixed and cannot be
## changed. If we need to update the contents of a directory in a running
## Docker container, we will need to mount a volume to that directory using
## the '-v' option when you start the container. This will allow you to
## update the files on the host machine, and those changes will be reflected
## in the container.
#VOLUME /HSMFS
#
## Run the dashboard
#CMD ["python3", "-m", "dashboard"]






# Use an official Python runtime as a parent image
FROM python:3.10

# Create a new user
RUN useradd -ms /bin/bash newuser

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get -y install cron supervisor && \
    rm -rf /var/lib/apt/lists/*

# Copy only the requirements file and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and resources
COPY dashboard /app/dashboard
COPY resources /app/resources

# Copy the supervisord configuration and cronjobs
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY cronjobs /etc/cron.d/cronjobs

# Create the log directory and give ownership to newuser
RUN mkdir -p /var/log/supervisor /var/run/crond && \
    touch /var/run/crond.pid && \
    chown -R newuser:newuser /var/log/supervisor /var/run/crond && \
    chmod -R 777 /app/resources && \
    chown newuser:newuser /var/run/crond.pid && \
    chmod gu+s /usr/sbin/cron && \
    chown newuser:newuser /etc/cron.d/cronjobs


# Switch to the new user
USER newuser

# Run supervisord as the main command
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
