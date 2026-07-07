# Paper Trading (simulation)

Portefeuille virtuel automatisé — **aucun argent réel, aucun courtier connecté**.
Un bot tourne chaque jour de bourse via GitHub Actions, évalue le watchlist avec
une stratégie breakout/momentum, et simule des achats/ventes. Le tableau de
bord (`index.html`) affiche le résultat.

## Mise en route

1. **Clé API Twelve Data (gratuite)** : créer un compte sur https://twelvedata.com,
   récupérer la clé API, puis l'ajouter comme secret du repo :
   `Settings → Secrets and variables → Actions → New repository secret`,
   nom `TWELVE_DATA_API_KEY`.
2. **Activer GitHub Pages** (optionnel, pour voir le tableau de bord en ligne) :
   `Settings → Pages → Deploy from a branch → main /(root)`. Le dashboard sera
   accessible sur `<url-pages>/paper-trading/`.
3. Le workflow `.github/workflows/paper-trading-bot.yml` se déclenche chaque
   jour de semaine, ou manuellement via l'onglet Actions → "Run workflow".
   **Le déclenchement automatique (`schedule`) ne fonctionne que sur la
   branche par défaut** — il faut merger cette branche sur `main` pour que
   le cron s'active.

## Paramètres (`config.json`)

- `watchlist` : tickers suivis.
- `starting_cash` : capital virtuel de départ (200 € par défaut — les cours viennent
  de Twelve Data en dollars US, traités ici comme équivalent 1:1 pour simplifier).
- `max_positions` / `position_size_pct` : nombre de positions simultanées et
  taille de chacune (% du cash).
- `take_profit_pct` / `stop_loss_pct` : seuils de sortie.
- `max_hold_days` : sortie forcée après ce nombre de jours de bourse (15 ≈ 3
  semaines), pour coller à un horizon court.
- `atr_volatility_min_pct` : volatilité minimale (ATR/prix) exigée à l'achat.
- `breakout_lookback` / `rsi_overbought` : réglages du signal d'entrée.

## Limites à garder en tête

- C'est une simulation à but éducatif : aucune stratégie ne garantit un gain,
  et les performances passées ne préjugent pas des futures.
- Le tier gratuit Twelve Data limite le débit (8 requêtes/minute, 800/jour) ;
  réduire `watchlist` si le job échoue pour rate-limit.
