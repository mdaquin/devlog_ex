import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

/**
 * En développement, les appels du prototype partent vers `/api/...` et sont
 * relayés par Vite vers l'API réelle. Cela évite d'avoir à configurer CORS
 * sur le serveur pour `http://localhost:5173`.
 *
 * Variables facultatives :
 *   VITE_API_PROXY_TARGET  (défaut : https://mathieu.com)
 *   VITE_API_PROXY_PREFIX  (défaut : /ecureuil/api/1.0)
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const cible = env.VITE_API_PROXY_TARGET || "https://mathieu.com";
  const prefixe = env.VITE_API_PROXY_PREFIX || "/ecureuil/api/1.0";

  return {
    plugins: [react()],
    server: {
      proxy: {
        "/api": {
          target: cible,
          changeOrigin: true,
          secure: true,
          rewrite: (chemin) => chemin.replace(/^\/api/, prefixe),
        },
      },
    },
  };
});
