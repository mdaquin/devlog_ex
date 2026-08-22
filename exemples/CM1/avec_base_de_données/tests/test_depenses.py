"""Tests de la base et des statistiques (bibliotheque standard : unittest).

Le decoupage en couches paie ici : on teste toute la logique sans ouvrir
la moindre fenetre, sur une base en memoire creee pour chaque test.

Usage :
    python -m unittest discover -s tests
"""

import os
import sys
import unittest
from datetime import date

# Permet de lancer les tests depuis le dossier du projet sans installation.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from depenses.base import BaseDeDonnees, ReleveDejaImporte  # noqa: E402
from depenses.modeles import Operation  # noqa: E402
from depenses.statistiques import (  # noqa: E402
    formater_montant,
    statistiques_des_derniers_releves,
    statistiques_du_releve,
)


def operations_de_mai():
    return [
        Operation(date(2026, 5, 2), "Loyer", "Logement", -780.00),
        Operation(date(2026, 5, 10), "Courses", "Courses", -60.50),
        Operation(date(2026, 5, 12), "Courses", "Courses", -39.50),
        Operation(date(2026, 5, 25), "Salaire", "Salaire", 2450.00),
    ]


class TestBaseDeDonnees(unittest.TestCase):
    def setUp(self):
        # ":memory:" : une base SQLite qui ne touche pas le disque.
        self.base = BaseDeDonnees(":memory:")

    def tearDown(self):
        self.base.fermer()

    def test_ajout_et_totaux(self):
        self.base.ajouter_releve("mai.xlsx", "empreinte-mai", operations_de_mai())

        releves = self.base.lister_releves()
        self.assertEqual(len(releves), 1)
        releve = releves[0]
        self.assertEqual(releve.nombre_operations, 4)
        self.assertAlmostEqual(releve.total_revenus, 2450.00)
        self.assertAlmostEqual(releve.total_depenses, -880.00)
        self.assertAlmostEqual(releve.solde, 1570.00)
        self.assertEqual(releve.debut, date(2026, 5, 2))
        self.assertEqual(releve.periode, "mai 2026")

    def test_import_en_double_refuse(self):
        self.base.ajouter_releve("mai.xlsx", "empreinte-mai", operations_de_mai())
        with self.assertRaises(ReleveDejaImporte):
            # Meme empreinte : c'est le meme fichier, meme renomme.
            self.base.ajouter_releve("copie.xlsx", "empreinte-mai", operations_de_mai())
        self.assertEqual(len(self.base.lister_releves()), 1)

    def test_suppression_en_cascade(self):
        identifiant = self.base.ajouter_releve("mai.xlsx", "e1", operations_de_mai())
        self.base.supprimer_releve(identifiant)
        self.assertEqual(self.base.lister_releves(), [])
        self.assertEqual(self.base.operations_du_releve(identifiant), [])

    def test_releve_vide_refuse(self):
        with self.assertRaises(ValueError):
            self.base.ajouter_releve("vide.xlsx", "e2", [])


class TestStatistiques(unittest.TestCase):
    def setUp(self):
        self.base = BaseDeDonnees(":memory:")
        self.identifiant = self.base.ajouter_releve("mai.xlsx", "e1", operations_de_mai())

    def tearDown(self):
        self.base.fermer()

    def test_statistiques_par_mois(self):
        statistiques = statistiques_du_releve(self.base, self.identifiant)
        self.assertEqual(len(statistiques), 1)

        mai = statistiques[0]
        self.assertEqual(mai.libelle, "mai 2026")
        self.assertAlmostEqual(mai.solde, 1570.00)
        self.assertEqual(
            [operation.libelle for operation in mai.plus_grosses_depenses],
            ["Loyer", "Courses", "Courses"],
        )
        categories = {totaux.categorie: totaux for totaux in mai.categories}
        self.assertAlmostEqual(categories["Courses"].depenses, -100.00)
        self.assertAlmostEqual(categories["Salaire"].revenus, 2450.00)

    def test_un_releve_sur_deux_mois_donne_deux_tableaux(self):
        self.base.ajouter_releve(
            "trimestre.xlsx",
            "e2",
            [
                Operation(date(2026, 6, 3), "Loyer", "Logement", -780.00),
                Operation(date(2026, 7, 3), "Loyer", "Logement", -780.00),
            ],
        )
        statistiques = statistiques_du_releve(self.base, 2)
        self.assertEqual([stats.libelle for stats in statistiques], ["juin 2026", "juillet 2026"])

    def test_trois_derniers_releves_du_plus_recent_au_plus_ancien(self):
        self.base.ajouter_releve(
            "juin.xlsx", "e2", [Operation(date(2026, 6, 3), "Loyer", "Logement", -780.00)]
        )
        self.base.ajouter_releve(
            "avril.xlsx", "e3", [Operation(date(2026, 4, 3), "Loyer", "Logement", -780.00)]
        )
        self.base.ajouter_releve(
            "mars.xlsx", "e4", [Operation(date(2026, 3, 3), "Loyer", "Logement", -780.00)]
        )

        groupes = statistiques_des_derniers_releves(self.base, 3)
        self.assertEqual(
            [releve.nom_fichier for releve, _ in groupes],
            ["juin.xlsx", "mai.xlsx", "avril.xlsx"],
        )


class TestFormatage(unittest.TestCase):
    def test_formater_montant(self):
        self.assertEqual(formater_montant(1234.5), "1 234,50 EUR")
        self.assertEqual(formater_montant(-780), "-780,00 EUR")
        self.assertEqual(formater_montant(0), "0,00 EUR")


if __name__ == "__main__":
    unittest.main()
