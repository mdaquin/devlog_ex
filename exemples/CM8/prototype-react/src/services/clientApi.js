import { BASE_API } from "../config.js";
import { nomDepuisEmail } from "../utilitaires/identite.js";

const CLE_SESSION = "ecureuil.session";

export class ErreurApi extends Error {
  constructor(message, { statut = 0, titre = "", details = null } = {}) {
    super(message);
    this.name = "ErreurApi";
    this.statut = statut;
    this.titre = titre;
    this.details = details;
  }
}

function lireSession() {
  try {
    const valeur = sessionStorage.getItem(CLE_SESSION);
    return valeur ? JSON.parse(valeur) : null;
  } catch {
    return null;
  }
}

let session = lireSession();
let rafraichissementEnCours = null;

function ecrireSession(valeur) {
  session = valeur;
  try {
    if (valeur) {
      sessionStorage.setItem(CLE_SESSION, JSON.stringify(valeur));
    } else {
      sessionStorage.removeItem(CLE_SESSION);
    }
  } catch {
    // Stockage indisponible (navigation privée stricte) : la session reste en mémoire.
  }
}

export function aSession() {
  return Boolean(session?.accessToken);
}

export function utilisateurCourant() {
  if (!session?.email) return null;
  return { email: session.email, nom: nomDepuisEmail(session.email) };
}

/** `fetch` avec un message d'erreur compréhensible quand l'API est injoignable. */
async function appelReseau(url, options) {
  try {
    return await fetch(url, options);
  } catch {
    throw new ErreurApi(
      "Impossible de joindre l'API. Vérifiez votre connexion, l'adresse de l'API " +
        "et, en développement, la configuration du proxy Vite.",
    );
  }
}

async function erreurDepuis(reponse) {
  let corps = null;
  try {
    corps = await reponse.json();
  } catch {
    // Le corps n'est pas du JSON (proxy, page d'erreur…).
  }

  const message =
    corps?.detail ||
    corps?.title ||
    (reponse.status === 401
      ? "Identifiants ou session invalides."
      : `Erreur HTTP ${reponse.status}.`);

  return new ErreurApi(message, {
    statut: reponse.status,
    titre: corps?.title ?? "",
    details: corps?.errors ?? null,
  });
}

async function rafraichir() {
  if (!session?.refreshToken) return false;

  if (!rafraichissementEnCours) {
    rafraichissementEnCours = (async () => {
      const email = session?.email;
      const reponse = await appelReseau(`${BASE_API}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refreshToken: session.refreshToken }),
      });

      if (!reponse.ok) {
        ecrireSession(null);
        return false;
      }

      const jetons = await reponse.json();
      // Si l'utilisateur s'est déconnecté entre-temps, on ne restaure pas la session.
      if (!session) return false;
      ecrireSession({ ...session, ...jetons, email });
      return true;
    })().finally(() => {
      rafraichissementEnCours = null;
    });
  }

  return rafraichissementEnCours;
}

async function requeteInterne(chemin, options, dejaRafraichi) {
  const entetes = new Headers(options.headers);
  if (session?.accessToken) {
    entetes.set("Authorization", `Bearer ${session.accessToken}`);
  }

  const estFormulaire = options.body instanceof FormData;
  if (options.body && !estFormulaire && !entetes.has("Content-Type")) {
    entetes.set("Content-Type", "application/json");
  }

  const url = `${BASE_API}${chemin.startsWith("/") ? chemin : `/${chemin}`}`;
  const reponse = await appelReseau(url, { ...options, headers: entetes });

  if (reponse.status === 401 && !dejaRafraichi && aSession()) {
    const rafraichi = await rafraichir();
    if (rafraichi) {
      return requeteInterne(chemin, options, true);
    }
  }

  if (!reponse.ok) {
    throw await erreurDepuis(reponse);
  }

  if (reponse.status === 204) return null;
  const texte = await reponse.text();
  return texte ? JSON.parse(texte) : null;
}

/** Requête authentifiée avec renouvellement automatique du jeton d'accès. */
export function requete(chemin, options = {}) {
  return requeteInterne(chemin, options, false);
}

export async function seConnecter({ email, password }) {
  const reponse = await appelReseau(`${BASE_API}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!reponse.ok) {
    throw await erreurDepuis(reponse);
  }

  const jetons = await reponse.json();
  ecrireSession({ ...jetons, email });
  return utilisateurCourant();
}

export function seDeconnecter() {
  rafraichissementEnCours = null;
  ecrireSession(null);
}
