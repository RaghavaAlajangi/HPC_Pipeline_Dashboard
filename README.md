# HPC_Pipeline_Dashboard

A web interface to create a data processing pipelines (issues) on HPC_Pipeline_requests repo

## Run dashboard

```bash
python -m dashboard
```

## Before the deployment:

- Make sure you have `Docker Desktop` installed on your computer. To install, go to [Official Docker page](https://docs.docker.com/get-docker/). 
This step might require administration rights.
- Sign in to [MPL harbor](https://harbor.intranet.mpl.mpg.de/) with MPL credentials and contact IT to have a developer account for your app

## Preparation for deployment:

### Build a docker Image:  
- Open `command prompt` in administrative mode
- Check weather you ``Docker`` installed or not.
- Change directory: ``cd <path/to/repo>``    

```bash
docker build -t <name_of_your_docker_image> .

docker build -t hpc-pipeline-dashboard .
```

### Run the container:
```bash
docker run -p 8050:8050  <name_of_your_docker_image>

docker run -p 8050:8050  hpc-pipeline-dashboard
```

- Open a browser and try reaching the following address. http://localhost:8050/hpc-pipeline-dashboard/. This should start the app.
- If it runs in the container properly, the changes can be pushed for deployment.
- Look up the container ID of the running container either by using ``Docker Desktop`` or by `docker ps` command.
```bash
docker ps -a
```
- Copy the container ID and stop it by running the following command:
```bash
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

## Pushing the changes:

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
