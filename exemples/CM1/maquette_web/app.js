/* Comportement de la maquette : navigation, rendu des vues, interactions.
 *
 * Le principe est le meme que dans les versions Python de l'exemple :
 * les donnees (donnees.js) et le dessin (graphiques.js) sont ailleurs, ce
 * fichier ne fait que les mettre en scene.
 */
(function () {
  "use strict";

  /* ------------------------------ Etat ------------------------------- */

  const etat = {
    utilisateur: Donnees.profils[0].id,
    nombreDeMois: 12, // la barre de filtres agit sur tous les graphiques
    tableauxOuverts: {}, // quel graphique est affiche sous forme de tableau
  };

  /* ---------------------------- Formatage ---------------------------- */

  const euros = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  });
  const eurosPrecis = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  });

  function formater(valeur) {
    return euros.format(valeur);
  }

  function formaterSigne(valeur) {
    return (valeur > 0 ? "+" : "") + eurosPrecis.format(valeur);
  }

  function element(html) {
    const gabarit = document.createElement("template");
    gabarit.innerHTML = html.trim();
    return gabarit.content.firstElementChild;
  }

  function couleur(nom) {
    return Graphiques.couleur(nom);
  }

  /* Le theme reellement affiche : celui choisi par l'utilisateur s'il en a
     choisi un, sinon celui du systeme d'exploitation. */
  function themeSombreActif() {
    const choisi = document.documentElement.dataset.theme;
    if (choisi) return choisi === "sombre";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  /* --------------------------- Vue courante -------------------------- */

  function changerDeVue(nom) {
    document.querySelectorAll(".onglet").forEach(function (onglet) {
      onglet.classList.toggle("actif", onglet.dataset.vue === nom);
    });
    document.querySelectorAll(".vue").forEach(function (vue) {
      vue.hidden = vue.id !== "vue-" + nom;
    });
  }

  /* ----------------------------- Rendu ------------------------------- */

  function rendre() {
    const donnees = Donnees.pourUtilisateur(etat.utilisateur);
    const depuis = Donnees.mois.length - etat.nombreDeMois;

    rendreTableauDeBord(donnees, depuis);
    rendreReleves(donnees);
    rendreAmis(donnees, depuis);
  }

  /* -- Tableau de bord -- */

  function rendreTableauDeBord(donnees, depuis) {
    const dernier = donnees.mois.length - 1;

    // Le chiffre vedette : un seul par vue.
    document.getElementById("solde-du-mois").textContent = formaterSigne(donnees.soldeDuMois);
    const ecart = donnees.soldeDuMois - donnees.soldePrecedent;
    document.getElementById("solde-delta").innerHTML =
      `<span class="${ecart >= 0 ? "hausse" : "baisse"}">${formaterSigne(ecart)}</span>` +
      ` par rapport a ${donnees.mois[dernier - 1]}`;

    // Les tuiles de chiffres cles.
    const tuiles = [
      {
        etiquette: "Revenus du mois",
        valeur: donnees.revenus[dernier],
        precedent: donnees.revenus[dernier - 1],
        serie: donnees.revenus.slice(depuis),
        couleur: couleur("--serie-1"),
        hausseEstBonne: true,
      },
      {
        etiquette: "Depenses du mois",
        valeur: donnees.depenses[dernier],
        precedent: donnees.depenses[dernier - 1],
        serie: donnees.depenses.slice(depuis),
        couleur: couleur("--serie-2"),
        hausseEstBonne: false,
      },
      {
        etiquette: "Epargne cumulee (12 mois)",
        valeur: donnees.epargneCumulee,
        serie: donnees.revenus.map((revenu, index) => revenu - donnees.depenses[index]).slice(depuis),
        couleur: couleur("--serie-3"),
      },
    ];

    const conteneur = document.getElementById("tuiles-cles");
    conteneur.innerHTML = "";

    tuiles.forEach(function (tuile) {
      let delta = "";
      if (tuile.precedent !== undefined) {
        const difference = tuile.valeur - tuile.precedent;
        const bonne = tuile.hausseEstBonne ? difference >= 0 : difference <= 0;
        delta =
          `<span class="delta"><span class="${bonne ? "hausse" : "baisse"}">` +
          `${formaterSigne(difference)}</span> vs mois precedent</span>`;
      }

      const noeud = element(
        `<div class="tuile">
           <span class="etiquette">${tuile.etiquette}</span>
           <span class="tuile-valeur">${formater(tuile.valeur)}</span>
           ${delta}
           <div class="miniature"></div>
         </div>`
      );
      conteneur.appendChild(noeud);
      Graphiques.miniature(noeud.querySelector(".miniature"), tuile.serie, tuile.couleur);
    });

    // Graphique 1 : deux series dans le temps -> courbes + legende.
    const mois = donnees.mois.slice(depuis);
    const seriesEvolution = [
      { nom: "Revenus", valeurs: donnees.revenus.slice(depuis), couleur: couleur("--serie-1") },
      { nom: "Depenses", valeurs: donnees.depenses.slice(depuis), couleur: couleur("--serie-2") },
    ];

    document.getElementById("sous-titre-evolution").textContent =
      `${mois.length} derniers mois`;
    legende("legende-evolution", seriesEvolution);
    Graphiques.courbes(document.getElementById("graphique-evolution"), {
      etiquettes: mois,
      series: seriesEvolution,
      format: formater,
      description: "Revenus et depenses mois par mois",
    });
    remplirTableau("tableau-evolution", ["Mois", "Revenus", "Depenses", "Solde"], mois.map(
      function (nom, index) {
        const revenus = seriesEvolution[0].valeurs[index];
        const depenses = seriesEvolution[1].valeurs[index];
        return [nom, formater(revenus), formater(depenses), formaterSigne(revenus - depenses)];
      }
    ));

    // Graphique 2 : comparer des categories entre elles -> une seule serie,
    // une seule couleur (une couleur par barre n'apporterait aucune
    // information que la longueur ne donne deja).
    const total = donnees.categories.reduce((somme, categorie) => somme + categorie.montant, 0);
    Graphiques.barres(document.getElementById("graphique-categories"), {
      categories: donnees.categories.map((categorie) => categorie.nom),
      series: [
        {
          nom: "Depenses",
          valeurs: donnees.categories.map((categorie) => categorie.montant),
          couleur: couleur("--serie-1"),
        },
      ],
      format: formater,
      description: "Depenses par categorie sur le dernier mois",
    });
    remplirTableau(
      "tableau-categories",
      ["Categorie", "Montant", "Part"],
      donnees.categories.map(function (categorie) {
        return [
          categorie.nom,
          formater(categorie.montant),
          Math.round((categorie.montant / total) * 100) + " %",
        ];
      })
    );
  }

  /* -- Mes releves -- */

  function rendreReleves(donnees) {
    const corps = document.querySelector("#tableau-releves tbody");
    corps.innerHTML = "";
    donnees.releves.forEach(function (releve) {
      corps.appendChild(ligneReleve(releve));
    });
    document.getElementById("sous-titre-releves").textContent =
      `${donnees.releves.length} releves pour ${donnees.profil.nom}`;
  }

  function ligneReleve(releve) {
    const enCours = releve.statut !== "importe";
    return element(
      `<tr>
         <td>${releve.fichier}</td>
         <td>${releve.periode}</td>
         <td class="nombre chiffres">${releve.operations}</td>
         <td class="nombre chiffres">${formater(releve.revenus)}</td>
         <td class="nombre chiffres">${formater(releve.depenses)}</td>
         <td class="nombre chiffres">${formaterSigne(releve.revenus - releve.depenses)}</td>
         <td><span class="badge${enCours ? " en-cours" : ""}">${
        enCours ? "Analyse en cours" : "Importe"
      }</span></td>
       </tr>`
    );
  }

  /* -- Mes amis -- */

  function rendreAmis(donnees, depuis) {
    // Classement du mois : chacun compare a son propre objectif.
    const participants = [{ nom: "Moi", initiales: donnees.profil.initiales, moi: true,
      depensesDuMois: donnees.depenses[donnees.depenses.length - 1],
      objectif: donnees.profil.objectif }].concat(donnees.amis);

    const liste = document.getElementById("liste-amis");
    liste.innerHTML = "";

    participants
      .slice()
      .sort((a, b) => a.depensesDuMois / a.objectif - b.depensesDuMois / b.objectif)
      .forEach(function (participant) {
        const part = participant.depensesDuMois / participant.objectif;
        const etatJauge = part > 1 ? "depasse" : part > 0.9 ? "attention" : "";
        const texteEtat =
          part > 1 ? "Objectif depasse" : part > 0.9 ? "Objectif presque atteint" : "Dans l'objectif";

        liste.appendChild(
          element(
            `<li class="ami">
               <span class="avatar">${participant.initiales}</span>
               <div>
                 <div class="ami-nom">
                   <strong>${participant.nom}</strong>
                   <span class="chiffres">${formater(participant.depensesDuMois)} / ${formater(
              participant.objectif
            )}</span>
                 </div>
                 <div class="jauge ${etatJauge}">
                   <div style="width:${Math.min(100, part * 100).toFixed(0)}%"></div>
                 </div>
               </div>
               <span class="ami-etat">${texteEtat}</span>
             </li>`
          )
        );
      });

    // Graphique 3 : moi + mes amis + la moyenne du groupe (en gris, c'est un
    // repere, pas une personne).
    const mois = donnees.mois.slice(depuis);
    const seriesAmis = [
      { nom: "Moi", valeurs: donnees.depenses.slice(depuis), couleur: couleur("--serie-1") },
      {
        nom: donnees.amis[0].nom.split(" ")[0],
        valeurs: donnees.amis[0].depenses.slice(depuis),
        couleur: couleur("--serie-2"),
      },
      {
        nom: donnees.amis[1].nom.split(" ")[0],
        valeurs: donnees.amis[1].depenses.slice(depuis),
        couleur: couleur("--serie-3"),
      },
      {
        nom: "Moyenne",
        valeurs: donnees.moyenneGroupe.slice(depuis),
        couleur: couleur("--contexte"),
        contexte: true,
      },
    ];

    legende("legende-amis", seriesAmis);
    Graphiques.courbes(document.getElementById("graphique-amis"), {
      etiquettes: mois,
      series: seriesAmis,
      format: formater,
      description: "Depenses mensuelles comparees entre amis",
    });
    remplirTableau(
      "tableau-amis",
      ["Mois"].concat(seriesAmis.map((serie) => serie.nom)),
      mois.map(function (nom, index) {
        return [nom].concat(seriesAmis.map((serie) => formater(serie.valeurs[index])));
      })
    );

    // Graphique 4 : moi face a la moyenne du groupe, categorie par categorie.
    const seriesComparaison = [
      {
        nom: "Moi",
        valeurs: donnees.categories.map((categorie) => categorie.montant),
        couleur: couleur("--serie-1"),
      },
      {
        nom: "Moyenne du groupe",
        valeurs: donnees.categories.map((categorie) => categorie.montantGroupe),
        couleur: couleur("--contexte"),
      },
    ];

    legende("legende-comparaison", seriesComparaison);
    Graphiques.barres(document.getElementById("graphique-comparaison"), {
      categories: donnees.categories.map((categorie) => categorie.nom),
      series: seriesComparaison,
      format: formater,
      description: "Depenses par categorie comparees a la moyenne du groupe",
    });
    remplirTableau(
      "tableau-comparaison",
      ["Categorie", "Moi", "Moyenne du groupe", "Ecart"],
      donnees.categories.map(function (categorie) {
        return [
          categorie.nom,
          formater(categorie.montant),
          formater(categorie.montantGroupe),
          formaterSigne(categorie.montant - categorie.montantGroupe),
        ];
      })
    );
  }

  /* ------------------- Legendes et tableaux jumeaux ------------------ */

  /* Des qu'il y a deux series, une legende est presente : la couleur seule
     ne doit jamais etre le seul moyen d'identifier une serie. */
  function legende(identifiant, series) {
    const conteneur = document.getElementById(identifiant);
    if (!conteneur) return;
    conteneur.innerHTML = series
      .map(
        (serie) =>
          `<span><span class="puce" style="background:${serie.couleur}"></span>${serie.nom}</span>`
      )
      .join("");
  }

  /* Chaque graphique a son tableau equivalent : c'est la version lisible
     sans couleurs, et sans survol. */
  function remplirTableau(identifiant, entetes, lignes) {
    const conteneur = document.getElementById(identifiant);
    conteneur.innerHTML =
      `<div class="tableau-defilant"><table class="tableau"><thead><tr>` +
      entetes
        .map(
          (entete, index) =>
            `<th scope="col"${index > 0 ? ' class="nombre"' : ""}>${entete}</th>`
        )
        .join("") +
      `</tr></thead><tbody>` +
      lignes
        .map(
          (ligne) =>
            "<tr>" +
            ligne
              .map(
                (cellule, index) =>
                  `<td${index > 0 ? ' class="nombre chiffres"' : ""}>${cellule}</td>`
              )
              .join("") +
            "</tr>"
        )
        .join("") +
      `</tbody></table></div>`;
  }

  /* --------------------------- Interactions -------------------------- */

  function messageFlash(texte) {
    const boite = document.getElementById("message-flash");
    boite.textContent = texte;
    boite.hidden = false;
    clearTimeout(messageFlash.minuterie);
    messageFlash.minuterie = setTimeout(() => (boite.hidden = true), 2600);
  }

  /* Simule l'import d'un fichier : la ligne apparait tout de suite, en
     "analyse en cours", puis passe a "importe". */
  function simulerImport(nomDuFichier) {
    const corps = document.querySelector("#tableau-releves tbody");
    const releve = {
      fichier: nomDuFichier || "releve_juin_26.xlsx",
      periode: "juin 26",
      operations: 34,
      revenus: 2461,
      depenses: 1912,
      statut: "en-cours",
    };
    const ligne = ligneReleve(releve);
    corps.prepend(ligne);
    changerDeVue("releves");

    setTimeout(function () {
      releve.statut = "importe";
      corps.replaceChild(ligneReleve(releve), ligne);
      messageFlash(`${releve.fichier} importe : 34 operations ajoutees.`);
    }, 1400);
  }

  function installerInteractions() {
    // Navigation par onglets.
    document.querySelectorAll(".onglet").forEach(function (onglet) {
      onglet.addEventListener("click", () => changerDeVue(onglet.dataset.vue));
    });

    // Choix de l'utilisateur : c'est ce qui simule le cote multi-utilisateurs.
    const choix = document.getElementById("choix-utilisateur");
    choix.innerHTML = Donnees.profils
      .map((profil) => `<option value="${profil.id}">${profil.nom}</option>`)
      .join("");
    choix.addEventListener("change", function () {
      etat.utilisateur = choix.value;
      rendre();
    });

    // Barre de filtres : une seule, qui agit sur tous les graphiques.
    document.querySelectorAll("#filtre-periode .segment").forEach(function (segment) {
      segment.addEventListener("click", function () {
        document
          .querySelectorAll("#filtre-periode .segment")
          .forEach((autre) => autre.classList.toggle("actif", autre === segment));
        etat.nombreDeMois = Number(segment.dataset.mois);
        rendre();
      });
    });

    // Bascule graphique <-> tableau, sur chaque carte.
    document.querySelectorAll("[data-bascule]").forEach(function (bouton) {
      bouton.addEventListener("click", function () {
        const nom = bouton.dataset.bascule;
        const ouvert = !etat.tableauxOuverts[nom];
        etat.tableauxOuverts[nom] = ouvert;
        document.getElementById("graphique-" + nom).hidden = ouvert;
        document.getElementById("tableau-" + nom).hidden = !ouvert;
        const legendeAssociee = document.getElementById("legende-" + nom);
        if (legendeAssociee) legendeAssociee.hidden = ouvert;
        bouton.textContent = ouvert ? "Voir le graphique" : "Voir le tableau";
      });
    });

    // Import : bouton, glisser-deposer, et le formulaire d'invitation.
    const zone = document.getElementById("zone-depot");
    document.getElementById("bouton-import").addEventListener("click", () => simulerImport());
    zone.addEventListener("dragover", function (evenement) {
      evenement.preventDefault();
      zone.classList.add("survol");
    });
    zone.addEventListener("dragleave", () => zone.classList.remove("survol"));
    zone.addEventListener("drop", function (evenement) {
      evenement.preventDefault();
      zone.classList.remove("survol");
      const fichier = evenement.dataTransfer.files[0];
      simulerImport(fichier ? fichier.name : undefined);
    });

    document.getElementById("formulaire-invitation").addEventListener("submit", function (evenement) {
      evenement.preventDefault();
      const champ = evenement.target.querySelector("input");
      messageFlash(`Invitation envoyee a ${champ.value || "votre ami"}.`);
      champ.value = "";
    });

    // Theme clair / sombre. Tant que l'utilisateur n'a rien choisi, la page
    // suit le reglage du systeme : le bouton doit donc proposer l'inverse de
    // ce qui est reellement affiche, pas l'inverse d'une valeur par defaut.
    const bouton = document.getElementById("bascule-theme");
    bouton.textContent = themeSombreActif() ? "Theme clair" : "Theme sombre";
    bouton.addEventListener("click", function () {
      const sombreActif = themeSombreActif();
      document.documentElement.dataset.theme = sombreActif ? "clair" : "sombre";
      bouton.textContent = sombreActif ? "Theme sombre" : "Theme clair";
      // Les graphiques lisent les couleurs dans la feuille de style : il faut
      // les redessiner apres la bascule.
      rendre();
    });
  }

  installerInteractions();
  rendre();
})();
