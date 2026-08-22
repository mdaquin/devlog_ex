import statistics

def montant_reel(op):
    """Montant à comptabiliser : les remboursements sont exclus."""
    if op["montant"] < 0:
        return -op["montant"]
    # remboursement : rien à comptabiliser

def depense_mediane(operations):
    """Dépense médiane du mois."""
    montants = [montant_reel(op) for op in operations]
    return statistics.median(montants)

janvier = [
    {"libelle": "Loyer",          "montant": -700.00},
    {"libelle": "Courses",        "montant":  -42.50},
    {"libelle": "Remb. mutuelle", "montant":   35.00},
    {"libelle": "Essence",        "montant":  -60.00},
]

print("Dépense médiane :", depense_mediane(janvier), "EUR")