# ADR-001 : séparation des interfaces de gestion et de réponse

## Statut

Accepté

## Contexte

OpenStudy permet à deux types d'utilisateurs d'interagir avec les questionnaires :

- les membres de l'équipe de recherche, qui créent et gèrent les questionnaires et analysent les réponses ;
- les participants, qui répondent aux questionnaires.

Ces deux usages n'ont pas les mêmes contraintes :

- l'interface de gestion n'a pas besoin d'être utilisable sur mobile ;
- l'interface de réponse doit l'être, car les participants peuvent répondre depuis un téléphone.

Nous voulons par ailleurs nous assurer que les deux interfaces sont bien isolées l'une de l'autre.

## Décision

Nous construisons deux interfaces web distinctes :

- une **interface web de gestion et d'analyse**, destinée à l'équipe de recherche ;
- une **interface web mobile de réponse**, destinée aux participants.

Les deux sont développées en HTML/JS, mais peuvent utiliser des technologies et des styles différents.

**Alternative écartée :** une interface web unique couvrant les deux usages. Elle aurait obligé à rendre l'ensemble utilisable sur mobile alors que seule la partie réponse l'exige. Elle aurait aussi rendu l'isolation entre les deux usages plus difficile à garantir.

## Conséquences

**Ce que ça nous facilite :**

- Chaque interface peut avoir ses propres choix techniques et son propre style, adaptés à son public.
- L'interface de gestion n'est pas contrainte par les exigences du mobile.
- L'isolation entre les deux interfaces est assurée par construction.

**Ce que ça nous coûte :**

- Deux interfaces à développer, tester et maintenir au lieu d'une.
- Un risque d'incohérence visuelle ou fonctionnelle entre les deux, à surveiller.
- Les deux interfaces s'appuient sur un serveur commun (voir ADR-002) : l'isolation concerne donc l'interface, pas la couche serveur.
