#!/bin/bash
# Double-cliquer sur ce fichier (macOS) pour lancer le programme.
#
# Il se charge de tout : trouver un Python dont l'interface graphique
# fonctionne, creer un environnement virtuel .venv, installer openpyxl,
# puis demarrer analyse_releve.py.

# Se placer dans le dossier du script, quel que soit l'endroit d'ou on le lance.
cd "$(dirname "$0")" || exit 1

echo "Preparation du programme..."

# Un Python utilisable doit savoir ouvrir une fenetre Tkinter ET disposer de
# Tk 8.6 au minimum. Le Python livre par Apple (/usr/bin/python3) n'a que
# Tk 8.5 : l'affichage est different et les fenetres ne se rafraichissent pas
# toujours apres une boite de dialogue. On ne le garde qu'en dernier recours.
tkinter_utilisable() {
    "$1" - <<'FIN_DU_TEST' >/dev/null 2>&1
import sys, tkinter
if tkinter.TkVersion < 8.6:
    sys.exit(1)
tkinter.Tk().destroy()
FIN_DU_TEST
}

# Candidats, du plus recommande au moins recommande. `realpath` evite un piege :
# un python3 atteint par un lien symbolique peut ne plus retrouver ses fichiers
# Tcl/Tk (cas des Python installes par uv dans ~/.local/bin).
lister_candidats() {
    for chemin in \
        /Library/Frameworks/Python.framework/Versions/*/bin/python3 \
        /opt/homebrew/bin/python3 \
        /usr/local/bin/python3 \
        "$CONDA_PREFIX/bin/python3" \
        /opt/homebrew/Caskroom/mambaforge/base/bin/python3 \
        "$(command -v python3 2>/dev/null)" \
        /usr/bin/python3
    do
        [ -x "$chemin" ] && realpath "$chemin" 2>/dev/null || true
    done
}

arreter_avec_erreur() {
    echo
    echo "ERREUR : $1"
    echo
    read -r -p "Appuyez sur Entree pour fermer cette fenetre."
    exit 1
}

# Un .venv deja construit avec un mauvais Python doit etre refait.
if [ -x ".venv/bin/python" ] && ! tkinter_utilisable ".venv/bin/python"; then
    echo "L'environnement virtuel existant n'a pas d'interface graphique utilisable, on le refait..."
    rm -rf .venv
fi

if [ ! -x ".venv/bin/python" ]; then
    for python in $(lister_candidats); do
        tkinter_utilisable "$python" || continue

        echo "Creation de l'environnement virtuel avec $python ..."
        rm -rf .venv
        "$python" -m venv .venv >/dev/null 2>&1 || continue

        # Tkinter peut fonctionner avec le Python de depart mais plus dans son
        # environnement virtuel : on verifie donc aussi le .venv obtenu.
        tkinter_utilisable ".venv/bin/python" && break
        echo "  -> inutilisable dans un environnement virtuel, on essaie un autre Python."
        rm -rf .venv
    done
fi

[ -x ".venv/bin/python" ] || arreter_avec_erreur \
    "aucun Python avec une interface graphique utilisable (Tk 8.6+) n'a ete trouve.
          Installez Python depuis https://www.python.org/downloads/ puis relancez."

# Installer openpyxl seulement s'il manque.
if ! .venv/bin/python -c "import openpyxl" >/dev/null 2>&1; then
    echo "Installation des dependances..."
    .venv/bin/python -m pip install --quiet --disable-pip-version-check -r requirements.txt ||
        arreter_avec_erreur "l'installation des dependances a echoue."
fi

echo "Lancement..."
.venv/bin/python analyse_releve.py || arreter_avec_erreur "le programme s'est arrete anormalement."
