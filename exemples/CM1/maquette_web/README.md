# Gestion des dépenses — maquette d'une plateforme web

Troisième étape de l'exemple, et la seule qui ne soit **qu'une maquette** :
aucun serveur, aucun compte, aucun fichier réellement lu. Les chiffres sont
factices et fabriqués dans le navigateur. L'objectif est de discuter de
l'interface d'une plateforme multi-utilisateurs *avant* de l'implémenter.

## Ouvrir la maquette

Double-cliquer sur `index.html` : la page s'ouvre dans le navigateur. Il n'y a
rien à installer, rien à compiler, aucune bibliothèque externe.

## Ce que la maquette montre

| Écran | Contenu |
| --- | --- |
| Tableau de bord | Solde du mois en chiffre vedette, trois tuiles de chiffres clés avec courbe miniature, l'évolution revenus / dépenses sur 6 ou 12 mois, la répartition par catégorie |
| Mes relevés | Zone de dépôt (glisser-déposer simulé), liste des relevés importés avec leur statut |
| Mes amis | Objectif du mois de chacun sous forme de jauge, dépenses mensuelles comparées, comparaison par catégorie avec la moyenne du groupe, invitation d'un ami |

Le sélecteur « Connecté comme » en haut à droite change d'utilisateur : c'est ce
qui simule le côté multi-utilisateurs (chaque profil a ses propres données et
ses propres amis).

## Organisation des fichiers

```
index.html        la structure de la page (aucun style, aucun script en ligne)
style.css         toutes les couleurs, déclarées une seule fois en variables CSS
donnees.js        le jeu de données factice (remplacé par une API, plus tard)
graphiques.js     une mini-bibliothèque de graphiques en SVG, écrite à la main
app.js            la navigation, le rendu des vues et les interactions
```

Le découpage reprend l'idée des versions Python : les données, le dessin et
l'orchestration sont séparés. `graphiques.js` ne sait rien des dépenses, il ne
connaît que des séries de nombres.

## Choix de visualisation à commenter en cours

Ces décisions sont volontaires, et chacune peut se discuter :

- **Une seule barre de filtres**, au-dessus de tous les graphiques qu'elle
  concerne, plutôt qu'un filtre par carte.
- **Un seul chiffre vedette par écran.** Le reste est en tuiles ; on ne fait
  pas un graphique là où un nombre suffit.
- **Comparer des catégories entre elles → une seule couleur.** Colorer chaque
  barre différemment n'ajouterait aucune information que la longueur ne donne
  déjà.
- **Une couleur par personne, toujours la même** d'un graphique à l'autre. La
  moyenne du groupe est en gris : c'est un repère, pas une personne.
- **La couleur n'est jamais le seul indice** : légende dès qu'il y a deux
  séries, étiquettes directes en bout de courbe, et un bouton « Voir le
  tableau » qui donne les mêmes chiffres sans aucune couleur.
- **Les valeurs ne sont pas écrites sur chaque point** — seulement au bout des
  courbes et au bout des barres ; le survol et le tableau donnent le reste.
- **Les couleurs des séries ont été vérifiées** pour rester distinguables en
  cas de daltonisme, en mode clair comme en mode sombre.
- **Les états (vert / orange / rouge) sont toujours accompagnés d'un texte**
  (« Dans l'objectif », « Objectif dépassé »).
- Mode clair et mode sombre : la page suit le réglage du système, et le bouton
  en haut à droite permet de forcer l'un ou l'autre.

## Questions ouvertes, à trancher avant d'implémenter

- Comment on s'authentifie, et qu'est-ce qu'un « ami » (invitation acceptée des
  deux côtés ?).
- Ce qu'un ami voit exactement. La maquette annonce « vos totaux et vos
  catégories, jamais le détail de vos opérations » : c'est un choix de
  conception, pas une contrainte technique.
- Où sont stockés les relevés, combien de temps, et ce qui se passe si un
  utilisateur supprime son compte.
- Ce qui est calculé côté serveur et ce qui est calculé côté navigateur.
