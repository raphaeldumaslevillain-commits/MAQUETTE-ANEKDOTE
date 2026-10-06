# Audit des contenus — 6 octobre 2026

Source principale : https://www.anekdote.fr/. Le crawl a exploré les liens internes de navigation, les archives projets, les pages individuelles, le pied de page et les liens légaux. 57 URL ont été identifiées, dont une route Coaching renvoyant une erreur 404. Les 56 pages répondant contiennent notamment des doublons d’archives ; 33 projets distincts ont été extraits.

## Arborescence source et destination

| Source | Destination et traitement |
|---|---|
| `/` | Accueil composé autour des projets, résultats, expertises, culture et actualités |
| `/agence/` | Texte institutionnel, valeurs, origine du nom, photographies |
| Six pages d’expertises | URLs conservées ; nouvelle vue d’ensemble `/expertises/` |
| `/hub-projets/` et archives paginées | Portfolio filtrable réunissant les 33 projets ; anciennes archives redirigées |
| `/projets/{slug}/` | URL de chaque cas conservée, y compris le slug historique `__trashed` |
| `/equipe/` | Huit biographies, portraits et anecdotes conservés |
| `/talents/` | Citations exactes et texte du network, sans ajouter de profil ou de collaboration |
| `/newsroom/` | Six contenus conservés ; création de six URL d’articles pour permettre leur lecture individuelle |
| `/contact/` | Boissons, lieux et champs originaux, présentés en trois étapes |
| Pages légales | Texte source conservé |
| `/coaching/` : 404 | Redirection vers Performance / Affiliation, qui présente réellement le coaching Growth Marketing |

## Six expertises réellement publiées

Campagne d’influence, Stratégie, Évènements, Brand Content, RSE / Corporate, Performance / Affiliation. Le libellé « 5 services » de la source n’a pas été répété car six expertises ont chacune une page réelle.

## Équipe et Newsroom

Christelle, Tiffany, Emma, Emma, Pauline, Carla, Raphaël, Margaux : huit fiches, deux personnes distinctes nommées Emma. La page source conserve parfois des éléments d’image vides : aucune image manquante n’a été remplacée par un visage artificiel.

Newsroom : Masterclass Influence à l’EFAP d’Aix en Provence ; Forum des Entrepreneurs au Vélodrome ; Une nouvelle aventure pour Anekdote ! ; UMICC ; Anekdote x Vivatech ; Soirée JO Paris.

## Cas et preuves

La narration reprend les chapitres présents dans chaque source, généralement « Le contexte », « Notre proposition » et « Les résultats ». Aucun insight, date de campagne, témoignage ou résultat n’a été ajouté pour remplir un gabarit. Les valeurs et libellés de KPI ont été conservés, y compris leurs conventions de séparateurs originales.

Les cas TikTok Dyson, Choose et Oh My Cream partagent dans la source une série de quatre résultats de marques. Cette série est conservée dans chaque cas ; l’aperçu du portfolio sélectionne le KPI correspondant à la marque du projet afin d’éviter une attribution ambiguë.

Les 21 logos clients distincts de l’accueil proviennent de la source. La phrase « plus de 50 partenaires » est celle du site original et ne prétend pas que les 50 logos sont disponibles.

## CTA et médias

Navigation générale, liens expertises, accès aux projets, film de présentation, Instagram, LinkedIn, articles, liens ARPP / UMICC et contact. Les images, vidéos verticales, portraits spontanés et icônes de boissons / lieux ont été récupérés depuis les URL publiques auditées. Les coordonnées visibles de contact sont celles du rooftop : 4 rue Jules Lefebvre, Paris 75009.

`content/source-pages.json` conserve les informations de crawl ; `content/site-content.json` les textes structurés ; `content/source-html/` les snapshots de lecture ; `docs/routes.json` la correspondance des nouvelles pages et de leurs URL source.

## Anomalies conservées ou documentées

Certains titres et contenus historiques comportent des graphies irrégulières. Ils n’ont pas été remplacés par des informations non vérifiées. Le siège enregistré figurant dans les mentions légales diffère de l’adresse de rendez-vous. La page légale contient également des références techniques historiques et un libellé d’email incomplet. Ces points nécessitent une validation éditoriale et légale de l’agence lors du passage en production.
