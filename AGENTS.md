# AGENTS.md

French-language teaching repo for a Python/software-engineering course (`devlog_ex`), not a single application. `exemples/CM*/` are lecture demos; `projet/TD*/` are assignments plus teacher feedback. Prose, identifiers, data keys and commit messages are in French; keep them.

## Do not "fix" teaching artifacts

Several files are deliberately broken or incomplete:

- `projet/TD1/fct_domaine.py` and `projet/TD2/traite_reponses.py` — stubs (`pass`/comments) for students to implement.
- `exemples/CM2/` — every file is a bug-hunting exercise and fails on purpose: `exemple1.py` syntax error (missing closing paren); `2.1` `KeyError`; `2.2` fixes that but hits `IndexError`; `3.1` counts a refund as an expense (777.5 instead of 742.5); `3.2` removes from a list while iterating over it; `4.1` `StatisticsError` (mean of an empty month); `4.2` `TypeError` (`None` passed to `median`). The `.2` files are the next step of the lecture, not fixes; don't merge or rewrite them.
- `exemples/CM3/test_budget.py` — fails against `budget.py` on purpose; `budget_v2.py` is the corrected version.
- `exemples/CM8/app.py` — skeleton only: routes return sample data, `require_auth` accepts any `Bearer` token, and the `TODO`s are the exercise. **It currently fails to import**: a stray `khjfkhfkjd` line sits just after the module docstring (`NameError`). CM8's README does not mention this, so confirm with the user before deleting it.
- `exemples/CM6/session-ses_e4b7.md` and `exemples/CM8/conv_ia/` — saved AI session transcripts, kept as the course-required traces. Don't edit or regenerate them.

Only change these when the task explicitly asks, and expect/report intentional failures when running tests.

## Layout / entrypoints

- `exemples/CM1/simple_programme/` — single-file expense analyzer (`analyse_releve.py`, Tkinter).
- `exemples/CM1/avec_base_de_données/` — layered SQLite version: `main.py`, package `depenses/`, tests in `tests/`.
- `exemples/CM1/maquette_web/` — static HTML/CSS/JS mockup; open `index.html` directly, no server or build.
- `exemples/CM3/` — budget tests. `exemples/CM5/` — SQLite/MySQL schemas and create/query scripts. `exemples/CM6/` — `generateur_de_releves_factices.py`, a fake French bank-statement generator (Excel output); sample output and the saved account profiles are committed in `releves/`.
- `exemples/CM8/` — expenses API + React prototype. `openapi.yaml` (OpenAPI 3.1) is the spec; `app.py` is the Flask skeleton served under `/v1`; `prototype-react/` is the Vite/React app; `maquette_*.{jpg,png}` are the design targets. CM8's `README.md` is detailed.
- `animation_commits.py` (root) — standalone pygame animation of the git history; not part of the course applications.
- `projet/TD4/` — OpenStudy user stories, ADRs and C4 diagrams; `td4_grille_correction_openstudy.md` is teacher-only ("Ne pas distribuer"). TD3/TD5 contain only `retours.md`.

## Commands (verified)

- No root build/lint/typecheck/CI config. Don't invent one. The root `package-lock.json` is an empty stub: there is no root Node project, only `exemples/CM8/prototype-react/`.
- CM1 DB app, 8 tests all passing:
  `cd exemples/CM1/avec_base_de_données && python -m unittest discover -s tests -v`
  Single test: `python -m unittest discover -s tests -k ajout -v`
  Run app: `python main.py` (creates gitignored `depenses.sqlite3`; only dependency `openpyxl`).
- CM1 simple app also needs `openpyxl`; run `python analyse_releve.py`.
- CM3: `cd exemples/CM3 && python -m unittest discover -v` → 1 expected failure in `test_budget`.
  Corrected suite: `python -m unittest Xtest_budget_v2 -v` → 4 pass (`Xtest_` prefix is not matched by default discovery).
- CM5: run from `exemples/CM5` (paths are cwd-relative): `python create_db.py`, then `python query_db.py`. Uses stdlib `sqlite3`.
- CM6: `cd exemples/CM6 && python generateur_de_releves_factices.py client-123 2026-05-07 2026-11-06 1mo` regenerates the committed `releves/` files exactly (needs `openpyxl`). Frequencies: `1w`, `2w`, `1mo`, `3mo`. Options: `--sortie DOSSIER` (default `releves`, cwd-relative), `--profil etudiant|jeune_actif|famille|couple|retraite|celibataire` (only used when the account's profile is first created).
- CM8 React prototype (Node `^20.19.0 || >=22.12.0`): `cd exemples/CM8/prototype-react && npm install && npm run dev` → <http://localhost:5173>. Mock data is the default; `cp .env.example .env.local` (sets `VITE_API_MODE=reel`) to call the deployed API via the Vite proxy. `npm run build` then `npm run preview` for the production build. No tests or linter in this package.
- CM8 Flask skeleton: there is **no `requirements.txt`** despite the docstring; install Flask yourself. Intended command: `flask --app app run --debug` (serves `/v1`), but see the import bug above.
- `animation_commits.py`: `python animation_commits.py [repo] --limite N`. For headless use, `--capture out.png --at SECONDES` writes an image instead of opening a window (needs `pygame`).
- TD2: `python traite_reponses.py <reponses.csv|xlsx> <questions.json>`; the body is not implemented.

## Gotchas

- Run scripts from their own directory: modules import siblings directly (`from budget import ...`) and use cwd-relative paths.
- French keys/identifiers are load-bearing (e.g. JSON `pondération`, `réponses_possibles`, `libellé`); don't transliterate.
- `exemples/CM1/avec_base_de_données/.gitignore` ignores `depenses.sqlite3`; don't commit it. In contrast, `exemples/CM5/budget.db` is committed — CM5 overwrites it, but output is deterministic so it stays unchanged in git.
- `openpyxl` is installed in the system Python and all three virtual environments. Local `.venv` dirs are Python 3.10 (CM1 apps) or 3.12 (root); gitignored.
- CM6 statements don't use the CM1 import format (CM6: 12-line header block, columns `Date, Date de valeur, Libellé, Catégorie, Débit, Crédit, Solde`; CM1 expects `Date, Libelle, Categorie, Montant` from row 1). Both CM1 apps reject CM6 files with "Aucune operation trouvee".
- CM6 balances only chain within a single run: each run starts again from the profile's `solde_initial`.
- CM8 local Flask serves `/v1`, while the React proxy defaults to `https://mathieu.com` + `/ecureuil/api/1.0`. To point the prototype at the local skeleton, override `VITE_API_PROXY_PREFIX` (and `VITE_API_PROXY_TARGET`).
- `projet/TD*/retours.md` state the course rules: specify before generating, verify AI output, and keep AI traces (tool, model, effort). Follow them if asked to produce student work.
