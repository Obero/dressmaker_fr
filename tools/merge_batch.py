#!/usr/bin/env python3
"""
Fusionne un lot de traductions dans translation/translations_fr.json.

Usage :
    python tools/merge_batch.py <collection> lot.tsv [--status draft]

Format du lot : une ligne par chaîne, clé<TAB>traduction (lignes vides et # ignorées).
Pour une chaîne sans clé (11 répliques de Dialogue), écrire id:<identifiant numérique>.
Écrire \\n pour un saut de ligne littéral du jeu. L'apostrophe ' est convertie en ’,
et une espace normale avant : ; ! ? % » (ou après «) devient insécable.
"""
import argparse
import hashlib
import json
import re

import yarn_colons
from paths import STRINGS_EN as SRC, TRANSLATIONS as TR
NBSP = " "
TAG_RE = re.compile(r"(<[^<>]+>|\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})")


def typo(s):
    # Ne touche pas aux balises ni aux placeholders.
    parts = TAG_RE.split(s)
    for i in range(0, len(parts), 2):
        p = parts[i].replace("'", "’")
        p = re.sub(r" ([:;!?%»])", NBSP + r"\1", p)
        p = p.replace(" \\:", NBSP + "\\:")  # deux-points échappé de Yarn
        p = p.replace("« ", "«" + NBSP)
        parts[i] = p
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("collection")
    ap.add_argument("batch")
    ap.add_argument("--status", default="draft")
    a = ap.parse_args()

    rows = [r for r in json.load(open(SRC, encoding="utf-8")) if r["collection"] == a.collection]
    src = {r["key"]: r for r in rows if r["key"]}
    by_id = {str(r["id"]): r for r in rows}
    raw = open(TR, encoding="utf-8").read()
    tr = json.loads(raw)

    n, unknown = 0, []
    for line in open(a.batch, encoding="utf-8"):
        line = line.rstrip("\n").rstrip("\r")
        if not line.strip() or line.startswith("#"):
            continue
        key, fr = line.split("\t", 1)
        s = by_id.get(key[3:]) if key.startswith("id:") else src.get(key)
        if s is None:
            unknown.append(key)
            continue
        sid = str(s["id"])
        entry = tr.get(sid, {})
        fr_text = typo(fr.replace("\\n", "\n"))
        if a.collection == "Dialogue" and yarn_colons.is_yarn_key(s["key"]):
            fr_text = yarn_colons.escape(fr_text, s["en"])  # sinon Yarn coupe avant le « : »
        entry.update({
            "collection": a.collection,
            "key": s["key"],
            "fr": fr_text,
            "src": hashlib.sha1(s["en"].encode("utf-8")).hexdigest()[:10],
            "status": a.status,
        })
        tr[sid] = entry
        n += 1

    open(TR, "w", encoding="utf-8", newline="\n").write(
        json.dumps(tr, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""))
    print(f"{n} chaînes fusionnées ({a.collection}).")
    if unknown:
        print("Clés inconnues :", ", ".join(unknown))


if __name__ == "__main__":
    main()
