"""Acces a la base de donnees SQLite.

Tout le SQL de l'application est regroupe ici : les autres modules ne
manipulent que des objets Python (voir `modeles.py`). C'est ce qui permet,
par exemple, de tester les statistiques sans interface graphique, ou de
changer de base de donnees sans toucher au reste.

SQLite est fourni avec Python : aucune installation, la base tient dans un
seul fichier (`depenses.sqlite3` par defaut).
"""

import sqlite3
from datetime import date, datetime

from .modeles import Operation, Releve, TotauxCategorie

# Le schema est cree au demarrage s'il n'existe pas deja.
SCHEMA = """
CREATE TABLE IF NOT EXISTS releve (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_fichier   TEXT NOT NULL,
    empreinte     TEXT NOT NULL UNIQUE,   -- empeche d'importer deux fois le meme fichier
    date_import   TEXT NOT NULL,
    debut         TEXT NOT NULL,          -- date de la premiere operation (AAAA-MM-JJ)
    fin           TEXT NOT NULL           -- date de la derniere operation
);

CREATE TABLE IF NOT EXISTS operation (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    releve_id  INTEGER NOT NULL REFERENCES releve(id) ON DELETE CASCADE,
    date       TEXT NOT NULL,
    libelle    TEXT NOT NULL,
    categorie  TEXT NOT NULL,
    montant    REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS index_operation_releve ON operation(releve_id);
CREATE INDEX IF NOT EXISTS index_operation_date ON operation(date);
"""


class ReleveDejaImporte(Exception):
    """Levee quand on tente d'importer un fichier deja present en base."""


class BaseDeDonnees:
    """Represente la base de donnees ouverte."""

    def __init__(self, chemin="depenses.sqlite3"):
        self.chemin = str(chemin)
        self.connexion = sqlite3.connect(self.chemin)
        # Les lignes se manipulent comme des dictionnaires : ligne["montant"].
        self.connexion.row_factory = sqlite3.Row
        # SQLite n'applique les cles etrangeres que si on le demande.
        self.connexion.execute("PRAGMA foreign_keys = ON")
        self.connexion.executescript(SCHEMA)

    def fermer(self):
        self.connexion.close()

    # ------------------------------------------------------------------
    # Ecriture
    # ------------------------------------------------------------------

    def ajouter_releve(self, nom_fichier, empreinte, operations):
        """Enregistre un releve et ses operations, puis retourne son identifiant.

        Tout est fait dans une seule transaction : si une operation echoue,
        aucun releve incomplet ne reste en base.
        """
        if not operations:
            raise ValueError("Ce releve ne contient aucune operation.")

        dates = [operation.date for operation in operations]

        try:
            with self.connexion:  # transaction : COMMIT si tout va bien, ROLLBACK sinon
                curseur = self.connexion.execute(
                    "INSERT INTO releve (nom_fichier, empreinte, date_import, debut, fin)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (
                        nom_fichier,
                        empreinte,
                        date.today().isoformat(),
                        min(dates).isoformat(),
                        max(dates).isoformat(),
                    ),
                )
                releve_id = curseur.lastrowid

                self.connexion.executemany(
                    "INSERT INTO operation (releve_id, date, libelle, categorie, montant)"
                    " VALUES (?, ?, ?, ?, ?)",
                    [
                        (
                            releve_id,
                            operation.date.isoformat(),
                            operation.libelle,
                            operation.categorie,
                            operation.montant,
                        )
                        for operation in operations
                    ],
                )
        except sqlite3.IntegrityError as erreur:
            # La contrainte UNIQUE sur l'empreinte a saute.
            raise ReleveDejaImporte(
                "Ce fichier a deja ete importe (contenu identique)."
            ) from erreur

        return releve_id

    def supprimer_releve(self, releve_id):
        """Supprime un releve ; ses operations partent avec (ON DELETE CASCADE)."""
        with self.connexion:
            self.connexion.execute("DELETE FROM releve WHERE id = ?", (releve_id,))

    # ------------------------------------------------------------------
    # Lecture
    # ------------------------------------------------------------------

    def lister_releves(self, limite=None):
        """Retourne les releves, du plus recent au plus ancien.

        Les totaux sont calcules par la base elle-meme : c'est son travail,
        et cela evite de charger toutes les operations en memoire.
        """
        requete = """
            SELECT r.id, r.nom_fichier, r.date_import, r.debut, r.fin,
                   COUNT(o.id) AS nombre_operations,
                   COALESCE(SUM(CASE WHEN o.montant > 0 THEN o.montant END), 0) AS revenus,
                   COALESCE(SUM(CASE WHEN o.montant < 0 THEN o.montant END), 0) AS depenses
            FROM releve AS r
            LEFT JOIN operation AS o ON o.releve_id = r.id
            GROUP BY r.id
            ORDER BY r.fin DESC, r.id DESC
        """
        if limite is not None:
            requete += " LIMIT ?"
            lignes = self.connexion.execute(requete, (limite,)).fetchall()
        else:
            lignes = self.connexion.execute(requete).fetchall()

        return [
            Releve(
                identifiant=ligne["id"],
                nom_fichier=ligne["nom_fichier"],
                date_import=date.fromisoformat(ligne["date_import"]),
                debut=date.fromisoformat(ligne["debut"]),
                fin=date.fromisoformat(ligne["fin"]),
                nombre_operations=ligne["nombre_operations"],
                total_revenus=ligne["revenus"],
                total_depenses=ligne["depenses"],
            )
            for ligne in lignes
        ]

    def mois_du_releve(self, releve_id):
        """Retourne la liste des (annee, mois) presents dans un releve."""
        lignes = self.connexion.execute(
            """
            SELECT DISTINCT CAST(strftime('%Y', date) AS INTEGER) AS annee,
                            CAST(strftime('%m', date) AS INTEGER) AS mois
            FROM operation
            WHERE releve_id = ?
            ORDER BY annee, mois
            """,
            (releve_id,),
        ).fetchall()
        return [(ligne["annee"], ligne["mois"]) for ligne in lignes]

    def totaux_du_mois(self, releve_id, annee, mois):
        """Retourne (revenus, depenses, nombre d'operations) pour un mois."""
        ligne = self.connexion.execute(
            """
            SELECT COALESCE(SUM(CASE WHEN montant > 0 THEN montant END), 0) AS revenus,
                   COALESCE(SUM(CASE WHEN montant < 0 THEN montant END), 0) AS depenses,
                   COUNT(*) AS nombre
            FROM operation
            WHERE releve_id = ? AND strftime('%Y-%m', date) = ?
            """,
            (releve_id, f"{annee:04d}-{mois:02d}"),
        ).fetchone()
        return ligne["revenus"], ligne["depenses"], ligne["nombre"]

    def totaux_par_categorie(self, releve_id, annee, mois):
        """Retourne les totaux par categorie pour un mois, les plus gros d'abord."""
        lignes = self.connexion.execute(
            """
            SELECT categorie,
                   COALESCE(SUM(CASE WHEN montant < 0 THEN montant END), 0) AS depenses,
                   COALESCE(SUM(CASE WHEN montant > 0 THEN montant END), 0) AS revenus
            FROM operation
            WHERE releve_id = ? AND strftime('%Y-%m', date) = ?
            GROUP BY categorie
            ORDER BY depenses ASC, revenus DESC
            """,
            (releve_id, f"{annee:04d}-{mois:02d}"),
        ).fetchall()
        return [
            TotauxCategorie(
                categorie=ligne["categorie"],
                depenses=ligne["depenses"],
                revenus=ligne["revenus"],
            )
            for ligne in lignes
        ]

    def plus_grosses_depenses(self, releve_id, annee, mois, limite=3):
        """Retourne les plus grosses depenses d'un mois."""
        lignes = self.connexion.execute(
            """
            SELECT date, libelle, categorie, montant
            FROM operation
            WHERE releve_id = ? AND strftime('%Y-%m', date) = ? AND montant < 0
            ORDER BY montant ASC
            LIMIT ?
            """,
            (releve_id, f"{annee:04d}-{mois:02d}", limite),
        ).fetchall()
        return [
            Operation(
                date=date.fromisoformat(ligne["date"]),
                libelle=ligne["libelle"],
                categorie=ligne["categorie"],
                montant=ligne["montant"],
            )
            for ligne in lignes
        ]

    def operations_du_releve(self, releve_id):
        """Retourne toutes les operations d'un releve, par date croissante."""
        lignes = self.connexion.execute(
            "SELECT date, libelle, categorie, montant FROM operation"
            " WHERE releve_id = ? ORDER BY date, id",
            (releve_id,),
        ).fetchall()
        return [
            Operation(
                date=date.fromisoformat(ligne["date"]),
                libelle=ligne["libelle"],
                categorie=ligne["categorie"],
                montant=ligne["montant"],
            )
            for ligne in lignes
        ]


def convertir_en_date(valeur):
    """Accepte une date, un datetime ou une chaine et retourne une date."""
    if isinstance(valeur, datetime):
        return valeur.date()
    if isinstance(valeur, date):
        return valeur
    return date.fromisoformat(str(valeur)[:10])
