def total_par_mois(operations, mois):
    total = 0
    for op in operations:
        if op["mois"] == mois:
            total += float(op["montant"]
    return total