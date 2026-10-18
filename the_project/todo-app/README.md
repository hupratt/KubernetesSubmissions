
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
