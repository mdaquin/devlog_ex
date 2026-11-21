import BadgeAcces from "./BadgeAcces.jsx";
import Modale from "./Modale.jsx";
import {
  formaterDate,
  formaterDepenses,
  formaterRevenus,
  nomMois,
} from "../utilitaires/formatage.js";

export default function ModaleDetail({ releve, onFermer }) {
  const pied = (
    <button type="button" className="bouton-secondaire" onClick={onFermer}>
      Fermer
    </button>
  );

  return (
    <Modale
      titre={`Relevé de ${nomMois(releve.mois, { capitale: false })} ${releve.annee}`}
      onFermer={onFermer}
      taille="normale"
      pied={pied}
    >
      <dl className="details-releve">
        <div>
          <dt>Fichier</dt>
          <dd>{releve.fichier}</dd>
        </div>
        <div>
          <dt>Importé le</dt>
          <dd>{releve.importeLe ? formaterDate(releve.importeLe) : "—"}</dd>
        </div>
        <div>
          <dt>Transactions</dt>
          <dd>
            {releve.transactionsImportees}
            {releve.doublonsIgnores > 0 ? (
              <span className="texte-discret"> ({releve.doublonsIgnores} doublon(s) ignoré(s))</span>
            ) : null}
          </dd>
        </div>
        <div>
          <dt>Période</dt>
          <dd>
            {nomMois(releve.mois)} {releve.annee}
          </dd>
        </div>
        <div>
          <dt>Revenus</dt>
          <dd className="montant montant--revenu">
            {releve.revenus === null || releve.revenus === undefined
              ? "—"
              : formaterRevenus(releve.revenus)}
          </dd>
        </div>
        <div>
          <dt>Dépenses</dt>
          <dd className="montant montant--depense">
            {releve.depenses === null || releve.depenses === undefined
              ? "—"
              : formaterDepenses(releve.depenses)}
          </dd>
        </div>
        <div className="pleine-largeur">
          <dt>Accès partagé</dt>
          <dd>
            {releve.acces.length === 0 ? (
              <span className="texte-discret">Vous uniquement</span>
            ) : (
              <span className="badges-acces">
                {releve.acces.map((personne) => (
                  <BadgeAcces key={personne.utilisateurId} personne={personne} />
                ))}
              </span>
            )}
          </dd>
        </div>
      </dl>
    </Modale>
  );
}
