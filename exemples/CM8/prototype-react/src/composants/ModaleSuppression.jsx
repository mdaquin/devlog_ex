import Modale from "./Modale.jsx";
import { nomMois } from "../utilitaires/formatage.js";

export default function ModaleSuppression({
  releve,
  enCours,
  annulable = false,
  onFermer,
  onConfirmer,
}) {
  const mois = nomMois(releve.mois, { capitale: false });
  const transactions = releve.transactionsImportees;
  const motTransaction = transactions > 1 ? "transactions" : "transaction";

  const pied = (
    <>
      <button type="button" className="bouton-secondaire" onClick={onFermer} disabled={enCours}>
        Annuler
      </button>
      <button type="button" className="bouton-danger" onClick={onConfirmer} disabled={enCours}>
        {enCours ? <span className="spinner" aria-hidden="true" /> : null}
        {enCours ? "Suppression…" : "Supprimer"}
      </button>
    </>
  );

  return (
    <Modale
      titre="Supprimer ce relevé ?"
      onFermer={onFermer}
      fermable={!enCours}
      taille="petite"
      pied={pied}
    >
      <p>
        Le relevé de <strong>{mois} {releve.annee}</strong> et ses{" "}
        <strong>{transactions} {motTransaction}</strong> seront supprimés.
      </p>
      <p className="texte-discret">
        L'extrait et les transactions qu'il contient seront supprimés.{" "}
        {annulable
          ? "Vous pourrez annuler juste après."
          : "Cette action est irréversible."}
      </p>
    </Modale>
  );
}
