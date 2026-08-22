"""Gestion des depenses : version avec persistance dans une base SQLite.

Les modules sont organises en couches, du plus interne au plus externe :

    modeles       les donnees (Operation, Releve, StatistiquesMois)
    base          la base de donnees SQLite et tout le SQL
    importation   la lecture des fichiers Excel
    statistiques  l'assemblage des chiffres a afficher
    interface     la fenetre Tkinter

Chaque couche ne connait que celles du dessus dans cette liste : l'interface
appelle les statistiques, jamais l'inverse.
"""

__all__ = ["base", "importation", "interface", "modeles", "statistiques"]
