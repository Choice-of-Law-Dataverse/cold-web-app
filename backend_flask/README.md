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
```
curl -X POST http://localhost:5000/search \
-H "Content-Type: application/json" \
-d '{"search_string": <search query>, "use_semantic_search": false}'
```

**url/curated_search**
```
curl -X POST http://localhost:5000/curated_search \
-H "Content-Type: application/json" \
-d '{"search_string": <search query>}'
```

**url/curated_search/details**
The "table" argument accepts only "Court decisions" or "Legal provisions" as arguments. Any other value will return an error message.
```
curl -X POST http://localhost:5000/curated_search/details \
-H "Content-Type: application/json" \
-d '{"table": <table>, "id": <id>}'
```