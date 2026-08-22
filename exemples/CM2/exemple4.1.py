import statistics

operations = [
    {"mois": "2026-01", "libelle": "Loyer",   "montant": -700.00},
    {"mois": "2026-01", "libelle": "Courses", "montant":  -42.50},
    {"mois": "2026-02", "libelle": "Loyer",   "montant": -700.00}]

for mois in ["2026-01", "2026-02", "2026-03"]:
   montants = [abs(op["montant"]) for op in operations if op["mois"] == mois]
   print(mois, ":", statistics.mean(montants), "EUR")