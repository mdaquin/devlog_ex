def total_depenses(operations, mois):
    """Total des dépenses du mois, en euros (valeur positive)."""
    total = 0
    for op in operations:
        if op["mois"] == mois:
            total += abs(op["montant"])
    return total

operations = [
  {"mois": "2026-01", "libelle": "Loyer", "montant": -700.00},
  {"mois": "2026-01", "libelle": "Courses", "montant": -42.50},
  {"mois": "2026-01", "libelle": "Remb. mutuelle", "montant": 35.00},
  {"mois": "2026-02", "libelle": "Loyer", "montant": -700.00},
]

print("Dépenses de 2026-01 :", total_depenses(operations, "2026-01"), "EUR")