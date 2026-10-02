# Dressmaker - traduction française (non officielle)

Patch de traduction française pour **Dressmaker** (Cozy Lives / Free Lives), sous forme de plugin [BepInEx 5](https://github.com/BepInEx/BepInEx).
Projet de fan, sans lien avec les développeurs ni l'éditeur. Il faut posséder le jeu. Aucun fichier du jeu n'est modifié ni fourni : le plugin ajoute seulement le français.

**Télécharger :** voir la page [Releases](../../releases) (archive `DressmakerFR-1.0.0.zip`, instructions d'installation dans `LISEZMOI.txt`).

## Ce qui est traduit

- L'interface, le tutoriel et tous les noms (tissus, patrons, accessoires, quêtes).
- Tous les dialogues des clientes, les chroniques mondaines du journal et les résumés de quête.

Restent en anglais : les images contenant du texte (titre du journal, affiches, logo, enseigne), le contenu propre à l'ancienne démo et quelques textes de développement qui ne s'affichent pas en jeu normal.

## Pourquoi ce patch

Mon but est de rendre le travail du studio accessible aux joueuses et joueurs francophones, et de mettre en valeur leur jeu. Si le studio annonce une traduction française officielle, ce projet sera retiré.
Ce patch reste un travail d'amateur, et non celui d'un traducteur professionnel.

## Comment cette traduction a été faite (usage de l'IA)

Par souci de transparence : cette traduction a été produite en grande partie avec une intelligence artificielle, y compris le plugin qui l'affiche dans le jeu et les outils de ce dépôt.

- **Automatisé** : le premier jet de la quasi-totalité des textes, à partir d'un guide de style et d'un glossaire établis pour le projet (registre Régence, vouvoiement, typographie française, vocabulaire de la couture).
- **Fait main** : les choix de fond (ton, noms, titres) et chaque jeu de mots, référence culturelle ou chanson du texte anglais. Ces passages ont été travaillés un par un, et réécrits pour trouver des équivalents qui parlent à un public français plutôt que de traduire mot à mot.
- **Vérifié en jeu** : les écrans et les passages les plus délicats (chroniques du journal, poème, libellés de l'interface, longueur des textes).

Toutes les répliques n'ont pas été relues une à une par un humain : si une phrase sonne faux, un signalement est bienvenu (onglet *Issues*).

## Signaler un problème ou contribuer

Toute aide est bienvenue : voir le [guide de contribution](CONTRIBUTING.md).


Ouvrir une *Issue* en précisant la scène (cliente, quête ou écran), le texte affiché et, si possible, une capture d'écran. Pour un problème technique, joindre `<dossier du jeu>\BepInEx\LogOutput.log`.

## Contenu du dépôt

Le dépôt ne contient **aucun texte anglais du jeu** : ces textes appartiennent aux développeurs. Les outils les extraient localement depuis votre propre copie du jeu, dans un dossier `local/` exclu du dépôt.

```
translation/translations_fr.json   la base de traduction
docs/guide_de_style.md             le guide de style
plugin/                            le plugin BepInEx (C#)
tools/                             les outils (Python 3)
local/                             créé par les outils, jamais publié (texte anglais du jeu)
```

| Fichier | Rôle |
|---|---|
| `translation/translations_fr.json` | Base de traduction : une entrée par identifiant de chaîne du jeu (`collection`, `key`, `fr`, empreinte de l'anglais d'origine `src`, `status`, `note`, `correction`). |
| `docs/guide_de_style.md` | Guide de style : décisions de traduction, voix des personnages, typographie, glossaire, noms du monde. |
| `CONTRIBUTING.md` | Guide de contribution : signaler un problème, proposer une correction. |
| `AGENTS.md` | Consignes pour les agents de code et les contributeurs : règles, méthode, pièges techniques, mode test (format ouvert AGENTS.md). |
| `plugin/` | Plugin BepInEx. Ajoute la langue `fr`, construit les tables françaises à la volée à partir des tables anglaises (repli sur l'anglais pour tout texte non traduit) et ne modifie aucun fichier du jeu. |
| `tools/extract_dressmaker_strings.py` | Extrait les textes anglais du jeu (lecture seule) → `local/dressmaker_strings_en.json`. |
| `tools/extract_dialogue_order.py`, `tools/make_dialogue_script.py` | Reconstituent l'ordre des dialogues (programme Yarn Spinner du jeu) et produisent un script lisible anglais + français, dans `local/`. |
| `tools/merge_batch.py` | Fusionne un lot de traductions (`clé<TAB>texte`) dans la base, avec la typographie française. |
| `tools/check_translations.py` | Contrôle balises, variables, sauts de ligne, deux-points Yarn, longueurs d'interface, textes anglais modifiés depuis la traduction. |
| `tools/yarn_colons.py` | Échappe les deux-points des répliques (voir ci-dessous). |
| `tools/export_fr_table.py` | Génère `plugin/fr.tsv`, le fichier lu par le plugin. |
| `tools/paths.py` | Chemins communs aux outils (ils fonctionnent quel que soit le dossier d'où on les lance). |

## Reconstruire le patch

Prérequis : le jeu (Windows, Steam) avec BepInEx 5.4.23.5 installé, Python 3 avec `pip install UnityPy`, et le SDK .NET. Depuis la racine du dépôt :

```bash
python tools/extract_dressmaker_strings.py --game "<dossier du jeu>"
python tools/check_translations.py
python tools/export_fr_table.py
dotnet build plugin -c Release -p:GameDir="<dossier du jeu>"
```

`<dossier du jeu>` est le dossier qui contient `Dressmaker.exe`. Pour ne pas le retaper à chaque compilation, il peut aussi être donné par la variable d'environnement `DRESSMAKER_DIR`, ou dans un fichier local `plugin/Directory.Build.props` (exclu du dépôt ; modèle en commentaire dans `plugin/DressmakerFR.csproj`).

La compilation copie `DressmakerFR.dll` et `fr.tsv` dans `BepInEx\plugins\DressmakerFR\` du jeu. Sous Windows, lancer `check_translations.py` avec la variable `PYTHONIOENCODING=utf-8`, sinon la console peut planter en affichant une erreur.

## Notes techniques

- **Deux-points dans les dialogues.** Le moteur de dialogue (Yarn Spinner) lit « Nom: texte » comme « personnage : réplique » et efface tout ce qui précède le premier deux-points non échappé. Dans les répliques, tout deux-points de phrase s'écrit donc `\:`. `merge_batch.py` le fait automatiquement et `check_translations.py` le vérifie.
- **Polices.** Les polices du jeu n'ont pas le caractère « œ » : le plugin l'affiche « oe » (option `RemplacerOE`). La base garde l'orthographe correcte.
- **Couleurs injectées.** Dans les chroniques, le jeu insère le nom de la couleur ou du tissu le plus utilisé, en minuscules : les phrases sont tournées pour éviter les accords (« une robe couleur {0} »).
- **Mise à jour du jeu.** Chaque traduction mémorise l'empreinte du texte anglais d'origine ; `check_translations.py` signale les textes modifiés par les développeurs.

## Licence

- **Code** (plugin et outils) : licence MIT, voir [`LICENSE`](LICENSE).
- **Traduction et guide de style** : CC BY-NC-SA 4.0 (créditer Obero, pas d'usage commercial, partage dans les mêmes conditions), voir [`LICENCE-TRADUCTION.md`](LICENCE-TRADUCTION.md).
- Ces licences ne donnent aucun droit sur le jeu ni sur ses textes originaux, qui appartiennent à Cozy Lives / Free Lives.

## Crédits

Traduction et plugin : Obero.
Dressmaker est une création de Cozy Lives / Free Lives. Tous droits sur le jeu et ses textes originaux appartiennent à leurs auteurs.
