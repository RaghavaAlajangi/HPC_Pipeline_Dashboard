# HPC Pipeline Dashboard  
  
[![CI](https://github.com/RaghavaAlajangi/hpc_pipeline_dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/RaghavaAlajangi/hpc_pipeline_dashboard/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/RaghavaAlajangi/hpc_pipeline_dashboard/branch/main/graph/badge.svg?token=Z4FAPNDJWN)](https://codecov.io/gh/RaghavaAlajangi/hpc_pipeline_dashboard)

A web interface to create and manage data processing pipelines (ML model inference) on HPC clusters.  


## ✨ Features  

### 📂 Pipeline Data  
The dashboard provides a centralized view of all pipelines. For each pipeline, users can see:  
- **User Information** – track who created and owns the pipeline.  
- **Pipeline ID** – a unique identifier for quick referencing and debugging.  
- **Parameters** – the configuration details used to run the pipeline.  
- **Status Monitoring** – live updates on progress with percentage completion and action logs.  
- **Output Links** – direct access to pipeline outputs and artifacts.  
- **Search & Filtering** – easily find pipelines by user, ID, or keywords.  
- **Badges & Labels** – categorize pipelines with tags such as *Important*, *Simple*, *Advanced*, etc. for quick prioritization.  

### ⚙️ Pipeline Parameters  
Pipelines can be customized before execution with a flexible set of parameters:  
- **Deep Learning Model Selection** – choose from a list of supported DL models.  
- **Image Classification Options** – switch between available classification architectures.  
- **Custom Parameters** – adjust hyperparameters, thresholds, and other pipeline-specific configurations.  

### 📑 Data Selection  
Users can define input data sources seamlessly from within the dashboard:  
- **S3 Integration** – fetch and process datasets stored in S3 buckets.  
- **Local File Explorer** – upload and use data directly from the HPC’s file system.  

### 🚀 Pipeline Creation  
The dashboard offers an intuitive interface to design and launch pipelines without needing command-line interaction:  
- Configure models, parameters, and datasets in just a few clicks.  
- Validate inputs and settings before execution.  
- Launch pipelines and track their progress from a single unified view.  


---

## 🖥 Interface  

### Dashboard  
![Dashboard](https://github.com/user-attachments/assets/719c8c9a-459c-4f1d-abce-2b59b7e9d153)   


## 🚀 Getting Started  

Clone the repo:  
```bash
git clone git@gitlab.gwdg.de:blood_data_analysis/hpc_pipeline_dashboard.git
cd hpc_pipeline_dashboard
```

Create a .env file (not committed to git):

```bash
# GWDG GitLab URL
REPO_URL="https://gitlab.gwdg.de"

# Request repo creds
REPO_TOKEN=<paste your request repo token>
PROJECT_NUM=<paste your project number>

# DVC repo creds
DVC_REPO_TOKEN=<paste your DVC repo token>
DVC_REPO_PROJECT_NUM=<paste your project number>

```

Run locally (development/debug):

```bash
python -m dashboard --local

```
Open in browser: 

- http://127.0.0.1:8050/local-dashboard


## 📦 Deployment

Prerequisites:

- [Docker Desktop](https://docs.docker.com/get-docker/) installed
- Developer account on [MPL harbor](https://harbor.intranet.mpl.mpg.de/)
- .env credentials shared with IT for deployment


Build Docker Images:

```bash
# Dashboard image
docker build -t hpc-pipeline-dashboard .

# Cron job image
docker build -t hpc-pipeline-dashboard-cron --target cron .
```

Test Images Locally:

```bash

# Windows command prompt:

docker run -p 8050:8050 ^
-e REPO_URL=<GITLAB_URL> ^
-e REPO_TOKEN=<REPO_TOKEN> ^
-e PROJECT_NUM=<PROJECT_NUMNER> ^
-e DVC_REPO_TOKEN=<DVC_REPO_TOKEN> ^
-e DVC_REPO_PROJECT_NUM=<DVC_REPO_PROJECT_NUM> ^
-e BASENAME_PREFIX="/hpc-pipeline-dashboard/" ^
 hpc-pipeline-dashboard
 
 # Bash command prompt
 
 docker run -p 8050:8050 \
-e REPO_URL=<GITLAB_URL> \
-e REPO_TOKEN=<REPO_TOKEN> \
-e PROJECT_NUM=<PROJECT_NUMNER> \
-e DVC_REPO_TOKEN=<DVC_REPO_TOKEN> \
-e DVC_REPO_PROJECT_NUM=<DVC_REPO_PROJECT_NUM> \
-e BASENAME_PREFIX="/hpc-pipeline-dashboard/" \
 hpc-pipeline-dashboard
```
Access app:

- http://localhost:8050/hpc-pipeline-dashboard/

Stop container:

```bash
docker ps -a

docker stop <containerID>
```
Environment Variables on MPL Server:

- Ensure IT sets all required tokens & environment variables on the server.

- Refresh tokens if the dashboard crashes due to expired access.

Get Latest Commit ID: 

```bash
git rev-parse --short HEAD
```

Log in to MPL Harbor:

```bash
docker login harbor.intranet.mpl.mpg.de
```
Tag & Push Images:

Dashboard Image

```bash
# Tag commit
docker tag hpc-pipeline-dashboard harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard:<commitID>

# Tag latest
docker tag hpc-pipeline-dashboard harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard:latest

# Push
docker push harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard:<commitID>
docker push harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard:latest

```

Cron Image

```bash
# Tag commit
docker tag hpc-pipeline-dashboard-cron harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard-cron:<commitID>

# Tag latest
docker tag hpc-pipeline-dashboard-cron harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard-cron:latest

# Push
docker push harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard-cron:<commitID>
docker push harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard-cron:latest

```


## 🛠 Useful Docker Commands

```bash
# To see the created Docker images
docker images

# To see running containers
docker ps -a

# Run an image
docker run <image_name>

#Stop container
docker stop <container_ID>

# Get into the image and test whether it is created properly.
docker run -it <image_name> /bin/bash

# Get into the running container and test whether it is running properly.
docker exec -it <container_ID> /bin/bash
```
