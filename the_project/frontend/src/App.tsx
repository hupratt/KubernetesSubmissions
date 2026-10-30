import { useEffect, useState, type ChangeEvent } from "react";

const MAX_LENGTH = 140;

type Todo = { id: number; text: string };

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);
  const [todo, setTodo] = useState("");
  const [todos, setTodos] = useState<Todo[]>([]);
  const [error, setError] = useState<string | null>(null);

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

      <ul>
        {todos.map((t) => (
          <li key={t.id}>{t.text}</li>
        ))}
      </ul>

      <h3>devops-with-kubernetes-2026</h3>
    </main>
  );
}