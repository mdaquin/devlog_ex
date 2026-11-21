import TableReleves from "./TableReleves.jsx";
import { IconeChevron, IconePlus } from "./Icones.jsx";

export default function PanneauAnnee({
  annee,
  releves,
  ouverte,
  triAscendant,
  peutModifier = true,
  onBasculer,
  onBasculerTri,
  onOuvrirReleve,
  onSupprimerReleve,
  onAjouterReleve,
}) {
  const relevesTries = [...releves].sort((a, b) => (triAscendant ? a.mois - b.mois : b.mois - a.mois));
  const nombre = releves.length;

  return (
    <section className={`panneau-annee ${ouverte ? "panneau-annee--ouverte" : ""}`}>
      <div className="panneau-entete">
        <button
          type="button"
          className="panneau-bascule"
          aria-expanded={ouverte}
          aria-controls={`annee-${annee}`}
          onClick={onBasculer}
        >
          <span className="panneau-annee-titre">{annee}</span>
          {ouverte ? (
            <span className="pastille-nombre">
              {nombre} {nombre > 1 ? "relevés" : "relevé"}
            </span>
          ) : (
            <span className="panneau-indication">Afficher les relevés</span>
          )}
          <IconeChevron
            direction={ouverte ? "haut" : "droite"}
            className="panneau-chevron"
          />
        </button>

        {ouverte && nombre > 0 ? (
          <button
            type="button"
            className="bouton-tri"
            onClick={onBasculerTri}
            aria-label={
              triAscendant
                ? "Trier du plus récent au plus ancien"
                : "Trier du plus ancien au plus récent"
            }
            title={
              triAscendant
                ? "Actuellement du plus ancien au plus récent"
                : "Actuellement du plus récent au plus ancien"
            }
          >
            <span className="texte-tri">
              {triAscendant ? "Du plus ancien au plus récent" : "Du plus récent au plus ancien"}
            </span>
          </button>
        ) : null}
      </div>

      <div id={`annee-${annee}`} className="panneau-corps" hidden={!ouverte}>
        {ouverte && nombre === 0 ? (
          <div className="annee-vide">
            <p className="annee-vide-titre">Aucun relevé pour {annee}.</p>
            <p className="annee-vide-texte">Importez un relevé CSV ou Excel pour compléter cette année.</p>
            {peutModifier ? (
              <button type="button" className="bouton-secondaire" onClick={onAjouterReleve}>
                <IconePlus />
                Ajouter un relevé
              </button>
            ) : null}
          </div>
        ) : null}

        {ouverte && nombre > 0 ? (
          <TableReleves
            annee={annee}
            releves={relevesTries}
            onOuvrirReleve={onOuvrirReleve}
            onSupprimerReleve={onSupprimerReleve}
            peutModifier={peutModifier}
          />
        ) : null}
      </div>
    </section>
  );
}
