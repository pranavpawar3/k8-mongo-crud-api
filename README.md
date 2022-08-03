## CDL Assignment

Code execution video - [here](https://www.youtube.com/watch?v=VWtzrmiF_Ec) (to skip to code execution go to 4:40)

Install minikube from [here](https://minikube.sigs.k8s.io/docs/start/)

Install kubectl from [here](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)

To start the services

```bash
minikube start --driver docker
kubectl apply -f db-config.yaml
kubectl apply -f db-secret.yaml
kubectl apply -f mongo.yaml
kubectl apply -f client.yaml
```

Find your minikube ip using `minikube ip` command and navigate to the `http://MINIKUBE_IP:30100/docs` to interact with the MongoDB CRUD API

### References
1. [MongoDB FastAPI tutorial](https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi)
2. [Docker hub image](https://hub.docker.com/r/pranavpawar3/mongo_crud_app)
