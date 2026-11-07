#!/usr/bin/env python3
"""Genere un jeu de releves bancaires francais synthetiques mais realistes.

Usage :
    python generateur_de_releves_factices.py <compte> <debut> <fin> <frequence>
    python generateur_de_releves_factices.py client-001 2026-01-01 2026-06-30 1mo

Le premier passage sur un identifiant de compte cree un profil complet
(titulaire, banque, IBAN/BIC, situation, revenus...). Ce profil est conserve
dans `profils_comptes.json` dans le dossier de sortie et reutilise ensuite.

Frequences acceptees : 1w (une semaine), 2w (deux semaines), 1mo (un mois),
3mo (trois mois). Chaque frequence produit un fichier Excel par periode.

Dependance : openpyxl (pip install openpyxl)
"""

import argparse
import calendar
import json
import math
import os
import random
import re
import sys
import unicodedata
from datetime import date, timedelta

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
except ImportError:
    sys.exit("openpyxl est requis : pip install openpyxl")


BANQUES = [
    ("BNP Paribas", "30004", "BNPAFRPP", "16 boulevard des Italiens", "75009", "Paris"),
    ("Société Générale", "30003", "SOGEFRPP", "29 boulevard Haussmann", "75009", "Paris"),
    ("Crédit Agricole", "10278", "AGRIFRPP", "1 rue de la Banque", "75002", "Paris"),
    ("Caisse d'Épargne", "17515", "CEPAFRPP", "5 rue Masseran", "75007", "Paris"),
    ("La Banque Postale", "20041", "PSSTFRPP", "115 rue de Sèvres", "75275", "Paris"),
    ("LCL", "30002", "CRLYFRPP", "19 boulevard des Italiens", "75002", "Paris"),
    ("CIC", "30066", "CMCIFRPP", "6 avenue de la Porte de Champerret", "75017", "Paris"),
    ("Crédit Mutuel", "15589", "CMCIFR2A", "4 rue Frédéric-Guillaume Raiffeisen", "67000", "Strasbourg"),
    ("Banque Populaire", "10207", "CCBPFRPP", "76 avenue de France", "75013", "Paris"),
    ("Boursorama Banque", "40618", "BOUSFRPP", "44 rue Traversière", "92100", "Boulogne-Billancourt"),
]

PRENOMS_FEMMES = [
    "Camille", "Léa", "Chloé", "Manon", "Emma", "Sarah", "Inès", "Julie",
    "Pauline", "Mathilde", "Amélie", "Sophie", "Nadia", "Fatou", "Aïcha",
    "Mélanie", "Claire", "Élodie", "Céline", "Lucie",
]
PRENOMS_HOMMES = [
    "Julien", "Thomas", "Nicolas", "Alexandre", "Maxime", "Antoine", "Hugo",
    "Lucas", "Mehdi", "Karim", "Yanis", "Rui", "Paul", "Pierre", "Olivier",
    "Romain", "Baptiste", "Mathieu", "Sébastien", "David",
]
NOMS = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier", "Morel",
    "Girard", "André", "Mercier", "Dupont", "Lambert", "Bonnet", "François",
    "Martinez", "Legrand", "Garnier", "Faure", "Rousseau", "Blanc", "Guérin",
    "Muller", "Henry", "Roussel", "Nicolas", "Perrin", "Morin", "Mathieu",
    "Clément", "Gauthier", "Dumont", "Lopez", "Fontaine", "Chevalier",
    "Robin", "Masson",
]

RUES = [
    "rue des Lilas", "avenue Victor Hugo", "rue de la République",
    "boulevard Gambetta", "rue Pasteur", "avenue de la Gare",
    "rue des Écoles", "chemin des Vignes", "rue du Moulin",
    "place de la Mairie", "rue Jean Jaurès", "avenue de la Liberté",
    "rue des Fleurs", "impasse du Château", "rue de Verdun",
    "allée des Pins", "rue du Général de Gaulle", "boulevard Saint-Michel",
]

VILLES = [
    ("75011", "Paris"), ("75015", "Paris"), ("69003", "Lyon"),
    ("13006", "Marseille"), ("31000", "Toulouse"), ("44000", "Nantes"),
    ("33000", "Bordeaux"), ("59000", "Lille"), ("67000", "Strasbourg"),
    ("35000", "Rennes"), ("34000", "Montpellier"), ("06000", "Nice"),
    ("51100", "Reims"), ("76100", "Rouen"), ("38000", "Grenoble"),
    ("21000", "Dijon"), ("76600", "Le Havre"), ("42000", "Saint-Étienne"),
]

EMPLOIS = {
    "etudiant": ["Étudiant(e)"],
    "jeune_actif": ["Développeur", "Infirmière", "Chargé de communication",
                    "Technicien", "Commercial", "Enseignant", "Comptable",
                    "Graphiste"],
    "famille": ["Cadre", "Enseignante", "Infirmier", "Artisan",
                "Fonctionnaire", "Responsable commercial"],
    "couple": ["Cadre", "Ingénieur", "Médecin", "Enseignante",
               "Chef de projet", "Avocat"],
    "retraite": ["Retraité(e)"],
    "celibataire": ["Employé", "Technicien", "Commercial", "Enseignant",
                    "Fonctionnaire", "Artisan"],
}

EMPLOYEURS = [
    "SOCIETE DUPONT", "CLINIQUE SAINT-JEAN", "MAIRIE DE LYON",
    "TECHNOLOGIES MARTIN", "GROUPE VERT", "ASSURANCES BLEUES",
    "LYCEE VICTOR HUGO", "HOPITAL SAINT-LOUIS", "STARTUP NOVA",
    "CONSEIL AZUR", "LOGISTIQUE EXPRESS",
]

PROFILS = {
    "etudiant": {
        "poids": 15,
        "age": (18, 26),
        "situations": ["célibataire", "en couple"],
        "enfants": (0, 0),
        "revenu": (450, 1100),
        "logement": {"poids": {"locataire": 70, "heberge": 30},
                     "loyer": (250, 600), "part": (0.35, 0.55)},
    },
    "jeune_actif": {
        "poids": 25,
        "age": (24, 36),
        "situations": ["célibataire", "en couple", "pacsé(e)"],
        "enfants": (0, 1),
        "revenu": (1800, 3500),
        "logement": {"poids": {"locataire": 65, "proprietaire": 25,
                               "heberge": 10},
                     "loyer": (400, 1100), "part": (0.25, 0.35)},
    },
    "famille": {
        "poids": 20,
        "age": (32, 52),
        "situations": ["marié(e)", "pacsé(e)", "en couple"],
        "enfants": (1, 3),
        "revenu": (2800, 6000),
        "logement": {"poids": {"locataire": 45, "proprietaire": 55},
                     "loyer": (600, 1800), "part": (0.18, 0.28)},
    },
    "couple": {
        "poids": 15,
        "age": (28, 55),
        "situations": ["marié(e)", "pacsé(e)", "en couple"],
        "enfants": (0, 2),
        "revenu": (3200, 7000),
        "logement": {"poids": {"locataire": 50, "proprietaire": 50},
                     "loyer": (600, 2000), "part": (0.18, 0.28)},
    },
    "retraite": {
        "poids": 10,
        "age": (62, 88),
        "situations": ["marié(e)", "veuf(ve)", "célibataire"],
        "enfants": (0, 0),
        "revenu": (1200, 3200),
        "logement": {"poids": {"locataire": 40, "proprietaire": 60},
                     "loyer": (350, 1000), "part": (0.15, 0.30)},
    },
    "celibataire": {
        "poids": 15,
        "age": (25, 55),
        "situations": ["célibataire", "divorcé(e)", "en couple"],
        "enfants": (0, 2),
        "revenu": (1700, 3800),
        "logement": {"poids": {"locataire": 60, "proprietaire": 30,
                               "heberge": 10},
                     "loyer": (400, 1100), "part": (0.22, 0.32)},
    },
}

FREQUENCES = {
    "1w": ("semaines", 1),
    "2w": ("semaines", 2),
    "1mo": ("mois", 1),
    "3mo": ("mois", 3),
}


# ---------------------------------------------------------------------------
# Profils
# ---------------------------------------------------------------------------

def _sans_accents(texte):
    return unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode("ascii")


def _slug(texte):
    return re.sub(r"[^a-z0-9]+", "-", _sans_accents(texte).lower()).strip("-")


def _iban_fr(rng, code_banque):
    """Construit un IBAN francais avec une cle RIB et une cle IBAN valides."""
    guichet = f"{rng.randint(0, 99999):05d}"
    compte = f"{rng.randint(0, 99999999999):011d}"
    cle_rib = 97 - ((89 * int(code_banque) + 15 * int(guichet) + 3 * int(compte)) % 97)
    bban = f"{code_banque}{guichet}{compte}{cle_rib:02d}"
    # FR00 -> F=15, R=27, 00, place en fin de BBAN pour le calcul modulo 97.
    cle_iban = 98 - (int(bban + "152700") % 97)
    return f"FR{cle_iban:02d}{bban}"


def _creer_logement(rng, type_profil, revenu):
    regles = PROFILS[type_profil]["logement"]
    statut = rng.choices(
        list(regles["poids"]), weights=list(regles["poids"].values())
    )[0]
    if statut == "heberge":
        return {"statut": "heberge", "montant_mensuel": 0.0,
                "libelle": None, "taxe_fonciere": 0.0}
    montant = rng.uniform(*regles["part"]) * revenu
    montant = round(min(max(montant, regles["loyer"][0]), regles["loyer"][1]), 2)
    if statut == "locataire":
        return {"statut": "locataire", "montant_mensuel": montant,
                "libelle": "PRLV LOYER", "taxe_fonciere": 0.0}
    credit = rng.random() < 0.55
    return {
        "statut": "proprietaire",
        "montant_mensuel": montant if credit else 0.0,
        "libelle": "ECHEANCE PRET IMMOBILIER" if credit else None,
        "taxe_fonciere": round(rng.uniform(500, 1800), 2),
    }


def _creer_profil(compte, type_profil=None):
    """Cree un profil coherent pour un identifiant de compte."""
    rng = random.Random(compte)
    type_profil = type_profil or rng.choices(
        list(PROFILS), weights=[PROFILS[p]["poids"] for p in PROFILS]
    )[0]
    regles = PROFILS[type_profil]

    genre = rng.choices(["femme", "homme", "autre"], weights=[47, 47, 6])[0]
    if genre == "femme":
        prenom = rng.choice(PRENOMS_FEMMES)
    elif genre == "homme":
        prenom = rng.choice(PRENOMS_HOMMES)
    else:
        prenom = rng.choice(PRENOMS_FEMMES + PRENOMS_HOMMES)
    nom = rng.choice(NOMS)
    civilite = "Mme" if genre == "femme" else "M."

    age = rng.randint(*regles["age"])
    naissance = date.today() - timedelta(days=age * 365 + rng.randint(0, 364))
    adresse = f"{rng.randint(1, 150)} {rng.choice(RUES)}"
    code_postal, ville = rng.choice(VILLES)
    email = (f"{_sans_accents(prenom).lower()}."
             f"{_sans_accents(nom).lower()}@"
             f"{rng.choice(['example.com', 'example.org', 'example.fr'])}")
    telephone = (f"06 {rng.randint(10, 99)} {rng.randint(10, 99)} "
                 f"{rng.randint(10, 99)} {rng.randint(10, 99)}")

    situation = rng.choice(regles["situations"])
    enfants = rng.randint(*regles["enfants"])
    revenu = round(rng.uniform(*regles["revenu"]), 2)
    logement = _creer_logement(rng, type_profil, revenu)
    emploi = rng.choice(EMPLOIS[type_profil])
    employeur = "JOB ETUDIANT" if type_profil == "etudiant" else rng.choice(EMPLOYEURS)

    if type_profil in ("famille", "couple") and situation in (
            "marié(e)", "pacsé(e)", "en couple"):
        type_compte = "Compte joint"
    elif type_profil == "etudiant" and rng.random() < 0.6:
        type_compte = "Compte étudiant"
    else:
        type_compte = "Compte courant"

    if rng.random() < 0.15:
        solde_initial = -round(rng.uniform(20, 300), 2)
    else:
        solde_initial = min(round(revenu * rng.uniform(0.15, 1.1), 2), 12000.0)

    banque = rng.choice(BANQUES)

    return {
        "id": compte,
        "profil": type_profil,
        "civilite": civilite,
        "genre": genre,
        "prenom": prenom,
        "nom": nom,
        "date_naissance": naissance.isoformat(),
        "adresse": adresse,
        "code_postal": code_postal,
        "ville": ville,
        "email": email,
        "telephone": telephone,
        "situation": situation,
        "enfants": enfants,
        "emploi": emploi,
        "employeur": employeur,
        "revenu_mensuel": revenu,
        "type_compte": type_compte,
        "logement": logement,
        "banque": {
            "nom": banque[0],
            "bic": banque[2],
            "adresse": f"{banque[3]}, {banque[4]} {banque[5]}",
            "iban": _iban_fr(rng, banque[1]),
        },
        "solde_initial": solde_initial,
        "date_creation": date.today().isoformat(),
    }


def _charger_profils(dossier):
    chemin = os.path.join(dossier, "profils_comptes.json")
    if not os.path.exists(chemin):
        return {}
    with open(chemin, encoding="utf-8") as fichier:
        return json.load(fichier)


def _sauver_profils(dossier, profils):
    chemin = os.path.join(dossier, "profils_comptes.json")
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(profils, fichier, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def _operations_du_mois(profil, annee, mois):
    """Operations d'un mois, tirees de facon reproductible pour ce compte."""
    rng = random.Random(f"{profil['id']}|{annee:04d}-{mois:02d}")
    operations = []
    dernier_jour = calendar.monthrange(annee, mois)[1]

    def ajouter(jour, libelle, categorie, montant):
        montant = round(montant, 2)
        if abs(montant) >= 0.01:
            operations.append({
                "date": date(annee, mois, min(jour, dernier_jour)),
                "libelle": libelle,
                "categorie": categorie,
                "montant": montant,
            })

    # Logement et charges fixes.
    logement = profil["logement"]
    if logement["montant_mensuel"] and logement["libelle"]:
        ajouter(rng.randint(2, 5), logement["libelle"], "Logement",
                -logement["montant_mensuel"])
    facteur_hiver = 1.25 + 0.45 * math.cos((mois - 1) / 12 * 2 * math.pi)
    ajouter(rng.randint(7, 12), "PRLV EDF", "Logement",
            -rng.uniform(45, 100) * facteur_hiver)
    if rng.random() < 0.35:
        ajouter(rng.randint(7, 12), "PRLV ENGIE", "Logement", -rng.uniform(25, 70))

    # Abonnements.
    internet = rng.choice([
        ("PRLV FREE HAUT DEBIT", [29.99, 39.99]),
        ("PRLV ORANGE INTERNET", [29.99, 39.99, 49.99]),
        ("PRLV SFR INTERNET", [24.99, 32.99]),
        ("PRLV BOUYGUES INTERNET", [26.99, 36.99]),
    ])
    ajouter(rng.randint(4, 9), internet[0], "Abonnements", -rng.choice(internet[1]))
    mobile = rng.choice([
        ("PRLV FREE MOBILE", [7.99, 9.99, 15.99, 19.99]),
        ("PRLV ORANGE MOBILE", [9.99, 14.99, 19.99]),
        ("PRLV SFR MOBILE", [7.99, 12.99, 19.99]),
        ("PRLV BOUYGUES MOBILE", [7.99, 12.99, 19.99]),
    ])
    ajouter(rng.randint(4, 9), mobile[0], "Abonnements", -rng.choice(mobile[1]))

    ajouter(rng.randint(8, 14), f"PRLV {rng.choice(['MAIF', 'MACIF', 'AXA', 'GMF', 'MATMUT'])}",
            "Assurance", -rng.uniform(18, 55))
    if profil["profil"] != "etudiant":
        ajouter(rng.randint(8, 14), "PRLV MUTUELLE", "Santé", -rng.uniform(25, 80))

    for _ in range(rng.randint(1, 2)):
        service = rng.choice(["NETFLIX", "SPOTIFY", "DISNEY+", "PRIME VIDEO", "CANAL+"])
        prix = {"NETFLIX": 13.49, "SPOTIFY": 10.99, "DISNEY+": 8.99,
                "PRIME VIDEO": 6.99, "CANAL+": 24.99}[service]
        ajouter(rng.randint(1, 20), f"PRLV {service}", "Abonnements", -prix)

    if profil["profil"] in ("jeune_actif", "famille", "couple", "celibataire") \
            and profil["revenu_mensuel"] > 1400:
        ajouter(rng.randint(12, 16), "PRLV IMPOT REVENU", "Impôts",
                -rng.uniform(30, 380))

    # Frais bancaires.
    if mois % 3 == 1:
        ajouter(28, "FRAIS TENUE DE COMPTE", "Banque", -rng.choice([2.0, 2.5, 3.0, 4.5]))
    if rng.random() < 0.06:
        ajouter(rng.randint(10, 25), "COTISATION CARTE", "Banque",
                -rng.choice([15.0, 25.0, 35.0, 45.0]))

    # Revenus.
    if profil["profil"] == "etudiant":
        ajouter(rng.randint(3, 7), "VIR BOURSE CROUS", "Bourse", rng.uniform(250, 600))
        if rng.random() < 0.75:
            ajouter(rng.randint(10, 20), "VIR JOB ETUDIANT", "Salaire",
                    rng.uniform(150, 500))
    elif profil["profil"] == "retraite":
        ajouter(rng.randint(1, 5), "VIR PENSION CNAV", "Pension", rng.uniform(900, 1800))
        if rng.random() < 0.55:
            ajouter(rng.randint(1, 5), "VIR PENSION AGIRC-ARRCO", "Pension",
                    rng.uniform(200, 900))
    else:
        revenu = profil["revenu_mensuel"]
        if profil["type_compte"] == "Compte joint":
            part = rng.uniform(0.4, 0.6)
            ajouter(rng.randint(25, 28), f"VIR SALAIRE {profil['employeur']}",
                    "Salaire", revenu * part)
            ajouter(rng.randint(25, 28), "VIR SALAIRE CONJOINT", "Salaire",
                    revenu * (1 - part))
        else:
            ajouter(rng.randint(25, 28), f"VIR SALAIRE {profil['employeur']}",
                    "Salaire", revenu)
        if profil["enfants"]:
            ajouter(rng.randint(3, 7), "VIR CAF ALLOCATIONS", "Revenus divers",
                    rng.uniform(80, 250) * profil["enfants"])

    # Depenses recurrentes.
    if profil["profil"] in ("etudiant", "jeune_actif", "celibataire") \
            and rng.random() < 0.8:
        ajouter(rng.randint(1, 5), "PRLV ABONNEMENT TRANSPORT", "Transport",
                -rng.choice([30.0, 75.2, 86.4, 90.0]))

    nombres_courses = {"etudiant": 3, "jeune_actif": 4, "famille": 6,
                       "couple": 5, "retraite": 4, "celibataire": 4}
    for _ in range(nombres_courses[profil["profil"]]):
        enseigne = rng.choice(["CARREFOUR MARKET", "LECLERC", "INTERMARCHE",
                               "MONOPRIX", "AUCHAN", "LIDL", "ALDI", "FRANPRIX"])
        montant = rng.uniform(15, 110)
        if profil["profil"] == "famille":
            montant *= 1.35
        ajouter(rng.randint(1, 28), enseigne, "Courses", -montant)

    for _ in range(rng.randint(1, 5)):
        lieu = rng.choice(["RESTAURANT LE BISTROT", "MCDONALD'S", "BOULANGERIE",
                           "CAFE DE LA GARE", "PIZZERIA", "SUSHI SHOP",
                           "BRASSERIE"])
        ajouter(rng.randint(1, 28), lieu, "Restauration", -rng.uniform(3, 45))
    if rng.random() < 0.5:
        ajouter(rng.randint(1, 28),
                rng.choice(["CINEMA PATHE", "UGC CINE CITE", "MUSEE", "THEATRE"]),
                "Loisirs", -rng.uniform(8, 45))

    for _ in range(rng.randint(1, 3)):
        ajouter(rng.randint(1, 28), "RETRAIT DAB", "Retraits",
                -rng.choice([20.0, 40.0, 50.0, 60.0, 80.0, 100.0]))
    if rng.random() < 0.7:
        ajouter(rng.randint(1, 28),
                rng.choice(["AMAZON", "FNAC", "ZARA", "DECATHLON", "IKEA",
                            "H&M", "LEROY MERLIN"]),
                "Shopping", -rng.uniform(10, 150))

    if profil["profil"] in ("jeune_actif", "famille", "couple", "celibataire") \
            and rng.random() < 0.85:
        for _ in range(rng.randint(1, 3)):
            ajouter(rng.randint(1, 28),
                    rng.choice(["TOTALENERGIES", "ESSO", "BP",
                                "INTERMARCHE CARBURANT"]),
                    "Transport", -rng.uniform(35, 85))

    if rng.random() < 0.6:
        ajouter(rng.randint(1, 28), "PHARMACIE", "Santé", -rng.uniform(5, 45))
    if rng.random() < 0.15:
        ajouter(rng.randint(1, 28), "CONSULTATION MEDECIN", "Santé",
                -rng.uniform(25, 80))

    if profil["enfants"]:
        if mois not in (7, 8):
            ajouter(rng.randint(1, 10), "PRLV CANTINE", "Enfants",
                    -rng.uniform(60, 150) * profil["enfants"])
        if mois == 9:
            ajouter(rng.randint(1, 10), "ACHAT FOURNITURES SCOLAIRES", "Enfants",
                    -rng.uniform(50, 200) * profil["enfants"])
        if rng.random() < 0.4:
            ajouter(rng.randint(1, 10), "PRLV ACTIVITE SPORTIVE", "Enfants",
                    -rng.uniform(30, 80))
        if rng.random() < 0.08:
            ajouter(rng.randint(1, 10), "PRLV CRECHE", "Enfants",
                    -rng.uniform(250, 650))

    if profil["profil"] != "etudiant" and rng.random() < 0.55:
        ajouter(rng.randint(5, 10), "VIR EPARGNE LIVRET A", "Épargne",
                -rng.uniform(50, 300))

    # Evenements ponctuels.
    if mois == 9:
        if profil["profil"] in ("famille", "couple"):
            ajouter(rng.randint(1, 10), "COTISATION SPORT", "Enfants",
                    -rng.uniform(50, 200))
        if profil["profil"] == "etudiant":
            ajouter(rng.randint(1, 15), "ACHAT ORDINATEUR", "Shopping",
                    -rng.uniform(400, 1200))
    if mois == 12:
        ajouter(rng.randint(1, 20), "ACHATS NOEL", "Shopping", -rng.uniform(50, 300))
    if mois in (7, 8) and profil["profil"] in ("famille", "couple", "retraite") \
            and rng.random() < 0.7:
        ajouter(rng.randint(1, 20), "LOCATION VACANCES", "Loisirs",
                -rng.uniform(300, 1500))
    if mois == 10 and profil["logement"]["statut"] == "proprietaire":
        ajouter(rng.randint(10, 20), "TAXE FONCIERE", "Impôts",
                -profil["logement"]["taxe_fonciere"])

    if rng.random() < 0.3:
        libelle, categorie, montant = rng.choice([
            ("REPARATION VOITURE", "Transport", -rng.uniform(150, 800)),
            ("ELECTROMENAGER", "Maison", -rng.uniform(200, 800)),
            ("REMBOURSEMENT MUTUELLE", "Santé", rng.uniform(20, 150)),
            ("VIREMENT RECU", "Revenus divers", rng.uniform(20, 300)),
            ("VENTE LEBONCOIN", "Revenus divers", rng.uniform(20, 250)),
            ("DON ASSOCIATION", "Dons", -rng.uniform(10, 100)),
            ("AMENDE", "Impôts", -rng.uniform(35, 135)),
            ("PAIEMENT ETRANGER", "Voyages", -rng.uniform(20, 300)),
            ("FRAIS CARTE ETRANGER", "Banque", -rng.uniform(2, 15)),
            ("CHEQUE", "Divers", -rng.uniform(50, 500)),
            ("REMISE CHEQUE", "Revenus divers", rng.uniform(50, 500)),
            ("ANNULATION PAIEMENT", "Revenus divers", rng.uniform(10, 100)),
            ("VIREMENT INSTANTANE RECU", "Revenus divers", rng.uniform(10, 200)),
            ("INTERETS CREDITEURS", "Revenus divers", rng.uniform(0.05, 5)),
            ("FRAIS RETRAIT DAB HORS RESEAU", "Banque", -rng.uniform(1, 5)),
            ("VIREMENT SEPA RECU", "Revenus divers", rng.uniform(20, 500)),
        ])
        ajouter(rng.randint(1, 28), libelle, categorie, montant)

    if rng.random() < 0.02:
        montant = round(rng.uniform(10, 100), 2)
        ajouter(rng.randint(1, 15), "PAIEMENT EN DOUBLE", "Divers", -montant)
        ajouter(rng.randint(16, 28), "REMBOURSEMENT DOUBLON", "Revenus divers", montant)

    if rng.random() < 0.03:
        ajouter(rng.randint(1, 28), "COMMISSION INTERVENTION", "Banque",
                -rng.uniform(5, 15))

    if rng.random() < 0.04:
        ajouter(rng.randint(5, 20), "REJET PRLV", "Banque", -rng.uniform(20, 150))
        ajouter(rng.randint(5, 20), "FRAIS REJET", "Banque", -rng.uniform(8, 20))

    _equilibrer_budget(profil, operations, rng, annee, mois)
    return operations


def _equilibrer_budget(profil, operations, rng, annee, mois):
    """Evite les soldes absurdes : ajuste les depenses et l'epargne du mois."""
    operations[:] = [operation for operation in operations
                     if operation["libelle"] != "VIR EPARGNE LIVRET A"]
    revenus = sum(operation["montant"] for operation in operations
                  if operation["montant"] > 0)
    net = sum(operation["montant"] for operation in operations)

    if net < 0:
        if profil["profil"] == "etudiant":
            # Un coup de pouce familial est plus credible que des depenses nulles.
            operations.append({
                "date": date(annee, mois, rng.randint(3, 10)),
                "libelle": "VIR AIDE FAMILIALE",
                "categorie": "Revenus divers",
                "montant": round(-net + rng.uniform(10, 50), 2),
            })
        else:
            # On reduit les postes les plus souples, sans les rendre insignifiants.
            categories = ("Restauration", "Loisirs", "Shopping", "Voyages", "Dons")
            variables = [operation for operation in operations
                         if operation["categorie"] in categories
                         and operation["montant"] < 0]
            total = -sum(operation["montant"] for operation in variables)
            if total > 0:
                reduction = min(-net, total * 0.5)
                facteur = 1 - reduction / total
                for operation in variables:
                    operation["montant"] = round(operation["montant"] * facteur, 2)

            net = sum(operation["montant"] for operation in operations)
            if net < 0:
                courses = [operation for operation in operations
                           if operation["categorie"] == "Courses"
                           and operation["montant"] < 0]
                total = -sum(operation["montant"] for operation in courses)
                if total > 0:
                    reduction = min(-net, total * 0.3)
                    facteur = 1 - reduction / total
                    for operation in courses:
                        operation["montant"] = round(operation["montant"] * facteur, 2)

            net = sum(operation["montant"] for operation in operations)
            if net < 0:
                operations.append({
                    "date": date(annee, mois, rng.randint(3, 10)),
                    "libelle": "VIR REMBOURSEMENT",
                    "categorie": "Revenus divers",
                    "montant": round(-net + rng.uniform(10, 50), 2),
                })
    else:
        # Le surplus au-dela de l'epargne mensuelle part sur le livret A.
        taux = {"etudiant": 0.02, "jeune_actif": 0.12, "famille": 0.08,
                "couple": 0.12, "retraite": 0.06, "celibataire": 0.10}
        surplus = net - revenus * taux[profil["profil"]]
        if surplus > 20:
            operations.append({
                "date": date(annee, mois, rng.randint(5, 12)),
                "libelle": "VIR EPARGNE LIVRET A",
                "categorie": "Épargne",
                "montant": -round(surplus, 2),
            })


def _generer_operations(profil, debut, fin):
    operations = []
    annee, mois = debut.year, debut.month
    while (annee, mois) <= (fin.year, fin.month):
        operations.extend(_operations_du_mois(profil, annee, mois))
        mois += 1
        if mois == 13:
            annee, mois = annee + 1, 1
    return operations


def _bornes_periodes(debut, fin, frequence):
    """Decoupe [debut, fin] en periodes de la frequence demandee."""
    unite, pas = FREQUENCES[frequence]
    index = 0
    courant = debut
    while courant <= fin:
        index += 1
        if unite == "mois":
            suivant = _ajouter_mois(debut, index * pas)
        else:
            suivant = debut + timedelta(weeks=index * pas)
        suivant = min(suivant, fin + timedelta(days=1))
        yield courant, suivant - timedelta(days=1)
        courant = suivant


def _ajouter_mois(depart, nombre):
    mois = depart.month - 1 + nombre
    annee = depart.year + mois // 12
    mois = mois % 12 + 1
    jour = min(depart.day, calendar.monthrange(annee, mois)[1])
    return date(annee, mois, jour)


def _ajouter_frais_decouvert(profil, debut, fin, operations, solde_ouverture):
    """Ajoute des frais si le releve se termine a decouvert."""
    solde = solde_ouverture + sum(operation["montant"] for operation in operations)
    if solde >= 0 or (fin - debut).days < 20:
        return operations

    rng = random.Random(f"{profil['id']}|{debut.isoformat()}")
    operations = list(operations)
    operations.append({
        "date": fin,
        "libelle": "FRAIS DE DECOUVERT",
        "categorie": "Banque",
        "montant": -round(rng.uniform(4, 12), 2),
    })
    interets = round(abs(solde) * rng.uniform(0.0005, 0.002), 2)
    if interets >= 0.01 and fin.month in (3, 6, 9, 12):
        operations.append({
            "date": fin,
            "libelle": "INTERETS DEBITEURS",
            "categorie": "Banque",
            "montant": -interets,
        })
    operations.sort(key=lambda operation: (operation["date"], operation["libelle"]))
    return operations


# ---------------------------------------------------------------------------
# Ecriture Excel
# ---------------------------------------------------------------------------

def _euros(montant):
    texte = f"{montant:,.2f}".replace(",", " ").replace(".", ",")
    return f"{texte} €"


def _ecrire_releve(chemin, profil, debut, fin, operations, solde_ouverture):
    """Ecrit un releve au format Excel et renvoie le solde de cloture."""
    banque = profil["banque"]
    classeur = Workbook()
    feuille = classeur.active
    feuille.title = "Relevé"

    feuille["A1"] = banque["nom"]
    feuille["A1"].font = Font(bold=True, size=14)
    feuille["A2"] = banque["adresse"]
    feuille["A4"] = "RELEVÉ DE COMPTE"
    feuille["A4"].font = Font(bold=True, size=12)
    feuille["A5"] = f"Titulaire : {profil['civilite']} {profil['prenom']} {profil['nom']}"
    feuille["A6"] = (f"Adresse : {profil['adresse']}, "
                     f"{profil['code_postal']} {profil['ville']}")
    feuille["A7"] = f"Compte : {profil['type_compte']} - IBAN {banque['iban']}"
    feuille["A8"] = f"BIC : {banque['bic']}"
    feuille["A9"] = f"Période : du {debut:%d/%m/%Y} au {fin:%d/%m/%Y}"
    feuille["A10"] = f"Solde précédent : {_euros(solde_ouverture)}"

    entetes = ["Date", "Date de valeur", "Libellé", "Catégorie",
               "Débit", "Crédit", "Solde"]
    ligne = 12
    for colonne, entete in enumerate(entetes, start=1):
        cellule = feuille.cell(row=ligne, column=colonne, value=entete)
        cellule.font = Font(bold=True)
        cellule.fill = PatternFill("solid", fgColor="D9E1F2")
        cellule.alignment = Alignment(horizontal="center")

    bord = Border(bottom=Side(style="thin"))
    for colonne in range(1, len(entetes) + 1):
        feuille.cell(row=ligne, column=colonne).border = bord

    solde = solde_ouverture
    total_debits = 0.0
    total_credits = 0.0
    ligne += 1
    for operation in operations:
        montant = operation["montant"]
        solde = round(solde + montant, 2)
        if montant < 0:
            debit, credit = -montant, None
            total_debits = round(total_debits + debit, 2)
        else:
            debit, credit = None, montant
            total_credits = round(total_credits + credit, 2)
        valeur = operation["date"] + timedelta(
            days=2 if operation["libelle"] == "CHEQUE" else 0
        )
        valeurs = [operation["date"], valeur, operation["libelle"],
                   operation["categorie"], debit, credit, solde]
        for colonne, contenu in enumerate(valeurs, start=1):
            cellule = feuille.cell(row=ligne, column=colonne, value=contenu)
            if colonne in (1, 2):
                cellule.number_format = "DD/MM/YYYY"
            elif colonne in (5, 6, 7):
                cellule.number_format = '#,##0.00 €'
        ligne += 1

    ligne += 1
    feuille.cell(row=ligne, column=3, value="Total des débits").font = Font(bold=True)
    feuille.cell(row=ligne, column=5, value=total_debits).number_format = '#,##0.00 €'
    ligne += 1
    feuille.cell(row=ligne, column=3, value="Total des crédits").font = Font(bold=True)
    feuille.cell(row=ligne, column=6, value=total_credits).number_format = '#,##0.00 €'
    ligne += 1
    feuille.cell(row=ligne, column=3, value="Nouveau solde").font = Font(bold=True)
    cellule = feuille.cell(row=ligne, column=7, value=solde)
    cellule.font = Font(bold=True)
    cellule.number_format = '#,##0.00 €'

    for colonne, largeur in zip("ABCDEFG", (12, 14, 36, 16, 12, 12, 14)):
        feuille.column_dimensions[colonne].width = largeur
    feuille.freeze_panes = "A13"

    classeur.save(chemin)
    return solde


# ---------------------------------------------------------------------------
# Point d'entree
# ---------------------------------------------------------------------------

def main():
    analyseur = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    analyseur.add_argument("compte", help="identifiant du compte (ex. client-001)")
    analyseur.add_argument("debut", help="date de debut, AAAA-MM-JJ")
    analyseur.add_argument("fin", help="date de fin, AAAA-MM-JJ")
    analyseur.add_argument("frequence", choices=sorted(FREQUENCES),
                           help="frequence des releves")
    analyseur.add_argument("--sortie", default="releves",
                           help="dossier de sortie (defaut : releves)")
    analyseur.add_argument("--profil", choices=sorted(PROFILS),
                           help="force le type de profil a la creation")
    arguments = analyseur.parse_args()

    try:
        debut = date.fromisoformat(arguments.debut)
        fin = date.fromisoformat(arguments.fin)
    except ValueError as erreur:
        analyseur.error(f"date invalide : {erreur}")
    if debut > fin:
        analyseur.error("la date de debut doit preceder la date de fin")

    os.makedirs(arguments.sortie, exist_ok=True)
    profils = _charger_profils(arguments.sortie)

    if arguments.compte in profils:
        profil = profils[arguments.compte]
        print(f"Profil existant : {profil['civilite']} {profil['prenom']} "
              f"{profil['nom']} ({profil['profil']})")
    else:
        profil = _creer_profil(arguments.compte, arguments.profil)
        profils[arguments.compte] = profil
        _sauver_profils(arguments.sortie, profils)
        print(f"Nouveau profil : {profil['civilite']} {profil['prenom']} "
              f"{profil['nom']} ({profil['profil']})")
        print(f"  {profil['banque']['nom']} - IBAN {profil['banque']['iban']}")

    operations = _generer_operations(profil, debut, fin)
    solde = profil["solde_initial"]

    for debut_periode, fin_periode in _bornes_periodes(debut, fin, arguments.frequence):
        du_releve = [operation for operation in operations
                     if debut_periode <= operation["date"] <= fin_periode]
        du_releve.sort(key=lambda operation: (operation["date"], operation["libelle"]))
        du_releve = _ajouter_frais_decouvert(
            profil, debut_periode, fin_periode, du_releve, solde
        )
        nom = (f"releve_{_slug(arguments.compte)}_"
               f"{debut_periode:%Y-%m-%d}_{fin_periode:%Y-%m-%d}.xlsx")
        chemin = os.path.join(arguments.sortie, nom)
        solde = _ecrire_releve(
            chemin, profil, debut_periode, fin_periode, du_releve, solde
        )
        print(f"{len(du_releve):3d} operations -> {chemin} "
              f"(solde : {_euros(solde)})")


if __name__ == "__main__":
    main()
