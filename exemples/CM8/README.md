# CM8 — API de gestion de dépenses et prototype React

Ce dossier rassemble les supports du CM8 autour de l'application de gestion de
dépenses déjà utilisée dans les exemples précédents :

| Fichier | Rôle |
| --- | --- |
| `openapi.yaml` | Spécification OpenAPI 3.1 de l'API (comptes, extraits, transactions, catégories, accès). |
| `app.py` | Squelette Flask de l'API : les routes existent, les fonctions sont des placeholders. |
| `maquette_dessin.jpg` | Première maquette de l'écran « Mes relevés bancaires », dessinée à la main. |
| `maquette_figma.png` | Maquette Figma du même écran, qui sert de cible visuelle. |
| `prototype-react/` | Prototype React semi-fonctionnel de cet écran. |

## Lancer le prototype React

Prérequis : Node.js et npm, avec une version de Node qui satisfait
`^20.19.0 || >=22.12.0` (exigence de Vite 7). Le prototype a été vérifié avec
Node 26.

### Mode factice (par défaut, sans serveur)

```bash
cd exemples/CM8/prototype-react
npm install
npm run dev
```

Vite affiche l'adresse à ouvrir, en général <http://localhost:5173>. Le
prototype fonctionne sans serveur Python : les données sont simulées dans le
navigateur.

### Mode API réelle

L'API est exposée à l'adresse <https://mathieu.com/ecureuil/api/1.0/>. Pour que
le prototype l'utilise :

```bash
cd exemples/CM8/prototype-react
npm install
cp .env.example .env.local
# vérifier que .env.local contient VITE_API_MODE=reel
npm run dev
```

L'écran de connexion s'affiche. Utilisez un compte créé via `POST /users` sur
l'API (le prototype ne crée pas de compte). Les appels partent vers
`/api/...` et sont relayés par le proxy Vite vers
`https://mathieu.com/ecureuil/api/1.0/...` : il n'y a donc pas de CORS à
configurer sur le serveur pour le développement local.

Si l'API se trouve ailleurs, modifiez `.env.local` :

```dotenv
VITE_API_MODE=reel
VITE_API_PROXY_TARGET=https://mon-serveur.example
VITE_API_PROXY_PREFIX=/ecureuil/api/1.0
```

Pour appeler l'API sans proxy (par exemple si elle autorise déjà l'origine du
prototype), donnez directement son URL :

```dotenv
VITE_API_MODE=reel
VITE_API_BASE_URL=https://mathieu.com/ecureuil/api/1.0
```

### Vérifier la version de production

```bash
npm run build
npm run preview
```

`npm run preview` sert le contenu de `dist/` sur <http://localhost:4173> et
reprend le proxy du serveur de développement.

Pour un déploiement statique, le proxy Vite n'existe plus. Deux options :

- construire avec une URL absolue :
  `VITE_API_BASE_URL=https://mathieu.com/ecureuil/api/1.0 npm run build`,
  en autorisant l'origine du site dans la configuration CORS de l'API ;
- servir le prototype et l'API derrière le même domaine (reverse proxy), et
  garder `VITE_API_BASE_URL=/api` avec une règle qui réécrit `/api` vers
  `/ecureuil/api/1.0`.

## Ce que fait le prototype

L'écran reprend la maquette Figma : en-tête avec le profil et « mes comptes »,
titre « Mes relevés bancaires », relevés regroupés par année, tableau des mois
avec revenus, dépenses et accès partagé, puis bouton « Ajouter un relevé ».

Les interactions sont réelles :

- **Connexion** (mode réel) : formulaire e-mail / mot de passe, jetons stockés
  dans `sessionStorage`, renouvellement automatique du jeton d'accès via
  `/auth/refresh`, retour à la connexion si la session expire.
- **Choix du compte** (mode réel) : si l'utilisateur a plusieurs comptes, un
  sélecteur apparaît au-dessus des relevés. Le rôle (`OWNER`, `WRITE`, `READ`)
  est affiché ; en lecture seule, l'import et la suppression sont masqués.
- **Accordéons par année** : une seule année ouverte à la fois, avec le nombre
  de relevés et le double sens de tri (du plus ancien au plus récent ou
  l'inverse).
- **Détail d'un relevé** : clic sur le nom du mois pour voir le fichier, la
  date d'import, le nombre de transactions, les totaux et les accès.
- **Suppression** : confirmation puis `DELETE` sur l'extrait. En mode factice,
  une notification propose **Annuler** ; en mode réel, l'API ne prévoit pas de
  restauration, donc l'action est définitive.
- **Ajout d'un relevé** : glisser-déposer ou sélection d'un fichier `.csv` /
  `.xlsx`, contrôle de l'extension et de la taille (10 Mo). En mode réel, le
  fichier est envoyé en `multipart/form-data` et l'API calcule la période et
  les totaux ; en mode factice, un relevé d'exemple est créé pour le mois
  choisi.
- **Navigation** : tiroir latéral, menu de profil et liens secondaires. Les
  écrans non implémentés affichent une notification explicite.
- **États de l'interface** : chargement initial avec squelettes, états vides,
  messages d'erreur, notifications, adaptation mobile (le tableau devient une
  liste de cartes).
- **Accessibilité** : boutons et liens natifs, `aria-expanded` sur les
  accordéons, libellés des actions, dialogues natifs `<dialog>` (Échap, focus,
  fond assombri), respect de `prefers-reduced-motion`.

## Ce qui est simulé (mode factice)

- Les données sont **en mémoire** : recharger la page remet le jeu de départ.
- Le fichier choisi n'est **pas lu**. Le prototype crée un relevé d'exemple
  pour le mois sélectionné, avec des montants pseudo-aléatoires déterministes.
- Il n'y a **ni authentification, ni appel réseau, ni base de données**.
- L'API Flask n'est pas démarrée par le prototype.

En mode réel, ces limites disparaissent : les données viennent de l'API et le
fichier est réellement importé. Le prototype reste cependant un prototype :
pas de gestion des comptes, des catégories ni des accès dans l'interface.

## Organisation

```text
prototype-react/
├── .env.example                  modèle de configuration de l'API
├── .gitignore
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js                proxy Vite vers l'API
└── src/
    ├── main.jsx                  point d'entrée React
    ├── config.js                 mode factice/réel, URL de l'API
    ├── App.jsx                   état de l'écran et orchestration
    ├── styles.css                styles, variables de couleur, responsive
    ├── donnees/
    │   └── relevesInitiaux.js    jeu de données factice
    ├── services/
    │   ├── api.js                façade commune factice/réel
    │   ├── apiFactice.js         « API » en mémoire, avec latence simulée
    │   ├── apiReelle.js          appels HTTP et adaptation des réponses
    │   └── clientApi.js          jetons, requêtes, refresh, erreurs
    ├── utilitaires/
    │   ├── formatage.js          mois français, montants en euros, dates
    │   ├── identite.js           nom affiché déduit de l'e-mail
    │   └── useDialogue.js        ouverture/fermeture des <dialog> natifs
    └── composants/
        ├── EcranConnexion.jsx    connexion à l'API réelle
        ├── Entete.jsx            en-tête, menu de profil, tiroir
        ├── PanneauAnnee.jsx      accordéon d'une année
        ├── TableReleves.jsx      tableau des relevés
        ├── BadgeAcces.jsx        pastille « Mary », « Hugo »…
        ├── Modale.jsx            enveloppe commune des dialogues
        ├── ModaleAjout.jsx       import d'un relevé
        ├── ModaleDetail.jsx      détail d'un relevé
        ├── ModaleSuppression.jsx confirmation de suppression
        ├── Notification.jsx      messages et action « Annuler »
        ├── Chargement.jsx        squelettes de chargement
        └── Icones.jsx            icônes SVG locales
```

## Brancher la vraie API

Le mode réel est déjà câblé. `src/services/api.js` choisit l'implémentation
selon `VITE_API_MODE`, et `src/services/apiReelle.js` traduit les réponses de
l'API vers la forme attendue par les composants.

| Fonction du prototype | Route de l'API |
| --- | --- |
| Connexion | `POST /auth/token` |
| Renouvellement de session | `POST /auth/refresh` |
| Lister les comptes | `GET /accounts` |
| Lister les relevés | `GET /accounts/{accountId}/statements?page=…&pageSize=200` |
| Totaux d'un relevé | `GET /accounts/{accountId}/summary?from=…&to=…` |
| Importer un fichier | `POST /accounts/{accountId}/statements` (`multipart/form-data`) |
| Supprimer un relevé | `DELETE /accounts/{accountId}/statements/{statementId}` |
| Accès partagé | `GET /accounts/{accountId}/access` (propriétaire uniquement) |

Points à connaître sur le branchement :

- **Pagination** : les extraits sont lus page par page (200 par page) jusqu'à
  épuisement de `totalItems`.
- **Totaux** : l'API ne renvoie pas les revenus/dépenses dans l'objet
  `Statement`. Le prototype appelle `/summary` sur la période
  `periodStart`–`periodEnd` de chaque extrait. Si cet appel échoue, les
  montants s'affichent « — » sans faire tomber tout l'écran.
- **Mois affiché** : déduit de `periodEnd` (ou `periodStart`, ou
  `importedAt`). Un extrait couvrant plusieurs mois apparaît donc sous son
  mois de fin.
- **Accès partagé** : l'API décrit un accès au niveau du **compte**, pas de
  l'extrait. La colonne affiche donc les mêmes personnes sur tous les relevés
  d'un compte. Un partage par relevé demanderait de faire évoluer la
  spécification.
- **Restauration** : il n'existe pas d'endpoint pour annuler une suppression.
  Le bouton « Annuler » n'est proposé qu'en mode factice.
- **CORS** : en développement, le proxy Vite évite le problème. En production,
  configurez CORS sur l'API ou servez les deux applications derrière le même
  domaine.
- **Sécurité** : les jetons sont conservés dans `sessionStorage` pour rester
  simple. Une vraie application préférera des cookies `HttpOnly`, `Secure` et
  `SameSite`, et ne stockera jamais le jeton d'accès dans du JavaScript
  accessible.
- **Préfixe** : si `https://mathieu.com/ecureuil/api/1.0/accounts` renvoie une
  page 404 ou une page WordPress, vérifiez `VITE_API_PROXY_PREFIX` (ou
  `VITE_API_BASE_URL`) et que l'API est bien déployée à cette adresse.

Le squelette `app.py` n'est pas utilisable tel quel : il répond avec des
données d'exemple et accepte n'importe quel jeton `Bearer`. Les `TODO` du
fichier indiquent le travail restant (validation, persistance, droits, import
réel des CSV/Excel, etc.).


## Notes de conception

- **Ordre des années** : comme la maquette, les années vont de la plus
  ancienne à la plus récente (2024, 2025, 2026), et l'année la plus récente est
  ouverte au chargement.
- **Une seule année ouverte** : le comportement de l'accordéon est volontaire ;
  il évite d'afficher plusieurs grands tableaux à la fois.
- **Le tri est commun à toutes les années** : le libellé du bouton décrit
  toujours l'ordre affiché. Le choix est conservé quand on change d'année.
- **Les montants sont manipulés sous forme de chaînes** (`"-42.50"`), comme dans
  l'API, pour éviter les erreurs d'arrondi. L'affichage ajoute le signe et le
  format français (`+ 3 545,00 €`, `− 1 022,00 €`).
- **Le tableau desktop reste la référence** ; sous 760 px, il devient une liste
  de cartes pour éviter un défilement horizontal.
- **Accès partagé par relevé** : la maquette montre des personnes différentes
  selon le mois, alors que l'API décrit un accès au niveau du **compte**. En
  mode factice, le prototype suit la maquette ; en mode réel, la colonne
  affiche les accès du compte, donc la même liste pour tous les relevés. Un
  partage par relevé demanderait de faire évoluer la spécification.
- **Le prototype ne cherche pas à masquer ses limites** : la mention en bas de
  page indique si les données sont simulées ou lues depuis l'API, et les
  notifications des écrans non implémentés le disent explicitement.
