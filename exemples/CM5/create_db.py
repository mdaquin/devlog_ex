#!/usr/bin/env python3
"""Crée une base SQLite à partir de schema.sql et donnees.sql, puis affiche un rapport."""

import sqlite3
import sys
from pathlib import Path

BASE    = Path("budget.db")
SCHEMA  = Path("schema_sqlite.sql")
DONNEES = Path("donnees.sql")


def lire(chemin: Path) -> str:
    if not chemin.exists():
        sys.exit(f"Fichier introuvable : {chemin}")
    return chemin.read_text(encoding="utf-8")


def executer(connexion, texte, nom_fichier):
    instruction = ""
    for ligne in texte.splitlines():
        instruction += ligne + "\n"
        if sqlite3.complete_statement(instruction):
            try:
                connexion.execute(instruction)
            except sqlite3.Error as erreur:
                extrait = " ".join(instruction.split())[:90]
                sys.exit(f"Erreur dans {nom_fichier} : {erreur}\n  sur : {extrait}…")
            instruction = ""

def creer_base(chemin: Path) -> sqlite3.Connection:
    if chemin.exists():
        chemin.unlink()                      # on repart toujours d'une base vierge
    connexion = sqlite3.connect(chemin)
    connexion.execute("PRAGMA foreign_keys = ON")
    for fichier in (SCHEMA, DONNEES):
        try:
            executer(connexion, lire(fichier), fichier)
        except sqlite3.Error as erreur:
            connexion.close()
            chemin.unlink(missing_ok=True)   # pas de base à moitié construite
            sys.exit(f"Erreur dans {fichier} : {erreur}")
    connexion.commit()
    return connexion


def rapport(connexion: sqlite3.Connection) -> None:
    tables = [ligne[0] for ligne in connexion.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name")]

    print(f"\nBase créée : {BASE}\n")
    print(f"  {'table':<12} {'lignes':>7}")
    print(f"  {'-' * 12} {'-' * 7}")
    for table in tables:
        n = connexion.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"  {table:<12} {n:>7}")

    print("\n  Quelques vérifications")
    verifs = {
        "comptes détenus par plusieurs personnes":
            "SELECT count(*) FROM (SELECT iban FROM detient "
            "GROUP BY iban HAVING count(*) > 1)",
        "partages accordés":
            "SELECT count(*) FROM partage",
        "opérations sans catégorie":
            "SELECT count(*) FROM operation WHERE id_categorie IS NULL",
    }
    for libelle, requete in verifs.items():
        print(f"    {libelle:<42} {connexion.execute(requete).fetchone()[0]}")

    debut, fin = connexion.execute(
        "SELECT min(date_operation), max(date_operation) FROM operation").fetchone()
    total = connexion.execute(
        "SELECT sum(montant) FROM operation WHERE montant < 0").fetchone()[0]
    print(f"    {'période couverte':<42} {debut} → {fin}")
    print(f"    {'total des dépenses':<42} {total:.2f} €")

    violations = connexion.execute("PRAGMA foreign_key_check").fetchall()
    print(f"\n  Intégrité référentielle : "
          f"{'aucune violation' if not violations else f'{len(violations)} VIOLATIONS'}")


if __name__ == "__main__":
    connexion = creer_base(BASE)
    rapport(connexion)
    connexion.close()