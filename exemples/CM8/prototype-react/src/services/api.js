import { EST_REEL } from "../config.js";
import * as factice from "./apiFactice.js";
import * as reelle from "./apiReelle.js";

/**
 * Point d'entrée unique des services de données.
 *
 * `VITE_API_MODE=factice` (défaut) utilise les données simulées ;
 * `VITE_API_MODE=reel` parle à l'API HTTP. Les composants n'ont pas à savoir
 * lequel des deux est actif.
 */

export const MODE_REEL = EST_REEL;
export const AUTHENTIFICATION_REQUISE = EST_REEL;
export const RESTAURATION_POSSIBLE = !EST_REEL;

const implementation = EST_REEL ? reelle : factice;

export const chargerComptes = implementation.chargerComptes;
export const chargerReleves = implementation.chargerReleves;
export const importerReleve = implementation.importerReleve;
export const supprimerReleve = implementation.supprimerReleve;
export const restaurerReleve = implementation.restaurerReleve;

export {
  aSession,
  seConnecter,
  seDeconnecter,
  utilisateurCourant,
} from "./clientApi.js";
