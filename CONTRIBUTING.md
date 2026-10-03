# Contribuer à la traduction française de Dressmaker

Merci de vouloir aider ! Toute contribution est bienvenue, de la simple coquille signalée à la proposition de correction. Ce projet est un travail d'amateur, mené dans un esprit bienveillant : les échanges aussi.

## Une règle avant tout : pas de texte anglais du jeu

Les textes originaux de *Dressmaker* appartiennent au studio. Ils ne doivent apparaître **nulle part** dans ce dépôt : ni dans les fichiers, ni dans les issues, ni dans les commentaires.
Pour désigner un passage, décrivez la scène et citez le **texte français** affiché. Une capture d'écran du jeu en français est parfaite.

## Signaler un problème (le plus simple)

Ouvrez une *Issue* en indiquant :

- **la version du jeu**, affichée en bas à droite de l'écran titre (par exemple `410.44874e6`) ;
- **où** : la cliente, la quête ou l'écran (par exemple « Dorothy, quête du labyrinthe, après la robe ratée » ou « écran de vente ») ;
- **quoi** : le texte français affiché, et ce qui ne va pas (faute, contresens, phrase qui sonne faux, texte qui déborde, texte resté en anglais, caractère manquant…) ;
- si possible, **une capture d'écran** et votre proposition de correction.

Pour un problème technique (le jeu ne passe pas en français, plantage…), joignez le fichier `<dossier du jeu>/BepInEx/LogOutput.log`.

## Proposer une correction directement

Toute la traduction se trouve dans **`translation/translations_fr.json`**, une entrée par texte du jeu :

```json
"7392685321982382": {
 "collection": "Dialogue",
 "key": "line:000489b",
 "fr": "Bonjour, ma dragée.",
 ...
}
```

1. Cherchez le texte français à corriger dans `translation/translations_fr.json` (recherche dans l'éditeur, ou directement sur GitHub).
2. Modifiez **uniquement le champ `fr`**. Ne touchez ni aux autres champs, ni aux identifiants.
3. Respectez les règles ci-dessous, puis proposez votre modification (*Pull Request*). Sur GitHub, le bouton crayon d'un fichier suffit, sans rien installer.

Si vous avez le jeu et Python, vous pouvez aussi vérifier et tester votre correction : voir « Reconstruire le patch » dans le [README](README.md).

## Les règles à respecter

Les règles de traduction (balises et variables, typographie, ton, longueur des libellés…) sont dans le [guide de style](docs/guide_de_style.md). En plus, propre à la contribution :

- **Deux-points des dialogues dans le JSON** : la barre oblique qui les protège se double dans `translations_fr.json`, écrivez donc `\\:` (forme visible dans les entrées existantes).
- **Espaces** : si vous tapez une espace ordinaire là où le guide demande une espace insécable, ce n'est pas grave, elle sera corrigée à la relecture.
- **Jeux de mots et références** : une nouvelle adaptation se discute d'abord dans une *Issue*.

## Usage de l'IA

Le projet est transparent sur son propre usage de l'IA (voir le README). Si votre contribution a été écrite avec l'aide d'une IA, merci de le préciser : ce n'est pas un problème, c'est une question de transparence.

## Comment les contributions sont validées

Les propositions sont relues par Obero, qui tranche sur le choix final, en particulier pour les jeux de mots et les questions de ton. Une proposition peut être retravaillée ou refusée ; ce n'est jamais un jugement sur son auteur.

## Licence

En contribuant, vous acceptez que votre contribution soit publiée sous la licence du fichier concerné : **CC BY-NC-SA 4.0** pour la traduction et le guide de style ([`LICENCE-TRADUCTION.md`](LICENCE-TRADUCTION.md)), **MIT** pour le code ([`LICENSE`](LICENSE)).
