import { useState } from "react";

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);

  return (
    <main style={{ display: "grid", placeItems: "center", minHeight: "100vh" }}>
      {!loaded && !failed && <p>Loading…</p>}
      {failed && <p>Could not load the image.</p>}
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
    </main>
  );
}
