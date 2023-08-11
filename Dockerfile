# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Create a new user
RUN useradd -ms /bin/bash newuser

# Set the working directory to /app
WORKDIR /app
# Copy the application code and resources
COPY dashboard /app/dashboard
COPY resources /app/resources

# Copy only the requirements file and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


ENV REPO_URL = None
ENV REPO_TOKEN = None
ENV PROJECT_NUM = None


# Install system dependencies
RUN apt-get update && \
    apt-get -y install cron supervisor && \
    rm -rf /var/lib/apt/lists/*


# Copy the supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create the log directory and give ownership to newuser
RUN mkdir -p /var/log/supervisor /var/run/crond && \
    touch /var/run/crond.pid && \
    chown -R newuser:newuser /var/log/supervisor /var/run/crond && \
    # Give permissions to read, write, and delete files from resources dir
    chmod -R 777 /app/resources && \
    # Run a cron job at 23:47 everyday
#    echo "47 23 * * * /usr/local/bin/python3 /app/resources/cache_handler.py > /proc/1/fd/1 2>&1" >> /etc/cron.d/scanfs && \
    echo "*/1 * * * * /usr/local/bin/python3 /app/resources/cache_handler.py > /proc/1/fd/1 2>&1" >> /etc/cron.d/scanfs && \
    crontab -u newuser /etc/cron.d/scanfs && \
    chmod u+s /usr/sbin/cron

# Switch to the new user
USER newuser

VOLUME /HSMFS

# Run supervisord as the main command
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
