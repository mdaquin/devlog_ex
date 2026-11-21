import { requete } from "./clientApi.js";
import { nomDepuisEmail } from "../utilitaires/identite.js";

/**
 * Adaptateur entre l'API décrite dans `openapi.yaml` et la forme attendue par
 * les composants de l'écran (`annee`, `mois`, `revenus`, `depenses`, `acces`).
 *
 * L'API raisonne par **compte** puis par **extrait de compte** ; l'écran, lui,
 * regroupe les extraits par année et par mois. C'est ici que se fait la
 * traduction, pas dans les composants.
 */

const TAILLE_PAGE = 200;
const LOTS = 4;
const TONS = ["bleu", "rose", "vert", "ambre", "violet"];

function urlCompte(compteId, suite = "") {
  return `/accounts/${encodeURIComponent(compteId)}${suite}`;
}

/** Liste les comptes auxquels l'utilisateur connecté a accès. */
export async function chargerComptes() {
  const comptes = await requete("/accounts");
  return Array.isArray(comptes) ? comptes : [];
}

/** Charge tous les extraits d'un compte, avec leurs totaux et les accès. */
export async function chargerReleves(compte) {
  const compteId = typeof compte === "string" ? compte : compte?.id;
  if (!compteId) return [];

  const [extraits, acces] = await Promise.all([
    chargerTousLesExtraits(compteId),
    chargerAcces(compteId, compte?.role),
  ]);

  return traiterParLots(extraits, LOTS, async (extrait) => {
    const totaux = await totauxExtrait(compteId, extrait);
    return mapperExtrait(extrait, totaux, acces);
  });
}

export async function importerReleve({ compte, fichier }) {
  const compteId = typeof compte === "string" ? compte : compte?.id;
  if (!compteId) throw new Error("Aucun compte bancaire sélectionné.");
  if (!fichier) throw new Error("Choisissez un fichier CSV ou Excel.");

  const donnees = new FormData();
  donnees.append("file", fichier);

  const extrait = await requete(urlCompte(compteId, "/statements"), {
    method: "POST",
    body: donnees,
  });

  const [totaux, acces] = await Promise.all([
    totauxExtrait(compteId, extrait),
    chargerAcces(compteId, compte?.role),
  ]);

  return mapperExtrait(extrait, totaux, acces);
}

export async function supprimerReleve(extraitId, compteId) {
  if (!compteId) throw new Error("Aucun compte bancaire sélectionné.");
  await requete(
    urlCompte(compteId, `/statements/${encodeURIComponent(extraitId)}`),
    { method: "DELETE" },
  );
}

/** L'API ne prévoit pas de « annuler la suppression » d'un extrait. */
export async function restaurerReleve() {
  throw new Error("L'API ne permet pas de restaurer un extrait supprimé.");
}

/* ------------------------------------------------------------------ Détails */

async function chargerTousLesExtraits(compteId) {
  const extraits = [];
  let page = 1;

  while (page <= 50) {
    const reponse = await requete(
      urlCompte(compteId, `/statements?page=${page}&pageSize=${TAILLE_PAGE}`),
    );
    const items = Array.isArray(reponse?.items) ? reponse.items : [];
    extraits.push(...items);

    const total = Number(reponse?.totalItems ?? extraits.length);
    if (items.length === 0 || extraits.length >= total) break;
    page += 1;
  }

  return extraits;
}

async function chargerAcces(compteId, role) {
  // `GET /accounts/{id}/access` est réservé au propriétaire (403 sinon).
  if (role && role !== "OWNER") return [];

  try {
    const acces = await requete(urlCompte(compteId, "/access"));
    if (!Array.isArray(acces)) return [];

    return acces.map((entree, index) => ({
      utilisateurId: entree.userId,
      nom: nomDepuisEmail(entree.email),
      permission: entree.permission,
      ton: TONS[index % TONS.length],
    }));
  } catch (erreur) {
    // 401 = session expirée : on laisse remonter pour revenir à la connexion.
    if (erreur?.statut === 401) throw erreur;
    return [];
  }
}

async function totauxExtrait(compteId, extrait) {
  const { from, to } = plageExtrait(extrait);

  try {
    const resume = await requete(
      urlCompte(compteId, `/summary?from=${from}&to=${to}`),
    );
    return {
      revenus: resume?.totalIncome ?? null,
      depenses: resume?.totalExpenses ?? null,
    };
  } catch (erreur) {
    // Une erreur ponctuelle (400, 403, 404…) ne doit pas vider l'écran :
    // les montants seront affichés comme indisponibles.
    if (erreur?.statut === 401) throw erreur;
    return { revenus: null, depenses: null };
  }
}

function mapperExtrait(extrait, totaux, acces) {
  const { annee, mois } = anneeMois(extrait);
  const format = String(extrait.format ?? "").toLowerCase();

  return {
    id: extrait.id,
    annee,
    mois,
    libelle:
      format === "xlsx"
        ? "Relevé Excel"
        : format === "csv"
          ? "Relevé CSV"
          : "Relevé importé",
    fichier: extrait.fileName || "relevé",
    importeLe: extrait.importedAt ?? null,
    transactionsImportees: Number(extrait.transactionsImported ?? 0),
    doublonsIgnores: Number(extrait.duplicatesSkipped ?? 0),
    revenus: totaux.revenus,
    depenses: totaux.depenses,
    acces,
  };
}

/** Année et mois (0 = janvier) d'un extrait, d'après sa période. */
function anneeMois(extrait) {
  const source =
    extrait.periodEnd || extrait.periodStart || extrait.importedAt || "";
  const [annee, mois] = source.slice(0, 10).split("-").map(Number);

  if (Number.isInteger(annee) && Number.isInteger(mois) && mois >= 1 && mois <= 12) {
    return { annee, mois: mois - 1 };
  }

  const maintenant = new Date();
  return { annee: maintenant.getFullYear(), mois: maintenant.getMonth() };
}

/** Période `from`/`to` (AAAA-MM-JJ) utilisée pour demander les totaux. */
function plageExtrait(extrait) {
  const debut = String(extrait.periodStart ?? "").slice(0, 10);
  const fin = String(extrait.periodEnd ?? "").slice(0, 10);
  if (debut && fin) return { from: debut, to: fin };

  const { annee, mois } = anneeMois(extrait);
  const numero = String(mois + 1).padStart(2, "0");
  const dernierJour = new Date(Date.UTC(annee, mois + 1, 0)).getUTCDate();

  return {
    from: debut || `${annee}-${numero}-01`,
    to: fin || `${annee}-${numero}-${String(dernierJour).padStart(2, "0")}`,
  };
}

/** Exécute `tache` sur `elements` par petits lots pour ne pas saturer l'API. */
async function traiterParLots(elements, taille, tache) {
  const resultats = [];

  for (let index = 0; index < elements.length; index += taille) {
    const lot = elements.slice(index, index + taille);
    resultats.push(...(await Promise.all(lot.map(tache))));
  }

  return resultats;
}
