export const MOIS = [
  "janvier",
  "février",
  "mars",
  "avril",
  "mai",
  "juin",
  "juillet",
  "août",
  "septembre",
  "octobre",
  "novembre",
  "décembre",
];

/**
 * Nom français d'un mois à partir de son index (0 = janvier).
 * `capitale` sert aux libellés de tableau, `false` aux phrases.
 */
export function nomMois(index, { capitale = true } = {}) {
  const nom = MOIS[index] ?? "";
  return capitale ? nom.charAt(0).toUpperCase() + nom.slice(1) : nom;
}

const formateurMontant = new Intl.NumberFormat("fr-FR", {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/** « + 3 545,00 € » */
export function formaterRevenus(montant) {
  return `+ ${formateurMontant.format(Math.abs(Number(montant)))}`;
}

/** « − 1 022,00 € » (signe moins typographique) */
export function formaterDepenses(montant) {
  return `− ${formateurMontant.format(Math.abs(Number(montant)))}`;
}

const formateurDate = new Intl.DateTimeFormat("fr-FR", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

export function formaterDate(dateIso) {
  return formateurDate.format(new Date(dateIso));
}

export function formaterTaille(octets) {
  if (octets < 1024) return `${octets} o`;
  if (octets < 1024 * 1024) return `${Math.round(octets / 1024)} Ko`;
  return `${(octets / (1024 * 1024)).toFixed(1)} Mo`;
}
