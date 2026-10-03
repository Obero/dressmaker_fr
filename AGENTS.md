# AGENTS.md — Dressmaker, traduction française

Consignes pour les agents de code (et les humains) qui travaillent sur ce dépôt. À lire en entier avant toute action. La langue de travail est le français.

## Le projet

Traduction française non officielle du jeu **Dressmaker** (Cozy Lives / Free Lives, Steam, Unity 6 / Mono). Le jeu n'a pas de français officiel. La traduction est livrée sous forme de plugin BepInEx 5 qui n'altère aucun fichier du jeu.

But du propriétaire (Obero) : rendre le travail du studio accessible au public francophone et le mettre en valeur. Le projet sera retiré si le studio annonce une traduction française officielle. C'est un travail d'amateur, transparent sur l'usage de l'IA (voir le README).

## Règle absolue : ne jamais publier de texte anglais du jeu

Les textes originaux appartiennent aux développeurs. Ils sont extraits **localement** depuis la copie du jeu de chacun, et ne doivent jamais entrer dans le dépôt, une release, une issue ou un message public.

- Le `.gitignore` est une **liste blanche** : tout est ignoré sauf les fichiers nommés. N'y ajouter un fichier qu'après avoir vérifié qu'il ne contient aucune phrase du jeu en anglais.
- Fichiers de travail locaux, jamais publiés, rangés dans `local/` (créé par les outils) : `dressmaker_strings_en.json/.csv` (export anglais), `dialogue_order.json`, `dialogue_script.txt` (script anglais + français), les lots de traduction, tout guide ou note qui cite l'anglais.
- Dans les textes publics (README, guide, notes de `translation/translations_fr.json`) : du vocabulaire courant à la rigueur, jamais de réplique ni de nom propre anglais du jeu.
- Ne pas nommer d'outil d'IA précis dans les textes publics (choix du propriétaire).

## Architecture

- **Textes du jeu** : tables Unity Localization, collections `UI`, `Tutorial`, `Content`, `Dialogue`, `Images` (les `Images` sont des références d'images, pas du texte ; les images restent en anglais).
- **Dialogues** : Yarn Spinner v3, programme compilé dans le jeu. Chaque quête a ses nœuds `_Prompt` (demande), `_Complete` (réussite), `_Failed` (échec), `_Excelled` (textes de remplissage des développeurs, non traduits). Les résumés de quête (`line:<Quête>_Summary`) et quelques clés (`line:marie_poem_*`, `line:marie_tag_*`) sont lus hors de Yarn. Le locuteur n'est pas dans le texte : il se déduit des commandes `set_portrait_*`.
- **`translation/translations_fr.json`** : la base de traduction (seule source de vérité du français). Une entrée par identifiant de chaîne : `collection`, `key`, `fr`, `src` (empreinte SHA-1 de l'anglais d'origine), `status`, `note`, et parfois `correction`.
- **`plugin/`** : plugin BepInEx (C#, netstandard2.1). Ajoute la locale `fr`, construit les tables françaises à la volée depuis les tables anglaises avec repli sur l'anglais pour tout texte non traduit, garde le drapeau *smart string*, recopie les références d'images (avec le nom de sous-image `guid[nom]`). Lit `fr.tsv` à côté de la DLL. Options dans `BepInEx/config/fr.dressmaker.localization.cfg`.
- **Outils** (`tools/`, Python 3, `pip install UnityPy` pour l'extraction). Ils se lancent depuis n'importe quel dossier (chemins communs dans `tools/paths.py`) :
  - `extract_dressmaker_strings.py --game <dossier du jeu>` → `local/dressmaker_strings_en.json`.
  - `extract_dialogue_order.py --game <dossier du jeu>` → `local/dialogue_order.json`.
  - `make_dialogue_script.py [--node Préfixe]` → `local/dialogue_script.txt`, script lisible anglais + français.
  - `merge_batch.py <collection> lot.tsv` : fusionne un lot `clé<TAB>texte` (ou `id:<n>` pour une chaîne sans clé) ; convertit ' en ’, pose les espaces insécables, échappe les deux-points des répliques.
  - `check_translations.py` : contrôle.
  - `yarn_colons.py [--check]` : corrige les deux-points non échappés déjà en base.
  - `export_fr_table.py` : génère `plugin/fr.tsv`, le fichier lu par le plugin.

## Méthode de travail

1. Extraire l'anglais localement, puis, pour une quête ou un personnage, produire le script lisible avec `python tools/make_dialogue_script.py --node <Préfixe>`.
2. Écrire un lot TSV (`clé<TAB>texte`), dans `local/lots/`. Écrire les fichiers avec un éditeur ou un outil d'écriture de fichier : les heredocs de shell sous Windows abîment les barres obliques inverses.
3. Avant de fusionner, vérifier que chaque clé du lot appartient bien aux nœuds visés et qu'aucune ne manque : une clé mal recopiée écraserait silencieusement la réplique d'un autre personnage.
4. `merge_batch.py`, puis `check_translations.py` lancé avec `PYTHONIOENCODING=utf-8` (sinon la console Windows plante en affichant une erreur et l'erreur passe inaperçue), puis `export_fr_table.py`, puis `dotnet build plugin -c Release -p:GameDir=<dossier du jeu>` (copie la DLL et `fr.tsv` dans le jeu).
5. Rendre compte au propriétaire en listant **chaque** jeu de mots ou adaptation : la scène, le sens du passage, la proposition française, une recommandation. Le propriétaire tranche ; ne rien considérer comme validé sans son accord.

## Règles de traduction

Le guide public `docs/guide_de_style.md` fait référence (voix des personnages, typographie, glossaire, noms du monde). Points bloquants :

- Ne jamais modifier ni ajouter de balises (`<i>`, `<size=…>`, `<shake>`…) ni de variables (`{0}`, `{1:0.00}`…). Pour une mise en valeur sans balise : des guillemets.
- **Deux-points dans les répliques Yarn** : tout « : » non échappé fait disparaître ce qui le précède (Yarn le prend pour un nom de personnage). Écrire `\:`, précédé d'une espace insécable. Exceptions : le préfixe technique `QuestGiver:`, un « : » initial présent dans l'original, les clés lues hors de Yarn.
- **Valeurs insérées par le jeu** (couleur, type de tissu dans les chroniques) : arrivent en minuscules ; tourner la phrase pour éviter tout accord (« une robe couleur {0} »).
- Typographie française : espace insécable avant `: ; ! ? %` et dans « », apostrophe ’, **jamais de tiret cadratin** à l'anglaise, « œ » écrit normalement (affiché « oe » par le plugin, faute de glyphe dans les polices).
- Pas de tics de traduction automatique : calques de syntaxe ou de ponctuation anglaises, tournures littérales.
- Jeux de mots et références : garder le mécanisme du gag ; pas de paroles de chanson recopiées ; préférer une référence française récente et populaire, glissée en phrase ordinaire crédible à l'époque.
- Erreurs du texte d'origine : corriger seulement si les fichiers du jeu le prouvent, et le tracer dans le champ `correction`.

## Préférences du propriétaire

- **Aucun risque de débordement** dans l'interface : raccourcir d'office, sans attendre de le voir en jeu. Repère : ne pas dépasser le libellé anglais le plus long de la même famille de clés.
- Coller à ce qu'on voit à l'écran **et** garder le patch simple à mettre à jour.
- Toujours distinguer les faits vérifiés des estimations et suppositions.
- Vérifier en ligne les informations susceptibles d'avoir changé (versions d'outils, etc.).
- Les commits sont faits par le propriétaire lui-même.

## Tester en jeu sans tout rejouer

- Activer `[Debug] ModeTest = true` dans la configuration du plugin (désactivé par défaut, et dans les releases). Au comptoir de la boutique : **F7** ouvre le menu de choix d'une quête, **F8** celui d'une chronique du journal. Au mannequin : **F10** / **F11** terminent la robe en réussite / échec. Ce sont les menus de triche des développeurs, réservés à l'éditeur Unity dans le jeu d'origine ; le plugin les ouvre directement.
- Une chronique ouverte sans avoir fait la robe correspondante affiche des trous à la place des couleurs : normal.
- Le mode test modifie la sauvegarde : tester sur un emplacement de sauvegarde à part, après une copie de sauvegarde.
- **Ne jamais utiliser Ctrl+Maj+A** (débloque tous les succès Steam) **ni Ctrl+Maj+R** (les réinitialise) : raccourcis de développement actifs quand les triches du jeu sont activées.
- Journal du plugin : `<dossier du jeu>/BepInEx/LogOutput.log`.

## État (version 1.0.0)

- Version du jeu traduite : `410.44874e6` (affichée en bas à droite de l'écran titre, datée du 24/09/2026 ; build Steam 25508059). Après une mise à jour du jeu : réextraire l'anglais, lancer `check_translations.py` (chaînes nouvelles et « obsolètes » = anglais modifié), traduire, puis mettre à jour cette ligne, le README et le LISEZMOI de la release.

- Traduits : interface, tutoriel, contenu (noms), tous les dialogues des personnages, les chroniques, les résumés de quête. Vérifié en jeu sur les écrans et passages délicats.
- Volontairement non traduits : le contenu de l'ancienne démo (quêtes `*Demo`, `ExampleQuest`, `Quest0`), les textes de remplissage des développeurs (« Stub… », « Unused »), les images.
- `check_translations.py` laisse une vingtaine d'avertissements de longueur, revus et jugés sûrs.
