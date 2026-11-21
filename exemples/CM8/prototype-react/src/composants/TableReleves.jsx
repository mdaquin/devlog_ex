import BadgeAcces from "./BadgeAcces.jsx";
import { IconeCorbeille, IconeDocument } from "./Icones.jsx";
import { formaterDepenses, formaterRevenus, nomMois } from "../utilitaires/formatage.js";

export default function TableReleves({
  annee,
  releves,
  onOuvrirReleve,
  onSupprimerReleve,
  peutModifier = true,
}) {
  return (
    <div className="table-defilante">
      <table className="table-releves">
        <caption className="sr-only">Relevés bancaires de l'année {annee}</caption>
        <thead>
          <tr>
            <th scope="col">Relevé</th>
            <th scope="col">Revenus</th>
            <th scope="col">Dépenses</th>
            <th scope="col">Accès partagé</th>
            <th scope="col">
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {releves.map((releve) => (
            <tr key={releve.id}>
              <td className="cellule-releve">
                <div className="releve-identite">
                  <span className="vignette-document" aria-hidden="true">
                    <IconeDocument />
                  </span>
                  <span className="releve-textes">
                    <button
                      type="button"
                      className="lien-releve"
                      onClick={() => onOuvrirReleve(releve)}
                    >
                      {nomMois(releve.mois)}
                    </button>
                    <span className="sous-libelle">{releve.libelle}</span>
                  </span>
                </div>
              </td>
              <td className="montant montant--revenu">
                {releve.revenus === null || releve.revenus === undefined
                  ? "—"
                  : formaterRevenus(releve.revenus)}
              </td>
              <td className="montant montant--depense">
                {releve.depenses === null || releve.depenses === undefined
                  ? "—"
                  : formaterDepenses(releve.depenses)}
              </td>
              <td>
                {releve.acces.length === 0 ? (
                  <span className="texte-discret">Vous uniquement</span>
                ) : (
                  <span className="badges-acces">
                    {releve.acces.map((personne) => (
                      <BadgeAcces key={personne.utilisateurId} personne={personne} />
                    ))}
                  </span>
                )}
              </td>
              <td className="cellule-action">
                {peutModifier ? (
                  <button
                    type="button"
                    className="bouton-supprimer"
                    aria-label={`Supprimer le relevé de ${nomMois(releve.mois, { capitale: false })} ${annee}`}
                    title="Supprimer ce relevé"
                    onClick={() => onSupprimerReleve(releve)}
                  >
                    <IconeCorbeille />
                  </button>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
