import { useState } from "react";

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);

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
      <h3>devops-with-kubernetes-2026</h3>
    </main>
  );
}
