#!/usr/bin/env python3
"""
Contrôle technique des traductions Dressmaker FR.

Usage :
    python tools/check_translations.py [anglais.json traductions.json]

Sans argument : local/dressmaker_strings_en.json et translation/translations_fr.json.
Sous Windows, lancer avec PYTHONIOENCODING=utf-8 (sinon la console peut planter
en affichant une erreur, qui passe alors inaperçue).

Vérifie pour chaque chaîne traduite :
  - mêmes balises (<i>, <style=c1>, <color=#...>, <sprite=0>, <shake>...) ;
  - mêmes placeholders ({0}, {1:0.00}, {0:list:{}|, }...) ;
  - même nombre de \\n littéraux ; deux-points des répliques Yarn échappés (\\:) ;
  - texte source inchangé depuis la traduction (empreinte "src") ;
  - longueur suspecte pour l'UI (libellé court > 130 % de l'anglais).
Code de retour 1 s'il y a au moins une erreur bloquante.
"""
import hashlib
import json
import re
import sys
from collections import Counter

import yarn_colons
from paths import STRINGS_EN, TRANSLATIONS

TAG_RE = re.compile(r"<[^<>]+>")


def placeholders(s):
    """Extrait les {…} de premier niveau en gérant l'imbrication ({0:list:{}|, })."""
    out, depth, start = [], 0, None
    for i, ch in enumerate(s):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0:
                out.append(s[start:i + 1])
    return Counter(out)


def fingerprint(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]


FAMILY_MAX = {}


def check(en, fr, collection, key=""):
    errors, warnings = [], []
    if Counter(TAG_RE.findall(en)) != Counter(TAG_RE.findall(fr)):
        errors.append(f"balises : {sorted(TAG_RE.findall(en))} ≠ {sorted(TAG_RE.findall(fr))}")
    if placeholders(en) != placeholders(fr):
        errors.append(f"placeholders : {dict(placeholders(en))} ≠ {dict(placeholders(fr))}")
    for esc in ("\n", "\\n"):
        if en.count(esc) != fr.count(esc):
            errors.append(f"saut de ligne/échappement {esc!r} : {en.count(esc)} ≠ {fr.count(esc)}")
    # Yarn coupe tout ce qui précède un « : » non échappé (nom de personnage) : voir yarn_colons.py.
    if collection == "Dialogue" and yarn_colons.is_yarn_key(key) and yarn_colons.escape(fr, en) != fr:
        errors.append("deux-points non échappé : Yarn effacera le début de la réplique (lancer yarn_colons.py)")
    if en.startswith("QuestGiver:") != fr.startswith("QuestGiver:"):
        errors.append("préfixe QuestGiver: absent ou ajouté")
    if en.endswith(" ") != fr.endswith(" "):
        warnings.append("espace final différent")
    # Libellés courts (boutons, étiquettes) : peu de marge, seuil plus strict.
    if collection == "UI" and "\n" not in en and len(en) <= 40 and len(fr) > 1.3 * len(en) and len(fr) - len(en) >= 4:
        warnings.append(f"longueur {len(fr)} vs {len(en)} (UI : risque de débordement)")
    # Noms d'objets Content (cartes, listes) : même règle ; les descriptions ont plus de place.
    # Repère : le nom anglais le plus long de la même famille (même affichage) tient forcément.
    fam_max = FAMILY_MAX.get((collection, key.split("/")[0]), 0)
    if collection == "Content" and len(en) <= 40 and len(fr) > max(1.3 * len(en), fam_max):
        warnings.append(f"longueur {len(fr)} vs {len(en)}, max famille {fam_max} (nom Content : risque de débordement)")
    if collection == "Content" and len(en) > 40 and len(fr) > 1.3 * len(en):
        warnings.append(f"longueur {len(fr)} vs {len(en)} (description > 130 %)")
    plain = TAG_RE.sub("", fr)
    if "'" in plain:
        warnings.append("apostrophe droite ' (attendu ’)")
    if "—" in plain:
        warnings.append("tiret cadratin « — » : calque de l'anglais, à remplacer par « … », « : », virgule ou point")
    if re.search(r" [:;!?»]|« | \\:", plain):
        warnings.append("espace normale devant : ; ! ? » ou après « (attendu U+00A0)")
    return errors, warnings


def main():
    src_path, tr_path = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else (STRINGS_EN, TRANSLATIONS)
    src = {str(r["id"]): r for r in json.load(open(src_path, encoding="utf-8"))}
    tr = json.load(open(tr_path, encoding="utf-8"))
    for r in src.values():
        if len(r["en"]) <= 40:
            k = (r["collection"], r["key"].split("/")[0])
            FAMILY_MAX[k] = max(FAMILY_MAX.get(k, 0), len(r["en"]))

    n_err = n_warn = n_stale = 0
    for sid, t in tr.items():
        s = src.get(sid)
        if s is None:
            print(f"[ERREUR] {sid} ({t.get('key')}) : id absent de la source")
            n_err += 1
            continue
        if t.get("src") and t["src"] != fingerprint(s["en"]):
            print(f"[OBSOLÈTE] {s['collection']}/{s['key']} : l'anglais a changé depuis la traduction")
            if t.get("correction"):
                print(f"           Correction volontaire de la source sur cette chaîne : les développeurs ont peut-être"
                      f" corrigé l'anglais ({s['en']!r}). Si oui, retirer le champ \"correction\".")
            n_stale += 1
        errors, warnings = check(s["en"], t["fr"], s["collection"], s["key"])
        for e in errors:
            print(f"[ERREUR] {s['collection']}/{s['key']} : {e}")
        for w in warnings:
            print(f"[avert.] {s['collection']}/{s['key']} : {w}")
        n_err += len(errors)
        n_warn += len(warnings)

    by_coll = Counter(src[i]["collection"] for i in tr if i in src)
    total = Counter(r["collection"] for r in src.values())
    print("\nCouverture :")
    for c in sorted(total):
        print(f"  {c:10s} {by_coll.get(c, 0):5d} / {total[c]}")
    n_corr = sum(1 for t in tr.values() if t.get("correction"))
    if n_corr:
        print(f"\n{n_corr} correction(s) volontaire(s) de la source anglaise (champ \"correction\").")
    print(f"\n{n_err} erreur(s), {n_warn} avertissement(s), {n_stale} chaîne(s) obsolète(s)")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
