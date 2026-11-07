# AGENTS.md

French-language teaching repo for a Python/software-engineering course (`devlog_ex`), not a single application. `exemples/CM*/` are lecture demos; `projet/TD*/` are assignments plus teacher feedback. Prose, identifiers, data keys and commit messages are in French; keep them.

## Do not "fix" teaching artifacts

Several files are deliberately broken or incomplete:

- `projet/TD1/fct_domaine.py` and `projet/TD2/traite_reponses.py` — stubs (`pass`/empty body) for students to implement.
- `exemples/CM2/` — every file is a bug-hunting exercise and fails on purpose: `exemple1.py` syntax error (missing closing paren); `2.1` `KeyError`; `2.2` fixes that but hits `IndexError`; `3.1` counts a refund as an expense (777.5 instead of 742.5); `3.2` removes from a list while iterating over it; `4.1` `StatisticsError` (mean of an empty month); `4.2` `TypeError` (`None` passed to `median`). The `.2` files are the next step of the lecture, not fixes; don't merge or rewrite them.
- `exemples/CM3/test_budget.py` — fails against `budget.py` on purpose; `budget_v2.py` is the corrected version.

Only change these when the task explicitly asks, and expect/report intentional failures when running tests.

## Layout / entrypoints

- `exemples/CM1/simple_programme/` — single-file expense analyzer (`analyse_releve.py`, Tkinter).
- `exemples/CM1/avec_base_de_données/` — layered SQLite version: `main.py`, package `depenses/`, tests in `tests/`.
- `exemples/CM1/maquette_web/` — static HTML/CSS/JS mockup; open `index.html` directly, no server or build.
- `exemples/CM3/` — budget tests. `exemples/CM5/` — SQLite/MySQL schemas and create/query scripts. `exemples/CM6/` — `generateur_de_releves_factices.py`, a fake French bank-statement generator (Excel output); sample output and the saved account profiles are committed in `releves/`.
- `projet/TD4/` — OpenStudy user stories, ADRs and C4 diagrams; `td4_grille_correction_openstudy.md` is teacher-only ("Ne pas distribuer").

## Commands (verified)

- No root build/lint/typecheck/CI config. Don't invent one.
- CM1 DB app, 8 tests all passing:
  `cd exemples/CM1/avec_base_de_données && python -m unittest discover -s tests -v`
  Run app: `python main.py` (creates `depenses.sqlite3`; only dependency `openpyxl`).
- CM1 simple app also needs `openpyxl`; run `python analyse_releve.py`.
- CM3: `cd exemples/CM3 && python -m unittest discover -v` → 1 expected failure in `test_budget`.
  Corrected suite: `python -m unittest Xtest_budget_v2 -v` → 4 pass (`Xtest_` prefix is not matched by default discovery).
- CM5: run from `exemples/CM5` (paths are cwd-relative): `python create_db.py`, then `python query_db.py`.
- CM5 overwrites the committed `budget.db`; output is deterministic, so the file stays unchanged in git.
- CM6: `cd exemples/CM6 && python generateur_de_releves_factices.py client-123 2026-05-07 2026-11-06 1mo` regenerates the committed `releves/` files exactly (needs `openpyxl`). Options: `--sortie DOSSIER` (default `releves`, cwd-relative), `--profil etudiant|jeune_actif|famille|couple|retraite|celibataire` (only used when the account's profile is first created).
- TD2: `python traite_reponses.py <reponses.csv|xlsx> <questions.json>`; the body is not implemented.

## Gotchas

- Run scripts from their own directory: modules import siblings directly (`from budget import ...`) and use cwd-relative paths.
- French keys/identifiers are load-bearing (e.g. JSON `pondération`, `réponses_possibles`, `libellé`); don't transliterate.
- Root `.gitignore` ignores `.venv/`, `.DS_Store`, `*.pyc` and `__pycache__/` recursively.
- `exemples/CM1/avec_base_de_données/.venv` and `exemples/CM1/simple_programme/.venv` are Python 3.10; root `.venv` and system Python are 3.12. All have `openpyxl` except system Python. Local virtual environments are ignored by git.
- CM6 statements don't use the CM1 import format (CM6: 12-line header block, columns `Date, Date de valeur, Libellé, Catégorie, Débit, Crédit, Solde`; CM1 expects `Date, Libelle, Categorie, Montant` from row 1). Both CM1 apps reject CM6 files with "Aucune operation trouvee".
- CM6 balances only chain within a single run: each run starts again from the profile's `solde_initial`.
- `projet/TD*/retours.md` state the course rules: specify before generating, verify AI output, and keep AI traces (tool, model, effort). Follow them if asked to produce student work.
