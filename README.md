# Tracker de sorties (ARPG et MMO)

- `index.html` : la page (aucune dépendance, sauf les polices Google).
- `data/events.json` : les sorties, à éditer à la main quand une date est annoncée.
- `scripts/update.py` : récupère les dernières annonces (flux Steam, Wowhead) et régénère `data.js`.
- `.github/workflows/update.yml` : lance le script chaque jour à 6 h UTC et publie le résultat.

## Mise en ligne
1. Créer un dépôt GitHub et y envoyer tous ces fichiers.
2. Settings → Pages → Source : « Deploy from a branch », branche `main`, dossier `/ (root)`.
3. Onglet Actions : lancer une fois « Mise à jour quotidienne » (Run workflow). Ensuite c'est automatique.

## Ajouter un jeu ou une source
- Dans `FEEDS` (`scripts/update.py`) : ajouter l'ID Steam du jeu ou un flux RSS officiel (Aion 2 est vide).
- Dans `data/events.json` : ajouter une ligne ; `precision` = `day`, `month`, `year` ou `none`, `status` = `confirmed`, `estimated`, `tba` ou `released`.

Les annonces trouvées par le script sont affichées avec les dates repérées dans leur titre ; c'est à toi de les reporter dans `events.json` après vérification.
