#!/usr/bin/env python3
"""
Extraction des textes anglais de Dressmaker (tables Unity Localization).

Usage (PowerShell) :
    pip install UnityPy
    python tools/extract_dressmaker_strings.py --game "<dossier du jeu>"

Produit dans local/ (fichiers de travail, jamais publiés : ils contiennent le texte anglais) :
    dressmaker_strings_en.json   (pour la traduction)
    dressmaker_strings_en.csv    (pour relire dans un tableur, UTF-8)

Rien n'est modifié dans les fichiers du jeu : lecture seule.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

from paths import LOCAL, STRINGS_EN, STRINGS_EN_CSV

try:
    import UnityPy
except ImportError:
    sys.exit("UnityPy manquant : lance d'abord  pip install UnityPy")


def find_data_dir(game: Path) -> Path:
    direct = game / "Dressmaker_Data"
    if direct.is_dir():
        return direct
    hits = [p for p in game.rglob("*_Data") if (p / "StreamingAssets").is_dir()]
    if hits:
        return hits[0]
    sys.exit(f"Dossier *_Data introuvable sous {game}")


def find_comments(node, out):
    """Récupère récursivement les commentaires (métadonnée Comment de Unity Localization)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "m_CommentText" and isinstance(v, str) and v.strip():
                out.append(v.strip())
            else:
                find_comments(v, out)
    elif isinstance(node, list):
        for v in node:
            find_comments(v, out)
    return out


def scan(env):
    shared, tables, failures = {}, [], 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            tree = obj.read_typetree()
        except Exception:
            failures += 1
            continue
        if not isinstance(tree, dict):
            continue
        name = tree.get("m_Name", "")
        if "m_Entries" in tree and ("m_TableCollectionName" in tree or "m_KeyGenerator" in tree):
            entries = {}
            for e in tree.get("m_Entries", []):
                entries[e.get("m_Id")] = {
                    "key": e.get("m_Key", ""),
                    "comments": find_comments(e.get("m_Metadata", {}), []),
                }
            shared[obj.path_id] = {
                "collection": tree.get("m_TableCollectionName") or name,
                "entries": entries,
            }
        elif "m_TableData" in tree and "m_LocaleId" in tree:
            tables.append({
                "name": name,
                "locale": (tree.get("m_LocaleId") or {}).get("m_Code", ""),
                "shared_pid": (tree.get("m_SharedData") or {}).get("m_PathID"),
                "entries": [
                    {
                        "id": e.get("m_Id"),
                        "text": e.get("m_Localized", ""),
                        "comments": find_comments(e.get("m_Metadata", {}), []),
                    }
                    for e in tree.get("m_TableData", [])
                ],
            })
    return shared, tables, failures


def try_typetree_generator(env, data_dir: Path):
    """Secours si les bundles n'embarquent pas les typetrees (UnityPy >= 1.20)."""
    try:
        from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
        version = None
        for obj in env.objects:
            version = getattr(obj.assets_file, "unity_version", None)
            if version:
                break
        gen = TypeTreeGenerator(version)
        gen.load_local_dll_folder(str(data_dir / "Managed"))
        env.typetree_generator = gen
        return True
    except Exception as exc:
        print(f"[!] Générateur de typetree indisponible : {exc}")
        return False


def match_shared(table, shared):
    if table["shared_pid"] in shared:
        return shared[table["shared_pid"]]
    ids = {e["id"] for e in table["entries"]}
    best, best_score = None, 0
    for s in shared.values():
        score = len(ids & s["entries"].keys())
        if score > best_score:
            best, best_score = s, score
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True, help="Dossier contenant Dressmaker.exe")
    ap.add_argument("--locale", default="en", help="Code de langue source (défaut : en)")
    args = ap.parse_args()

    data_dir = find_data_dir(Path(args.game))
    aa = data_dir / "StreamingAssets" / "aa"
    bundles = sorted(p for p in aa.rglob("*.bundle") if "locali" in p.name.lower())
    if not bundles:
        sys.exit(f"Aucun bundle de localisation trouvé sous {aa}")
    print(f"{len(bundles)} bundle(s) de localisation :")
    for b in bundles:
        print(f"   - {b.name}")

    env = UnityPy.load(*map(str, bundles))
    shared, tables, failures = scan(env)

    if not tables and failures and try_typetree_generator(env, data_dir):
        env = UnityPy.load(*map(str, bundles))
        try_typetree_generator(env, data_dir)
        shared, tables, failures = scan(env)

    locales = sorted({t["locale"] for t in tables})
    print(f"Locales trouvées : {', '.join(locales) or 'aucune'}")
    if not tables:
        sys.exit(f"Aucune table lisible ({failures} objets illisibles). Envoie-moi cette sortie.")

    rows = []
    for t in tables:
        if not t["locale"].lower().startswith(args.locale.lower()):
            continue
        s = match_shared(t, shared)
        for e in t["entries"]:
            meta = s["entries"].get(e["id"], {}) if s else {}
            comments = meta.get("comments", []) + e["comments"]
            rows.append({
                "collection": s["collection"] if s else t["name"],
                "key": meta.get("key", ""),
                "id": e["id"],
                "en": e["text"],
                "comment": " | ".join(dict.fromkeys(comments)),
            })

    rows.sort(key=lambda r: (r["collection"], r["key"], r["id"]))
    LOCAL.mkdir(exist_ok=True)
    STRINGS_EN.write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(STRINGS_EN_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["collection", "key", "id", "en", "comment"])
        w.writeheader()
        w.writerows(rows)

    words = sum(len(r["en"].split()) for r in rows)
    per_coll = {}
    for r in rows:
        per_coll[r["collection"]] = per_coll.get(r["collection"], 0) + 1
    print(f"\n{len(rows)} chaînes, ~{words} mots, {len(per_coll)} collections :")
    for c, n in sorted(per_coll.items(), key=lambda x: -x[1]):
        print(f"   {n:5d}  {c}")
    print(f"\nFichiers écrits : {STRINGS_EN} / .csv")


if __name__ == "__main__":
    main()
