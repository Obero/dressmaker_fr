"""Chemins du projet, communs à tous les outils (indépendants du dossier courant)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Publié dans le dépôt
TRANSLATIONS = ROOT / "translation" / "translations_fr.json"
FR_TSV = ROOT / "plugin" / "fr.tsv"  # généré par export_fr_table.py

# Fichiers de travail locaux, jamais publiés (contiennent le texte anglais du jeu)
LOCAL = ROOT / "local"
STRINGS_EN = LOCAL / "dressmaker_strings_en.json"
STRINGS_EN_CSV = LOCAL / "dressmaker_strings_en.csv"
DIALOGUE_ORDER = LOCAL / "dialogue_order.json"
DIALOGUE_SCRIPT = LOCAL / "dialogue_script.txt"
LOTS = LOCAL / "lots"
