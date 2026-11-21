/**
 * Configuration de l'accès à l'API.
 *
 * - `VITE_API_MODE=factice` (défaut) : données simulées dans le navigateur.
 * - `VITE_API_MODE=reel` : appels HTTP vers `VITE_API_BASE_URL`.
 *
 * En développement, la valeur par défaut `/api` passe par le proxy Vite
 * configuré dans `vite.config.js` : `/api/...` est réécrit vers
 * `https://mathieu.com/ecureuil/api/1.0/...` (voir README.md).
 *
 * Pour appeler directement l'API sans proxy, définir par exemple :
 *   VITE_API_BASE_URL=https://mathieu.com/ecureuil/api/1.0
 * L'API doit alors autoriser l'origine du prototype (CORS).
 */
export const MODE_API = import.meta.env.VITE_API_MODE === "reel" ? "reel" : "factice";
export const EST_REEL = MODE_API === "reel";
export const BASE_API = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/+$/, "");
