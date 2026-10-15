import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": { target: `http://localhost:${process.env.PORT ?? 8787}`, changeOrigin: true } },
  },
});
