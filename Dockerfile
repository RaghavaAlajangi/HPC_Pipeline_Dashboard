FROM python:alpine as cron
RUN pip install yacron
COPY crontab.yaml /tmp/crontab.yaml
COPY cache_handler.py /app/cache_handler.py
ENTRYPOINT ["yacron"]
CMD ["-c", "/tmp/crontab.yaml"]

FROM python:alpine as hpc_pipeline_dashboard
RUN apk --no-cache add --virtual .builddeps g++
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY dashboard /app/dashboard
COPY resources /app/resources

ENV PATHNAME_PREFIX="/"

# GWDG GitLab URL
ENV REPO_URL=None

# HPC_pipeline_requests repo credentials
ENV REPO_TOKEN=None
ENV PROJECT_NUM=None

# HPC_pipeline_data repo credentials
ENV DVC_REPO_TOKEN=None
ENV DVC_REPO_PROJECT_NUM=None

ENTRYPOINT ["python3"]
CMD ["-m", "dashboard"]
