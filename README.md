# devlog_ex — exemples et TD de génie logiciel

Dépôt pédagogique d'un cours de Python et de génie logiciel. Ce n'est pas une
application unique : `exemples/` contient les démonstrations de cours et
`projet/` les travaux dirigés avec leurs retours.

## Contenu

| Dossier | Rôle |
| --- | --- |
| `exemples/CM1/simple_programme/` | Analyse d'un relevé bancaire Excel avec Tkinter (programme en un fichier) |
| `exemples/CM1/avec_base_de_données/` | Même application, en couches avec SQLite, import Excel et tests `unittest` |
| `exemples/CM1/maquette_web/` | Maquette statique HTML/CSS/JS d'une plateforme multi-utilisateurs |
| `exemples/CM2/` | Exemples Python de cours (bases, dictionnaires, fonctions) en versions avant/après |
| `exemples/CM3/` | Tests unitaires autour d'un calcul de budget |
| `exemples/CM5/` | Schémas SQL (SQLite et MySQL) et scripts de création/interrogation |
| `exemples/CM6/` | Générateur de relevés bancaires français synthétiques au format Excel |
| `projet/TD1/` | Fonctions de domaine OpenStudy (squelette à compléter) |
| `projet/TD2/` | Traitement de réponses de questionnaires (squelette à compléter) |
| `projet/TD3/` | Retours sur les tests |
| `projet/TD4/` | User stories, ADR et diagrammes C4 du projet OpenStudy |
| `projet/TD5/` | Retours sur le diagramme entité-association et le SQL |

## Prérequis

- Python 3.10 ou plus récent.
- Une seule dépendance externe pour les exemples Excel : `openpyxl`.

```bash
pip install openpyxl
```

## Démarrage rapide

### Application de gestion des dépenses

```bash
cd exemples/CM1/avec_base_de_données
pip install -r requirements.txt
python main.py

# Tests (8 tests, tous verts)
python -m unittest discover -s tests -v
```

Version minimale, sans base de données :

```bash
cd exemples/CM1/simple_programme
pip install -r requirements.txt
python analyse_releve.py
```

La maquette web s'ouvre directement : double-cliquer sur
`exemples/CM1/maquette_web/index.html`.

### Tests de budget (CM3)

```bash
cd exemples/CM3
python -m unittest discover -v          # 1 échec attendu dans test_budget
python -m unittest Xtest_budget_v2 -v   # 4 tests, version corrigée
```

### SQL (CM5)

```bash
cd exemples/CM5
python create_db.py
python query_db.py
```

### Générateur de relevés bancaires (CM6)

```bash
cd exemples/CM6
python generateur_de_releves_factices.py client-123 2026-05-07 2026-11-06 1mo
```

Chaque période produit un fichier Excel. Le premier passage sur un identifiant
de compte crée un profil (titulaire, banque, IBAN/BIC, revenus, situation) dans
`releves/profils_comptes.json` ; les passages suivants le réutilisent.

Fréquences acceptées : `1w`, `2w`, `1mo`, `3mo`. Options utiles :
`--sortie DOSSIER` et `--profil etudiant|jeune_actif|famille|couple|retraite|celibataire`.

## À savoir

- Plusieurs fichiers sont volontairement incomplets ou cassés pour le cours :
  `projet/TD1/fct_domaine.py`, `projet/TD2/traite_reponses.py`,
  `exemples/CM2/exemple1.py` et `exemples/CM3/test_budget.py`. Ne pas les
  « corriger » en dehors d'un exercice demandé.
- Lancer les scripts depuis leur propre dossier : les chemins et les imports
  sont relatifs au dossier courant.
- Il n'y a pas de build, de lint ni de CI à la racine du dépôt.
- Les fichiers `retours.md` rappellent les règles du cours sur l'usage de l'IA :
  spécifier avant de générer, vérifier ce qui est produit et conserver les
  traces (outil, modèle, effort).
- `projet/TD4/td4_grille_correction_openstudy.md` est réservé à l'enseignant
  (« Ne pas distribuer »).

Les instructions destinées aux agents de développement sont dans
[`AGENTS.md`](AGENTS.md).
