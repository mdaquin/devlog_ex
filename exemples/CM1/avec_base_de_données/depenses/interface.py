"""Interface graphique (Tkinter / ttk).

Ce module ne fait aucun calcul et n'ecrit aucune requete SQL : il appelle
`importation` et `statistiques`, et se contente d'afficher le resultat.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .base import ReleveDejaImporte
from .importation import FichierInvalide, importer_releve
from .statistiques import (
    formater_montant,
    statistiques_des_derniers_releves,
    statistiques_du_releve,
)

NOMBRE_DE_RELEVES_COMPARES = 3
POLICE_FIXE = ("Courier", 12)


class CadreDefilant(ttk.Frame):
    """Un cadre vertical dans lequel on peut empiler autant de tableaux qu'on veut."""

    def __init__(self, parent):
        super().__init__(parent)

        self.canevas = tk.Canvas(self, highlightthickness=0)
        barre = ttk.Scrollbar(self, orient="vertical", command=self.canevas.yview)
        self.canevas.configure(yscrollcommand=barre.set)

        self.contenu = ttk.Frame(self.canevas)
        self.fenetre = self.canevas.create_window((0, 0), window=self.contenu, anchor="nw")

        # La zone defilante doit suivre la taille du contenu...
        self.contenu.bind(
            "<Configure>",
            lambda evenement: self.canevas.configure(scrollregion=self.canevas.bbox("all")),
        )
        # ... et le contenu doit occuper toute la largeur disponible.
        self.canevas.bind(
            "<Configure>",
            lambda evenement: self.canevas.itemconfigure(self.fenetre, width=evenement.width),
        )
        self.canevas.bind_all("<MouseWheel>", self._molette)

        self.canevas.pack(side="left", fill="both", expand=True)
        barre.pack(side="right", fill="y")

    def _molette(self, evenement):
        self.canevas.yview_scroll(-1 * (evenement.delta // 3 or 1), "units")

    def vider(self):
        for enfant in self.contenu.winfo_children():
            enfant.destroy()


class OngletReleves(ttk.Frame):
    """Liste des releves importes et statistiques du releve selectionne."""

    COLONNES = ("fichier", "periode", "operations", "revenus", "depenses", "solde", "import")
    TITRES = {
        "fichier": "Fichier",
        "periode": "Periode",
        "operations": "Operations",
        "revenus": "Revenus",
        "depenses": "Depenses",
        "solde": "Solde",
        "import": "Importe le",
    }

    def __init__(self, parent, application):
        super().__init__(parent, padding=10)
        self.application = application

        barre = ttk.Frame(self)
        barre.pack(fill="x", pady=(0, 10))
        ttk.Button(barre, text="Importer un releve...", command=self.importer).pack(side="left")
        ttk.Button(barre, text="Supprimer", command=self.supprimer).pack(side="left", padx=6)
        ttk.Button(barre, text="Actualiser", command=self.application.rafraichir).pack(side="left")

        self.tableau = ttk.Treeview(self, columns=self.COLONNES, show="headings", height=8)
        for colonne in self.COLONNES:
            self.tableau.heading(colonne, text=self.TITRES[colonne])
            largeur = 190 if colonne == "fichier" else 110
            ancrage = "w" if colonne in ("fichier", "periode") else "e"
            self.tableau.column(colonne, width=largeur, anchor=ancrage)
        self.tableau.pack(fill="both", expand=True)
        self.tableau.bind("<<TreeviewSelect>>", lambda evenement: self.afficher_details())

        ttk.Label(self, text="Statistiques du releve selectionne :").pack(
            anchor="w", pady=(12, 4)
        )
        self.details = tk.Text(self, height=14, font=POLICE_FIXE, state="disabled", wrap="none")
        self.details.pack(fill="both", expand=True)

    # -- actions ------------------------------------------------------

    def importer(self):
        chemin = filedialog.askopenfilename(
            title="Choisir un releve de compte",
            filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")],
        )
        if not chemin:
            return

        try:
            _, nombre = importer_releve(self.application.base, chemin)
        except (FichierInvalide, ReleveDejaImporte) as erreur:
            messagebox.showwarning("Import impossible", str(erreur))
            return
        except Exception as erreur:  # filet de securite : rien ne doit echouer en silence
            messagebox.showerror("Erreur", f"{type(erreur).__name__} : {erreur}")
            return

        self.application.rafraichir()
        messagebox.showinfo("Import termine", f"{nombre} operations importees.")

    def supprimer(self):
        releve = self.releve_selectionne()
        if releve is None:
            messagebox.showinfo("Suppression", "Selectionnez d'abord un releve dans la liste.")
            return
        if not messagebox.askyesno(
            "Suppression", f"Supprimer definitivement le releve {releve.nom_fichier} ?"
        ):
            return
        self.application.base.supprimer_releve(releve.identifiant)
        self.application.rafraichir()

    # -- affichage ----------------------------------------------------

    def releve_selectionne(self):
        selection = self.tableau.selection()
        if not selection:
            return None
        return self.application.releves_par_identifiant.get(int(selection[0]))

    def rafraichir(self, releves):
        selection = self.tableau.selection()
        self.tableau.delete(*self.tableau.get_children())

        for releve in releves:
            self.tableau.insert(
                "",
                "end",
                iid=str(releve.identifiant),
                values=(
                    releve.nom_fichier,
                    releve.periode,
                    releve.nombre_operations,
                    formater_montant(releve.total_revenus),
                    formater_montant(releve.total_depenses),
                    formater_montant(releve.solde),
                    releve.date_import.strftime("%d/%m/%Y"),
                ),
            )

        # On conserve la selection si le releve existe toujours, sinon on prend le premier.
        enfants = self.tableau.get_children()
        if selection and selection[0] in enfants:
            self.tableau.selection_set(selection[0])
        elif enfants:
            self.tableau.selection_set(enfants[0])

        # `selection_set` declenche l'evenement <<TreeviewSelect>>, mais seulement
        # au prochain tour de boucle : on met les details a jour tout de suite,
        # sinon ils resteraient vides au demarrage ou perimes apres un import.
        self.afficher_details()

    def afficher_details(self):
        releve = self.releve_selectionne()
        if releve is None:
            self.ecrire("Aucun releve selectionne. Utilisez « Importer un releve... ».")
            return

        lignes = [f"{releve.nom_fichier}  ({releve.periode})", ""]

        for stats in statistiques_du_releve(self.application.base, releve.identifiant):
            lignes += [
                f"{stats.libelle}  -  {stats.nombre_operations} operations",
                f"  Revenus  : {formater_montant(stats.total_revenus)}",
                f"  Depenses : {formater_montant(stats.total_depenses)}",
                f"  Solde    : {formater_montant(stats.solde)}",
                "  3 plus grosses depenses :",
            ]
            for numero, operation in enumerate(stats.plus_grosses_depenses, start=1):
                lignes.append(
                    f"    {numero}. {operation.date.strftime('%d/%m/%Y')}  "
                    f"{operation.libelle} ({operation.categorie}) : "
                    f"{formater_montant(operation.montant)}"
                )
            if not stats.plus_grosses_depenses:
                lignes.append("    (aucune depense ce mois-ci)")
            lignes.append("")

        self.ecrire("\n".join(lignes))

    def ecrire(self, texte):
        """Remplace le contenu de la zone de details (normalement en lecture seule)."""
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", texte)
        self.details.configure(state="disabled")


class OngletComparaison(ttk.Frame):
    """Un tableau par mois, pour chacun des trois derniers releves."""

    COLONNES = ("categorie", "depenses", "revenus")
    TITRES = {"categorie": "Categorie", "depenses": "Depenses", "revenus": "Revenus"}

    def __init__(self, parent, application):
        super().__init__(parent, padding=10)
        self.application = application

        ttk.Label(
            self,
            text=f"Les {NOMBRE_DE_RELEVES_COMPARES} derniers releves importes, "
            "du plus recent au plus ancien :",
        ).pack(anchor="w", pady=(0, 8))

        self.zone = CadreDefilant(self)
        self.zone.pack(fill="both", expand=True)

    def rafraichir(self):
        self.zone.vider()

        groupes = statistiques_des_derniers_releves(
            self.application.base, NOMBRE_DE_RELEVES_COMPARES
        )
        if not groupes:
            ttk.Label(self.zone.contenu, text="Aucun releve importe pour le moment.").pack(
                anchor="w"
            )
            return

        for releve, statistiques in groupes:
            for stats in statistiques:
                self.construire_tableau(releve, stats)

    def construire_tableau(self, releve, stats):
        """Construit le tableau d'un mois : un titre, les categories, les totaux."""
        cadre = ttk.LabelFrame(
            self.zone.contenu,
            text=f"{stats.libelle}  -  {releve.nom_fichier}",
            padding=8,
        )
        cadre.pack(fill="x", expand=True, pady=(0, 12))

        resume = (
            f"Revenus {formater_montant(stats.total_revenus)}   "
            f"Depenses {formater_montant(stats.total_depenses)}   "
            f"Solde {formater_montant(stats.solde)}   "
            f"({stats.nombre_operations} operations)"
        )
        ttk.Label(cadre, text=resume).pack(anchor="w", pady=(0, 6))

        # +1 ligne pour le total ; hauteur fixee au contenu, le defilement est global.
        tableau = ttk.Treeview(
            cadre,
            columns=self.COLONNES,
            show="headings",
            height=len(stats.categories) + 1,
        )
        for colonne in self.COLONNES:
            tableau.heading(colonne, text=self.TITRES[colonne])
            tableau.column(
                colonne,
                width=220 if colonne == "categorie" else 140,
                anchor="w" if colonne == "categorie" else "e",
            )

        for totaux in stats.categories:
            tableau.insert(
                "",
                "end",
                values=(
                    totaux.categorie,
                    formater_montant(totaux.depenses) if totaux.depenses else "",
                    formater_montant(totaux.revenus) if totaux.revenus else "",
                ),
            )

        tableau.insert(
            "",
            "end",
            tags=("total",),
            values=(
                "TOTAL",
                formater_montant(stats.total_depenses),
                formater_montant(stats.total_revenus),
            ),
        )
        tableau.tag_configure("total", font=("TkDefaultFont", 12, "bold"))
        tableau.pack(fill="x")


class Application(tk.Tk):
    """Fenetre principale : deux onglets, une base de donnees."""

    def __init__(self, base):
        super().__init__()
        self.base = base
        self.releves_par_identifiant = {}

        self.title("Gestion des depenses")
        self.geometry("900x700")

        carnet = ttk.Notebook(self)
        self.onglet_releves = OngletReleves(carnet, self)
        self.onglet_comparaison = OngletComparaison(carnet, self)
        carnet.add(self.onglet_releves, text="Releves")
        carnet.add(
            self.onglet_comparaison, text=f"{NOMBRE_DE_RELEVES_COMPARES} derniers releves"
        )
        carnet.pack(fill="both", expand=True)

        self.rafraichir()

    def rafraichir(self):
        """Relit la base et remet a jour les deux onglets."""
        releves = self.base.lister_releves()
        self.releves_par_identifiant = {releve.identifiant: releve for releve in releves}
        self.onglet_releves.rafraichir(releves)
        self.onglet_comparaison.rafraichir()
        self.update_idletasks()
