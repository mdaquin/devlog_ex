import { RELEVES_INITIAUX } from "../donnees/relevesInitiaux.js";

/**
 * API factice : mêmes signatures que `apiReelle.js`, mais les données vivent
 * en mémoire et une latence est simulée.
 *
 * Le choix entre les deux implémentations se fait dans `services/api.js`,
 * piloté par `VITE_API_MODE` (voir README.md).
 */

const LATENCE = 550;

/** État « serveur » du prototype : perdu au rechargement de la page. */
let releves = structuredClone(RELEVES_INITIAUX);

/** Compte unique du mode factice, pour garder la même interface que l'API. */
const COMPTE_FACTICE = {
  id: "compte-factice",
  name: "Compte courant",
  currency: "EUR",
  role: "OWNER",
};

function attendre(duree = LATENCE) {
  return new Promise((resolve) => setTimeout(resolve, duree));
}

export async function chargerComptes() {
  await attendre(200);
  return [structuredClone(COMPTE_FACTICE)];
}

export async function chargerReleves() {
  await attendre(650);
  return structuredClone(releves);
}

export async function supprimerReleve(id) {
  await attendre(450);
  const index = releves.findIndex((releve) => releve.id === id);
  if (index === -1) {
    throw new Error("Ce relevé n'existe plus.");
  }
  releves.splice(index, 1);
}

export async function restaurerReleve(releve) {
  await attendre(300);
  if (!releves.some((existant) => existant.id === releve.id)) {
    releves.push(structuredClone(releve));
  }
}

export async function importerReleve({ annee, mois, fichier }) {
  await attendre(850);

  if (!/\.(csv|xlsx)$/i.test(fichier.name)) {
    throw new Error("Formats acceptés : .csv ou .xlsx.");
  }
  if (releves.some((releve) => releve.annee === annee && releve.mois === mois)) {
    throw new Error("Un relevé existe déjà pour ce mois.");
  }

  const numeroMois = String(mois + 1).padStart(2, "0");
  const graine = annee * 12 + mois;
  const revenusCentimes = 215000 + ((graine * 3751) % 140000);
  const depensesCentimes = 95000 + ((graine * 6203) % 85000);

  const nouveau = {
    id: `rel-${annee}-${numeroMois}`,
    annee,
    mois,
    libelle: "Relevé mensuel",
    fichier: fichier.name,
    importeLe: new Date().toISOString(),
    transactionsImportees: 32 + ((graine * 7) % 24),
    revenus: (revenusCentimes / 100).toFixed(2),
    depenses: (-depensesCentimes / 100).toFixed(2),
    acces: [],
  };

  releves.push(nouveau);
  return structuredClone(nouveau);
}
