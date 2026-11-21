#!/usr/bin/env python3
"""Animation pygame de l'historique git d'un depot.

Chaque commit apparait le long d'une ligne du temps, avec sa date, son
identifiant court et son message. La comete qui parcourt la ligne allume les
noeuds un par un.

Usage :
    python animation_commits.py [chemin/du/depot]

Options :
    --limite N            nombre de commits affiches (40 par defaut)
    --capture FICHIER.png enregistre une image au lieu d'ouvrir une fenetre
    --at SECONDES         instant a capturer (avec --capture)

Touches :
    Espace                pause / reprise
    Fleches gauche/droite reculer / avancer
    R                     relancer depuis le debut
    F                     plein ecran
    Echap ou Q            quitter

Prerequis : pygame (`pip install pygame`).
"""

import argparse
import math
import os
import random
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime

try:
    import pygame
except ImportError:  # message clair plutot qu'une trace d'import
    raise SystemExit("pygame est requis : pip install pygame")

# ---------------------------------------------------------------------------
# Reglages visuels
# ---------------------------------------------------------------------------

LARGEUR, HAUTEUR = 1280, 720
MARGE = 96
BASE = 410                 # ordonnee de la ligne du temps
STAGGER = 0.62             # secondes entre deux commits
TEMPS_FINAL = 3.0          # pause sur l'image finale

FOND_HAUT = (9, 13, 26)
FOND_BAS = (18, 25, 44)
TITRE = (232, 238, 246)
TEXTE = (205, 214, 229)
DIM = (118, 130, 154)
ACCENT = (110, 231, 255)
VERT = (96, 220, 140)
AMBRE = (245, 190, 90)
ROUGE = (240, 110, 120)

PALETTE = [(94, 234, 212), (129, 140, 248), (244, 114, 182)]

MOIS_COURTS = [
    "janv.", "févr.", "mars", "avr.", "mai", "juin",
    "juil.", "août", "sept.", "oct.", "nov.", "déc.",
]
MOIS_LONGS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]

POLICES = "Avenir Next,Helvetica Neue,Helvetica,Arial,DejaVu Sans"
POLICE_MONO = "SF Mono,Menlo,Monaco,Consolas,DejaVu Sans Mono,Courier New"


# ---------------------------------------------------------------------------
# Lecture du depot
# ---------------------------------------------------------------------------


def git(depot, *arguments, verifier=True):
    """Lance une commande git et retourne sa sortie standard."""
    resultat = subprocess.run(
        ["git", "-C", depot, *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if verifier and resultat.returncode != 0:
        raise SystemExit(
            f"git {' '.join(arguments)} a echoue : {resultat.stderr.strip()}"
        )
    return resultat.stdout if resultat.returncode == 0 else None


@dataclass
class Commit:
    sha: str
    court: str
    auteur: str
    date: datetime
    horodatage: float
    references: str
    sujet: str


@dataclass
class Depot:
    nom: str
    chemin: str
    branche: str
    commits: list = field(default_factory=list)
    amont: str = None
    avance: int = 0
    retard: int = 0
    modifs: int = 0
    total: int = 0


def lire_depot(chemin, limite=40):
    """Rassemble les commits et l'etat de synchronisation du depot."""
    racine = git(chemin, "rev-parse", "--show-toplevel", verifier=False)
    if racine is None:
        raise SystemExit(f"{chemin} n'est pas un depot git.")
    racine = racine.strip()

    depot = Depot(
        nom=os.path.basename(racine),
        chemin=racine,
        branche=git(racine, "rev-parse", "--abbrev-ref", "HEAD").strip(),
    )

    separateur = "\x1f"
    sortie = git(
        racine,
        "log",
        f"-n{limite}",
        "--date=iso-strict",
        "--pretty=format:"
        + separateur.join(["%H", "%h", "%an", "%ad", "%D", "%s"]),
    )

    for ligne in sortie.splitlines():
        if not ligne.strip():
            continue
        champs = ligne.split(separateur, 5)
        if len(champs) < 6:
            continue
        sha, court, auteur, date_texte, references, sujet = champs
        date = datetime.fromisoformat(date_texte)
        depot.commits.append(
            Commit(
                sha=sha,
                court=court,
                auteur=auteur,
                date=date,
                horodatage=date.timestamp(),
                references=references,
                sujet=sujet,
            )
        )

    if not depot.commits:
        raise SystemExit("Ce depot ne contient encore aucun commit.")

    # `git log` sort du plus recent au plus ancien : l'animation, elle, part du
    # premier commit et remonte le temps jusqu'a HEAD.
    depot.commits.reverse()
    depot.total = int((git(racine, "rev-list", "--count", "HEAD") or "0").strip())

    # Etat par rapport a la branche amont (si elle existe).
    amont = git(
        racine,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
        verifier=False,
    )
    if amont:
        depot.amont = amont.strip()
        compte = git(racine, "rev-list", "--left-right", "--count", "HEAD...@{upstream}")
        if compte:
            avant, arriere = compte.split()
            depot.avance, depot.retard = int(avant), int(arriere)

    statut = git(racine, "status", "--porcelain") or ""
    depot.modifs = len([l for l in statut.splitlines() if l.strip()])

    return depot


# ---------------------------------------------------------------------------
# Petites fonctions utilitaires
# ---------------------------------------------------------------------------


def melange(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def couleur_commit(i, total):
    """Degrade teal -> indigo -> rose le long de l'historique."""
    if total <= 1:
        return PALETTE[0]
    position = i / (total - 1) * (len(PALETTE) - 1)
    indice = min(int(position), len(PALETTE) - 2)
    return melange(PALETTE[indice], PALETTE[indice + 1], position - indice)


def borner(valeur, mini=0.0, maxi=1.0):
    return max(mini, min(maxi, valeur))


def ease_out_cubic(x):
    x = borner(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x):
    x = borner(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def date_courte(date):
    return f"{date.day:02d} {MOIS_COURTS[date.month - 1]} {date.year}"


def tronquer(police, texte, largeur_max):
    if police.size(texte)[0] <= largeur_max:
        return texte
    coupe = texte
    while coupe and police.size(coupe + "...")[0] > largeur_max:
        coupe = coupe[:-1]
    return coupe.rstrip() + "..."


def ecrire(surface, police, texte, couleur, position, ancre="topleft", alpha=255):
    image = police.render(texte, True, couleur)
    if alpha < 255:
        image.set_alpha(alpha)
    rectangle = image.get_rect(**{ancre: position})
    surface.blit(image, rectangle)
    return rectangle


# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------


class Animation:
    def __init__(self, depot, taille=(LARGEUR, HAUTEUR)):
        pygame.font.init()
        self.depot = depot
        self.commits = depot.commits
        self.taille = taille
        self.surface = pygame.Surface((LARGEUR, HAUTEUR))

        self.police_titre = pygame.font.SysFont(POLICES, 27, bold=True)
        self.police_sujet = pygame.font.SysFont(POLICES, 15, bold=True)
        self.police_texte = pygame.font.SysFont(POLICES, 14)
        self.police_petite = pygame.font.SysFont(POLICES, 12)
        self.police_mono = pygame.font.SysFont(POLICE_MONO, 12)
        self.police_grande = pygame.font.SysFont(POLICES, 21, bold=True)

        self.positions = self._calculer_positions()
        self.nb = len(self.commits)
        self.revelation = max((self.nb - 1) * STAGGER, 0.001)
        self.duree = self.revelation + TEMPS_FINAL
        self.t = 0.0
        self.pause = False

        self.fond = self._preparer_fond()
        self.etoiles = self._preparer_etoiles()

    # -- geometrie ----------------------------------------------------

    def _calculer_positions(self):
        n = len(self.commits)
        if n == 1:
            return [(LARGEUR / 2, BASE)]

        premier = self.commits[0].horodatage
        dernier = self.commits[-1].horodatage
        intervalle = max(dernier - premier, 1.0)

        fractions = []
        for i, commit in enumerate(self.commits):
            par_date = (commit.horodatage - premier) / intervalle
            par_index = i / (n - 1)
            # Moitie date, moitie index : les gros trous restent visibles sans
            # ecraser les rafales de commits.
            fractions.append(0.55 * par_date + 0.45 * par_index)

        minimum = 66 / (LARGEUR - 2 * MARGE)
        for i in range(1, n):
            fractions[i] = max(fractions[i], fractions[i - 1] + minimum)

        if fractions[-1] > 1:
            fractions = [f / fractions[-1] for f in fractions]

        return [
            (MARGE + f * (LARGEUR - 2 * MARGE), BASE) for f in fractions
        ]

    def position_comete(self, t):
        """Position de la comete a l'instant t, le long de la ligne."""
        if self.nb == 1:
            return self.positions[0]
        u = borner(t / self.revelation) * (self.nb - 1)
        i = min(int(u), self.nb - 2)
        local = u - i
        x1, y1 = self.positions[i]
        x2, y2 = self.positions[i + 1]
        return (x1 + (x2 - x1) * local, y1 + (y2 - y1) * local)

    # -- decor --------------------------------------------------------

    def _preparer_fond(self):
        fond = pygame.Surface((LARGEUR, HAUTEUR))
        for y in range(HAUTEUR):
            fond.fill(melange(FOND_HAUT, FOND_BAS, y / (HAUTEUR - 1)), (0, y, LARGEUR, 1))

        halo = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        for rayon in range(460, 20, -24):
            alpha = int(7 * (1 - rayon / 460))
            pygame.draw.circle(halo, (80, 110, 190, alpha), (LARGEUR // 2, BASE), rayon)
        fond.blit(halo, (0, 0))

        grille = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        for x in range(0, LARGEUR, 64):
            pygame.draw.line(grille, (255, 255, 255, 7), (x, 0), (x, HAUTEUR))
        for y in range(0, HAUTEUR, 64):
            pygame.draw.line(grille, (255, 255, 255, 6), (0, y), (LARGEUR, y))
        fond.blit(grille, (0, 0))
        return fond

    def _preparer_etoiles(self):
        hasard = random.Random(7)
        return [
            {
                "x": hasard.uniform(0, LARGEUR),
                "y": hasard.uniform(0, HAUTEUR),
                "r": hasard.choice([1, 1, 1, 2]),
                "v": hasard.uniform(2, 11),
                "phase": hasard.uniform(0, math.tau),
            }
            for _ in range(90)
        ]

    def _etoiles(self, t):
        for etoile in self.etoiles:
            x = (etoile["x"] + etoile["v"] * t) % (LARGEUR + 20) - 10
            scintillement = 0.5 + 0.5 * math.sin(t * 1.4 + etoile["phase"])
            alpha = int(18 + 52 * scintillement)
            couleur = (120 + int(60 * scintillement), 150 + int(40 * scintillement), 210)
            pygame.draw.circle(
                self.surface,
                melange(FOND_BAS, couleur, alpha / 255),
                (int(x), int(etoile["y"])),
                etoile["r"],
            )

    # -- boucle -------------------------------------------------------

    def maj(self, dt):
        if not self.pause:
            self.t = min(self.t + dt, self.duree)

    def dessiner(self):
        t = self.t
        self.surface.blit(self.fond, (0, 0))
        self._etoiles(t)

        lueur = pygame.Surface((LARGEUR, HAUTEUR))
        lueur.fill((0, 0, 0))

        self._dessiner_ligne(lueur, t)
        self._dessiner_noeuds(lueur, t)
        self._dessiner_comete(lueur, t)
        self.surface.blit(lueur, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        self._dessiner_etiquettes(t)
        self._dessiner_entete(t)
        self._dessiner_pied(t)

    # -- elements de la ligne ----------------------------------------

    def _dessiner_ligne(self, lueur, t):
        # Ligne de fond : tout le trajet reste visible, tres discret.
        if self.nb > 1:
            pygame.draw.line(
                self.surface, (34, 44, 68), self.positions[0], self.positions[-1], 2
            )

        for i in range(self.nb - 1):
            depart = i * STAGGER
            avancement = borner((t - depart) / STAGGER)
            if avancement <= 0:
                continue
            x1, y1 = self.positions[i]
            x2, y2 = self.positions[i + 1]
            x = x1 + (x2 - x1) * avancement
            couleur = couleur_commit(i, self.nb)
            pygame.draw.line(self.surface, couleur, (x1, y1), (x, y1), 3)
            pygame.draw.line(
                lueur,
                tuple(int(c * 0.22) for c in couleur),
                (x1, y1),
                (int(x), int(y1)),
                9,
            )

    def _dessiner_noeuds(self, lueur, t):
        for i, (x, y) in enumerate(self.positions):
            age = t - i * STAGGER

            if age < 0:
                # Commit pas encore revele : simple graduation.
                pygame.draw.circle(self.surface, (46, 56, 82), (int(x), int(y)), 3)
                continue

            couleur = couleur_commit(i, self.nb)
            apparition = borner(age / 0.45)
            echelle = ease_out_back(apparition)
            rayon = 6.5 * echelle

            # Onde de choc a l'allumage.
            onde = borner(age / 1.0)
            if onde < 1:
                rayon_onde = 8 + 34 * ease_out_cubic(onde)
                alpha = int(120 * (1 - onde))
                halo = pygame.Surface((int(rayon_onde * 2) + 4, int(rayon_onde * 2) + 4), pygame.SRCALPHA)
                pygame.draw.circle(
                    halo, (*couleur, alpha), (halo.get_width() // 2, halo.get_height() // 2), int(rayon_onde), 2
                )
                self.surface.blit(halo, (x - halo.get_width() / 2, y - halo.get_height() / 2))

            # Halo additif, en trois cercles concentriques pour un degrade doux.
            for multiplicateur, rayon_lueur in ((0.24, 12), (0.11, 20), (0.045, 30)):
                pygame.draw.circle(
                    lueur,
                    tuple(int(c * multiplicateur) for c in couleur),
                    (int(x), int(y)),
                    rayon_lueur,
                )

            pygame.draw.circle(self.surface, tuple(int(c * 0.55) for c in couleur), (int(x), int(y)), int(rayon + 3), 1)
            pygame.draw.circle(self.surface, couleur, (int(x), int(y)), max(1, int(rayon)))
            if rayon > 3:
                pygame.draw.circle(
                    self.surface,
                    melange(couleur, (255, 255, 255), 0.7),
                    (int(x - rayon * 0.3), int(y - rayon * 0.35)),
                    max(1, int(rayon * 0.3)),
                )

            # Petite etiquette HEAD sur le commit courant.
            if i == self.nb - 1 and apparition >= 1:
                badge = pygame.Rect(0, 0, 52, 19)
                badge.center = (int(x), int(y) - 34)
                pygame.draw.rect(self.surface, (24, 33, 51), badge, border_radius=9)
                pygame.draw.rect(self.surface, ACCENT, badge, width=1, border_radius=9)
                ecrire(
                    self.surface, self.police_mono, "HEAD", ACCENT,
                    badge.center, ancre="center",
                )

    def _dessiner_comete(self, lueur, t):
        if t > self.revelation + 0.9:
            return
        fin = 1 - borner((t - self.revelation) / 0.9)
        if t >= self.revelation:
            position = self.position_comete(self.revelation)
        else:
            position = self.position_comete(t)

        couleur = ACCENT
        # Trainee analytique : fonction du temps, donc stable en mode pause.
        # Echantillonnage serre pour obtenir une trace continue plutot qu'un
        # chapelet de points.
        for k in range(28, 0, -1):
            arriere = t - k * 0.02
            if arriere < 0:
                continue
            x, y = self.position_comete(arriere)
            facteur = k / 28
            # Uniquement de la lumiere additive : dessiner des disques opaques
            # ici masquerait le trait deja trace entre les deux noeuds.
            pygame.draw.circle(
                lueur,
                tuple(int(c * 0.16 * (1 - facteur)) for c in couleur),
                (int(x), int(y)),
                max(2, int(8 * (1 - facteur))),
            )
            if facteur < 0.55:
                pygame.draw.circle(
                    self.surface,
                    melange(couleur, (255, 255, 255), 0.6),
                    (int(x), int(y)),
                    max(1, int(2 * (1 - facteur))),
                )

        x, y = position
        for multiplicateur, rayon in ((0.55, 10), (0.25, 22), (0.10, 38)):
            pygame.draw.circle(
                lueur,
                tuple(int(c * multiplicateur * fin) for c in couleur),
                (int(x), int(y)),
                rayon,
            )
        pygame.draw.circle(self.surface, (235, 252, 255), (int(x), int(y)), max(1, int(4 * fin)))

    # -- etiquettes ---------------------------------------------------

    def _dessiner_etiquettes(self, t):
        bandes = [(-58, "haut"), (-130, "haut"), (58, "bas"), (130, "bas")]

        for i, (x, y) in enumerate(self.positions):
            age = t - i * STAGGER - 0.05
            if age <= 0:
                continue
            apparition = ease_out_cubic(borner(age / 0.45))
            alpha = int(255 * apparition)
            distance, cote = bandes[i % 4]
            couleur = couleur_commit(i, self.nb)
            commit = self.commits[i]

            largeur_texte = 230
            sujet = tronquer(self.police_sujet, commit.sujet, largeur_texte)
            ligne_meta = f"{commit.court}   {date_courte(commit.date)}"
            largeur = max(
                self.police_sujet.size(sujet)[0],
                self.police_mono.size(commit.court)[0] + self.police_petite.size("   " + date_courte(commit.date))[0],
                132,
            )
            largeur = min(int(largeur) + 4, 248)

            gauche = min(max(x - 6, MARGE / 2), LARGEUR - MARGE / 2 - largeur)
            if cote == "haut":
                bas = y + distance + (1 - apparition) * 10
                haut = bas - 40
            else:
                haut = y + distance - (1 - apparition) * 10
                bas = haut + 40

            # Attache verticale discrete entre le noeud et l'etiquette.
            extremite = bas + 6 if cote == "haut" else haut - 6
            pygame.draw.line(
                self.surface,
                (52, 64, 92),
                (int(x), int(y) + (-14 if cote == "haut" else 14)),
                (int(x), int(extremite)),
                1,
            )

            ecrire(
                self.surface, self.police_sujet, sujet, melange(FOND_BAS, TEXTE, apparition),
                (gauche, haut), alpha=alpha,
            )
            rectangle_hash = ecrire(
                self.surface, self.police_mono, commit.court, melange(FOND_BAS, couleur, apparition),
                (gauche, haut + 22), alpha=alpha,
            )
            ecrire(
                self.surface, self.police_petite, date_courte(commit.date), melange(FOND_BAS, DIM, apparition),
                (rectangle_hash.right + 10, haut + 23), alpha=alpha,
            )

    # -- interface ----------------------------------------------------

    def _dessiner_entete(self, t):
        x = MARGE
        y = 42

        # Petite icone de branche.
        pygame.draw.circle(self.surface, ACCENT, (x + 8, y - 4), 4)
        pygame.draw.circle(self.surface, ACCENT, (x + 8, y + 16), 4)
        pygame.draw.circle(self.surface, ACCENT, (x + 24, y + 6), 4)
        pygame.draw.line(self.surface, ACCENT, (x + 8, y - 4), (x + 8, y + 16), 2)
        pygame.draw.line(self.surface, ACCENT, (x + 8, y + 6), (x + 20, y + 6), 2)

        ecrire(self.surface, self.police_titre, self.depot.nom, TITRE, (x + 40, y - 24))
        premier = self.depot.commits[0].date
        dernier = self.depot.commits[-1].date
        if self.depot.total > self.nb:
            nombre = f"{self.nb} derniers commits sur {self.depot.total}"
        else:
            nombre = f"{self.nb} commit{'s' if self.nb > 1 else ''}"
        sous_titre = (
            f"{self.depot.branche}   |   {premier.day:02d} "
            f"{MOIS_LONGS[premier.month - 1]} {premier.year}  -  "
            f"{dernier.day:02d} {MOIS_LONGS[dernier.month - 1]} {dernier.year}"
            f"   |   {nombre}"
        )
        ecrire(self.surface, self.police_petite, sous_titre, DIM, (x + 40, y + 16))

        self._dessiner_pastille_etat()

        if self.pause:
            ecrire(
                self.surface, self.police_texte, "PAUSE", AMBRE,
                (LARGEUR - MARGE, HAUTEUR - 44), ancre="topright",
            )

    def _dessiner_pastille_etat(self):
        if self.depot.amont is None:
            texte, couleur = "pas de branche amont", DIM
        elif self.depot.avance and self.depot.retard:
            texte = f"divergente ({self.depot.avance}/{self.depot.retard})"
            couleur = ROUGE
        elif self.depot.avance:
            texte = f"{self.depot.avance} commit(s) en avance"
            couleur = AMBRE
        elif self.depot.retard:
            texte = f"{self.depot.retard} commit(s) en retard"
            couleur = ROUGE
        else:
            texte = f"à jour avec {self.depot.amont}"
            couleur = VERT

        if self.depot.modifs:
            texte += f"  |  {self.depot.modifs} modification(s) locale(s)"
            if couleur == VERT:
                couleur = AMBRE

        largeur = self.police_petite.size(texte)[0] + 38
        rectangle = pygame.Rect(LARGEUR - MARGE - largeur, 38, largeur, 30)
        pygame.draw.rect(self.surface, (18, 26, 42), rectangle, border_radius=15)
        pygame.draw.rect(self.surface, couleur, rectangle, width=1, border_radius=15)
        pygame.draw.circle(self.surface, couleur, (rectangle.x + 16, rectangle.centery), 4)
        ecrire(
            self.surface, self.police_petite, texte, melange(FOND_BAS, couleur, 0.85),
            (rectangle.x + 28, rectangle.centery), ancre="midleft",
        )

    def _dessiner_pied(self, t):
        self._dessiner_progression(t)

        ecrire(
            self.surface, self.police_petite,
            "Espace pause   |   flèches reculer/avancer   |   R relancer   |   F plein écran   |   Échap quitter",
            DIM, (MARGE, HAUTEUR - 54),
        )

        courants = sum(1 for i in range(self.nb) if t >= i * STAGGER)
        ecrire(
            self.surface, self.police_mono, f"{courants:02d} / {self.nb:02d}",
            DIM, (LARGEUR - MARGE, HAUTEUR - 56), ancre="topright",
        )

    def _dessiner_progression(self, t):
        y = HAUTEUR - 30
        gauche, droite = MARGE, LARGEUR - MARGE
        fraction = borner(t / self.duree)

        pygame.draw.rect(self.surface, (36, 46, 68), (gauche, y, droite - gauche, 3), border_radius=2)
        if fraction > 0:
            bout = gauche + (droite - gauche) * fraction
            couleur = melange(PALETTE[0], PALETTE[2], fraction)
            pygame.draw.rect(self.surface, couleur, (gauche, y, bout - gauche, 3), border_radius=2)
            pygame.draw.circle(self.surface, melange(couleur, (255, 255, 255), 0.5), (int(bout), y + 1), 4)


# ---------------------------------------------------------------------------
# Entree du programme
# ---------------------------------------------------------------------------


def capturer(animation, chemin, instant):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    animation.t = borner(instant, 0, animation.duree)
    animation.dessiner()
    pygame.image.save(animation.surface, chemin)
    pygame.quit()
    print(f"Image enregistree : {chemin}")


def principal():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("depot", nargs="?", default=os.path.dirname(os.path.abspath(__file__)),
                           help="chemin du depot git (par defaut : dossier du script)")
    analyseur.add_argument("--limite", type=int, default=40, help="nombre de commits affiches")
    analyseur.add_argument("--capture", metavar="FICHIER.png", help="enregistre une image et quitte")
    analyseur.add_argument("--at", type=float, default=6.0, metavar="SECONDES",
                           help="instant capture (avec --capture)")
    arguments = analyseur.parse_args()

    depot = lire_depot(arguments.depot, limite=arguments.limite)
    animation = Animation(depot)

    if arguments.capture:
        capturer(animation, arguments.capture, arguments.at)
        return

    pygame.display.init()
    pygame.display.set_caption(f"Commits de {depot.nom}")
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR), pygame.RESIZABLE)
    horloge = pygame.time.Clock()

    en_cours = True
    while en_cours:
        dt = horloge.tick(60) / 1000

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key in (pygame.K_ESCAPE, pygame.K_q):
                    en_cours = False
                elif evenement.key == pygame.K_SPACE:
                    animation.pause = not animation.pause
                elif evenement.key == pygame.K_r:
                    animation.t = 0
                    animation.pause = False
                elif evenement.key == pygame.K_LEFT:
                    animation.t = max(0, animation.t - 0.4)
                elif evenement.key == pygame.K_RIGHT:
                    animation.t = min(animation.duree, animation.t + 0.4)
                elif evenement.key == pygame.K_HOME:
                    animation.t = 0
                elif evenement.key == pygame.K_END:
                    animation.t = animation.duree
                elif evenement.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()
            elif evenement.type == pygame.MOUSEWHEEL:
                animation.t = max(0, min(animation.duree, animation.t + evenement.y * 0.35))
            elif evenement.type == pygame.VIDEORESIZE:
                ecran = pygame.display.set_mode((evenement.w, evenement.h), pygame.RESIZABLE)

        animation.maj(dt)
        animation.dessiner()

        taille = ecran.get_size()
        if taille == (LARGEUR, HAUTEUR):
            ecran.blit(animation.surface, (0, 0))
        else:
            ecran.blit(pygame.transform.smoothscale(animation.surface, taille), (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    principal()
