FROM python:alpine as cron
RUN pip install yacron
COPY crontab.yaml /tmp/crontab.yaml
COPY resources/cache_handler.py /app/resources/cache_handler.py
ENTRYPOINT ["yacron"]
CMD ["-c", "/tmp/crontab.yaml"]

FROM python:alpine as hpc_pipeline_dashboard
RUN apk --no-cache add --virtual .builddeps g++
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY dashboard /app/dashboard
COPY resources /app/resources

ENV REPO_URL=None
ENV REPO_TOKEN=None
ENV PROJECT_NUM=None
ENV PATHNAME_PREFIX="/"

ENTRYPOINT ["python3"]
CMD ["-m", "dashboard"]
