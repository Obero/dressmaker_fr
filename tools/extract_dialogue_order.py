#!/usr/bin/env python3
"""
Reconstitue l'ordre des dialogues de Dressmaker à partir du programme Yarn Spinner compilé.

Usage :
    python tools/extract_dialogue_order.py --game "<dossier du jeu>"

Lit (sans rien modifier) le MonoBehaviour « DressmakerYarnProject » de sharedassets2.assets,
décode son programme protobuf (nœuds = scènes) et écrit local/dialogue_order.json :
    [{"node": nom, "headers": {...}, "lines": [ids dans l'ordre],
      "events": [{"t": "line"|"option"|"cmd", "v": id ou commande}, ...]}, ...]
Instructions Yarn (v3) : champ 3 = réplique (RunLine), 5 = choix de la joueuse (AddOption),
4 = commande (set_portrait_* indique le personnage et l'émotion).
L'ordre des instructions suit l'ordre du script source (les branches d'options apparaissent
à la suite les unes des autres). Ne contient que des identifiants, pas de texte.
"""
import argparse
import json
import re
from pathlib import Path

import UnityPy

from paths import DIALOGUE_ORDER

LINE_RE = re.compile(rb"line:[0-9a-f]+")


def varint(b, i):
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        s += 7
        if not x & 0x80:
            return r, i


def fields(b):
    """Itère (numéro, type, valeur) sur un message protobuf ; valeur = bytes pour le type 2."""
    i = 0
    while i < len(b):
        key, i = varint(b, i)
        f, wt = key >> 3, key & 7
        if wt == 0:
            v, i = varint(b, i)
        elif wt == 1:
            v, i = b[i:i + 8], i + 8
        elif wt == 2:
            n, i = varint(b, i)
            v, i = b[i:i + n], i + n
        elif wt == 5:
            v, i = b[i:i + 4], i + 4
        else:
            raise ValueError(f"type de fil {wt} inattendu")
        yield f, wt, v


def find_program(raw):
    """Le MonoBehaviour contient le nom du projet puis un tableau d'octets (int32 longueur + données)."""
    name = b"DressmakerYarnProject"
    i = raw.index(name) + len(name)
    i += (-i) % 4  # alignement Unity
    n = int.from_bytes(raw[i:i + 4], "little")
    return raw[i + 4:i + 4 + n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--out", default=str(DIALOGUE_ORDER))
    a = ap.parse_args()

    env = UnityPy.load(str(Path(a.game) / "Dressmaker_Data" / "sharedassets2.assets"))
    raw = next(o.get_raw_data() for o in env.objects
               if o.type.name == "MonoBehaviour" and b"DressmakerYarnProject" in o.get_raw_data()[:200])
    prog = find_program(raw)

    nodes = []
    for f, wt, v in fields(prog):
        if f != 2 or wt != 2:  # map<string, Node> nodes = 2
            continue
        entry = dict((ff, vv) for ff, _, vv in fields(v))
        node = entry[2]
        name, headers = None, {}
        for nf, nwt, nv in fields(node):
            if nf == 1 and nwt == 2:
                name = nv.decode("utf-8")
            elif nf == 6 and nwt == 2:  # Header { key = 1; value = 2; }
                h = dict((hf, hv) for hf, _, hv in fields(nv))
                headers[h.get(1, b"").decode("utf-8")] = h.get(2, b"").decode("utf-8")
        events = []
        for nf, nwt, nv in fields(node):
            if nf != 7 or nwt != 2:  # repeated Instruction instructions = 7
                continue
            for kf, kwt, kv in fields(nv):
                if kwt != 2:
                    continue
                if kf in (3, 5):
                    m = LINE_RE.search(kv)
                    if m:
                        events.append({"t": "line" if kf == 3 else "option", "v": m.group().decode()})
                elif kf == 4:
                    cmd = dict((cf, cv) for cf, _, cv in fields(kv)).get(1, b"").decode("utf-8", "replace")
                    events.append({"t": "cmd", "v": cmd})
        lines = list(dict.fromkeys(e["v"] for e in events if e["t"] != "cmd"))
        nodes.append({"node": name or entry[1].decode("utf-8"), "headers": headers, "lines": lines,
                      "events": events})

    json.dump(nodes, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n_lines = sum(len(n["lines"]) for n in nodes)
    print(f"{len(nodes)} nœuds, {n_lines} références de lignes -> {a.out}")


if __name__ == "__main__":
    main()
