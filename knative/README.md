Install postgres locally and run the app locally before deploying to k3d

```bash
docker network create my-app-net
docker volume create pingpong-pgdata-17
docker run -d --name ping-db \
  --network my-app-net \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=strongpw \
  -e POSTGRES_DB=pingpong \
  -p 5432:5432 \
  -v pingpong-pgdata-17:/var/lib/postgresql/data \
  postgres:17-alpine
docker build -t hupratt/log_output:latest .
docker push hupratt/log_output:latest
docker run --rm \
  --network my-app-net \
  -e DATABASE_URL="postgresql://postgres:strongpw@ping-db:5432/pingpong" \
  hupratt/log_output:latest
```