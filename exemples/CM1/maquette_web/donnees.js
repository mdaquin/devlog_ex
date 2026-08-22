/* Donnees factices de la maquette.
 *
 * Rien n'est reel et il n'y a aucun serveur : les chiffres sont produits par
 * un generateur pseudo-aleatoire a graine fixe, donc identiques a chaque
 * rechargement de la page. Dans la vraie application, ce module serait
 * remplace par des appels a une API.
 */
const Donnees = (function () {
  "use strict";

  const MOIS = [
    "juin 25", "juil. 25", "aout 25", "sept. 25", "oct. 25", "nov. 25",
    "dec. 25", "janv. 26", "fevr. 26", "mars 26", "avril 26", "mai 26",
  ];

  const CATEGORIES = ["Logement", "Courses", "Transport", "Loisirs", "Abonnements", "Sante"];

  // Poids moyen de chaque categorie dans les depenses d'un mois.
  const POIDS = [0.42, 0.22, 0.12, 0.13, 0.05, 0.06];

  const PROFILS = [
    { id: "lea", nom: "Lea Martin", initiales: "LM", graine: 11, revenus: 2450, depenses: 1880, objectif: 2000 },
    { id: "karim", nom: "Karim Benali", initiales: "KB", graine: 29, revenus: 2680, depenses: 2210, objectif: 2200 },
    { id: "chloe", nom: "Chloe Dupont", initiales: "CD", graine: 47, revenus: 2180, depenses: 1640, objectif: 1700 },
  ];

  /* Generateur pseudo-aleatoire deterministe (algorithme "mulberry32"). */
  function generateur(graine) {
    let etat = graine >>> 0;
    return function () {
      etat = (etat + 0x6d2b79f5) | 0;
      let valeur = Math.imul(etat ^ (etat >>> 15), 1 | etat);
      valeur = (valeur + Math.imul(valeur ^ (valeur >>> 7), 61 | valeur)) ^ valeur;
      return ((valeur ^ (valeur >>> 14)) >>> 0) / 4294967296;
    };
  }

  function arrondir(valeur) {
    return Math.round(valeur * 100) / 100;
  }

  /* Construit les 12 mois d'un profil. */
  function serieMensuelle(profil) {
    const tirage = generateur(profil.graine);
    const revenus = [];
    const depenses = [];

    MOIS.forEach(function (_, index) {
      // Legere tendance a la hausse des revenus + une prime en mars.
      const prime = index === 9 ? 850 : 0;
      revenus.push(arrondir(profil.revenus * (1 + index * 0.004) + prime));

      // Les depenses montent en decembre (fetes) et en aout (vacances).
      const saison = index === 6 ? 1.28 : index === 2 ? 1.18 : 1;
      depenses.push(arrondir(profil.depenses * saison * (0.9 + tirage() * 0.2)));
    });

    return { revenus: revenus, depenses: depenses };
  }

  /* Repartition par categorie du dernier mois. */
  function repartition(profil, depensesDuMois) {
    const tirage = generateur(profil.graine + 100);
    return CATEGORIES.map(function (categorie, index) {
      return {
        nom: categorie,
        montant: arrondir(depensesDuMois * POIDS[index] * (0.85 + tirage() * 0.3)),
      };
    }).sort((a, b) => b.montant - a.montant);
  }

  /* Liste des releves importes, du plus recent au plus ancien. */
  function releves(profil, serie) {
    const derniers = 6;
    const liste = [];
    for (let index = MOIS.length - 1; index >= MOIS.length - derniers; index--) {
      const tirage = generateur(profil.graine + index);
      liste.push({
        fichier: `releve_${MOIS[index].replace(/[ .]+/g, "_")}.xlsx`,
        periode: MOIS[index],
        operations: 30 + Math.floor(tirage() * 15),
        revenus: serie.revenus[index],
        depenses: serie.depenses[index],
        statut: "importe",
      });
    }
    return liste;
  }

  /* Assemble tout ce dont la page a besoin pour un utilisateur. */
  function pourUtilisateur(identifiant) {
    const profil = PROFILS.find((candidat) => candidat.id === identifiant) || PROFILS[0];
    const serie = serieMensuelle(profil);
    const dernier = MOIS.length - 1;
    const depensesDuMois = serie.depenses[dernier];

    const amis = PROFILS.filter((candidat) => candidat.id !== profil.id).map(function (autre) {
      const serieAmi = serieMensuelle(autre);
      return {
        id: autre.id,
        nom: autre.nom,
        initiales: autre.initiales,
        objectif: autre.objectif,
        depenses: serieAmi.depenses,
        depensesDuMois: serieAmi.depenses[dernier],
        repartition: repartition(autre, serieAmi.depenses[dernier]),
      };
    });

    // Moyenne du groupe : l'utilisateur et ses amis, mois par mois.
    const moyenneGroupe = MOIS.map(function (_, index) {
      const total = amis.reduce((somme, ami) => somme + ami.depenses[index], serie.depenses[index]);
      return arrondir(total / (amis.length + 1));
    });

    const maRepartition = repartition(profil, depensesDuMois);
    const categories = maRepartition.map(function (element) {
      const totalAmis = amis.reduce(function (somme, ami) {
        const correspondance = ami.repartition.find((autre) => autre.nom === element.nom);
        return somme + (correspondance ? correspondance.montant : 0);
      }, 0);
      return {
        nom: element.nom,
        montant: element.montant,
        montantGroupe: arrondir(totalAmis / amis.length),
      };
    });

    return {
      profil: profil,
      mois: MOIS,
      revenus: serie.revenus,
      depenses: serie.depenses,
      soldeDuMois: arrondir(serie.revenus[dernier] - depensesDuMois),
      soldePrecedent: arrondir(serie.revenus[dernier - 1] - serie.depenses[dernier - 1]),
      epargneCumulee: arrondir(
        serie.revenus.reduce((somme, valeur, index) => somme + valeur - serie.depenses[index], 0)
      ),
      categories: categories,
      releves: releves(profil, serie),
      amis: amis,
      moyenneGroupe: moyenneGroupe,
    };
  }

  return { mois: MOIS, profils: PROFILS, pourUtilisateur: pourUtilisateur };
})();
