import sys

if len(sys.argv) != 3:
    print("Usage: python traite_reponses.py <chemin_vers_reponses.csv/xlsx> <chemin_vers_questions.json>")
    sys.exit(1)

fichier_reponses = sys.argv[1]
fichier_questions = sys.argv[2]

# traiter les fichiers (en faisan les vérifications et calculs nécessaires)
# sauvegarder les résultats (anonymisation et score) dans un nouveau fichier XLSX
