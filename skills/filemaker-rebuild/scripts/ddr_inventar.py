#!/usr/bin/env python3
"""Inventar eines FileMaker-DDR (Database Design Report, XML) als Markdown.

Liest den DDR (UTF-16 oder UTF-8), zählt und listet alle Kataloge auf und meldet
Geheimnisse als Sicherheitsbefund, OHNE ihre Werte auszugeben.

  python3 -I ddr_inventar.py <DDR.xml> [--texte layout-texte.md] > inventar.md

--texte schreibt zusätzlich alle Textobjekte der Layouts (Brief-, Druck-, Hinweistexte)
je Layout in eine eigene Datei: Grundlage für die wörtliche Übernahme.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

GEHEIM = {"Password", "Passwort", "Username"}


def lade(pfad: Path) -> ET.Element:
    roh = pfad.read_bytes()
    if roh[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = roh.decode("utf-16")
    else:
        text = roh.decode("utf-8-sig")
    # Die XML-Deklaration kann noch "UTF-16" nennen – für den Parser entfernen
    if text.startswith("<?xml"):
        text = text[text.index("?>") + 2 :]
    return ET.fromstring(text)


def name(e: ET.Element) -> str:
    return e.get("name") or "(ohne Name)"


def alle(e: ET.Element | None, tag: str) -> list[ET.Element]:
    """Elemente eines Katalogs inkl. solcher in (verschachtelten) Gruppen"""
    if e is None:
        return []
    out: list[ET.Element] = []
    for c in e:
        if c.tag == tag:
            out.append(c)
        elif c.tag == "Group":
            out.extend(alle(c, tag))
    return out


def tabelle(zeilen: list[list[str]], kopf: list[str]) -> str:
    if not zeilen:
        return "_keine_\n"
    z = ["| " + " | ".join(kopf) + " |", "|" + "---|" * len(kopf)]
    z += ["| " + " | ".join(s.replace("|", "\\|") for s in r) + " |" for r in zeilen]
    return "\n".join(z) + "\n"


def datei(f: ET.Element, texte: list[str]) -> str:
    md = [f"## Datei `{name(f)}`\n"]

    bt = alle(f.find("BaseTableCatalog"), "BaseTable")
    zeilen = []
    for t in bt:
        felder = t.findall("./FieldCatalog/Field")
        arten = Counter(x.get("fieldType", "?") for x in felder)
        extern = "ja" if t.find("DataSourceRef") is not None else ""
        zeilen.append(
            [
                name(t),
                t.get("records", ""),
                str(len(felder)),
                ", ".join(f"{k} {v}" for k, v in sorted(arten.items())),
                extern,
            ]
        )
    md.append(f"### Basistabellen ({len(bt)})\n")
    md.append(tabelle(zeilen, ["Tabelle", "Datensätze", "Felder", "Feldarten", "extern"]))

    rg = f.find("RelationshipGraph")
    to = rg.findall("./TableList/Table") if rg is not None else []
    rel = rg.findall("./RelationshipList/Relationship") if rg is not None else []
    md.append(f"\n### Beziehungsgraph\n\n{len(to)} Tabellenauftreten, {len(rel)} Beziehungen.\n")

    sk = alle(f.find("ScriptCatalog"), "Script")
    md.append(f"\n### Skripte ({len(sk)})\n")
    md.append(
        tabelle(
            [[name(s), str(len(s.findall("./StepList/Step")))] for s in sk],
            ["Skript", "Schritte"],
        )
    )

    la = alle(f.find("LayoutCatalog"), "Layout")
    zeilen = []
    for lay in la:
        tab = lay.find("Table")
        objs = lay.findall(".//Object")
        txt = [
            "".join(d.itertext()).strip()
            for o in objs
            if o.get("type") == "Text"
            for d in o.findall(".//Data")
        ]
        txt = [t for t in txt if t]
        if txt:
            texte.append(f"## {name(f)} – Layout `{name(lay)}`\n")
            texte.extend(f"```\n{t}\n```\n" for t in txt)
        zeilen.append(
            [name(lay), name(tab) if tab is not None else "", str(len(objs)), str(len(txt))]
        )
    md.append(f"\n### Layouts ({len(la)})\n")
    md.append(tabelle(zeilen, ["Layout", "Tabellenauftreten", "Objekte", "Textobjekte"]))

    wl = alle(f.find("ValueListCatalog"), "ValueList")
    md.append(f"\n### Wertelisten ({len(wl)})\n")
    md.append(
        tabelle(
            [[name(v), (v.find("Source").get("value", "") if v.find("Source") is not None else "")] for v in wl],
            ["Werteliste", "Quelle"],
        )
    )

    ps = f.findall("./PrivilegesCatalog/PrivilegeSet")
    md.append(f"\n### Berechtigungssets ({len(ps)}) – Grundlage für Rollen\n")
    md.append(tabelle([[name(p), p.get("comment", "")] for p in ps], ["Set", "Kommentar"]))

    ac = f.findall("./AccountCatalog/Account")
    md.append(f"\n### Konten ({len(ac)}) – nur Namen\n")
    md.append(
        tabelle(
            [[name(a), a.get("privilegeSet", ""), a.get("status", "")] for a in ac],
            ["Konto", "Set", "Status"],
        )
    )

    cf = f.findall("./CustomFunctionCatalog/CustomFunction")
    md.append(f"\n### Eigene Funktionen ({len(cf)})\n")
    md.append(", ".join(f"`{name(c)}`" for c in cf) + "\n" if cf else "_keine_\n")

    ex = f.find("ExternalDataSourcesCatalog")
    md.append("\n### Externe Datenquellen\n")
    zeilen = []
    for q in list(ex) if ex is not None else []:
        zeilen.append([q.tag, name(q), q.get("pathList") or q.get("DSN") or q.get("dsn", "")])
    md.append(tabelle(zeilen, ["Art", "Name", "Pfad/DSN"]))
    return "\n".join(md)


def befunde(root: ET.Element) -> list[str]:
    """Stellen mit Zugangsdaten – nur Fundort, niemals der Wert"""
    out = []
    for f in root.iter("File"):
        for e in f.iter():
            # Werte stehen direkt im Element oder als <Calculation> darunter
            if e.tag in GEHEIM and "".join(e.itertext()).strip():
                out.append(f"- `{name(f)}`: Element `{e.tag}` ist befüllt (Wert nicht ausgegeben)")
    # doppelte Fundorte zusammenfassen
    return [f"{z} ×{n}" if n > 1 else z for z, n in Counter(out).items()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ddr", type=Path)
    ap.add_argument("--texte", type=Path, help="Layout-Texte in diese Datei schreiben")
    a = ap.parse_args()
    root = lade(a.ddr)
    texte: list[str] = []
    teile = [f"# DDR-Inventar `{a.ddr.name}`\n"]
    teile += [datei(f, texte) for f in root.iter("File")]
    b = befunde(root)
    teile.append("\n## Sicherheitsbefunde\n")
    teile.append(
        "\n".join(b)
        + "\n\n**Werte niemals übernehmen oder wiederholen – Zugangsdaten rotieren lassen.**\n"
        if b
        else "_keine befüllten Zugangsdaten gefunden_\n"
    )
    sys.stdout.write("\n".join(teile))
    if a.texte:
        a.texte.write_text("# Layout-Texte (wörtlich)\n\n" + "\n".join(texte), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
