# ADR-002 : serveur unique pour les deux interfaces

## Statut

Accepté

## Contexte

Suite à la séparation des interfaces de gestion et de réponse (ADR-001), il faut décider si la partie serveur est elle aussi séparée.

Les deux interfaces s'appuient sur des éléments communs, en particulier la définition des questionnaires : l'équipe de recherche la crée et la modifie, et les participants en ont besoin pour afficher le questionnaire auquel ils répondent.

## Décision

Nous utilisons un **seul système de gestion (serveur)**, partagé par les deux interfaces. Il s'appuie sur une base de données unique.

**Alternative écartée :** deux serveurs séparés, un par interface, comme pour le front. Cela aurait obligé à dupliquer les éléments communs, en particulier la définition des questionnaires, ce qui est inefficace.

## Conséquences

**Ce que ça nous facilite :**

- Une seule définition des questionnaires, sans duplication ni risque de désynchronisation.
- Un seul serveur à développer, déployer et maintenir.

**Ce que ça nous coûte :**

- Les deux interfaces dépendent du même serveur : une panne ou une régression côté serveur touche à la fois la gestion et la réponse.
- L'isolation entre gestion et réponse (voulue en ADR-001) n'est pas assurée au niveau serveur : il faudra la garantir autrement, par exemple par le contrôle des accès.
- Le serveur doit servir deux publics aux besoins différents (équipe de recherche et participants).
