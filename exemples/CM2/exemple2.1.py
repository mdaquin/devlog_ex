operations = [
    {"mois": "2026-01", "libelle": "Loyer",   "montant": 700.0},
    {"mois": "2026-01", "libelle": "Courses", "montant": 42.5},
    {"mois": "2026-02", "libelle": "Loyer",   "montant": 700.0},
]

# Somme des montants, mois par mois.
totaux = {}
for op in operations:
    totaux[op["mois"]] += op["montant"]

print(totaux)