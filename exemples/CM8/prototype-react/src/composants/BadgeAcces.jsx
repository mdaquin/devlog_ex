import { IconeUtilisateur } from "./Icones.jsx";

export default function BadgeAcces({ personne }) {
  const ton = personne.ton ?? "bleu";

  return (
    <span
      className={`badge-acces badge-acces--${ton}`}
      title={
        personne.permission
          ? `Accès ${personne.permission} — ${personne.nom}`
          : `Accès partagé avec ${personne.nom}`
      }
    >
      <span className="badge-acces-pastille" aria-hidden="true">
        <IconeUtilisateur />
      </span>
      {personne.nom}
    </span>
  );
}
