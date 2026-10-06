# Editorial × Human × Proof

L’accueil présente d’abord Anekdote, puis ses six expertises, ses partenaires et son équipe. La preuve apparaît ensuite avec les trois résultats réels. Les études de cas disposent de leur portfolio et de leurs pages dédiées.

Inter structure les informations, les citations de l’agence et les chiffres. Instrument Serif porte certains titres et invitations. Le crème, le noir et l’orange #FF471F restent les repères de marque. Le vrai logo apparaît dans le header et, à grande échelle et en gris discret, dans le footer. Les partenaires ARPP / UMICC y prennent davantage de place.

L’agence réunit histoire, raison d’être et engagements dans un deck de trois chapitres. Le manifeste dispose de six slides, chacune reprenant son titre et son paragraphe source. Les commandes visibles, la navigation au clavier et des transitions courtes permettent d’explorer ces contenus sans une longue succession verticale. Ces decks ne tournent pas automatiquement.

Les expertises utilisent un accordéon natif, des descriptions lisibles et des liens directs. Le nouveau visuel vient de l’activation Soskin à Cannes. Les talents associent un vrai portrait à trois principes stratégiques, puis un deck de cinq témoignages publiés.

Les biographies et photos de l’équipe occupent la même hauteur. Les biographies longues sont réparties en pages lisibles, sans couper les textes ni ajouter une zone de défilement interne. Le bouton « Une Anekdote » remplace la biographie. Les préférences sont présentées par des cœurs et cœurs barrés sur la photo, avec un accès au toucher et au clavier. Seules les préférences effectivement publiées sont utilisées : Carla a deux éléments « Je n’aime pas », et aucune liste n’est inventée pour Christelle.

Les deux bandeaux de marques défilent en sens opposés. Une commande permet de les arrêter ou de les reprendre ; le survol des logos et le focus mettent le mouvement en pause. Les chiffres comptent rapidement à leur première apparition, puis gardent les valeurs et formats exacts. Les lecteurs d’écran accèdent aux chiffres finaux, sans annonce de chaque image de l’animation.

Les labels suivent la nomenclature `02 • NOS EXPERTISES`. La Newsroom est supprimée. Le contact conserve exactement son formulaire et ses interactions ; seuls les éléments globaux et l’adresse changent.

Les mouvements utilisent principalement transformation et opacité. Ils respectent `prefers-reduced-motion`. Une feuille de repli rend les contenus complets consultables sans JavaScript. Aucune librairie d’animation, scène 3D ou image générée n’est ajoutée.

Le benchmark initial [Woo](https://www.woo.paris/) et [BETC](https://www.betc.com/fr/) a fourni des principes de rythme et de composition, sans reprise de leur identité. Cette révision suit la demande du client et les règles pertinentes d’UI/UX Pro Max : lisibilité, priorité du contenu, navigation clavier, alternatives au survol, contrôle des contenus animés et stabilité des mises en page.


## Révision des annotations et du motion

La présente révision prend le pas sur les dispositions antérieures concernant les portraits, la grille des projets, les contrôles de logos et la navigation institutionnelle. Coins photo : token --photo-radius, 24 px desktop et 20 px à 800 px ou moins. Ombre : --portrait-shadow, légère et commune à tous les portraits. Le carrousel Équipe utilise la largeur de son propre conteneur pour fixer un carré et un texte de même hauteur. Le contenu débordant reste lisible par défilement, avec un corps de 16 px minimum.

La baseline est alignée à gauche seulement pour .service-intro et .portfolio-intro ; cette annotation ne modifie pas le formulaire Contact ni les autres baselines. La signature serif est limitée à la citation Agence. Les logos restent en niveaux de gris sous la souris ; les images projet révèlent leurs couleurs. Christelle dispose d’une composition indépendante et complète.

Frappe institutionnelle 460 ms, compteurs 720 ms, changements de carrousel 320–420 ms, révélations environ 650 ms. Les grands visuels ont un déplacement vertical borné à 14 px, suivi uniquement quand ils sont visibles. L’orbite Solar Metrics est décorative et s’arrête en mouvement réduit. Les préférences restent sans animation autonome.
