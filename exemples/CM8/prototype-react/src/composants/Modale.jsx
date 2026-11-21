import { useId } from "react";

import { useDialogue } from "../utilitaires/useDialogue.js";
import { IconeFermer } from "./Icones.jsx";

/**
 * Boîte de dialogue native (<dialog>) partagée par les trois modales.
 * `fermable=false` bloque la fermeture pendant une opération en cours.
 */
export default function Modale({
  ouverte = true,
  titre,
  onFermer,
  fermable = true,
  taille = "normale",
  children,
  pied,
}) {
  const reference = useDialogue(ouverte);
  const idTitre = useId();

  function fermerSiPossible() {
    if (fermable) onFermer();
  }

  return (
    <dialog
      ref={reference}
      className={`modale modale--${taille}`}
      aria-labelledby={idTitre}
      onCancel={(event) => {
        event.preventDefault();
        fermerSiPossible();
      }}
      onClick={(event) => {
        // Un clic sur le fond assombri a pour cible le <dialog> lui-même.
        if (event.target === reference.current) fermerSiPossible();
      }}
    >
      <div className="modale-boite">
        <div className="modale-entete">
          <h2 className="modale-titre" id={idTitre}>
            {titre}
          </h2>
          <button
            type="button"
            className="bouton-icone modale-fermer"
            aria-label="Fermer"
            onClick={fermerSiPossible}
            disabled={!fermable}
          >
            <IconeFermer />
          </button>
        </div>
        <div className="modale-corps">{children}</div>
        {pied ? <div className="modale-pied">{pied}</div> : null}
      </div>
    </dialog>
  );
}
