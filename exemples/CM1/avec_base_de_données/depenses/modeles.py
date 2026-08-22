"""Les objets manipules par l'application.

Ce module ne contient que des donnees : pas de base, pas d'interface.
C'est le vocabulaire commun aux autres modules.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List

NOMS_DES_MOIS = [
    "janvier", "fevrier", "mars", "avril", "mai", "juin",
    "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
]


def nom_du_mois(annee, mois):
    """Retourne par exemple 'mai 2026'."""
    return f"{NOMS_DES_MOIS[mois - 1]} {annee}"


@dataclass(frozen=True)
class Operation:
    """Une ligne du releve de compte."""

    date: date
    libelle: str
    categorie: str
    montant: float

    @property
    def est_une_depense(self):
        return self.montant < 0


@dataclass(frozen=True)
class Releve:
    """Un fichier importe, avec quelques chiffres deja calcules."""

    identifiant: int
    nom_fichier: str
    date_import: date
    debut: date
    fin: date
    nombre_operations: int
    total_revenus: float
    total_depenses: float

    @property
    def solde(self):
        return self.total_revenus + self.total_depenses

    @property
    def periode(self):
        """Texte decrivant la periode couverte, par exemple 'mai 2026'."""
        debut = nom_du_mois(self.debut.year, self.debut.month)
        fin = nom_du_mois(self.fin.year, self.fin.month)
        return debut if debut == fin else f"{debut} - {fin}"


@dataclass(frozen=True)
class TotauxCategorie:
    """Ce qui a ete depense et recu dans une categorie, sur un mois."""

    categorie: str
    depenses: float  # negatif ou nul
    revenus: float  # positif ou nul


@dataclass(frozen=True)
class StatistiquesMois:
    """Les statistiques d'un mois, pour un releve donne."""

    annee: int
    mois: int
    total_revenus: float
    total_depenses: float
    nombre_operations: int
    categories: List[TotauxCategorie] = field(default_factory=list)
    plus_grosses_depenses: List[Operation] = field(default_factory=list)

    @property
    def solde(self):
        return self.total_revenus + self.total_depenses

    @property
    def libelle(self):
        return nom_du_mois(self.annee, self.mois)
