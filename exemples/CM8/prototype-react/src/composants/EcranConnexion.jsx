import { useState } from "react";

import { BASE_API } from "../config.js";
import { IconeDocument } from "./Icones.jsx";

export default function EcranConnexion({ onConnexion, message = "" }) {
  const [email, setEmail] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState("");
  const [enCours, setEnCours] = useState(false);

  async function soumettre(event) {
    event.preventDefault();
    if (enCours) return;

    setEnCours(true);
    setErreur("");

    try {
      await onConnexion({ email: email.trim(), password: motDePasse });
      // En cas de succès, App démonte cet écran.
    } catch (erreurConnexion) {
      setErreur(erreurConnexion?.message || "La connexion a échoué.");
      setEnCours(false);
    }
  }

  return (
    <div className="ecran-connexion">
      <main className="carte-connexion">
        <div className="marque-connexion">
          <span className="marque-connexion-logo" aria-hidden="true">
            <IconeDocument />
          </span>
          <span>Mes dépenses</span>
        </div>

        <h1>Mes relevés bancaires</h1>
        <p className="intro-connexion">
          Connectez-vous pour retrouver vos relevés, vos revenus et vos dépenses.
        </p>

        {message ? (
          <p className="message-info" role="status">
            {message}
          </p>
        ) : null}

        <form className="formulaire-connexion" onSubmit={soumettre} aria-busy={enCours}>
          <div className="champ">
            <label htmlFor="connexion-email">Adresse e-mail</label>
            <input
              id="connexion-email"
              type="email"
              autoComplete="username"
              required
              autoFocus
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              disabled={enCours}
            />
          </div>

          <div className="champ">
            <label htmlFor="connexion-mot-de-passe">Mot de passe</label>
            <input
              id="connexion-mot-de-passe"
              type="password"
              autoComplete="current-password"
              required
              value={motDePasse}
              onChange={(event) => setMotDePasse(event.target.value)}
              disabled={enCours}
            />
          </div>

          {erreur ? (
            <p className="message-erreur" role="alert">
              {erreur}
            </p>
          ) : null}

          <button type="submit" className="bouton-principal bouton-large" disabled={enCours}>
            {enCours ? <span className="spinner" aria-hidden="true" /> : null}
            {enCours ? "Connexion…" : "Se connecter"}
          </button>
        </form>

        <p className="note-connexion">
          API : <code>{BASE_API}</code>
        </p>
      </main>
    </div>
  );
}
