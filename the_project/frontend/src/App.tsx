import { useState } from "react";

const MAX_LENGTH = 140;

const INITIAL_TODOS = [
  "Learn how Kubernetes Deployments work",
  "Write a Dockerfile for the todo app",
  "Set up the cluster ingress",
];

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);
  const [todo, setTodo] = useState("");
  const [todos] = useState(INITIAL_TODOS);

  const handleChange = (e) => {
    // Guard against pasted text exceeding the limit
    setTodo(e.target.value.slice(0, MAX_LENGTH));
  };

  const handleSend = () => {
    // Does not send anything yet
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

      <div>
        <input
          type="text"
          value={todo}
          onChange={handleChange}
          maxLength={MAX_LENGTH}
          placeholder="What needs to be done?"
          aria-label="New todo"
        />
        <button type="button" onClick={handleSend}>
          Send
        </button>
        <p>
          {todo.length}/{MAX_LENGTH}
        </p>
      </div>

      <ul>
        {todos.map((t, i) => (
          <li key={i}>{t}</li>
        ))}
      </ul>

      <h3>devops-with-kubernetes-2026</h3>
    </main>
  );
}