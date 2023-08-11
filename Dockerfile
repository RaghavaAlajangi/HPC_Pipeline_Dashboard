# Use an official Python runtime as a parent image
FROM python:3.10

# Create a new user
RUN useradd -ms /bin/bash newuser

# Set the working directory to /app
WORKDIR /app

ENV REPO_URL = None
ENV REPO_TOKEN = None
ENV PROJECT_NUM = None


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

# Create the log directory and give ownership to newuser
RUN mkdir -p /var/log/supervisor /var/run/crond && \
    touch /var/run/crond.pid && \
    chown -R newuser:newuser /var/log/supervisor /var/run/crond && \
    chmod -R 777 /app/resources && \
    echo "47 23 * * * /usr/local/bin/python3 /app/resources/cache_handler.py > /proc/1/fd/1 2>&1" >> /etc/cron.d/scanfs && \
    crontab -u newuser /etc/cron.d/scanfs && \
    chmod u+s /usr/sbin/cron

# Switch to the new user
USER newuser

# Run supervisord as the main command
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
