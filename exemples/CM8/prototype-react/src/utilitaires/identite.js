/** Transforme « mathieu.dupont@example.com » en « Mathieu Dupont ». */
export function nomDepuisEmail(email) {
  if (!email) return "Mon compte";
  const partieLocale = email.split("@")[0].replace(/[._-]+/g, " ").trim();
  if (!partieLocale) return email;
  return partieLocale
    .split(/\s+/)
    .map((mot) => mot.charAt(0).toUpperCase() + mot.slice(1))
    .join(" ");
}
