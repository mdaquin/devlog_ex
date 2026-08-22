def retirer_petites_operations(operations, seuil=5.0):
    """Retire les opérations dont le montant est inférieur au seuil."""
    for op in operations:
        if abs(op["montant"]) < seuil:
            operations.remove(op)
    return operations

janvier = [
    {"libelle": "Loyer",   "montant": -700.00},
    {"libelle": "Café",    "montant":   -3.20},
    {"libelle": "Pain",    "montant":   -2.10},
    {"libelle": "Courses", "montant":  -42.50},
    {"libelle": "Timbre",  "montant":   -1.50},
]

retirer_petites_operations(janvier, seuil=5.0)
for op in janvier: print(op["libelle"], ":\t", op["montant"])


