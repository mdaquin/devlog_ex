# OpenStudy — user stories

> **Statut : brut.** Ces stories ont été recueillis lors d'entretiens avec les
> différentes parties prenantes, puis recopiés tels quels. Ils n'ont pas encore
> été analysés : rien ne garantit qu'ils soient tous bien formulés, ni qu'ils
> soient cohérents entre eux, ni qu'ils couvrent tout ce qui est nécessaire.

---

## Contexte

**L'organisation.** Une équipe de recherche en psychologie : trois
enseignants-chercheurs, deux doctorants, un assistant de recherche à mi-temps.
L'équipe mène deux à quatre études par an, chacune reposant sur un
questionnaire rempli par des participants recrutés à l'université ou en ligne.

**La situation actuelle.** Chaque étude est montée de zéro avec l'outil qui
tombe sous la main — formulaire en ligne gratuit, tableur partagé, parfois
questionnaire papier. Les réponses sont ensuite exportées, recopiées,
nettoyées et scorées à la main dans un tableur, avec une formule différente
par étude. Entre la fin de la collecte et les premiers résultats exploitables,
il s'écoule deux à trois semaines. Des erreurs de barème ont déjà été
découvertes après soumission d'un article.

**Objectif métier.** Réduire le délai entre la fin de la collecte et les
premiers résultats, et fiabiliser les scores — c'est-à-dire ne plus recalculer
à la main.

**Parties prenantes.**

| Qui | Rôle |
|---|---|
| Claire Fontaine | chercheuse, responsable d'étude — conçoit le questionnaire, analyse |
| Yanis Redouane | doctorant — monte les études, suit la collecte |
| Nadia Sorel | assistante de recherche — nettoie les données, vérifie les scores |
| Les participants | répondent aux questionnaires |
| Le comité d'éthique de l'université | rend un avis avant toute collecte |
| La déléguée à la protection des données | contrôle la conformité RGPD |

**Contraintes connues.** Les réponses contiennent des données personnelles :
le RGPD s'applique. Aucune collecte ne peut démarrer sans avis favorable du
comité d'éthique. L'hébergement doit se faire sur les serveurs de
l'université. Aucun budget pour des licences. La première étude prévue — sur
le sommeil et le bien-être — doit démarrer dans trois mois.

---

## Les user stories

### US-01 — Définir un questionnaire

**En tant que** chercheuse,
**je veux** définir les questions de mon étude, leur type et leur barème,
**afin de** collecter des réponses comparables d'un participant à l'autre.

*Critères d'acceptation*
1. Étant donné une question numérique, alors je peux fixer l'intervalle de
   valeurs acceptées.
2. Étant donné une question à choix, alors je peux définir les réponses
   possibles et le score associé à chacune.
3. Étant donné une question, alors je peux lui donner une pondération.
4. Étant donné un questionnaire sans aucune question, alors il ne peut pas
   être ouvert à la collecte.

*Demandé par : Claire Fontaine*

---

### US-02 — Répondre au questionnaire

**En tant que** participant,
**je veux** répondre au questionnaire depuis mon téléphone ou mon ordinateur,
**afin de** participer sans avoir à me déplacer au laboratoire.

*Critères d'acceptation*
1. Étant donné une question obligatoire laissée vide, quand je valide, alors
   le système m'indique ce qui manque et n'enregistre pas la réponse.
2. Étant donné un questionnaire complété, quand je valide, alors une
   confirmation m'est affichée.

*Demandé par : Yanis Redouane, d'après les retours des participants*

---

### US-03 — Gérer mes études

**En tant que** chercheuse,
**je veux** gérer mes études de bout en bout,
**afin que** la recherche avance.

*Critères d'acceptation*
1. Les études sont gérées.

*Demandé par : Claire Fontaine*

---

### US-04 — Consulter les réponses

**En tant que** chercheuse,
**je veux** voir les réponses reçues,
**afin de** pouvoir consulter les réponses reçues.

*Critères d'acceptation*
1. Les réponses s'affichent.

*Demandé par : Claire Fontaine*

---

### US-05 — Une API REST

**En tant que** développeur,
**je veux** que le système expose une API REST en JSON,
**afin que** l'architecture soit moderne et évolutive.

*Critères d'acceptation*
1. L'API est en REST.

*Demandé par : un collègue d'un autre laboratoire, consulté informellement*

---

### US-06 — Un questionnaire agréable

**En tant que** participant,
**je veux** un questionnaire clair et agréable,
**afin de** ne pas l'abandonner en cours de route.

*Critères d'acceptation*
1. Le questionnaire est agréable.

*Demandé par : Yanis Redouane*

---

### US-07 — Relancer les participants qui n'ont pas répondu

**En tant que** chercheuse,
**je veux** savoir lesquels des participants invités n'ont pas encore répondu,
**afin de** les relancer et d'atteindre la taille d'échantillon prévue.

*Critères d'acceptation*
1. Étant donné une étude en cours, quand je consulte le suivi, alors j'obtiens
   la liste nominative des invités n'ayant pas encore répondu.

*Demandé par : Claire Fontaine*

---

### US-08 — Réponses non rattachables à mon identité

**En tant que** participant,
**je veux** que mes réponses ne puissent pas être rattachées à mon identité,
**afin de** répondre honnêtement à des questions personnelles sur mon sommeil
et mon état psychologique.

*Critères d'acceptation*
1. Étant donné une réponse enregistrée, quand quelqu'un consulte les données
   de l'étude, alors il ne peut pas savoir de quelle personne elle provient.

*Demandé par : plusieurs participants d'une étude précédente, et relayé par la
déléguée à la protection des données*

---

### US-09 — Exporter les données pour l'analyse

**En tant que** chercheuse,
**je veux** exporter l'ensemble des réponses et des scores au format CSV,
**afin de** conduire mes analyses statistiques dans R.

*Critères d'acceptation*
1. Étant donné une étude, quand je demande l'export, alors j'obtiens un
   fichier contenant une ligne par participant, avec ses réponses et ses
   scores.

*Demandé par : Claire Fontaine*

---

### US-10 — Télécharger le tableau des scores

**En tant qu'** assistante de recherche,
**je veux** télécharger un tableau des scores calculés par participant,
**afin de** faire mes vérifications dans un tableur.

*Critères d'acceptation*
1. Étant donné une étude, quand je demande le tableau, alors j'obtiens un
   fichier tableur des scores par participant.

*Demandé par : Nadia Sorel*

---

### US-11 — Une seule réponse par participant

**En tant que** système,
**je veux** qu'un participant ne puisse répondre qu'une seule fois à une étude
donnée,
**afin d'** éviter les doublons dans l'échantillon.

*Critères d'acceptation*
1. Un participant a au plus une réponse par étude.

*Demandé par : Nadia Sorel*

---

### US-12 — Calculer les scores automatiquement

**En tant que** chercheuse,
**je veux** que le score de chaque participant soit calculé automatiquement
selon le barème défini dans le questionnaire,
**afin de** ne plus refaire les calculs à la main et de ne plus me tromper de
formule.

*Critères d'acceptation*
1. Étant donné un questionnaire comportant des items inversés, alors le score
   en tient compte.
2. Étant donné des questions pondérées, alors le score reflète les
   pondérations.
3. Étant donné une réponse incomplète, alors le score n'est pas calculé et la
   raison est indiquée — il ne vaut pas 0.

*Demandé par : Claire Fontaine*

---

### US-13 — Suivre l'avancement de la collecte

**En tant que** doctorant,
**je veux** voir combien de réponses complètes ont été reçues et à quelle
date,
**afin de** décider quand arrêter la collecte.

*Critères d'acceptation*
1. Étant donné une étude en cours, quand je consulte le suivi, alors j'obtiens
   le nombre de réponses complètes et leur répartition dans le temps.

*Demandé par : Yanis Redouane*

---

### US-14 — Exclure une réponse de l'analyse

**En tant qu'** assistante de recherche,
**je veux** marquer une réponse comme exclue en indiquant un motif (échec au
contrôle d'attention, participant hors critères d'inclusion),
**afin que** les analyses ne portent que sur les données exploitables.

*Critères d'acceptation*
1. Étant donné une réponse exclue, alors elle n'entre pas dans les scores
   agrégés, mais elle reste conservée.
2. Étant donné un export, alors le motif d'exclusion et le nombre de réponses
   exclues y figurent.

*Demandé par : Nadia Sorel*

---

### US-15 — Corriger une question après le début de la collecte

**En tant que** chercheuse,
**je veux** corriger la formulation d'une question après l'ouverture de
l'étude,
**afin de** rattraper une ambiguïté signalée par les premiers participants.

*Critères d'acceptation*
1. Étant donné une question corrigée, alors les réponses déjà collectées sont
   conservées.
2. Étant donné un export, alors on peut savoir quelle version du questionnaire
   chaque participant a vue.

*Demandé par : Claire Fontaine*
