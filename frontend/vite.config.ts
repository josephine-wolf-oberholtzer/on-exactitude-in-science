import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
	plugins: [react()],
	server: {
		// The backend sends no CORS headers, so proxy it during development.
		proxy: {
			"/api": {
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api/, ""),
				target: "http://localhost:9090",
			},
		},
	},
	test: {
		env: { VITE_API_URL: "http://api.test" },
		environment: "jsdom",
		setupFiles: ["./src/test/setup.ts"],
	},
});
