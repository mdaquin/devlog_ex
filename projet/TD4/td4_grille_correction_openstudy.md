# TD4 — OpenStudy — grille de correction (enseignant)

> **Ne pas distribuer.** Diagnostic récit par récit, trous à découvrir,
> priorisation attendue et carte des récits.

---

## 1. Diagnostic récit par récit

| ID | État | Critère INVEST en cause | Ce qu'on attend |
|---|---|---|---|
| US-01 | correct | — | référence : critères vérifiables, y compris le cas « questionnaire vide » |
| US-02 | correct | — | référence également |
| US-03 | **epic déguisé** | *Small*, *Testable* | ce n'est pas un récit mais tout le projet ; à découper **verticalement** (définir / collecter / scorer / exporter), pas par couche technique |
| US-04 | **« afin de » tautologique** | *Valuable* | le bénéfice ne remonte pas au métier ; il faut retourner demander pourquoi — probablement : vérifier que la collecte se passe bien, ou repérer des réponses aberrantes, ce qui donnerait deux récits très différents |
| US-05 | **solution technique déguisée en besoin** | *Negotiable*, *Valuable* | décision d'architecture, pas besoin utilisateur ; à sortir du backlog et à consigner dans un ADR une fois les vrais besoins connus. Noter aussi la source : un collègue extérieur, qui n'est pas une partie prenante de cette étude |
| US-06 | **non vérifiable** | *Testable* | « agréable » ne se teste pas — mais le « afin de » contient déjà la solution : le taux d'abandon, lui, se mesure. Bon exemple pour montrer que le bénéfice suggère souvent le critère |
| US-07 | **en conflit avec US-08** | — | voir §2 |
| US-08 | **en conflit avec US-07** | — | voir §2 |
| US-09 | **recouvre US-10** | *Independent* | même capacité (exporter des données de l'étude) demandée par deux personnes avec deux périmètres ; à fusionner en un récit paramétré, ou à délimiter explicitement |
| US-10 | **recouvre US-09** | *Independent* | idem |
| US-11 | **règle métier, pas un récit** | *Valuable* — « en tant que système » n'est pas une partie prenante | à sortir du backlog et à consigner dans les règles métier ou le glossaire ; elle contraint plusieurs récits au lieu d'en être un. Elle entre d'ailleurs en tension avec US-08 : comment garantir l'unicité sans identifier ? |
| US-12 | correct | — | le critère 3 reprend exactement le bogue silencieux de la séance 2 : une réponse manquante ne vaut pas 0 |
| US-13 | correct | — | le mot « complètes » est un indice du trou n° 3 (§3) |
| US-14 | correct | — | domaine authentique : l'exclusion motivée est une pratique standard en psychologie |
| US-15 | correct | — | crée une vraie tension de conception (versionnement du questionnaire) : ce n'est pas un défaut, c'est une discussion |

**Bilan :** six récits corrects, sept défauts distincts (dont deux paires),
trois trous (§3).

---

## 2. Le conflit US-07 / US-08

La chercheuse veut savoir nominativement qui n'a pas répondu ; les
participants veulent que leurs réponses ne soient rattachables à personne.
Les deux demandes sont légitimes, et incompatibles telles qu'elles sont
formulées.

**Ce qu'on attend :** que les étudiants remontent au *pourquoi* de chaque
demande au lieu d'arbitrer entre les deux formulations.

- Pourquoi la chercheuse veut-elle les noms ? Pour **atteindre la taille
  d'échantillon** — donc pour relancer. Pas pour savoir qui a répondu quoi.
- Pourquoi les participants refusent-ils ? Pour **répondre honnêtement à des
  questions intimes**. Pas pour échapper à la relance.

Les deux objectifs sont compatibles, et la solution réelle est connue : on
sépare la **liste des invités** (nominative, qui sert à relancer et qui
enregistre seulement « a répondu / n'a pas répondu ») des **réponses**
(pseudonymes, sans lien exploitable vers l'identité). La chercheuse peut
relancer ; personne ne peut relier une réponse à une personne.

C'est un excellent moment pour trois remarques : cette séparation est une
décision d'**architecture** qui découle directement d'un besoin non
fonctionnel, donc elle mérite un ADR ; elle relève aussi des **contraintes**
(RGPD, avis du comité d'éthique), donc elle n'est pas négociable ; et c'est
précisément ce que fait la fonction `anonymiser` écrite au TD1 — les étudiants
ont déjà implémenté un bout de la réponse sans en connaître la justification.

---

## 3. Les trous à découvrir

**Trou n° 1 — le consentement.** C'est le principal, et il devrait être trouvé
en premier par les étudiants de psychologie. Le contexte précise que le RGPD
s'applique et qu'aucune collecte ne peut démarrer sans avis du comité
d'éthique ; US-02, US-08 et US-14 manipulent des données personnelles. Et
**aucun récit ne traite du recueil et de la conservation du consentement
éclairé**, ni de son corollaire, le droit de retrait — qui implique de pouvoir
supprimer les données d'un participant.

C'est un cas d'école de besoin implicite : personne ne l'énonce parce qu'il va
de soi dans le métier. Il est de surcroît **non négociable**, donc il relève
autant de la contrainte que du besoin, et il doit se retrouver en *Must*.

**Trou n° 2 — les comptes et les droits.** Trois chercheurs, deux doctorants,
une assistante, plusieurs études en parallèle. US-08 demande explicitement une
restriction d'accès. Aucun récit ne dit qui se connecte, ni qui a le droit de
voir ou de modifier quelle étude.

**Trou n° 3 — les réponses partielles.** US-13 parle de réponses
« complètes », ce qui suppose qu'il en existe d'incomplètes ; US-06 évoque
l'abandon en cours de route ; US-12 traite le cas d'une réponse incomplète au
moment du score. Mais rien ne dit ce qu'on conserve d'un participant qui
commence et n'achève pas — ni si l'on peut reprendre plus tard.

---

## 4. Priorisation attendue (MoSCoW)

L'objectif métier est double : **réduire le délai entre la fin de la collecte
et les premiers résultats**, et **fiabiliser les scores**. Une justification
qui ne s'y rattache pas n'est pas une justification.

**Must** — la chaîne minimale qui permet de mener la première étude dans trois
mois, sans illégalité :
US-01 (définir), **le récit manquant de consentement**, US-02 (répondre),
US-12 (scorer). Le consentement n'est pas là par excès de prudence : sans lui,
la collecte est interdite, donc aucun autre récit n'a de valeur.

**Should** — US-09/US-10 fusionnés (l'export est la sortie attendue du
système), US-13 (savoir quand arrêter), US-14 (la qualité des données est la
moitié de l'objectif « fiabiliser »).

**Could** — la version résolue de US-07/US-08, US-15, le trou n° 2 (comptes)
si l'équipe reste à une étude pour commencer.

**Won't (pour cette version)** — US-06 reformulé en objectif de taux
d'abandon, mesurable une fois la première étude passée.

**Hors backlog** — US-03 (à découper), US-05 (ADR), US-11 (règle métier).

Une équipe qui place US-05 en *Must* parce que « c'est technique et
structurant » a manqué le point : ce n'est pas un besoin, et la décision ne
peut pas être prise avant de savoir combien d'études, combien de participants
et quelles contraintes d'hébergement.

---

## 5. Carte des récits — colonne vertébrale attendue

De gauche à droite, le parcours d'une étude :

```
  Préparer         Recruter et       Collecter        Nettoyer         Analyser
  l'étude          inviter           les réponses     les données      et publier
  ──────────       ──────────        ──────────       ──────────       ──────────
  US-01            US-07             [MANQUANT :      US-14            US-12
  US-15            US-08              consentement]   US-11 = règle    US-09/10
  [MANQUANT :      [MANQUANT :       US-02                             US-13
   comptes]         partielles]      US-04 ?                           
```

La colonne « collecter » est celle qui doit faire réagir : c'est là que se
place le consentement, qui est la toute première chose qu'un participant
rencontre dans un vrai questionnaire de recherche. Si une équipe ne le trouve
pas, la question « qu'est-ce que le participant voit en tout premier écran ? »
suffit généralement à le faire apparaître.

---

## 6. Indications de déroulement

Environ 20 minutes de lecture et de construction de la carte, 20 minutes de
diagnostic INVEST, 20 minutes de priorisation argumentée, le reste en mise en
commun — c'est en comparant deux cartes différentes que la discussion devient
intéressante.

Les étudiants de psychologie et de biologie ont ici un avantage réel sur les
informaticiens : le consentement, les critères d'inclusion, l'exclusion
motivée et le contrôle d'attention font partie de leur métier. C'est un bon
moment pour le dire explicitement — la connaissance du domaine est une
compétence de développement, et elle vient de se démontrer.

Si une équipe soumet le lot à une IA, c'est prévu par la règle du cours. Elle
trouvera la plupart des défauts de formulation et signalera probablement
l'absence de gestion des comptes. Le consentement est plus incertain : selon
la façon dont on la sollicite, elle le mentionne ou elle produit une liste
générique de fonctionnalités de plateforme de sondage. En revanche elle ne
priorisera pas en fonction de l'échéance de trois mois et de l'avis du comité
d'éthique, et elle ne tranchera pas le conflit US-07/US-08 autrement que par
un compromis vague. Le rendu doit permettre de voir où chaque équipe s'est
située.
