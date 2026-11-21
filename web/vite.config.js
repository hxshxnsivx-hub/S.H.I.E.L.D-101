import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: `npm run dev` on :5173, proxying /api to the Python console server (:8765).
// Prod: `npm run build` -> dist/, which the Python server serves directly.
export default defineConfig({
  plugins: [react()],
  build: { outDir: "dist", emptyOutDir: true },
  server: { proxy: { "/api": "http://localhost:8765" } },
});
