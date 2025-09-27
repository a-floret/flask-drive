# Flask Drive

Flask-Drive is a web application for file management built with Flask and PostgreSQL, deployed in a Docker/Podman environment and orchestrated with Kubernetes.

It allows:

- Uploading, viewing, and deleting files via a web interface.
- Storage of files directly in a PostgreSQL database with persistence thanks to a Persistent Volume.
- A scalable architecture with multiple replicas for the API and an Nginx reverse proxy.
- Clean and secure configuration of credentials via Kubernetes Secrets.

The project illustrates a modern approach to microservices deployment, combining containers, orchestration, persistence, and security in a cloud-native environment.

## About
This application contains a user system; a login is required and accounts can be created via a registration page. A password policy has been added and the code is resilient to SQL injection.

Once logged in, it is possible to add, delete, and download files saved in the database. The PostgreSQL database has been mounted on a volume so that data is persistent even when the containers are shut down.

## Run with podman

### Build Images
```bash
podman build -t postgres-drive -f docker/postgres/Dockerfile .
podman build -t flask-drive -f docker/flask/Dockerfile .
podman build -t proxy-drive -f docker/nginx/Dockerfile .
```

### Start cluster
With podman:
```bash
podman run -d --name postgres --env-file flaskr/.env -p 5432:5432 -v drive-database:/var/lib/postgresql/data --network drive-n postgres-drive
podman run -d --name drive --network drive-n flask-drive
podman run -d --name proxy -p 8080:80 --network drive-n proxy-drive
```

With podman-compose:
```bash
podman-compose -f docker/podman-compose.yml up -d
```

### Use Flask Drive

You can now access to the [Flask-Driver](http://localhost:8080).

You can also manage your Database by running this command:
```bash
psql -h localhost -p 5432 -U flaskuser -d flaskdb
```


## Run with Kubernetes

### Build Images in Minikube
```bash
minikube image build -t postgres-drive:latest -f docker/postgres/Dockerfile .
minikube image build -t flask-drive:latest -f docker/flask/Dockerfile .
minikube image build -t proxy-drive:latest -f docker/nginx/Dockerfile .
```

### Setup namespace, PVC and secrets
```bash
kubectl apply -f k8s/drive-namespace.yml 
kubectl apply -f k8s/postgres-pvc.yml -n flask-drive
kubectl apply -f k8s/postgres-secrets.yml -n flask-drive
```

### Start cluster
```bash
kubectl apply -f k8s/postgres-deployment.yml -n flask-drive
kubectl apply -f k8s/flask-deployment.yml -n flask-drive
kubectl apply -f k8s/proxy-deployment.yml -n flask-drive
```
OR
```bash
kubectl apply -f k8s/postgres-deployment.yml -f k8s/flask-deployment.yml -f k8s/proxy-deployment.yml -n flask-drive
```
### Use Flask Drive
To acces to Flask-Drive run the following comand to get the url

```bash
minikube service proxy -n flask-drive --url
```

To access databse
```bash
kubectl exec -it -n flask-drive <name-of-pod-postgres> -- bash
psql -U $POSTGRES_USER -d $POSTGRES_DB
```
OR
```bash
kubectl port-forward -n flask-drive svc/postgres 5432:5432
psql -h localhost -U <user> -d <db>
```