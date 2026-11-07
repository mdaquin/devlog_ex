# AGENTS.md

French-language teaching repo for a Python/software-engineering course (`devlog_ex`), not a single application. `exemples/CM*/` are lecture demos; `projet/TD*/` are assignments plus teacher feedback. Prose, identifiers, data keys and commit messages are in French; keep them.

## Do not "fix" teaching artifacts

Several files are deliberately broken or incomplete:

- `projet/TD1/fct_domaine.py` and `projet/TD2/traite_reponses.py` — stubs (`pass`/empty body) for students to implement.
- `exemples/CM2/exemple1.py` — syntax error (missing closing paren), used in class.
- `exemples/CM3/test_budget.py` — fails against `budget.py` on purpose; `budget_v2.py` is the corrected version.
- Numbered examples (`exemple2.1.py` vs `exemple2.2.py`, etc.) are before/after lecture snapshots; don't merge or rewrite them.

Only change these when the task explicitly asks, and expect/report intentional failures when running tests.

## Layout / entrypoints

- `exemples/CM1/simple_programme/` — single-file expense analyzer (`analyse_releve.py`, Tkinter).
- `exemples/CM1/avec_base_de_données/` — layered SQLite version: `main.py`, package `depenses/`, tests in `tests/`.
- `exemples/CM1/maquette_web/` — static HTML/CSS/JS mockup; open `index.html` directly, no server or build.
- `exemples/CM3/` — budget tests. `exemples/CM5/` — SQLite/MySQL schemas and create/query scripts. `exemples/CM6/` — empty, untracked placeholder.
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
- TD2: `python traite_reponses.py <reponses.csv|xlsx> <questions.json>`; the body is not implemented.

## Gotchas

- Run scripts from their own directory: modules import siblings directly (`from budget import ...`) and use cwd-relative paths.
- French keys/identifiers are load-bearing (e.g. JSON `pondération`, `réponses_possibles`, `libellé`); don't transliterate.
- Root `.gitignore` only covers `/.venv` and `/.DS_Store`; some `.venv`, `__pycache__/*.pyc` and `.DS_Store` files are already tracked. Don't mass-delete tracked files.
- `exemples/CM1/avec_base_de_données/.venv` is Python 3.10; root `.venv` and system Python are 3.12.
- `projet/TD*/retours.md` state the course rules: specify before generating, verify AI output, and keep AI traces (tool, model, effort). Follow them if asked to produce student work.
