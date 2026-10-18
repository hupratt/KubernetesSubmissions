# Frontend in reactjs and vite

download latest node LTS and create a project from the template (react + typescript+ eslint)

v24.22.0 (npm v11.19.1)

```bash
nvm install --lts
nvm use --lts
npm create vite@latest frontend -- --template react-ts
```

test the template and build it

```bash
npm run dev
npm run build
```

at this point all of my SPA artifacts are in /dist which we will move to the backend project

```bash
cp -r dist ../todo-app/static
```

and run it

```bash
cd ../todo-app && uv run fastapi dev src/todo_app/main.py
```