# retours sur les rendus du TD1

## Le code 

 1. J'ai eu des rendu qui n'incluaient que le fichier que je vous avez donné à la base. Erreurs ? (E0450)
 2. Un des messages principaux du cours précédent est qu'il faut spécifier avant de produire ! (voir point 2 ci-dessous)
 3. La specification était dans la docstring pour anonymiser. Je m'attendait à ce que vous fassier la même chose pour les autres fonctions (et certainnement pas que vous l'enleviez). 
 4. Certain code étaient incomplet (dans verif par exemple E7630)
 5. Un truc auquel vous auriez dû/pu penser : si le nom du participant est en majuscule, est-ce que la fonction anonyser fonctionne vraiment ? 
 6. Le nom du fichier n'aurait pas dû être changé. 

## Les traces d'IA

 1. J'en ai demandé, donc il faut les rendre. Si vous n'en avez pas rendu parce que vous n'avez pas utilisé l'IA, mentionnez le quelque part. (E0450, E1613)
 2. Un meilleur prompt est un prompt précis. Un prompt précis inclus la spécification. Je l'avais donnée pour anonymiser, c'est idiot de ne pas s'en servir. 
 3. Ca veut dire aussi que vous devez SPECIFIER. C'est le point le plus important, sinon vous laissez les non-dits à l'IA. Ce qui est produit n'est pas ce vous voulez, et vous ne le maitrisez pas. 
 4. L'IA produit, et vous vérifiez ! Copier l'énoncé suivit de copier-coller n'est pas du développement, c'est un appel à se faire remplacer et de nombreux problèmes pour la suite. 
 5. J'avais demander d'être précis (nom de l'outils d'IA, et modèle (donc Claude Sonnet 5 élevé, pas juste Claude))
 6. S'il y a des exemples, les mettre dans le prompt. L'IA ne peut pas devinner à quoi va ressembler le JSON, donc ça fait partie de la specification, mais un exemple fonctionner très bien pour le faire. (E5230) 
 7. Beaucoup de système d'IA vont faire plus que ce que vous leur demandez. Forcer les à faire exactement ce que vous demandez, ou coupez ce qu'ils ajoute. 

## Un mauvais exemple :

E9520 : "Pour choix_multiple, la clé "inversé" du dict questions n'est pas réutilisée dans
le calcul : je pars du principe que les valeurs de réponses_possibles encodent déjà
l'inversion (ce que suggère ton exemple, où q2 et q4 ont des pondérations différentes
pour les mêmes lettres). Si en réalité tu veux que la fonction applique elle-même 1 -
score quand inversé=True sur un choix multiple, dis-le-moi et j'ajuste." --> rien...

## Un autre mauvais exemple 

E7321: "Plus important, pour générer un identifiant à 4 chiffres Claude a pris la liberté de
réduire l’intervalle de randint à (1000,9999), bien que techniquement correct cela est
sous-optimal. Par design on s’attend à pouvoir générer les 10000 combinaisons entre
“0000” et “9999”. Pour conserver le format à 4 chiffres tout en permettant toutes les
combinaisons, on converti la clé de integer à string. Par soucis de clareté on distingue
et renomme également la variable “identifiant_unique” en “identifiantint” et _“identifiant_str”

Que l'identifiant doit être à 4 chiffres n'étaient pas dans la spécification. Il aurait était plus judicieux d'ajouter dans la spécification un choix explicite et regénérer, plutôt que de se focaliser sur une optimisation qui en plus est mauvaise. 
