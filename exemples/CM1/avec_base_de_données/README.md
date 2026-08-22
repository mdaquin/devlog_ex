# Gestion des dépenses — version avec base de données

Deuxième étape de l'exemple : le programme ne se contente plus d'analyser un
fichier, il **conserve** les relevés importés dans une base SQLite et permet de
les comparer d'un mois sur l'autre.

Fonctionnalités :

- importer un nouveau relevé Excel (avec refus des doublons) ;
- consulter la liste des relevés déjà importés, et en supprimer ;
- voir les statistiques d'un relevé (revenus, dépenses, solde, 3 plus grosses
  dépenses) ;
- comparer les **3 derniers relevés**, avec un tableau par mois de chaque
  relevé : totaux par catégorie, puis ligne de total.

## Lancement

- **macOS** : double-cliquer sur `depenses.command`
- **Windows** : double-cliquer sur `depenses.bat`
- **en ligne de commande** :

  ```bash
  python -m venv .venv
  source .venv/bin/activate     # Windows : .venv\Scripts\activate
  pip install -r requirements.txt
  python main.py
  ```

La base `depenses.sqlite3` est créée toute seule au premier lancement, à côté
du programme. La supprimer remet l'application à zéro.

Pour disposer de relevés à importer :

```bash
python generer_exemples.py        # écrit 4 fichiers dans donnees_exemple/
```

Les fichiers sont déjà générés dans `donnees_exemple/` (février à mai 2026) :
importer les quatre permet de voir le troisième onglet se remplir et le plus
ancien sortir de la comparaison.

## Organisation du code

C'est le principal intérêt pédagogique par rapport à `simple_programme` : le
script unique devient un ensemble de modules **en couches**, chacun ne
connaissant que la couche du dessous.

```
main.py                  point d'entrée : ouvre la base, lance la fenêtre
depenses/
├── modeles.py           les données : Operation, Releve, StatistiquesMois
├── base.py              SQLite : le schéma et tout le SQL de l'application
├── importation.py       lecture des fichiers Excel + empreinte anti-doublon
├── statistiques.py      assemblage des chiffres à afficher
└── interface.py         la fenêtre Tkinter/ttk (aucun calcul, aucun SQL)
tests/test_depenses.py   tests de la base et des statistiques (unittest)
```

Cette séparation n'est pas décorative : elle est ce qui rend les tests
possibles. `tests/test_depenses.py` vérifie toute la logique **sans ouvrir de
fenêtre**, sur une base `:memory:` recréée pour chaque test :

```bash
python -m unittest discover -s tests -v      # 8 tests
```

## Points à discuter en cours

| Sujet | Où le voir |
| --- | --- |
| Schéma relationnel, clé étrangère, `ON DELETE CASCADE` | `base.py`, constante `SCHEMA` |
| Transaction (`with self.connexion`) : tout ou rien à l'import | `base.py`, `ajouter_releve` |
| Contrainte `UNIQUE` + empreinte SHA-256 pour refuser un doublon | `base.py` et `importation.py` |
| Agrégation côté base (`SUM`, `GROUP BY`, `strftime`) plutôt qu'en Python | `base.py`, `totaux_par_categorie` |
| Requête paramétrée (`?`) et non concaténation de chaînes | partout dans `base.py` |
| Erreurs métier remontées par des exceptions dédiées | `ReleveDejaImporte`, `FichierInvalide` |
| Interface qui ne fait qu'afficher | `interface.py` |

## Format attendu du fichier Excel

Identique à la version simple : une ligne d'en-tête, puis une ligne par
opération.

| Date | Libelle | Categorie | Montant |
| --- | --- | --- | --- |
| 02/05/2026 | Loyer appartement | Logement | -780.00 |
| 25/05/2026 | Salaire | Salaire | 2450.00 |

Les **dépenses sont négatives**, les **revenus positifs**. Un relevé peut
couvrir plusieurs mois : l'application produit alors un tableau par mois.
