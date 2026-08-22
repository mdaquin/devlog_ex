operations = [
    {"mois": "2026-01", "libelle": "Loyer",   "montant": 700.0},
    {"mois": "2026-01", "libelle": "Courses", "montant": 42.5},
    {"mois": "2026-02", "libelle": "Loyer",   "montant": 700.0},
]

# Somme des montants, mois par mois.
totaux = {}
for op in operations:
    if op["mois"] not in totaux: totaux[op["mois"]] = 0.0
    totaux[op["mois"]] += op["montant"]

mois = sorted(totaux)
ecarts = {}
for i in range(len(mois)):
    ecarts[mois[i]] = totaux[mois[i + 1]] - totaux[mois[i]]

print(ecarts)
