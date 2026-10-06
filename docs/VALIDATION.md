# Vérification de la révision des annotations

## Sources et structure

58 fichiers HTML : 49 pages principales et neuf redirections historiques. Contrôle du H1, des métadonnées, de la langue, des données structurées, des liens locaux et des textes alternatifs. Les paragraphes / KPI des 33 projets, les biographies / anecdotes / goûts des huit personnes et les contenus institutionnels sont comparés aux sources. La suppression explicite de la baseline Agence est une exception ciblée. Aucun autre paragraphe source n’est omis. Voir static-validation.json.

## Navigateur

Onze pages contrôlées à 390 et 1168 px : accueil, agence, expertises, équipe, portfolio et les six expertises détaillées. Les sept descriptions visées ont exactement le même bord gauche que leur titre. Aucun débordement horizontal ni image chargée en échec détecté ; aucune erreur JavaScript remontée dans ces contrôles.

Les 33 études de cas ont aussi été contrôlées à 390 px : aucun chiffre animé plus large que sa zone et aucun débordement de page ; Projet suivant existe sur chaque cas. Le filtre Évènements affiche neuf projets et ouvre l’étude de cas sélectionnée. Les KPI ont été observés en progression puis dans leur format final.

Les sept portraits et blocs de texte ont des hauteurs identiques ; les photos sont carrées à 375, 390, 768, 1168 et 1920 px. Les textes longs défilent sur mobile sans réduire le corps. Navigation par noms, flèches et clavier, révélation des goûts, fermeture du menu et flèche institutionnelle vérifiées. La frappe se termine puis retire son clone visuel. Les slides inactifs portent aria-hidden et inert dans le navigateur ; leurs contenus restent disponibles au repli sans script.

Les logos ont été contrôlés sous la souris : filtre grayscale(1) conservé, deux animations toujours running. Les suppressions demandées ne laissent aucun ancien bouton dans les sections concernées. Les trois KPI d’accueil utilisent rgb(255, 71, 31). La signature de la citation utilise Instrument Serif et les images ciblées ont un rayon de 24 px à 1168 px, 20 px sur mobile.

Les résultats et relevés sont archivés dans round3-browser-checks.json. Les captures de la nouvelle composition sont dans previews/.

## Limites et livraison

Les règles de mouvement réduit et le repli sans script sont contrôlés dans le code ; aucune certification d’accessibilité ni score Lighthouse n’est revendiqué. Les 27 vidéos et le script Contact sont inchangés ; leur validation précédente reste applicable. Aucun formulaire n’a été envoyé.

Les données manquantes de deux projets sont signalées, sans résultats fictifs. Le code, les médias et les polices sont autonomes, avec un workflow de vérification et de préparation GitHub Pages. L’activation de Pages dans GitHub reste nécessaire : un build réussi ne confirme pas une publication.
