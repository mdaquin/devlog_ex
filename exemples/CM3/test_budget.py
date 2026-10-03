import unittest
from budget import total_depenses


class TestTotalDepenses(unittest.TestCase):
    """Suite de tests pour la fonction total_depenses."""

    def test_mois_simple(self):
        operations = [
            {"mois": "2026-02", "libelle": "Loyer",   "montant": -700.00},
            {"mois": "2026-02", "libelle": "Courses", "montant":  -42.50},
        ]
        self.assertAlmostEqual(total_depenses(operations, "2026-02"), 742.50, places=2)

    def test_remboursement_n_est_pas_une_depense(self):
        operations = [
            {"mois": "2026-01", "libelle": "Loyer",          "montant": -700.00},
            {"mois": "2026-01", "libelle": "Courses",        "montant":  -42.50},
            {"mois": "2026-01", "libelle": "Remb. mutuelle", "montant":   35.00},
        ]
        self.assertAlmostEqual(total_depenses(operations, "2026-01"), 742.50, places=2)

    def test_mois_sans_operation(self):
        operations = [{"mois": "2026-01", "libelle": "Loyer", "montant": -700.00}]
        self.assertEqual(total_depenses(operations, "2026-03"), 0.0)


if __name__ == "__main__":
    unittest.main()