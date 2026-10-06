# Mise en ligne sur GitHub Pages

Le site complet et ses médias sont présents dans le dépôt MAQUETTE-ANEKDOTE. La construction et les contrôles des pages ont réussi dans GitHub Actions. L’activation initiale de Pages est un réglage du dépôt accessible au propriétaire connecté.

1. Ouvrir [Settings → Pages](https://github.com/raphaeldumaslevillain-commits/MAQUETTE-ANEKDOTE/settings/pages).
2. Dans **Build and deployment → Source**, choisir **GitHub Actions**.
3. Ouvrir le workflow [Validate and publish Anekdote](https://github.com/raphaeldumaslevillain-commits/MAQUETTE-ANEKDOTE/actions/workflows/pages.yml) et lancer **Run workflow → main** si aucune nouvelle exécution n’est démarrée.
4. Attendre la réussite du job `deploy`, puis ouvrir l’URL indiquée par GitHub.

L’adresse attendue après activation est `https://raphaeldumaslevillain-commits.github.io/MAQUETTE-ANEKDOTE/`. Elle ne doit pas être considérée comme publiée tant que le déploiement n’a pas réussi et que sa réponse HTTP n’a pas été vérifiée.

Les prochaines modifications sur `main` sont vérifiées et publiées automatiquement. Le dossier public produit ne contient que les pages, styles, scripts, médias et fichiers SEO. Les snapshots de source, scripts de maintenance et documents restent dans le dépôt, hors du dossier publié.
