# FLASK API

## Docker Commands
For local development, simply use:  
`docker-compose up --build --force-recreate`  
For resetting everything, use:  
`docker-compose down --rmi all -v --remove-orphans`  

The docker image has been pushed to dockerhub using:  
`docker tag backend-web simonweigold/cold-flask-backend:latest`  
`docker push simonweigold/cold-flask-backend:latest`  

## Endpoints
**url/search**
`curl ...`

**url/curated_search**
`curl ...`