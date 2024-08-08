FROM python:alpine as auto-rapid-dashboard
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

ENTRYPOINT ["python3"]
CMD ["-m", "dashboard"]
