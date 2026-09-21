
def total_depenses(operations, mois):
    """Total des dépenses du mois, en euros (valeur positive)."""
    total = 0.0
    for op in operations:
        if op["mois"] == mois and op["montant"] < 0:
            total += abs(op["montant"])
    return total