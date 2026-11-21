import { useEffect, useMemo, useRef, useState } from "react";

import Chargement from "./composants/Chargement.jsx";
import EcranConnexion from "./composants/EcranConnexion.jsx";
import Entete from "./composants/Entete.jsx";
import ModaleAjout from "./composants/ModaleAjout.jsx";
import ModaleDetail from "./composants/ModaleDetail.jsx";
import ModaleSuppression from "./composants/ModaleSuppression.jsx";
import Notification from "./composants/Notification.jsx";
import PanneauAnnee from "./composants/PanneauAnnee.jsx";
import { IconeComptes, IconeDocument, IconePlus } from "./composants/Icones.jsx";
import {
  AUTHENTIFICATION_REQUISE,
  MODE_REEL,
  RESTAURATION_POSSIBLE,
  aSession,
  chargerComptes,
  chargerReleves,
  importerReleve,
  restaurerReleve,
  seConnecter,
  seDeconnecter,
  supprimerReleve,
  utilisateurCourant,
} from "./services/api.js";
import { nomMois } from "./utilitaires/formatage.js";

const ANNEE_COURANTE = new Date().getFullYear();

const LIBELLES_ROLE = {
  OWNER: "Propriétaire",
  WRITE: "Modification",
  READ: "Lecture seule",
};

export default function App() {
  const [utilisateur, setUtilisateur] = useState(() =>
    AUTHENTIFICATION_REQUISE
      ? aSession()
        ? utilisateurCourant()
        : null
      : { nom: "Mathieu", email: "" },
  );
  const [comptes, setComptes] = useState([]);
  const [compteId, setCompteId] = useState(null);
  const [releves, setReleves] = useState([]);
  const [chargement, setChargement] = useState(true);
  const [erreurChargement, setErreurChargement] = useState(null);
  const [relance, setRelance] = useState(0);
  const [anneeOuverte, setAnneeOuverte] = useState(null);
  const [triAscendant, setTriAscendant] = useState(true);
  const [modaleAjout, setModaleAjout] = useState(false);
  const [releveDetail, setReleveDetail] = useState(null);
  const [releveASupprimer, setReleveASupprimer] = useState(null);
  const [suppressionEnCours, setSuppressionEnCours] = useState(false);
  const [notification, setNotification] = useState(null);
  const [messageConnexion, setMessageConnexion] = useState("");
  const minuterie = useRef(null);

  function notifier(message, action = null) {
    clearTimeout(minuterie.current);
    setNotification({ id: Date.now(), message, action });
    minuterie.current = setTimeout(() => setNotification(null), 6500);
  }

  /** Déconnecte proprement l'utilisateur si l'API répond 401. */
  function signalerExpiration(erreur) {
    if (!AUTHENTIFICATION_REQUISE || erreur?.statut !== 401) return false;

    seDeconnecter();
    setUtilisateur(null);
    setComptes([]);
    setCompteId(null);
    setReleves([]);
    setReleveDetail(null);
    setReleveASupprimer(null);
    setModaleAjout(false);
    setChargement(false);
    setErreurChargement(null);
    setMessageConnexion("Votre session a expiré. Reconnectez-vous.");
    return true;
  }

  useEffect(() => {
    if (!utilisateur) return undefined;
    let actif = true;

    setErreurChargement(null);
    chargerComptes()
      .then((liste) => {
        if (!actif) return;
        setComptes(liste);
        setCompteId((actuel) =>
          liste.some((compte) => compte.id === actuel) ? actuel : (liste[0]?.id ?? null),
        );

        if (liste.length === 0) {
          setReleves([]);
          setChargement(false);
        }
      })
      .catch((erreur) => {
        if (!actif) return;
        if (signalerExpiration(erreur)) return;
        const message = erreur?.message || "Impossible de charger vos comptes.";
        setErreurChargement(message);
        notifier(message);
        setChargement(false);
      });

    return () => {
      actif = false;
    };
    // `signalerExpiration` et `notifier` sont recréés à chaque rendu mais ne
    // doivent pas relancer le chargement.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [utilisateur, relance]);

  const compteActif = comptes.find((compte) => compte.id === compteId) ?? null;
  const peutModifier = !MODE_REEL || compteActif?.role !== "READ";

  useEffect(() => {
    if (!utilisateur || !compteActif) return undefined;
    let actif = true;

    setChargement(true);
    setErreurChargement(null);
    chargerReleves(compteActif)
      .then((donnees) => {
        if (!actif) return;
        setReleves(donnees);
        const anneesChargees = [...new Set(donnees.map((releve) => releve.annee))].sort(
          (a, b) => b - a,
        );
        setAnneeOuverte(anneesChargees[0] ?? ANNEE_COURANTE);
      })
      .catch((erreur) => {
        if (!actif) return;
        if (signalerExpiration(erreur)) return;
        const message = erreur?.message || "Impossible de charger les relevés.";
        setErreurChargement(message);
        notifier(message);
        setReleves([]);
      })
      .finally(() => {
        if (actif) setChargement(false);
      });

    return () => {
      actif = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [utilisateur, compteActif?.id, relance]);

  useEffect(() => () => clearTimeout(minuterie.current), []);

  // Comme la maquette : les années les plus anciennes d'abord.
  const annees = useMemo(
    () => [...new Set(releves.map((releve) => releve.annee))].sort((a, b) => a - b),
    [releves],
  );
  const anneesDisponibles = annees.length > 0 ? annees : [ANNEE_COURANTE];

  // Si l'année ouverte disparaît (dernier relevé supprimé), on replie proprement.
  useEffect(() => {
    if (chargement || anneeOuverte === null) return;
    if (!annees.includes(anneeOuverte)) {
      setAnneeOuverte(annees[annees.length - 1] ?? null);
    }
  }, [annees, anneeOuverte, chargement]);

  async function connecter(identifiants) {
    const profil = await seConnecter(identifiants);
    setMessageConnexion("");
    setUtilisateur(profil);
    setChargement(true);
  }

  function deconnecter() {
    seDeconnecter();
    setUtilisateur(null);
    setComptes([]);
    setCompteId(null);
    setReleves([]);
    setAnneeOuverte(null);
    setModaleAjout(false);
    setReleveDetail(null);
    setReleveASupprimer(null);
    setNotification(null);
    setErreurChargement(null);
    setMessageConnexion("");
    setChargement(true);
  }

  function basculerAnnee(annee) {
    setAnneeOuverte((actuelle) => (actuelle === annee ? null : annee));
  }

  function actionHorsPerimetre(libelle) {
    notifier(`« ${libelle} » n'est pas implémenté dans ce prototype.`);
  }

  function demanderSuppression(releve) {
    setReleveDetail(null);
    setReleveASupprimer(releve);
  }

  async function confirmerSuppression() {
    if (!releveASupprimer || !compteActif) return;
    const releve = releveASupprimer;
    setSuppressionEnCours(true);

    try {
      await supprimerReleve(releve.id, compteActif.id);
      setReleves((liste) => liste.filter((element) => element.id !== releve.id));
      setReleveASupprimer(null);
      notifier(
        `Le relevé de ${nomMois(releve.mois, { capitale: false })} ${releve.annee} a été supprimé.`,
        RESTAURATION_POSSIBLE
          ? { libelle: "Annuler", executer: () => restaurer(releve) }
          : null,
      );
    } catch (erreur) {
      if (signalerExpiration(erreur)) return;
      notifier(erreur?.message || "La suppression a échoué.");
    } finally {
      setSuppressionEnCours(false);
    }
  }

  async function restaurer(releve) {
    try {
      await restaurerReleve(releve, compteActif?.id);
      setReleves((liste) =>
        liste.some((element) => element.id === releve.id) ? liste : [...liste, releve],
      );
      setAnneeOuverte(releve.annee);
      notifier(
        `Le relevé de ${nomMois(releve.mois, { capitale: false })} ${releve.annee} a été restauré.`,
      );
    } catch {
      notifier("La restauration du relevé a échoué.");
    }
  }

  async function gererImport(parametres) {
    if (!compteActif) throw new Error("Aucun compte bancaire sélectionné.");

    try {
      const nouveau = await importerReleve({ ...parametres, compte: compteActif });
      setReleves((liste) => [...liste.filter((element) => element.id !== nouveau.id), nouveau]);
      setAnneeOuverte(nouveau.annee);
      setModaleAjout(false);

      const doublons =
        nouveau.doublonsIgnores > 0
          ? `, ${nouveau.doublonsIgnores} doublon(s) ignoré(s)`
          : "";
      notifier(
        `« ${nouveau.fichier} » a été importé ` +
          `(${nouveau.transactionsImportees} transaction(s)${doublons}).`,
      );
    } catch (erreur) {
      if (!signalerExpiration(erreur)) throw erreur;
    }
  }

  function fermerNotification() {
    clearTimeout(minuterie.current);
    setNotification(null);
  }

  function executerActionNotification() {
    const action = notification?.action;
    if (!action) return;
    fermerNotification();
    action.executer();
  }

  function ouvrirAjout() {
    if (peutModifier) {
      setModaleAjout(true);
    } else {
      notifier("Votre accès en lecture seule ne permet pas d'importer un relevé.");
    }
  }

  if (AUTHENTIFICATION_REQUISE && !utilisateur) {
    return <EcranConnexion onConnexion={connecter} message={messageConnexion} />;
  }

  const compteSansReleve = MODE_REEL && comptes.length === 0;

  return (
    <div className="application">
      <a className="lien-evitement" href="#contenu">
        Aller au contenu principal
      </a>

      <Entete
        utilisateur={utilisateur}
        onActionHorsPerimetre={actionHorsPerimetre}
        onAjouterReleve={ouvrirAjout}
        onSeDeconnecter={MODE_REEL ? deconnecter : null}
      />

      <main className="contenu" id="contenu">
        <p className="surtitre">Votre espace personnel</p>
        <h1>Mes relevés bancaires</h1>
        <p className="intro">
          Retrouvez vos revenus, vos dépenses et les personnes avec qui vous partagez vos relevés.
        </p>

        {MODE_REEL && compteActif ? (
          <div className="bandeau-compte">
            <span className="bandeau-compte-icone" aria-hidden="true">
              <IconeComptes />
            </span>

            <div className="bandeau-compte-identite">
              <span className="bandeau-compte-libelle">Compte</span>
              {comptes.length > 1 ? (
                <select
                  className="bandeau-compte-select"
                  aria-label="Compte bancaire affiché"
                  value={compteId ?? ""}
                  onChange={(event) => setCompteId(event.target.value)}
                >
                  {comptes.map((compte) => (
                    <option key={compte.id} value={compte.id}>
                      {compte.name} — {LIBELLES_ROLE[compte.role] ?? compte.role}
                    </option>
                  ))}
                </select>
              ) : (
                <strong>{compteActif.name}</strong>
              )}
            </div>

            <span className={`badge-role badge-role--${String(compteActif.role).toLowerCase()}`}>
              {LIBELLES_ROLE[compteActif.role] ?? compteActif.role}
            </span>
          </div>
        ) : null}

        {chargement ? (
          <Chargement />
        ) : erreurChargement ? (
          <div className="etat-vide">
            <span className="etat-vide-icone" aria-hidden="true">
              <IconeDocument />
            </span>
            <h2>Impossible de charger vos données</h2>
            <p>{erreurChargement}</p>
            <button
              type="button"
              className="bouton-principal"
              onClick={() => setRelance((valeur) => valeur + 1)}
            >
              Réessayer
            </button>
          </div>
        ) : compteSansReleve ? (
          <div className="etat-vide">
            <span className="etat-vide-icone" aria-hidden="true">
              <IconeComptes />
            </span>
            <h2>Aucun compte bancaire</h2>
            <p>
              Votre utilisateur n'a encore aucun compte. Créez-en un depuis l'application avant
              d'importer un relevé.
            </p>
          </div>
        ) : (
          <>
            {annees.length === 0 ? (
              <div className="etat-vide">
                <span className="etat-vide-icone" aria-hidden="true">
                  <IconeDocument />
                </span>
                <h2>Aucun relevé pour le moment</h2>
                <p>Importez votre premier relevé CSV ou Excel pour voir vos revenus et vos dépenses.</p>
                {peutModifier ? (
                  <button type="button" className="bouton-principal" onClick={ouvrirAjout}>
                    <IconePlus />
                    Ajouter un relevé
                  </button>
                ) : null}
              </div>
            ) : (
              <div className="liste-annees">
                {annees.map((annee) => {
                  const relevesAnnee = releves.filter((releve) => releve.annee === annee);
                  return (
                    <PanneauAnnee
                      key={annee}
                      annee={annee}
                      releves={relevesAnnee}
                      ouverte={anneeOuverte === annee}
                      triAscendant={triAscendant}
                      peutModifier={peutModifier}
                      onBasculer={() => basculerAnnee(annee)}
                      onBasculerTri={() => setTriAscendant((valeur) => !valeur)}
                      onOuvrirReleve={setReleveDetail}
                      onSupprimerReleve={demanderSuppression}
                      onAjouterReleve={ouvrirAjout}
                    />
                  );
                })}
              </div>
            )}

            <div className="pied-de-page">
              <div>
                <p className="pied-titre">Votre historique à jour, mois après mois.</p>
                <p className="pied-texte">
                  {peutModifier
                    ? "Ajoutez un relevé pour compléter vos transactions."
                    : "Votre accès en lecture seule ne permet pas d'ajouter un relevé."}
                </p>
              </div>
              {peutModifier ? (
                <button type="button" className="bouton-principal" onClick={ouvrirAjout}>
                  <IconePlus />
                  Ajouter un relevé
                </button>
              ) : null}
            </div>

            <p className="mention-prototype">
              {MODE_REEL
                ? "Prototype React — données lues depuis l'API."
                : "Prototype React — données simulées, aucune donnée bancaire réelle."}
            </p>
          </>
        )}
      </main>

      {modaleAjout ? (
        <ModaleAjout
          annees={anneesDisponibles}
          releves={releves}
          anneeInitiale={anneeOuverte ?? anneesDisponibles[anneesDisponibles.length - 1]}
          modeReel={MODE_REEL}
          onFermer={() => setModaleAjout(false)}
          onImporter={gererImport}
        />
      ) : null}

      {releveDetail ? (
        <ModaleDetail releve={releveDetail} onFermer={() => setReleveDetail(null)} />
      ) : null}

      {releveASupprimer ? (
        <ModaleSuppression
          releve={releveASupprimer}
          enCours={suppressionEnCours}
          annulable={RESTAURATION_POSSIBLE}
          onFermer={() => {
            if (!suppressionEnCours) setReleveASupprimer(null);
          }}
          onConfirmer={confirmerSuppression}
        />
      ) : null}

      <Notification
        notification={notification}
        onFermer={fermerNotification}
        onAction={executerActionNotification}
      />
    </div>
  );
}
