# Vérifications de la livraison

## Contenus et structure

La validation de `scripts/check_site.py` contrôle les 65 fichiers HTML de la livraison : un seul H1 par page principale, langue française, titre et description, JSON-LD valide, présence des images alternatives et existence des liens internes et médias. Les redirections historiques sont identifiées séparément.

Elle compare chaque paragraphe et chaque liste des 33 études de cas avec l’extraction source, puis vérifie les valeurs et libellés de KPI. Elle contrôle aussi les biographies, anecdotes des huit personnes, paragraphes des six articles et textes institutionnels, expertises, talents et pages légales. Les caractères invisibles de direction de texte sont ignorés pour la comparaison. Résultat : aucune erreur. Voir `static-validation.json`.

Les 27 vidéos ont été contrôlées : première image décodable et index MP4 placé avant les données pour le démarrage rapide (`video-validation.json`).

La syntaxe des cinq fichiers JavaScript est contrôlée avec Node. Le site ne charge aucune librairie JavaScript tierce.

## Vérifications dans le navigateur

Accueil : composition vérifiée en 1440 px et 390 px. Agence, équipe, expertises, Newsroom, cas GHD et Biocyte : contrôlés en 390 px, sans débordement horizontal ni image chargée en échec. Le portfolio a été testé avec le filtre Performance / Affiliation : deux projets réels, compteur et URL cohérents. Le menu s’ouvre, se ferme avec Échap et restaure le focus. Le formulaire conserve « Espresso / Rooftop » jusqu’à la troisième étape.

Les captures desktop et mobile accompagnent la livraison. Les contrôles de dimensions figurent dans `responsive-checks.json`.

## Accessibilité

HTML sémantique, navigation et champs nommés, états de filtres `aria-pressed`, statut de formulaire annoncé, lien d’évitement, contrôles vidéo natifs, focus visible, fenêtre de navigation native et prise en compte de `prefers-reduced-motion`. Les contenus restent visibles sans JavaScript ; les animations ne sont pas un préalable à leur consultation.

Ces vérifications ne constituent pas une certification RGAA. Aucun audit automatisé externe Lighthouse ou axe n’a été exécuté ; aucun score de performance ou de conformité n’est prétendu.

## Performance

187 médias principaux utilisés passent de 350,89 Mo de fichiers source à environ 96,32 Mo après optimisation, soit environ 72 % de réduction. Cette somme représente tout le portfolio, pas le poids d’une page visitée. Les variantes responsive, posters, polices et textes complètent le dépôt.

Les images ont des dimensions déclarées, une source responsive lorsque nécessaire et un chargement différé, sauf les visuels d’entrée. Les vidéos utilisent `preload="none"`, une affiche locale et une lecture volontaire. Le showreel est injecté seulement à l’ouverture de son lecteur. La compression de la longue vidéo Aroma-Zone ramène son fichier à environ 24,66 Mo. Les polices locales utilisent `font-display: swap` et des sous-ensembles latin / latin étendu.

## Limites à valider avant remplacement de la production

- L’envoi et la réception effectifs du formulaire n’ont pas été testés : aucun message n’a été expédié. Le serveur original a été vérifié en lecture et via OPTIONS / CORS. La réussite n’est affichée qu’après une réponse `mail_sent`.
- Les mentions légales sont les textes historiques ; l’adresse de siège et les références au prestataire / hébergeur doivent être revues pour la nouvelle mise en production.
- PP Editorial New Italic n’a pas été redistribuée sans licence web ; Instrument Serif est l’alternative libre utilisée dans cette version.
- GitHub Pages fournit un site statique. Le formulaire dépend du serveur Anekdote existant pour l’envoi, sans dépendance au Drive.
