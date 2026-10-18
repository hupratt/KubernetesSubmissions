
# todo-app

FastAPI web app

```bash
sudo dnf install uv
mkdir todo-app && cd todo-app 
uv init --app
uv add fastapi --extra standard
# in case i edit the pyproject.toml, this adds python dependencies into the virtual environment under .venv
uv sync
# run it with hot reloads on save and dev dependencies:
uv run fastapi dev src/todo_app/main.py
# run it with the CLI for prod:
export PORT=8081
uv run fastapi run src/todo_app/main.py --host 0.0.0.0 --port "$PORT"
```

build the project

```bash
# in case i changed the python app
docker build --no-cache -t hupratt/todo-app:1.2 .
# in case i just changed the dockerfile
docker build -t hupratt/todo-app:1.2 .
# push it to dockerhub
docker push hupratt/todo-app --all-tags 
```

run the image in k3d

```bash
kubectl create deployment todo --image=hupratt/todo-app:1.2
```

or locally:

```bash
export PORT=9091
docker run --rm -e UVICORN_PORT="$PORT" -p "$PORT":"$PORT" hupratt/todo-app:1.2
# or simply
docker run --rm hupratt/todo-app:1.2
```

clear k3d image from kubernetes. The deployment does not pull the latest image everytime from dockerhub

```bash
docker exec k3d-k3s-default-server-0 crictl rmi hupratt/todo-app:1.2
docker exec k3d-k3s-default-agent-0 crictl rmi hupratt/todo-app:1.2
docker exec k3d-k3s-default-agent-1 crictl rmi hupratt/todo-app:1.2
```