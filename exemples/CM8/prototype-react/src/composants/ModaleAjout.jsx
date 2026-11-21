import { useState } from "react";

import Modale from "./Modale.jsx";
import { IconeDocument, IconePlus, IconeTelechargement } from "./Icones.jsx";
import { MOIS, formaterTaille, nomMois } from "../utilitaires/formatage.js";

const TAILLE_MAX = 10 * 1024 * 1024;

export default function ModaleAjout({
  annees,
  releves,
  anneeInitiale,
  modeReel = false,
  onFermer,
  onImporter,
}) {
  const anneeDeDepart = anneeInitiale ?? annees[0] ?? new Date().getFullYear();

  const [annee, setAnnee] = useState(anneeDeDepart);
  const [mois, setMois] = useState(() => premierMoisLibre(releves, anneeDeDepart));
  const [fichier, setFichier] = useState(null);
  const [erreur, setErreur] = useState("");
  const [survol, setSurvol] = useState(false);
  const [enCours, setEnCours] = useState(false);

  const moisPris = new Set(
    releves.filter((releve) => releve.annee === annee).map((releve) => releve.mois),
  );
  const moisDisponibles = MOIS.map((_, index) => index).filter((index) => !moisPris.has(index));
  const moisEffectif = moisPris.has(mois) ? moisDisponibles[0] : mois;
  const peutImporter = modeReel || moisDisponibles.length > 0;

  function controlerFichier(nouveauFichier) {
    if (!nouveauFichier) return;
    if (!/\.(csv|xlsx)$/i.test(nouveauFichier.name)) {
      setErreur("Formats acceptés : un fichier .csv ou .xlsx.");
      setFichier(null);
      return;
    }
    if (nouveauFichier.size > TAILLE_MAX) {
      setErreur("Le fichier dépasse la limite de 10 Mo.");
      setFichier(null);
      return;
    }
    setErreur("");
    setFichier(nouveauFichier);
  }

  async function soumettre(event) {
    event.preventDefault();
    if (enCours) return;
    if (!fichier) {
      setErreur("Choisissez un fichier CSV ou Excel.");
      return;
    }
    if (!peutImporter) {
      setErreur(`Tous les mois de ${annee} ont déjà un relevé.`);
      return;
    }

    setEnCours(true);
    setErreur("");
    try {
      await onImporter(
        modeReel ? { fichier } : { annee, mois: moisEffectif, fichier },
      );
    } catch (erreurImport) {
      setErreur(erreurImport.message || "L'import a échoué.");
      setEnCours(false);
    }
  }

  const pied = (
    <>
      <button type="button" className="bouton-secondaire" onClick={onFermer} disabled={enCours}>
        Annuler
      </button>
      <button
        type="submit"
        form="formulaire-import"
        className="bouton-principal"
        disabled={enCours || !peutImporter}
      >
        {enCours ? <span className="spinner" aria-hidden="true" /> : <IconePlus />}
        {enCours ? "Import en cours…" : "Importer le relevé"}
      </button>
    </>
  );

  return (
    <Modale
      titre="Ajouter un relevé"
      onFermer={onFermer}
      fermable={!enCours}
      taille="normale"
      pied={pied}
    >
      <form id="formulaire-import" className="formulaire-import" onSubmit={soumettre} aria-busy={enCours}>
        {modeReel ? (
          <p className="note-prototype">
            L'API déduit l'année, le mois et les totaux à partir du contenu du fichier.
          </p>
        ) : (
          <div className="champs-grille">
            <div className="champ">
              <label htmlFor="annee-import">Année</label>
              <select
                id="annee-import"
                value={annee}
                onChange={(event) => setAnnee(Number(event.target.value))}
                disabled={enCours}
              >
                {annees.map((valeur) => (
                  <option key={valeur} value={valeur}>
                    {valeur}
                  </option>
                ))}
              </select>
            </div>

            <div className="champ">
              <label htmlFor="mois-import">Mois</label>
              <select
                id="mois-import"
                value={moisEffectif ?? ""}
                onChange={(event) => setMois(Number(event.target.value))}
                disabled={enCours || !peutImporter}
              >
                {peutImporter ? (
                  moisDisponibles.map((index) => (
                    <option key={index} value={index}>
                      {nomMois(index)}
                    </option>
                  ))
                ) : (
                  <option value="">Aucun mois disponible</option>
                )}
              </select>
            </div>
          </div>
        )}

        <div className="champ">
          <label htmlFor="fichier-import">Fichier du relevé</label>
          <label
            className={`zone-fichier ${survol ? "zone-fichier--survol" : ""}`}
            onDragOver={(event) => {
              event.preventDefault();
              setSurvol(true);
            }}
            onDragLeave={() => setSurvol(false)}
            onDrop={(event) => {
              event.preventDefault();
              setSurvol(false);
              controlerFichier(event.dataTransfer.files?.[0]);
            }}
          >
            <input
              id="fichier-import"
              type="file"
              className="champ-fichier"
              accept=".csv,.xlsx"
              onChange={(event) => {
                controlerFichier(event.target.files?.[0]);
                event.target.value = "";
              }}
              disabled={enCours}
            />

            {fichier ? (
              <span className="fichier-choisi">
                <span className="fichier-choisi-icone" aria-hidden="true">
                  <IconeDocument />
                </span>
                <span className="fichier-choisi-textes">
                  <strong>{fichier.name}</strong>
                  <span>{formaterTaille(fichier.size)} · cliquez pour remplacer</span>
                </span>
              </span>
            ) : (
              <>
                <span className="zone-fichier-icone" aria-hidden="true">
                  <IconeTelechargement />
                </span>
                <span className="zone-fichier-titre">Glissez votre relevé ici</span>
                <span className="zone-fichier-texte">
                  ou cliquez pour parcourir · CSV ou Excel, 10 Mo max.
                </span>
              </>
            )}
          </label>
        </div>

        {erreur ? (
          <p className="message-erreur" role="alert">
            {erreur}
          </p>
        ) : null}

        {!peutImporter ? (
          <p className="message-erreur" role="alert">
            Tous les mois de {annee} ont déjà un relevé.
          </p>
        ) : null}

        <p className="note-prototype">
          {modeReel
            ? "Le fichier est envoyé tel quel à l'API : le serveur calcule la période, les totaux et ignore les doublons."
            : "Prototype : le contenu du fichier n'est pas lu. Un relevé d'exemple est créé pour le mois choisi."}
        </p>
      </form>
    </Modale>
  );
}

function premierMoisLibre(releves, annee) {
  const pris = new Set(releves.filter((releve) => releve.annee === annee).map((releve) => releve.mois));
  const libre = MOIS.map((_, index) => index).find((index) => !pris.has(index));
  return libre ?? 0;
}
