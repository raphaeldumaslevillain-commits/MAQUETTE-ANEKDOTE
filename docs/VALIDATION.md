# Vérification des 76 annotations

## Contenus et structure

58 fichiers HTML, dont neuf redirections historiques. Le contrôle vérifie H1, métadonnées, langue, données structurées, liens locaux et textes alternatifs. Les 33 études de cas et leurs KPI sont comparés aux sources. Les biographies, anecdotes et goûts des sept personnes affichées restent complets. Le retrait demandé de Pauline et des sections sous l’approche des expertises constitue des exceptions explicites et ciblées. Les snapshots originaux sont archivés. Voir static-validation.json.

## Navigateur

Douze pages ont été contrôlées à 390 et 1457 px : accueil, agence, expertises, équipe, portfolio, Contact et les six détails d’expertise. Aucun débordement de page ni image chargée en échec n’a été relevé. Les descriptions visées commencent au même bord gauche que leur titre. Le bandeau de pied de page est absent partout.

Les 33 études de cas ont été contrôlées à 390 px : chiffres contenus dans leur zone, valeurs de chaque ligne alignées et lien Projet suivant présent. Le portfolio a été contrôlé intégralement sur ordinateur et mobile : chaque valeur et son libellé partent du bord gauche de leur cellule ; les lignes de valeurs et de libellés sont communes, sans débordement. Les filtres et préfixes numériques des catégories sont retirés.

Les six profils sont vérifiés à 375, 390, 768, 1168 et 1920 px : photo carrée, texte de même hauteur, aucun débordement de page. Noms, flèches, compte dynamique, navigation clavier et affichage des goûts sont fonctionnels. Le menu se ferme et son bouton a une bordure de 0 px.

Le manifeste change sans action de l’utilisateur ; aucune commande n’y reste. Son titre et son panneau partagent le même bord supérieur. La temporisation de trois secondes, la frappe de 460 ms, les arrêts hors écran / onglet masqué et le repli en mouvement réduit sont vérifiés dans le script. À 1457 px, Coaching en Growth Marketing et la phrase des mesures Solar Metrics tiennent chacun sur une ligne ; Coaching tient aussi sur une ligne à 390 px. Les indicateurs sont sans contour et centrés.

Le parcours Contact a été suivi jusqu’à la troisième étape après sélection Espresso / Rooftop. Le récapitulatif reste correct et le bouton Envoyer est présent. Aucun formulaire n’a été envoyé. Aucune erreur JavaScript n’a été relevée dans les contrôles de cette révision.

Les observations sont dans round4-browser-checks.json. Le rapport round3-browser-checks.json reste un historique de la révision précédente. Les neuf aperçus sont actualisés dans previews/ ; les transitions ont été figées uniquement pendant les captures, puis la feuille finale a été restaurée.

## Livraison

Aucun score Lighthouse ni certification d’accessibilité n’est revendiqué. Les deux projets sans résultats publiés sont signalés, sans KPI fictif. Le code, médias et polices sont autonomes. Le workflow vérifie et prépare GitHub Pages ; l’activation du service dans le dépôt reste nécessaire. Un build réussi ne confirme pas une publication.

## Complément : accordéon d’accueil sans numéros

Les six index sont absents du DOM à 390 et 1456 px. Les six titres et les descriptions commencent sur le même bord gauche (20 px sur mobile, 61,15 px sur ordinateur), sans débordement horizontal. Les six liens restent présents. L’ouverture de Stratégie referme la première expertise. Voir round5-browser-checks.json et previews/accueil-expertises-desktop.jpg.

## Thèmes clair et sombre

Les deux palettes et le contrôle soleil/lune sont vérifiés dans le navigateur. Le thème sombre persiste au rechargement et lors de la navigation. Le contrôle conserve son nom accessible, expose son état, fonctionne avec Entrée et Espace et garde le focus. L’en-tête est vérifié à 320, 375, 390, 768, 1050, 1150, 1280 et 1456 px, sans débordement ; le bouton mesure au moins 44 × 44 px. À 320 px, une adaptation conserve l’espace entre le logo et les commandes.

Les fonds et textes des sections Agence, du manifeste, du menu, du portfolio, de Solar Metrics et du pied de page sont vérifiés. Le parcours Contact arrive jusqu’aux champs de la troisième étape, avec choix et textes lisibles, sans envoi. Les photographies chargées gardent leurs couleurs ou leur noir et blanc existant. Aucune erreur JavaScript n’a été observée. Voir theme-browser-checks.json et previews/themes-clair-sombre.jpg.

Le contraste calculé est de 15,71:1 pour le texte principal sombre et de 8,66:1 pour le texte secondaire. Les neuf contrôles de scripts/check_theme.cjs passent : préférence enregistrée, préférence système et changement du système, priorité du choix manuel, mouvement réduit, stockage indisponible, repli sans transition de vue, animation et clics répétés, récupération après transition interrompue et synchronisation entre onglets. Les scénarios de repli sont testés dans un environnement simulé ; la transition circulaire et sa fin sont observées dans le navigateur local.

La validation du site reste sans erreur sur 58 fichiers HTML, 33 projets et sept personnes. Les aperçus de l’accueil sont actualisés ; les captures de cette révision utilisent les styles et mouvements livrés.

Référence d’implémentation : [transition de vue MDN](https://developer.mozilla.org/en-US/docs/Web/API/Document/startViewTransition).

## Carrousel compact et deux nouvelles personnes

Les huit profils sont vérifiés à 1456 × 790, 1280 × 660, 390 × 844, 375 × 667 et 768 × 1024 px, soit 40 observations. Chaque carrousel tient dans la hauteur disponible sous l’en-tête, sans débordement horizontal de page. Les photos chargent toutes et restent carrées ; les sept profils inactifs sont masqués et inertes. Sur ordinateur à 1456 × 790, toutes les biographies tiennent dans leur panneau sans défilement. Sur mobile, les longues biographies peuvent défiler dans la zone de texte ; celle de Louise tient entièrement à 390 × 844.

Les goûts de Louana et Louise sont comparés aux contenus transmis, et leur affichage au clavier est vérifié. Les flèches bouclent correctement entre Louise et Tiffany et le compte indique huit personnes. Les neuf personnes publiques, avec Christelle, passent la vérification des contenus.

Les deux accordéons comportent six lignes et aucune ligne ouverte au chargement ; après rechargement de l’accueil, ils restent fermés. L’ouverture de Stratégie ferme Campagne d’influence. Le curseur du thème parcourt 66 px sur ordinateur et 20 px à 390 px, avec un bouton de 44 px de hauteur. À 320 px, le bouton mesure 60 px de largeur et l’en-tête conserve un espace entre le logo et les commandes.

Les neuf tests du thème restent valides et le contrôle statique ne relève aucune erreur sur 58 fichiers HTML et 33 projets. Aucune erreur JavaScript n’a été observée. Voir compact-team-browser-checks.json et les aperçus equipe-louana-desktop.jpg, equipe-louise-desktop.jpg et equipe-louise-mobile.jpg.
