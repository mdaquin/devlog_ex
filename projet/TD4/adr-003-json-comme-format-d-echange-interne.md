# ADR-003 : JSON comme format d'échange interne

## Statut

Accepté

## Contexte

Les interfaces web et le serveur doivent échanger des informations. Ces échanges portent à la fois sur les définitions des questionnaires et sur les réponses des participants.

Le serveur est développé en Python.

## Décision

Nous utilisons **JSON** comme format de communication des informations en interne, entre les interfaces et le serveur.

Les définitions de questionnaires et les réponses sont toutes deux représentées par des objets JSON. Une réponse est donc elle-même un objet JSON de type « questionnaire rempli », ce qui permet de traiter les deux avec le même format.

**Alternatives écartées :** Les échanges aux formats CSV et Excel, habituellement utilisé par les chercheurs. XML pouvait aussi être considéré mais est plus lourd que JSON.

## Conséquences

**Ce que ça nous facilite :**

- JSON est pratique à traiter en Python.
- Un seul format pour les définitions de questionnaires et pour les réponses, ce qui simplifie les échanges et le code qui les traite.
- Format natif côté navigateur, donc simple à utiliser dans les interfaces HTML/JS.

**Ce que ça nous coûte :**

- Il faudra définir et maintenir la structure des objets JSON (le schéma d'un questionnaire et celui d'une réponse), sinon le format risque de dériver.
- Si le volume de données grandit, JSON n'est pas le format le plus compact. [À compléter : à discuter si c'est un enjeu.]
