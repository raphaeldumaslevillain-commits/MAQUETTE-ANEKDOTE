# Révision des 30 annotations — 6 octobre 2026

Toutes les annotations s’appliquent aux composants et styles de la source, aux différents formats d’écran. Aucune donnée temporaire du navigateur n’est copiée dans le site.

| Annotations | Modification |
|---|---|
| 1, 2 | Liens Agence et Film retirés du grand visuel d’accueil. |
| 3, 16 | Bouton Pause retiré. Logos constamment monochromes ; aucun changement de couleur ni pause au survol. Les deux bandes continuent en sens opposés. |
| 4 | Photo d’équipe d’accueil en noir et blanc. |
| 5, 6, 7 | Liens Rencontrer l’équipe, Notre histoire et Découvrir nos projets retirés des sections indiquées. |
| 8–13, 23 | Descriptions des six expertises et du portfolio alignées sur le bord gauche des titres. |
| 14 | Solar Metrics entièrement recomposé : titre éditorial, orbite animée, quatre expertises en lignes et six indicateurs de mesure. Les contenus publiés restent complets. |
| 15 | Ancienne grande infographie Solar Metrics retirée. |
| 17, 24 | Baselines indiquées retirées des pages Agence et Expertises. |
| 18 | Une seule flèche pour parcourir les trois chapitres institutionnels. Frappe très rapide à chaque changement, 460 ms ; texte intégral stable pour les lecteurs d’écran. |
| 19, 20 | Grand guillemet retiré ; signature Christelle, Co-Founder en Instrument Serif, Georgia, serif. |
| 21, 22 | Deux liens de sortie de la page Agence retirés. |
| 25, 26, 27 | Coins arrondis sur la photo Expertises, la photo Agence et le grand visuel d’accueil. |
| 28, 29, 30 | Trois KPI d’accueil orange, y compris au survol. |

## Équipe

Christelle est présentée indépendamment du carrousel, avec sa biographie complète, son anecdote et son vrai visuel des deux mantras, tous consultables sans ouverture ni bouton. Sa photo est carrée, monochrome, arrondie et accompagnée d’une ombre légère.

Les sept autres personnes partagent un carrousel manuel. Chaque slide contient un portrait carré, un nom et un seul paragraphe réunissant la biographie et l’anecdote réelles. Les goûts apparaissent sur le portrait au survol, avec une alternative au focus, au clavier et au toucher. Aucun bouton Anecdote ou Goûts ne s’ajoute à la composition. Les flèches, noms indexés et gestes horizontaux permettent de changer de personne ; les deux Emma restent distinguées par leur position.

Les hauteurs de la photo et du texte dépendent de la largeur du carrousel, via les unités de conteneur CSS, pour rester identiques même dans les grands formats. À 800 px et moins, les deux éléments passent l’un sous l’autre. Le paragraphe peut défiler dans son bloc sur les petits écrans : aucun texte n’est coupé ni supprimé, et le corps reste à 16 px minimum. Les préférences publiées sont conservées exactement, y compris les deux seuls éléments connus dans les dislikes de Carla.

## Projets

Les 33 réalisations suivent la même composition : image monochrome révélée en couleur au survol ou au focus, titre, paragraphe source, KPI et ouverture de l’étude de cas. Les filtres sont conservés. Les études de cas gardent tous leurs contenus et le lien Projet suivant ; leurs chiffres s’animent à l’apparition pendant 720 ms et finissent dans leur format publié exact, unités comprises.

Deux projets n’ont pas de résultats chiffrés dans les sources : @skincarebysamy x Yves Rocher et L’Oréal Luxe x My Origines. Leur zone de résultats indique cette absence ; aucun chiffre n’est inventé. Les autres valeurs, dont les signes +, décimales, K, M, %, € et espaces, restent exactes.

## Mouvement et direction

UI/UX Pro Max accompagne la révision. La direction conserve Inter, Instrument Serif, crème, noir et orange. Révélations progressives, légère profondeur des grands visuels, transitions de page natives, flèches et liens animés, orbite Solar Metrics et carrousels souples utilisent des effets CSS / JS locaux. Les photos de l’équipe et les logos ne reçoivent pas de mouvement décoratif au survol. Aucune dépendance tierce n’est ajoutée.

Les carrousels n’avancent pas automatiquement. Les effets respectent le mouvement réduit ; les bandes s’arrêtent hors de l’écran ou lorsque la page est masquée. Le texte reste accessible sans JavaScript. Le formulaire Contact et son script sont inchangés. La Newsroom reste retirée, et l’adresse Anekdote est toujours 29 rue de Mogador, 75009 Paris.
