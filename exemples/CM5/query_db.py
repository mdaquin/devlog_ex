#!/usr/bin/env python3
"""Récapitulatif des dépenses d'un compte, sur un relevé, par catégorie."""

import sqlite3
import sys
from pathlib import Path

BASE = Path("budget.db")

REQUETE = """
SELECT COALESCE(c.nom, '(non catégorisé)') AS categorie,
       SUM(-o.montant)                     AS total
  FROM operation o
  LEFT JOIN categorie c USING (id_categorie)
 WHERE o.iban = ?
   AND o.periode_debut = ?
   AND o.montant < 0
 GROUP BY categorie
 ORDER BY total DESC
"""


def recapitulatif(connexion, iban, periode_debut):
    """Renvoie [(catégorie, total), ...] pour ce compte et ce relevé."""
    return connexion.execute(REQUETE, (iban, periode_debut)).fetchall()


def afficher(lignes, iban, periode_debut):
    print(f"\nDépenses du compte {iban}")
    print(f"relevé commençant le {periode_debut}\n")
    if not lignes:
        print("  aucune dépense sur cette période.")
        return
    for categorie, total in lignes:
        print(f"  {categorie:<20} {total:>9.2f} €")
    print(f"  {'-' * 30}")
    print(f"  {'Total':<20} {sum(t for _, t in lignes):>9.2f} €")


if __name__ == "__main__":
    if not BASE.exists():
        sys.exit(f"Base introuvable : {BASE} (lancez d'abord creer_base.py)")
    connexion = sqlite3.connect(BASE)
    iban, debut = "FR7630001007941234567890185", "2026-01-01"
    afficher(recapitulatif(connexion, iban, debut), iban, debut)
    connexion.close()