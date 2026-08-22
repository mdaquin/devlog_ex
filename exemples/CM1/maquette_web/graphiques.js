/* Petite bibliotheque de graphiques en SVG, ecrite a la main.
 *
 * Aucune dependance : chaque fonction fabrique du SVG sous forme de texte,
 * l'insere dans un element hote, puis y accroche les interactions.
 *
 * Regles de dessin suivies partout :
 *   - traits fins, grille en filet, beaucoup d'air ;
 *   - couleurs sur les marques uniquement, jamais sur le texte ;
 *   - une legende des qu'il y a deux series, plus quelques etiquettes
 *     directes (jamais une valeur sur chaque point) ;
 *   - un ecart de 2 px de la couleur du fond separe deux marques qui se
 *     touchent (on ne dessine pas de contour autour des barres).
 */
const Graphiques = (function () {
  "use strict";

  // Les couleurs sont lues sur la page : elles changent donc avec le theme.
  function couleur(nom) {
    return getComputedStyle(document.documentElement).getPropertyValue(nom).trim();
  }

  function echapper(texte) {
    return String(texte).replace(/[&<>"]/g, function (caractere) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[caractere];
    });
  }

  /* Choisit un pas de graduation "propre" (1, 2, 2,5 ou 5 fois une puissance
     de 10) pour que l'axe affiche 0 / 1 000 / 2 000 plutot que 0 / 875 / 1 750. */
  function pasPropre(maximum, nombreDeGraduations) {
    const brut = Math.max(maximum, 1) / nombreDeGraduations;
    const puissance = Math.pow(10, Math.floor(Math.log10(brut)));
    const facteur = [1, 2, 2.5, 5, 10].find((candidat) => brut <= candidat * puissance) || 10;
    return facteur * puissance;
  }

  /* Arrondit une valeur maximale a un multiple du pas de graduation. */
  function maximumPropre(valeur, nombreDeGraduations) {
    const graduations = nombreDeGraduations || 4;
    const pas = pasPropre(valeur, graduations);
    return pas * graduations;
  }

  /* ----------------------------------------------------------------
   * L'infobulle : un seul element, partage par tous les graphiques.
   * ---------------------------------------------------------------- */

  function infobulle() {
    let element = document.getElementById("infobulle");
    if (!element) {
      element = document.createElement("div");
      element.id = "infobulle";
      element.setAttribute("role", "status");
      document.body.appendChild(element);
    }
    return element;
  }

  function montrerInfobulle(contenu, evenement) {
    const element = infobulle();
    element.innerHTML = contenu;
    element.hidden = false;
    const marge = 14;
    const largeur = element.offsetWidth;
    const gauche = Math.min(evenement.clientX + marge, window.innerWidth - largeur - 8);
    element.style.left = Math.max(8, gauche) + "px";
    element.style.top = Math.max(8, evenement.clientY - element.offsetHeight - marge) + "px";
  }

  function cacherInfobulle() {
    infobulle().hidden = true;
  }

  /* ----------------------------------------------------------------
   * Courbes : evolution dans le temps, une ou plusieurs series.
   * ---------------------------------------------------------------- */

  function courbes(hote, options) {
    const etiquettes = options.etiquettes;
    const series = options.series;
    const format = options.format || String;
    const largeur = 760;
    const hauteur = 320;
    const marge = { haut: 20, droite: 152, bas: 38, gauche: 62 };

    const toutes = series.reduce((liste, serie) => liste.concat(serie.valeurs), []);
    const maximum = maximumPropre(Math.max.apply(null, toutes));
    const x = (index) =>
      marge.gauche +
      (index * (largeur - marge.gauche - marge.droite)) / Math.max(1, etiquettes.length - 1);
    const y = (valeur) =>
      hauteur - marge.bas - (valeur / maximum) * (hauteur - marge.haut - marge.bas);

    const grille = couleur("--grille");
    const axe = couleur("--axe");
    const encreDiscrete = couleur("--encre-discrete");
    const encreSecondaire = couleur("--encre-secondaire");
    const fond = couleur("--surface-graphique");

    let svg = "";

    // Grille horizontale (filets pleins, jamais en pointilles) et graduations.
    for (let i = 0; i <= 4; i++) {
      const valeur = (maximum / 4) * i;
      const position = y(valeur);
      svg +=
        `<line x1="${marge.gauche}" y1="${position}" x2="${largeur - marge.droite}" ` +
        `y2="${position}" stroke="${grille}" stroke-width="1" />` +
        `<text x="${marge.gauche - 10}" y="${position + 4}" text-anchor="end" ` +
        `font-size="12" fill="${encreDiscrete}" class="chiffres">${format(valeur, true)}</text>`;
    }

    // Axe des mois : une etiquette sur deux, comptees depuis la fin, pour que
    // le dernier mois soit toujours ecrit sans chevaucher son voisin.
    etiquettes.forEach(function (nomDuMois, index) {
      if ((etiquettes.length - 1 - index) % 2 !== 0) return;
      svg +=
        `<text x="${x(index)}" y="${hauteur - marge.bas + 20}" text-anchor="middle" ` +
        `font-size="12" fill="${encreDiscrete}">${echapper(nomDuMois)}</text>`;
    });

    svg +=
      `<line x1="${marge.gauche}" y1="${hauteur - marge.bas}" x2="${largeur - marge.droite}" ` +
      `y2="${hauteur - marge.bas}" stroke="${axe}" stroke-width="1" />`;

    // Le repere vertical suit la souris ; il est cache au depart.
    svg +=
      `<line class="repere" x1="0" y1="${marge.haut}" x2="0" y2="${hauteur - marge.bas}" ` +
      `stroke="${axe}" stroke-width="1" opacity="0" />`;

    // Les courbes : 2 px, jointures arrondies.
    series.forEach(function (serie) {
      const points = serie.valeurs.map((valeur, index) => `${x(index)},${y(valeur)}`).join(" ");
      svg +=
        `<polyline points="${points}" fill="none" stroke="${serie.couleur}" ` +
        `stroke-width="2" stroke-linejoin="round" stroke-linecap="round" ` +
        `opacity="${serie.contexte ? 0.85 : 1}" />`;
    });

    // Etiquettes directes en bout de courbe : une pastille de la couleur de la
    // serie, puis le texte en encre neutre. On decale verticalement le minimum
    // necessaire pour que deux etiquettes ne se superposent pas.
    const positions = series
      .map(function (serie, index) {
        const derniere = serie.valeurs[serie.valeurs.length - 1];
        return { index: index, serie: serie, valeur: derniere, y: y(derniere) };
      })
      .sort((a, b) => a.y - b.y);

    // L'etiquette tient sur une seule ligne (nom puis valeur) : deux lignes
    // demanderaient deux fois plus de place et les etiquettes finiraient par
    // se chevaucher des que les courbes se rapprochent.
    const hauteurEtiquette = 20;
    positions.forEach(function (element, rang) {
      if (rang > 0 && element.y - positions[rang - 1].y < hauteurEtiquette) {
        element.y = positions[rang - 1].y + hauteurEtiquette;
      }
    });

    const xFin = x(etiquettes.length - 1);
    positions.forEach(function (element) {
      const derniere = element.serie.valeurs[element.serie.valeurs.length - 1];
      svg +=
        // Point de fin, avec son anneau de 2 px de la couleur du fond.
        `<circle cx="${xFin}" cy="${y(derniere)}" r="4.5" fill="${element.serie.couleur}" ` +
        `stroke="${fond}" stroke-width="2" />` +
        // Pastille de couleur a cote du texte : l'identite vient de la marque,
        // jamais de la couleur du texte lui-meme.
        `<circle cx="${xFin + 14}" cy="${element.y}" r="4" fill="${element.serie.couleur}" />` +
        `<text x="${xFin + 24}" y="${element.y + 4}" font-size="12" fill="${encreSecondaire}">` +
        `${echapper(element.serie.nom)}` +
        `<tspan fill="${encreDiscrete}" class="chiffres"> ${format(derniere)}</tspan></text>`;
    });

    // Bandes invisibles : elles servent de grandes cibles pour le survol.
    const pas = (largeur - marge.gauche - marge.droite) / Math.max(1, etiquettes.length - 1);
    etiquettes.forEach(function (nomDuMois, index) {
      svg +=
        `<rect class="bande" data-index="${index}" x="${x(index) - pas / 2}" y="${marge.haut}" ` +
        `width="${pas}" height="${hauteur - marge.haut - marge.bas}" fill="transparent" />`;
    });

    hote.innerHTML =
      `<svg viewBox="0 0 ${largeur} ${hauteur}" role="img" aria-label="${echapper(
        options.description || ""
      )}">${svg}</svg>`;

    // Survol : repere vertical + infobulle listant toutes les series du mois.
    const repere = hote.querySelector(".repere");
    hote.querySelectorAll(".bande").forEach(function (bande) {
      const index = Number(bande.dataset.index);
      bande.addEventListener("mousemove", function (evenement) {
        repere.setAttribute("x1", x(index));
        repere.setAttribute("x2", x(index));
        repere.setAttribute("opacity", "1");
        const lignes = series
          .map(
            (serie) =>
              `<span class="puce" style="background:${serie.couleur}"></span>` +
              `${echapper(serie.nom)} <b>${format(serie.valeurs[index])}</b>`
          )
          .join("<br>");
        montrerInfobulle(`<strong>${echapper(etiquettes[index])}</strong><br>${lignes}`, evenement);
      });
      bande.addEventListener("mouseleave", function () {
        repere.setAttribute("opacity", "0");
        cacherInfobulle();
      });
    });
  }

  /* ----------------------------------------------------------------
   * Barres horizontales : comparer des categories entre elles.
   * `series` contient une ou deux series (par exemple moi / le groupe).
   * ---------------------------------------------------------------- */

  function barres(hote, options) {
    const categories = options.categories;
    const series = options.series;
    const format = options.format || String;
    const largeur = 760;
    const margeGauche = 168;
    const margeDroite = 108;
    const hauteurBarre = series.length > 1 ? 12 : 18; // <= 24 px, jamais plus
    const ecart = 2; // l'espace de 2 px qui separe deux barres voisines
    const pas = series.length * (hauteurBarre + ecart) + 18;
    const hauteur = categories.length * pas + 16;

    const maximum = maximumPropre(
      Math.max.apply(
        null,
        series.reduce((liste, serie) => liste.concat(serie.valeurs), [1])
      )
    );
    const largeurUtile = largeur - margeGauche - margeDroite;
    const encreDiscrete = couleur("--encre-discrete");
    const encreSecondaire = couleur("--encre-secondaire");

    let svg = "";

    categories.forEach(function (categorie, ligne) {
      const hautDuGroupe = ligne * pas + 8;

      svg +=
        `<text x="${margeGauche - 12}" y="${
          hautDuGroupe + (series.length * (hauteurBarre + ecart)) / 2 + 4
        }" text-anchor="end" font-size="13" fill="${encreSecondaire}">` +
        `${echapper(categorie)}</text>`;

      series.forEach(function (serie, rang) {
        const valeur = serie.valeurs[ligne];
        const longueur = Math.max(1, (valeur / maximum) * largeurUtile);
        const y = hautDuGroupe + rang * (hauteurBarre + ecart);
        svg +=
          `<path class="barre" data-categorie="${echapper(categorie)}" ` +
          `data-serie="${echapper(serie.nom)}" data-valeur="${valeur}" ` +
          `d="${cheminBarre(margeGauche, y, longueur, hauteurBarre)}" fill="${serie.couleur}" />`;

        // La valeur est ecrite au bout de la barre, jamais dedans : elle ne
        // risque donc jamais d'etre coupee par une barre trop courte.
        if (series.length === 1 || rang === 0) {
          svg +=
            `<text x="${margeGauche + longueur + 10}" y="${y + hauteurBarre - 2}" ` +
            `font-size="12" fill="${encreDiscrete}" class="chiffres">${format(valeur)}</text>`;
        }
      });
    });

    hote.innerHTML =
      `<svg viewBox="0 0 ${largeur} ${hauteur}" role="img" aria-label="${echapper(
        options.description || ""
      )}">${svg}</svg>`;

    hote.querySelectorAll(".barre").forEach(function (barre) {
      barre.addEventListener("mousemove", function (evenement) {
        montrerInfobulle(
          `<strong>${echapper(barre.dataset.categorie)}</strong><br>` +
            `${echapper(barre.dataset.serie)} <b>${format(Number(barre.dataset.valeur))}</b>`,
          evenement
        );
      });
      barre.addEventListener("mouseleave", cacherInfobulle);
    });
  }

  /* Barre au bout arrondi (4 px) et au pied carre, comme une barre de progression. */
  function cheminBarre(x, y, longueur, hauteur) {
    const rayon = Math.min(4, longueur);
    return (
      `M ${x} ${y} H ${x + longueur - rayon} A ${rayon} ${rayon} 0 0 1 ${x + longueur} ${y + rayon}` +
      ` V ${y + hauteur - rayon} A ${rayon} ${rayon} 0 0 1 ${x + longueur - rayon} ${y + hauteur}` +
      ` H ${x} Z`
    );
  }

  /* ----------------------------------------------------------------
   * Courbe miniature affichee dans une tuile de chiffre cle.
   * ---------------------------------------------------------------- */

  function miniature(hote, valeurs, couleurAccent) {
    const largeur = 120;
    const hauteur = 32;
    const minimum = Math.min.apply(null, valeurs);
    const maximum = Math.max.apply(null, valeurs);
    const etendue = maximum - minimum || 1;
    const x = (index) => (index * largeur) / (valeurs.length - 1);
    const y = (valeur) => hauteur - 4 - ((valeur - minimum) / etendue) * (hauteur - 8);

    const points = valeurs.map((valeur, index) => `${x(index)},${y(valeur)}`).join(" ");
    hote.innerHTML =
      `<svg viewBox="0 0 ${largeur} ${hauteur}" aria-hidden="true">` +
      `<polyline points="${points}" fill="none" stroke="${couleur("--encre-discrete")}" ` +
      `stroke-width="2" stroke-linejoin="round" stroke-linecap="round" opacity="0.5" />` +
      `<circle cx="${x(valeurs.length - 1)}" cy="${y(valeurs[valeurs.length - 1])}" r="3.5" ` +
      `fill="${couleurAccent}" stroke="${couleur("--surface-graphique")}" stroke-width="2" />` +
      `</svg>`;
  }

  return { courbes: courbes, barres: barres, miniature: miniature, couleur: couleur };
})();
