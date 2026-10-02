#!/usr/bin/env python3
"""
Produit un script de dialogue lisible, scène par scène, dans l'ordre du jeu.

Usage :
    python tools/make_dialogue_script.py [--node Préfixe] [--out local/dialogue_script.txt]

Entrées : local/dialogue_order.json (extract_dialogue_order.py), local/dressmaker_strings_en.json,
translation/translations_fr.json. Pour chaque réplique : identifiant, type (> réplique, * choix
de la joueuse), portrait courant, anglais et français s'il existe.
Contient le texte anglais du jeu : fichier de travail local, ne pas publier.
"""
import argparse
import json
import re

from paths import DIALOGUE_ORDER, DIALOGUE_SCRIPT, STRINGS_EN, TRANSLATIONS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", default="", help="ne garder que les nœuds dont le nom commence ainsi")
    ap.add_argument("--out", default=str(DIALOGUE_SCRIPT))
    a = ap.parse_args()

    nodes = json.load(open(DIALOGUE_ORDER, encoding="utf-8"))
    en = {e["key"]: e for e in json.load(open(STRINGS_EN, encoding="utf-8"))
          if e["collection"] == "Dialogue" and e["key"]}
    fr = {t["key"]: t["fr"] for t in json.load(open(TRANSLATIONS, encoding="utf-8")).values()
          if t["collection"] == "Dialogue"}

    out, seen = [], set()
    for n in nodes:
        if not n["node"].startswith(a.node) or not n["events"]:
            continue
        out.append(f"\n=== {n['node']} ===")
        portrait = ""
        for ev in n["events"]:
            if ev["t"] == "cmd":
                m = re.match(r"set_portrait_(\w+)", ev["v"])
                if m:
                    portrait = m.group(1)
                elif not ev["v"].startswith("modify_relationship"):
                    out.append(f"    <<{ev['v']}>>")
                continue
            lid = ev["v"]
            seen.add(lid)
            mark = "*" if ev["t"] == "option" else ">"
            e = en.get(lid, {}).get("en", "(absent de la table)")
            out.append(f"{lid} {mark} [{portrait}] {e}")
            if lid in fr:
                out.append(f"{' ' * 14}FR {fr[lid]}")

    if not a.node:
        orphans = [k for k in en if k not in seen]
        out.append(f"\n=== Hors programme ({len(orphans)} lignes de la table non référencées) ===")
        for k in orphans:
            out.append(f"{k}   {en[k]['en']}")
            if k in fr:
                out.append(f"{' ' * 14}FR {fr[k]}")

    open(a.out, "w", encoding="utf-8", newline="\n").write("\n".join(out).lstrip() + "\n")
    print(f"{a.out} écrit.")


if __name__ == "__main__":
    main()
