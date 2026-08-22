# Gestion des dépenses — programme simple

Petit programme qui lit un relevé de compte mensuel au format Excel et affiche
quelques statistiques : total des revenus, total des dépenses, solde du mois et
les 3 plus grosses dépenses.

## Contenu

| Fichier | Rôle |
| --- | --- |
| `analyse_releve.py` | Le programme : interface Tkinter + calcul des statistiques |
| `generer_exemple.py` | Génère un relevé factice pour tester |
| `releve_mai_2026.xlsx` | Relevé d'exemple déjà généré (39 opérations) |
| `requirements.txt` | La seule dépendance externe : `openpyxl` |
| `analyse.command` | Lanceur double-clic pour macOS |
| `analyse.bat` | Lanceur double-clic pour Windows |

## Lancement par double-clic (le plus simple)

- **macOS** : double-cliquer sur `analyse.command`
- **Windows** : double-cliquer sur `analyse.bat`

Le lanceur cherche Python, crée l'environnement virtuel `.venv`, installe
`openpyxl` puis démarre le programme. La première exécution prend quelques
secondes (installation) ; les suivantes sont immédiates.

Sur macOS, il n'accepte qu'un Python capable d'ouvrir une vraie fenêtre avec
**Tk 8.6 ou plus**. Le Python fourni par Apple (`/usr/bin/python3`) n'a que
Tk 8.5 : l'apparence des fenêtres est datée et l'affichage ne se rafraîchit pas
toujours après une boîte de dialogue. Si un `.venv` a été construit avec un
Python inadapté, le lanceur le détecte et le reconstruit tout seul.

Deux points à connaître :

- Sur macOS, le fichier doit rester **exécutable** (`chmod +x analyse.command`
  si besoin, par exemple après un téléchargement en `.zip`). Si macOS refuse de
  l'ouvrir, faire un clic droit → *Ouvrir* la première fois.
- Sur macOS toujours, une fenêtre Terminal reste ouverte derrière le programme :
  c'est normal, elle affiche les messages d'erreur éventuels et se referme
  quand on quitte le programme.

## Installation manuelle (en ligne de commande)

Tkinter est fourni avec Python. Seule la lecture des fichiers Excel demande une
bibliothèque supplémentaire :

```bash
python -m venv .venv
source .venv/bin/activate    # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python analyse_releve.py
```

## Utilisation

Une fenêtre s'ouvre : cliquer sur « Choisir un relevé Excel... », sélectionner
le fichier, les statistiques s'affichent.

Pour régénérer (ou personnaliser) le relevé d'exemple :

```bash
python generer_exemple.py releve_mai_2026.xlsx
```

## Format attendu du fichier Excel

Une ligne d'en-tête, puis une ligne par opération :

| Date | Libelle | Categorie | Montant |
| --- | --- | --- | --- |
| 02/05/2026 | Loyer appartement | Logement | -780.00 |
| 25/05/2026 | Salaire mai | Salaire | 2450.00 |

Les **dépenses sont négatives**, les **revenus positifs**. Les lignes dont le
montant n'est pas un nombre sont ignorées.
