/**
 * Jeu de données factice du prototype.
 *
 * Il reprend volontairement la forme des réponses de l'API (montants en
 * chaîne, identifiants stables) pour que le remplacement par de vrais appels
 * réseau se limite au fichier `services/apiFactice.js`.
 *
 * Les montants sont des chaînes : négatif = dépense, positif = revenu.
 */

const MARY = { utilisateurId: "u-mary", nom: "Mary", ton: "bleu" };
const HUGO = { utilisateurId: "u-hugo", nom: "Hugo", ton: "rose" };
const LEA = { utilisateurId: "u-lea", nom: "Léa", ton: "vert" };

function creerReleve(annee, mois, revenus, depenses, acces = []) {
  const numeroMois = String(mois + 1).padStart(2, "0");
  const jour = String(3 + (mois % 4)).padStart(2, "0");

  return {
    id: `rel-${annee}-${numeroMois}`,
    annee,
    mois,
    libelle: "Relevé mensuel",
    fichier: `releve-${annee}-${numeroMois}.csv`,
    importeLe: `${annee}-${numeroMois}-${jour}T10:15:00Z`,
    transactionsImportees: 34 + ((mois * 7 + annee) % 18),
    revenus,
    depenses,
    acces,
  };
}

export const RELEVES_INITIAUX = [
  // 2026 — les cinq relevés de la maquette Figma.
  creerReleve(2026, 0, "3545.00", "-1022.00", [MARY, HUGO]),
  creerReleve(2026, 1, "2401.00", "-1502.00"),
  creerReleve(2026, 2, "2110.00", "-1160.00", [MARY]),
  creerReleve(2026, 3, "2542.00", "-1325.00", [HUGO]),
  creerReleve(2026, 4, "2324.00", "-1024.00"),
  // 2025
  creerReleve(2025, 0, "3180.00", "-1490.00", [MARY]),
  creerReleve(2025, 1, "2950.00", "-1310.00"),
  creerReleve(2025, 2, "3120.00", "-1720.00", [HUGO]),
  creerReleve(2025, 3, "3010.00", "-1240.00", [MARY, HUGO]),
  creerReleve(2025, 4, "2890.00", "-1650.00"),
  creerReleve(2025, 5, "3260.00", "-1180.00", [LEA]),
  // 2024
  creerReleve(2024, 0, "2900.00", "-1380.00"),
  creerReleve(2024, 1, "2760.00", "-1210.00", [HUGO]),
  creerReleve(2024, 2, "2870.00", "-1560.00", [MARY]),
  creerReleve(2024, 3, "2840.00", "-1190.00"),
  creerReleve(2024, 4, "3010.00", "-1420.00", [HUGO, LEA]),
];
