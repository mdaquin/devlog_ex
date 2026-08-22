"""Assemblage des statistiques a partir des donnees de la base.

Les calculs lourds (sommes, regroupements) sont faits en SQL dans `base.py`.
Ce module se contente d'assembler les resultats en objets utilisables par
l'interface, et de les mettre en forme.
"""

from .modeles import StatistiquesMois


def statistiques_du_releve(base, releve_id, nombre_de_grosses_depenses=3):
    """Retourne les statistiques de chaque mois presents dans un releve.

    Un releve couvre normalement un seul mois, mais rien ne l'impose : on
    retourne donc une liste, dans l'ordre chronologique.
    """
    statistiques = []

    for annee, mois in base.mois_du_releve(releve_id):
        revenus, depenses, nombre = base.totaux_du_mois(releve_id, annee, mois)
        statistiques.append(
            StatistiquesMois(
                annee=annee,
                mois=mois,
                total_revenus=revenus,
                total_depenses=depenses,
                nombre_operations=nombre,
                categories=base.totaux_par_categorie(releve_id, annee, mois),
                plus_grosses_depenses=base.plus_grosses_depenses(
                    releve_id, annee, mois, nombre_de_grosses_depenses
                ),
            )
        )

    return statistiques


def statistiques_des_derniers_releves(base, nombre_de_releves=3):
    """Retourne [(releve, [statistiques par mois]), ...] pour les N derniers.

    Les releves sont ranges du plus recent au plus ancien.
    """
    return [
        (releve, statistiques_du_releve(base, releve.identifiant))
        for releve in base.lister_releves(limite=nombre_de_releves)
    ]


def formater_montant(montant):
    """Formate un montant en euros, par exemple : 1 234,56 EUR."""
    texte = f"{abs(montant):,.2f}".replace(",", " ").replace(".", ",")
    signe = "-" if montant < 0 else ""
    return f"{signe}{texte} EUR"
