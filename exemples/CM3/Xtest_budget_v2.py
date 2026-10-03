import unittest
from budget_v2 import total_depenses

class TestTotalDepenses_v2(unittest.TestCase):

    """Suite de tests pour la fonction total_depenses."""

    def setUp(self):
        """Fixture : reconstruite avant CHAQUE cas de test."""
        self.janvier = [
            {"mois": "2026-01", "libelle": "Loyer",          "montant": -700.00},
            {"mois": "2026-01", "libelle": "Courses",        "montant":  -42.50},
            {"mois": "2026-01", "libelle": "Remb. mutuelle", "montant":   35.00},
        ]

    def test_depenses_du_mois(self):
        self.assertAlmostEqual(total_depenses(self.janvier, "2026-01"), 742.50, places=2)

    def test_mois_sans_operation(self):
        self.assertEqual(total_depenses(self.janvier, "2026-03"), 0.0)

    def test_ajouter_une_depense_augmente_le_total(self):
        self.janvier.append({"mois": "2026-01", "libelle": "Essence", "montant": -60.00})
        self.assertAlmostEqual(total_depenses(self.janvier, "2026-01"), 802.50, places=2)

    def test_la_fixture_est_neuve_a_chaque_fois(self):
        self.assertEqual(len(self.janvier), 3)