import { useEffect, useRef, useState } from "react";

import { useDialogue } from "../utilitaires/useDialogue.js";
import {
  IconeChevron,
  IconeComptes,
  IconeDocument,
  IconeFermer,
  IconeMenu,
  IconePlus,
  IconeUtilisateur,
} from "./Icones.jsx";

function TiroirNavigation({ ouverte, onFermer, onActionHorsPerimetre, onAjouterReleve }) {
  const reference = useDialogue(ouverte);

  function naviguer(libelle) {
    onFermer();
    onActionHorsPerimetre(libelle);
  }

  return (
    <dialog
      ref={reference}
      className="tiroir"
      aria-label="Navigation principale"
      onCancel={(event) => {
        event.preventDefault();
        onFermer();
      }}
      onClick={(event) => {
        if (event.target === reference.current) onFermer();
      }}
    >
      <div className="tiroir-boite">
        <div className="tiroir-entete">
          <span className="tiroir-marque">
            <span className="tiroir-logo" aria-hidden="true">
              <IconeDocument />
            </span>
            Mes dépenses
          </span>
          <button type="button" className="bouton-icone" aria-label="Fermer le menu" onClick={onFermer}>
            <IconeFermer />
          </button>
        </div>

        <nav className="tiroir-navigation" aria-label="Sections de l'application">
          <button type="button" className="tiroir-lien tiroir-lien--actif" aria-current="page" onClick={onFermer}>
            <IconeDocument />
            Mes relevés
          </button>
          <button type="button" className="tiroir-lien" onClick={() => naviguer("Tableau de bord")}>
            <IconeComptes />
            Tableau de bord
          </button>
          <button type="button" className="tiroir-lien" onClick={() => naviguer("Mes catégories")}>
            <IconeComptes />
            Mes catégories
          </button>
          <button type="button" className="tiroir-lien" onClick={() => naviguer("Mes comptes")}>
            <IconeComptes />
            Mes comptes
          </button>
          <button type="button" className="tiroir-lien" onClick={() => naviguer("Paramètres")}>
            <IconeComptes />
            Paramètres
          </button>
        </nav>

        <p className="tiroir-note">
          Prototype : seul l'écran « Mes relevés » est implémenté. Les autres entrées affichent une notification.
        </p>

        <button
          type="button"
          className="tiroir-nouveau"
          onClick={() => {
            onFermer();
            onAjouterReleve();
          }}
        >
          <IconePlus />
          Ajouter un relevé
        </button>
      </div>
    </dialog>
  );
}

export default function Entete({
  utilisateur = { nom: "Mathieu", email: "" },
  onActionHorsPerimetre,
  onAjouterReleve,
  onSeDeconnecter = null,
}) {
  const [tiroirOuvert, setTiroirOuvert] = useState(false);
  const [profilOuvert, setProfilOuvert] = useState(false);
  const blocProfil = useRef(null);

  useEffect(() => {
    if (!profilOuvert) return undefined;

    function surClicExterieur(event) {
      if (blocProfil.current && !blocProfil.current.contains(event.target)) {
        setProfilOuvert(false);
      }
    }

    function surEchap(event) {
      if (event.key === "Escape") setProfilOuvert(false);
    }

    document.addEventListener("pointerdown", surClicExterieur);
    document.addEventListener("keydown", surEchap);
    return () => {
      document.removeEventListener("pointerdown", surClicExterieur);
      document.removeEventListener("keydown", surEchap);
    };
  }, [profilOuvert]);

  function actionProfil(libelle) {
    setProfilOuvert(false);
    if (libelle === "Se déconnecter" && onSeDeconnecter) {
      onSeDeconnecter();
      return;
    }
    onActionHorsPerimetre(libelle);
  }

  return (
    <>
      <header className="entete">
        <div className="entete-contenu">
          <div className="entete-gauche">
            <button
              type="button"
              className="bouton-icone"
              aria-label="Ouvrir le menu"
              aria-expanded={tiroirOuvert}
              onClick={() => setTiroirOuvert(true)}
            >
              <IconeMenu />
            </button>

            <div className="bloc-profil" ref={blocProfil}>
              <button
                type="button"
                className="bouton-profil"
                aria-haspopup="menu"
                aria-expanded={profilOuvert}
                onClick={() => setProfilOuvert((ouvert) => !ouvert)}
              >
                <span className="avatar" aria-hidden="true">
                  <IconeUtilisateur />
                </span>
                <span className="identite">
                  <strong>{utilisateur.nom}</strong>
                  <span title={utilisateur.email || undefined}>
                    {utilisateur.email || "Mon compte"}
                  </span>
                </span>
                <IconeChevron direction="bas" className="chevron-profil" />
              </button>

              {profilOuvert ? (
                <div className="menu-profil" role="menu" aria-label="Mon compte">
                  <button type="button" role="menuitem" onClick={() => actionProfil("Mon compte")}>
                    Mon compte
                  </button>
                  <button type="button" role="menuitem" onClick={() => actionProfil("Paramètres")}>
                    Paramètres
                  </button>
                  <button type="button" role="menuitem" onClick={() => actionProfil("Se déconnecter")}>
                    Se déconnecter
                  </button>
                </div>
              ) : null}
            </div>
          </div>

          <button type="button" className="lien-comptes" onClick={() => onActionHorsPerimetre("Mes comptes")}>
            <IconeComptes />
            <span>mes comptes</span>
          </button>
        </div>
      </header>

      <TiroirNavigation
        ouverte={tiroirOuvert}
        onFermer={() => setTiroirOuvert(false)}
        onActionHorsPerimetre={onActionHorsPerimetre}
        onAjouterReleve={onAjouterReleve}
      />
    </>
  );
}
