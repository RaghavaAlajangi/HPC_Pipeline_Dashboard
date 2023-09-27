# HPC_Pipeline_Dashboard

A web interface to create a data processing pipelines (issues) on
HPC_Pipeline_requests repo

## Installation

### Clone the repository

```bash
git clone git@gitlab.gwdg.de:blood_data_analysis/hpc_pipeline_dashboard.git
```

### Install prerequisites for deployment

- Make sure you have `Docker Desktop` installed on your computer.
- To install, go to [Official Docker page](https://docs.docker.com/get-docker/).
  This step might require administration rights.
- Contact IT to have a developer account
  on [MPL harbor](https://harbor.intranet.mpl.mpg.de/) for deployment


## Build App and Cron docker images:

- Open `command prompt` in administrative mode<br><br>
- Check weather you have ``Docker`` installed or not.<br><br>
- Change directory: ``cd <path/to/repo>``<br><br>
- Below command creates a docker image for the application
```bash
docker build -t hpc-pipeline-dashboard .
```
- Below command creates a docker image for the cron job
```bash
docker build -t hpc-pipeline-dashboard-cron --target cron .
```

## Test webapp locally

### Run the docker image:

```bash
# Test the app locally by running the below command

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

- Open a browser and try reaching the following
  address. http://localhost:8050/hpc-pipeline-dashboard/. This should start the
  app.
- If container runs properly, the changes can be pushed for deployment.
- Look up for running container ID and stop it.

```bash
docker ps -a

docker stop <containerID>
```

### Committing the changes:

```bash
# Add your changes:
git add .

# Commit your changes:
git commit -m "My message"

# Get the last commit ID (sort form) and copy it:
git rev-parse --short HEAD
```

## Deploy the webapp on server:

- Login to harbor-intranet using your developer credentials:

```bash
docker login harbor.intranet.mpl.mpg.de
```

- Tag both your commit and latest versions:

```bash
# Tag commit
docker tag hpc-pipeline-dashboard harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard:yourcommitID

# Tag latest
docker tag hpc-pipeline-dashboard harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard:latest
```

- Push both your commit and latest versions:

```bash
# Tag commit
docker push harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard:yourcommitID

# Tag latest
docker push harbor.intranet.mpl.mpg.de/guck-tools/hpc-pipeline-dashboard:latest
```

## Useful Docker commands

```bash
# To see created docker images
docker images

# To see running containers
docker ps -a

# Run an image
docker run <image_name>

#Stop container
docker stop <container_ID>

# Get into the image and test weather it is created properly.
docker run -it <image_name> /bin/bash

# Get into the running container and test weather it is running properly.
docker exec -it <container_ID> /bin/bash
```