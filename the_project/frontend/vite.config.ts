import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../todo-app/src/todo_app/static",
    emptyOutDir: true,
  },
  server: {
    proxy: { "/todos": "http://localhost:8000", "/api": "http://localhost:8000" },
  },
});