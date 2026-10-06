# Vérifications de la révision

## Structure et fidélité

58 fichiers HTML, dont 49 pages principales et 9 redirections historiques. Le contrôle vérifie un H1, les métadonnées, la langue, les données structurées, les textes alternatifs et les liens / médias locaux. Les 33 études de cas, leurs paragraphes et KPI, les biographies / anecdotes des huit personnes et les textes des expertises, de l’agence, des talents et des pages légales sont comparés aux sources. Les préférences restent dans la page, sur les portraits. Les corrections explicites de l’adresse et de l’attribution sont documentées.

La Newsroom ne génère plus de pages, ne figure dans aucun lien public ni dans le sitemap. Résultat : aucune erreur dans `static-validation.json`.

## Navigateur

Sept pages principales ont été contrôlées à 375, 768, 1024 et 1440 px : accueil, agence, expertises, équipe, talents, contact et portfolio. Aucun débordement horizontal ni image en échec détecté dans ces vues. Les hauteurs des portraits et des textes sont identiques ; les biographies et les anecdotes tiennent dans les zones prévues, y compris à 375 px. Voir `responsive-checks.json`.

Navigation des decks Agence et Manifeste, ouverture de Brand Content dans l’accordéon, remplacement biographie / anecdote, préférences sur portrait, pause / reprise des bandeaux et fermeture du menu avec Échap vérifiés. Les compteurs ont été observés pendant leur progression puis à leurs valeurs finales exactes. Le formulaire Contact est strictement identique à la version précédente ; son script est inchangé. Aucun message n’a été envoyé.

La syntaxe des six fichiers JavaScript est valide. Les 27 vidéos sont inchangées ; la validation précédente de leur première image et de l’index MP4 reste applicable.

## Accessibilité et performance

Commandes visibles de carrousel, focus, états ARIA, slides inactifs retirés de la navigation clavier, accordéon natif, contrôle du mouvement des logos, chiffres finaux disponibles aux lecteurs d’écran. Les règles de mouvement réduit ont été vérifiées dans le code ; aucune émulation système ni certification RGAA n’est revendiquée. Le repli sans JavaScript rend les contenus consultables.

169 médias principaux utilisés, environ 362.72 Mo avant optimisation et 99.76 Mo après optimisation. Ce total représente l’ensemble du portfolio. Images responsive, dimensions réservées, vidéos chargées volontairement et polices locales sont conservées. Aucune dépendance JavaScript tierce n’est ajoutée. Aucun score Lighthouse n’est prétendu.

## Livraison et hébergement

Le dépôt contient tous les médias utilisés et le workflow GitHub Pages. L’activation du service Pages reste nécessaire dans les paramètres GitHub ; une validation du code ne confirme pas une publication. Le formulaire dépend du serveur Anekdote existant pour son envoi, sans dépendance au Drive. Les références historiques aux prestataires dans les textes légaux restent à adapter lors du remplacement de la production.
