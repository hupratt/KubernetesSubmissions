import { useEffect, useState, type ChangeEvent } from "react";

const MAX_LENGTH = 140;

type Todo = { id: number; text: string; done: boolean };

function ErrorPage() {
  const [checking, setChecking] = useState(false);

  const retry = async () => {
    setChecking(true);
    try {
      const r = await fetch("/healthz");
      if (r.ok) {
        window.location.reload();
        return;
      }
    } catch {
      // pod is restarting; fall through
    }
    setChecking(false);
  };

  return (
    <main style={{ display: "grid", placeItems: "center", minHeight: "100vh" }}>
      <h1>Something went wrong</h1>
      <p>The app is unhealthy. Kubernetes should restart it shortly.</p>
      <button onClick={retry} disabled={checking}>
        {checking ? "Checking…" : "Try again"}
      </button>
    </main>
  );
}

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);
  const [broken, setBroken] = useState(false);
  const [todo, setTodo] = useState("");
  const [todos, setTodos] = useState<Todo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [updatingTodoId, setUpdatingTodoId] = useState<number | null>(null);

  useEffect(() => {
    fetch("/todos")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setTodos)
      .catch(() => setError("Could not load todos."));
  }, []);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setTodo(e.target.value.slice(0, MAX_LENGTH));
  };

  const handleSend = async () => {
    const text = todo.trim();
    if (!text) return;
    try {
      const r = await fetch("/todos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const created = await r.json();
      setTodos((prev) => [...prev, created]);
      setTodo("");
      setError(null);
    } catch {
      setError("Could not create todo.");
    }
  };

  const handleMarkDone = async (todo: Todo) => {
    if (todo.done || updatingTodoId !== null) return;

    setUpdatingTodoId(todo.id);
    try {
      const r = await fetch(`/todos/${todo.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ done: true }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);

      setTodos((prev) =>
        prev.map((item) =>
          item.id === todo.id ? { ...item, done: true } : item,
        ),
      );
      setError(null);
    } catch {
      setError(`Could not mark todo ${todo.id} as done.`);
    } finally {
      setUpdatingTodoId(null);
    }
  };

  const handleBreak = async () => {
    try {
      await fetch("/api/break", { method: "POST" });
    } finally {
      setBroken(true);
    }
  };

  if (broken) return <ErrorPage />;

  return (
    <main style={{ display: "grid", placeItems: "center", minHeight: "100vh" }}>
      {!loaded && !failed && <p>Loading…</p>}
      {failed && <p>Could not load the image.</p>}
      <h1>Todo app</h1>
      <img
        src="/api/image"
        alt="Random from Lorem Picsum"
        onLoad={() => setLoaded(true)}
        onError={() => setFailed(true)}
        style={{
          maxWidth: "100%",
          height: "auto",
          display: loaded ? "block" : "none",
        }}
      />

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          type="text"
          value={todo}
          onChange={handleChange}
          maxLength={MAX_LENGTH}
          placeholder="What needs to be done?"
          aria-label="New todo"
        />
        <button type="submit">Send</button>
        <p>
          {todo.length}/{MAX_LENGTH}
        </p>
      </form>

      {error && <p role="alert">{error}</p>}

      <h2>Todos</h2>
      <ul style={{ listStyle: "none", padding: 0, width: "min(100%, 640px)" }}>
        {todos.map((t) => (
          <li
            key={t.id}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "1rem",
              padding: "0.8rem",
              marginBottom: "0.5rem",
              background: t.done ? "#f0f0f0" : "#fafafa",
              borderLeft: `4px solid ${t.done ? "#999" : "#4caf50"}`,
              borderRadius: "4px",
            }}
          >
            <span
              style={{
                textDecoration: t.done ? "line-through" : "none",
                color: t.done ? "#666" : "inherit",
              }}
            >
              {t.text}
            </span>
            {t.done ? (
              <strong style={{ color: "#218838", whiteSpace: "nowrap" }}>
                Done
              </strong>
            ) : (
              <button
                type="button"
                onClick={() => handleMarkDone(t)}
                disabled={updatingTodoId !== null}
              >
                {updatingTodoId === t.id ? "Saving…" : "Mark done"}
              </button>
            )}
          </li>
        ))}
      </ul>

      <button onClick={handleBreak} style={{ marginTop: "2rem" }}>
        Break the app
      </button>

      <h3>devops-with-kubernetes-2026</h3>
    </main>
  );
}