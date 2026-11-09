# Jenkins Fullstack App

A small task dashboard demonstrating a FastAPI backend, PostgreSQL persistence, a static frontend, Docker Compose, Kubernetes, and Jenkins.

## Run locally

Requires Docker Engine and Docker Compose v2.

```sh
docker compose up --build
```

Open [http://localhost:8080](http://localhost:8080). Set `APP_PORT` to change the host port. Compose uses `local-only-change-me` as a development database password; set `POSTGRES_PASSWORD` to a strong value for non-local use.

The API is available at `/api/health` and `/api/tasks`. The interactive API docs are at `/docs` on the backend service. Task records persist in the `postgres-data` volume.

## Deploy to Kubernetes / Argo CD

1. Create the namespace and database Secret before deploying the database workload:

   ```sh
   kubectl create namespace jenkins-fullstack-app --dry-run=client -o yaml | kubectl apply -f -
   kubectl -n jenkins-fullstack-app create secret generic app-db \
     --from-literal=POSTGRES_DB=app \
     --from-literal=POSTGRES_USER=app \
     --from-literal=POSTGRES_PASSWORD='<strong-password>'
   kubectl apply -f k8s-manifests/db-deploy.yaml
   ```

2. Build and publish the backend/frontend images, then update the `image` values in their deployment manifests to the published image references.
3. Configure Argo CD to track `k8s-manifests/`, or apply the files directly:

   ```sh
   kubectl apply -f k8s-manifests/backend-deploy.yaml
   kubectl apply -f k8s-manifests/frontend-deploy.yaml
   ```

4. Access the UI locally with:

   ```sh
   kubectl -n jenkins-fullstack-app port-forward service/frontend 8080:80
   ```

The database manifest creates a persistent volume claim. Ensure the cluster has a default StorageClass, or specify one in `db-deploy.yaml`. Keep Secret values out of Git; use your cluster's secret-management workflow for Argo CD.

## Jenkins

The `Jenkinsfile` runs backend syntax checks, a frontend JavaScript syntax check, and builds both container images. The Jenkins agent needs Python 3, pip/venv, Node.js, Docker, and the Docker Compose plugin.
