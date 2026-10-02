# Dressmaker — guide de style de la traduction française

Ce guide rassemble les décisions qui encadrent la traduction française non officielle de *Dressmaker*. Il sert de référence pour corriger ou compléter la traduction de façon cohérente.

Il ne reproduit aucun texte du jeu : les termes anglais cités ci-dessous sont du vocabulaire courant (couture, interface), pas des répliques.

## 1. Décisions de fond

| Sujet | Décision |
|---|---|
| Personnage joué | Au féminin : « la Couturière ». Hors récit (interface, tutoriel), tournures épicènes quand c'est possible (« quand vous le souhaitez » plutôt que « quand vous serez prête »). |
| Adresse à la joueuse | Vouvoiement partout. En apostrophe : « Couturière », avec majuscule. |
| Clientes | Au féminin. |
| Registre | Époque Régence : vouvoiement entre tous les personnages, tournures soignées, sans archaïsme lourd. |
| Noms propres | Conservés : villes, royaume, noms et prénoms. Exception : les noms construits sur un jeu de mots peuvent être adaptés (voir § 6). |
| Titres et civilités | « Lady » et « Miss » conservés ; « Mr » → « M. » ; « Mrs » et « Ms » → « Mme » ; duchesse, duc, princesse, reine en minuscules dans le texte (« le duc Hassan »), « Votre Altesse » en apostrophe. |
| Ton par type de texte | Interface : court, infinitif ou nom. Tutoriel : impératif, chaleureux. Dialogues : la voix de chaque personnage (§ 2). Chroniques du journal : précieux, ironique, phrases longues. |

## 2. Voix des personnages

- **Alice** : douce, timide, gothique. Ses deux esprits ont leur propre voix : **Kroq**, démon, parle EN MAJUSCULES et **tutoie tout le monde** (seule exception au vouvoiement : il est brut) ; **Selafie la Vertueuse**, en italique, vouvoie et s'exprime avec emphase.
- **Dorothy** : commère attendrissante, parle au nom de ses pigeons. Vouvoie la couturière (« ma mignonne », « ma chère »), tutoie ses pigeons.
- **Edith** : ancienne diva, chaleureuse. Vouvoie, mais couvre la couturière de petits noms gourmands : mon chou, ma brioche, ma madeleine, ma dragée, ma citrouille, mon ange, ma chérie, ma douce, ma toute belle.
- **Fiona** : fermière ambitieuse, pince-sans-rire, jargon d'entreprise employé avec aplomb (et parfois de travers).
- **Marie** : diplomate ironique et déterminée.
- **Priya** : peintre, piquante, sujette à des explosions (« AHHH ! »).
- **Prudence** : snob grandiloquente, ridicule et touchante.
- **Vivian** : séductrice menaçante ; appelle la couturière « mon agneau », tutoie le chat.
- **Chroniques du journal** : une chroniqueuse anonyme qui parle d'elle-même à l'impersonnel (« on », « l'on ») et s'adresse à « notre lectrice ». Récit au passé simple, commentaires au présent.

## 3. Règles techniques (bloquantes, contrôlées par `check_translations.py`)

- **Balises** (`<i>`, `<b>`, `<style=c1>`, `<size=60%>`, `<shake>`, `<wave>`, etc.) : jamais modifiées, jamais ajoutées. On peut les déplacer dans la phrase. Pour mettre un mot en valeur sans balise, utiliser des guillemets.
- **Variables** (`{0}`, `{1:0.00}`, `{0:F2}`, `{0:list:{}|, }`…) : jamais modifiées, déplaçables. Tourner la phrase pour éviter les accords et élisions impossibles : « Utiliser : {0} » plutôt que « Utiliser le {0} ».
- **Valeurs insérées par le jeu** : dans les chroniques, le jeu insère le nom de la couleur ou du type de tissu le plus utilisé, **en minuscules**. Formulations sans accord : « une robe couleur {0} », « sa robe de {1}, couleur {0} », « d'un {0} des plus scandaleux ».
- **Sauts de ligne** et préfixe technique `QuestGiver:` : conservés à l'identique.
- **Deux-points dans les dialogues** : le moteur de dialogue (Yarn Spinner) lit « Nom: texte » comme « personnage : réplique » et efface tout ce qui précède le premier deux-points non échappé. Dans les répliques, tout deux-points de phrase s'écrit donc `\:`, précédé d'une espace insécable. `merge_batch.py` le fait automatiquement. Ne s'applique pas aux résumés de quête ni aux vers du poème de Marie, lus hors de Yarn.
- **Images** : la collection Images contient des références d'images, pas du texte. Ces images (titre du journal, affiches, logo, enseigne) restent en anglais.

## 4. Typographie

- Espace insécable (U+00A0) avant `: ; ! ? %`, à l'intérieur des guillemets « », et entre un nombre et son unité (« 2,4 m »). `merge_batch.py` la pose : écrire avec une espace normale.
- Apostrophe typographique ’ (conversion automatique).
- Guillemets français « ».
- Points de suspension : caractère « … » dans les dialogues et les chroniques, comme le texte d'origine. Dans l'interface et le tutoriel, trois points « ... », car le caractère « … » manque dans certaines polices de l'interface.
- **Jamais de tiret cadratin « — » à l'anglaise** : c'est un calque qui trahit la traduction automatique. Selon le sens : parole interrompue → « … » ; incise ou explication → deux-points, virgule, parenthèses ou deux phrases.
- « œ » s'écrit normalement dans la base de traduction. Les polices du jeu n'ont pas ce caractère : le plugin l'affiche « oe ».
- Décimales : le jeu affiche la virgule française.
- Plus généralement : éviter tout calque de syntaxe ou de ponctuation anglaise ; écrire ce qu'écrirait un traducteur français.
- Dans le tutoriel, les noms de boutons et d'onglets cités prennent la majuscule et reprennent exactement le libellé (« le bouton Coudre »).

## 5. Longueur des textes d'interface

- Règle : **aucun risque de débordement**. Un libellé trop long est raccourci d'office, sans attendre de le voir déborder.
- Repère : ne pas dépasser le libellé anglais le plus long de la même famille d'écrans. `check_translations.py` signale tout libellé d'interface à plus de 130 % de l'anglais.
- Quand c'est possible, préférer un mot plus court au terme exact plutôt qu'une abréviation (« Valider » plutôt que « Appliq. »).

## 6. Jeux de mots, références et noms à sens

Principes (chaque cas est décidé un par un) :

- **Garder le mécanisme du gag**, pas les mots : un calembour devient un calembour français sur le même thème (couture, oiseaux, légumes, pâtisserie…), même si le sens change.
- **Pas de paroles de chanson recopiées.** Quand l'anglais cite une chanson ou un poème, on cherche une référence française récente et populaire, glissée sous forme de phrase ordinaire, crédible dans la bouche d'un personnage d'époque (exemples retenus : Indila, « Dernière danse » ; Sinsemilia, « Tout le bonheur du monde », retourné en malédiction).
- **Références que le public français ne reconnaîtrait pas** : remplacées par un équivalent connu en France (exemple : un bouc de conte anglais devient Blanquette, la chèvre de monsieur Seguin). Quand la version française d'une œuvre utilise déjà les mêmes noms (Shrek), la référence est gardée telle quelle.
- **Mots inventés** : rendus par des mots inventés français (« épouseuses », « Ourlitude », « embuissonné »).
- **Lieux portant un nom de tissu** : adaptés quand un nom de tissu français fonctionne (Tulle, Chambray, Charmeuse) ; Twillford et Hemstitch restent en anglais.
- **Noms à sens** : adaptés quand le sens fait le gag (Adora Dédufil, le chat Pompon, Bouton-d'or) ; sinon conservés.

## 7. Glossaire

### Couture et métier

| Anglais | Français |
|---|---|
| dressmaker | couturière |
| dress / gown | robe |
| commission | commande |
| client | cliente |
| off the rack dress | robe de prêt-à-porter (court : prêt-à-porter) |
| fabric / swatch | tissu / échantillon |
| haberdashery | mercerie |
| pattern / pattern piece | patron / pièce de patron |
| draft / undraft | tracer le patron / annuler le tracé |
| cut / sew | couper / coudre |
| grain line / cross grain / bias | droit-fil / travers / biais |
| roll (of fabric) | rouleau |
| measuring tape | mètre ruban |
| measurements | mensurations (personne) / mesures (action) |
| bust / waist / hips | poitrine / taille / hanches (« tour de poitrine ») |
| mannequin / knobs | mannequin / molettes |
| sketchbook | carnet de croquis (court : carnet) |
| design | modèle |
| cutting room / front desk | salle de coupe / comptoir |
| trim / lace trim | galon / galon de dentelle |
| labour / materials | main-d'œuvre / matériaux |
| prestige / rank | prestige / rang |
| knighthood | adoubement ; Chevalière du Royaume |

### Vêtements, tissus, accessoires

- Pièces : corsage, jupe, manche, col, poignet ; devant / dos.
- Types de tissu : coton, lin, soie, velours, laine, dentelle, sequins, jute (toile de jute).
- Accessoires : appliqué, grelot, nœud, broche, bouton, plume, fleur, joyau, pompon, galon.
- Noms de tissus : matière + motif + couleur (« Coton Liberty fleuri orange »). Imprimé, dégradé, chatoyant, dévoré, frappé, perlé, brocart, cachemire (motif), tartan, pied-de-poule, à pois, à fines rayures, vichy.
- Noms de patrons : « Corsage / Jupe / Manche / Col » + qualificatif. Cache-cœur, jupe portefeuille, col Claudine, lavallière, manche gigot, mancheron, basque, tournure, étagé, volanté, corps, empiècement, col américain, bandeau.
- Pièces de patron, en style d'étiquette : [vêtement] [pièce] [n°] [position] ; lé, patte, boutonnage, laçage, emmanchure, jupon, surjupe.

### Étiquettes de style

Au masculin singulier (forme neutre d'étiquette) : décontracté, cool, mignon, de jour, éclectique, recherché, élégant, de soirée, fleuri, habillé, chaud, glamour, gothique, à motifs, espiègle, professionnel, osé, romantique, chatoyant, simple, inconfortable, de travail.

### Rangs

Inconnue, novice, apprentie, compagnonne, respectée, professionnelle, renommée, vénérée, illustre, maîtresse, créatrice.

## 8. Noms du monde (à réutiliser tels quels)

- **Lieux et événements** : Twillford, Hemstitch, Tulle (et sa filature), Chambray, Charmeuse ; la Fête du printemps, le Bal d'été, le concours de la Journée sportive des dames, le gala de l'Opéra, la foire du marché, le concours annuel des animaux de Twillford, la soirée d'observation des étoiles, le labyrinthe de haies.
- **Personnages et animaux** : Pompon (le chat de la couturière), Adora Dédufil (Addy), Sophie Vasar, princesse de Hemstitch ; Kroq, Selafie la Vertueuse ; Berty, Judy, Monty (les pigeons de Dorothy) ; Bouton-d'or (le chat d'Edith) ; Alphonse (Alfie), le bœuf de Fiona ; Blanquette, la chèvre de l'héritage ; le duc Hassan ; M. Dervisham.
- **Œuvres citées** : *La Maison de velours et de soie*, *Fard et Fripons*, *Entre les lunes*, *Chaos en haute mer*, *Passions courtoises*, *Neige sur Ashbanks*, *La Revanche des crustacés tueurs*, *Le Vagabond des étendues blanches*, *Que se lèvent les couchants* ; la *Gazette de Twillford*.
- **Boutons de commande** : « Accepter la commande » / « Retoucher la commande ».

## 9. Erreurs du texte d'origine

On ne corrige une erreur de l'anglais que si les fichiers du jeu la prouvent (par exemple un nom de tissu qui contredit la couleur réelle du matériau). L'entrée est alors marquée d'un champ `correction` dans `translations_fr.json`, avec la raison et la preuve. `check_translations.py` signale toute correction dont l'anglais a changé depuis (les développeurs l'ont peut-être corrigée).
