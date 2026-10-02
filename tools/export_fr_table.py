#!/usr/bin/env python3
"""
Convertit translation/translations_fr.json en plugin/fr.tsv (format lu par le plugin).

Usage :
    python tools/export_fr_table.py [source.json destination.tsv]

Sans argument : translation/translations_fr.json → plugin/fr.tsv.
Format : collection<TAB>id<TAB>texte, avec \\n, \\t et \\\\ échappés.
"""
import json
import sys

from paths import FR_TSV, TRANSLATIONS


def escape(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\r", "").replace("\n", "\\n")


def main():
    src, dst = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else (TRANSLATIONS, FR_TSV)
    tr = json.load(open(src, encoding="utf-8"))
    n = 0
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Dressmaker FR - généré par export_fr_table.py, ne pas éditer à la main\n")
        for sid, t in sorted(tr.items(), key=lambda kv: (kv[1]["collection"], kv[0])):
            if not t.get("fr"):
                continue
            f.write(f"{t['collection']}\t{sid}\t{escape(t['fr'])}\n")
            n += 1
    print(f"{n} chaînes écrites dans {dst}")


if __name__ == "__main__":
    main()
