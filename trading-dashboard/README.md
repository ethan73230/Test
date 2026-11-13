# Tableau de bord investissement

Un site statique (GitHub Pages) qui affiche, pour une liste d'actions américaines :
cours, courbes sur 3 mois, configurations graphiques, actualités, plans de trade
(stop, objectif, simulation, taille, contrôle des risques), résultats trimestriels
et transactions déclarées au Congrès.

Les données viennent des 11 skills du pack
[day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill) (licence MIT,
Jake Schincariol), copiés dans `skills/`. Un workflow GitHub Actions les lance
automatiquement et écrit `data/dashboard.json`, que la page `index.html` affiche.

**Ce n'est pas un conseil financier.** Le site ne passe aucun ordre. Les cours
gratuits de Yahoo Finance sont non officiels et peuvent avoir du retard.

## Fonctionnement

Le workflow `.github/workflows/trading-dashboard.yml` tourne tout seul : une fois
avant l'ouverture, puis toutes les 15 minutes pendant la séance de New York, du
lundi au vendredi. Il analyse toutes les actions américaines, écrit
`data/dashboard.json`, puis copie la page dans la branche `gh-pages`
(dossier `trading-dashboard/` uniquement). Lancement manuel : onglet Actions >
« Tableau de bord trading » > Run workflow.

Le site est servi par GitHub Pages à l'adresse `<url-pages>/trading-dashboard/`.

## Personnaliser

- **Ma liste d'actions** : `trader/watchlist.txt`. La ligne `ALL` analyse tout le marché ; ajoute des tickers en dessous pour les afficher toujours.
- **Mes règles** (budget, perte max par trade, trades par jour, etc.) : `trader/config.json`, en dollars.
- **Résultats trimestriels et dépôts 8-K (SEC)** : la SEC demande de s'identifier.
  Ajoute un secret `SEC_USER_AGENT` (Settings > Secrets and variables > Actions)
  de la forme `Prénom Nom email@exemple.com`. Sans lui, ces deux parties sont
  simplement ignorées.

## Tester en local

```bash
python3 tools/build_data.py        # génère data/dashboard.json
python3 -m http.server 8000        # puis ouvrir http://localhost:8000
```

## Fichiers

```
index.html                    la page
data/dashboard.json           les données affichées (générées)
tools/build_data.py           lance les skills et rassemble leurs sorties
skills/trader-*/              les 11 skills (scripts Python + instructions)
trader/watchlist.txt          la liste d'actions
trader/config.json            les règles de risque
```
