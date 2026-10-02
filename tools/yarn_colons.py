#!/usr/bin/env python3
"""
Échappe les deux-points des répliques Yarn (collection Dialogue).

Yarn Spinner lit « Nom: texte » comme « personnage : réplique » et retire de l'affichage
tout ce qui précède le premier deux-points non échappé (constaté en jeu le 02/10/2026 :
le début de FuneralTea disparaissait). L'anglais écrit donc « \\: » dans ses phrases.

Règles : seulement les clés de répliques (pas les résumés *_Summary, ni marie_poem_* /
marie_tag_*, lus hors de Yarn) ; on garde le préfixe « QuestGiver: » et un « : » initial
si l'anglais commence ainsi ; on ne touche ni aux balises <…> ni aux {placeholders}.

Usage : python tools/yarn_colons.py            (corrige la base et les lots locaux)
        python tools/yarn_colons.py --check    (compte seulement)
"""
import glob
import json
import re
import sys

from paths import LOTS, STRINGS_EN, TRANSLATIONS

BS = "\\"
TOKEN = re.compile(r"(<[^<>]*>|\{[^{}]*\})")


def is_yarn_key(key):
    k = key or ""
    return not (k.endswith("_Summary") or k.startswith("line:marie_poem_") or k.startswith("line:marie_tag_"))


def escape(fr, en):
    if fr == en:  # ex. « ::( » : identique à l'anglais, on n'y touche pas
        return fr
    keep = 0
    if fr.startswith("QuestGiver:") and en.startswith("QuestGiver:"):
        keep = len("QuestGiver:")
    elif fr.startswith(":") and en.startswith(":"):
        keep = 1
    head, body = fr[:keep], fr[keep:]
    parts = TOKEN.split(body)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"(?<!" + re.escape(BS) + r"):", BS + ":", parts[i])
    return head + "".join(parts)


def main():
    check = "--check" in sys.argv
    en = {str(r["id"]): r for r in json.load(open(STRINGS_EN, encoding="utf-8"))}
    raw = open(TRANSLATIONS, encoding="utf-8").read()
    tr = json.loads(raw)
    fixed = {}
    for sid, v in tr.items():
        if v.get("collection") != "Dialogue" or not is_yarn_key(v.get("key")):
            continue
        new = escape(v["fr"], en[sid]["en"])
        if new != v["fr"]:
            fixed[v.get("key") or "id:" + sid] = (sid, new)
    print(f"{len(fixed)} réplique(s) à échapper.")
    if check or not fixed:
        return
    for key, (sid, new) in fixed.items():
        tr[sid]["fr"] = new
    open(TRANSLATIONS, "w", encoding="utf-8", newline="\n").write(
        json.dumps(tr, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""))
    # Mêmes corrections dans les lots, pour qu'une nouvelle fusion ne les annule pas.
    n = 0
    for path in glob.glob(str(LOTS / "dialogue" / "*.tsv")):
        lines = open(path, encoding="utf-8").read().split("\n")
        changed = False
        for i, l in enumerate(lines):
            if "\t" not in l or l.startswith("#"):
                continue
            key, fr = l.split("\t", 1)
            if key in fixed:
                sid = fixed[key][0]
                new = escape(fr, en[sid]["en"])
                if new != fr:
                    lines[i] = key + "\t" + new; changed = True; n += 1
        if changed:
            open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print(f"translations_fr.json corrigé ; {n} ligne(s) corrigée(s) dans les lots.")


if __name__ == "__main__":
    main()
