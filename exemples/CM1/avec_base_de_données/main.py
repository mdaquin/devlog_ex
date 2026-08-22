"""Point d'entree de l'application.

Usage :
    python main.py [chemin/vers/la/base.sqlite3]

La base est creee automatiquement au premier lancement.
"""

import os
import sys

from depenses.base import BaseDeDonnees
from depenses.interface import Application

# Par defaut la base est rangee a cote du programme, quel que soit le dossier
# depuis lequel on le lance.
BASE_PAR_DEFAUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "depenses.sqlite3")


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else BASE_PAR_DEFAUT
    base = BaseDeDonnees(chemin)
    try:
        Application(base).mainloop()
    finally:
        base.fermer()


if __name__ == "__main__":
    main()
