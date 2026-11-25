#!/usr/bin/env python3
"""Inventory of a FileMaker DDR (Database Design Report, XML) as Markdown.

Reads the DDR (UTF-16 or UTF-8), counts and lists all catalogs and reports stored
credentials as security findings WITHOUT printing their values.

  python3 -I ddr_inventory.py <DDR.xml> [--texts layout-texts.md] > inventory.md

--texts additionally writes all text objects of the layouts (letter, print and notice
texts), grouped by layout, to a separate file: the basis for taking texts over verbatim.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

# Element names that hold credentials (FileMaker also localises some of them)
SECRET = {"Password", "Passwort", "Username"}


def load(path: Path) -> ET.Element:
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig")
    # The XML declaration may still say "UTF-16" - strip it for the parser
    if text.startswith("<?xml"):
        text = text[text.index("?>") + 2 :]
    return ET.fromstring(text)


def name(e: ET.Element) -> str:
    return e.get("name") or "(unnamed)"


def collect(e: ET.Element | None, tag: str) -> list[ET.Element]:
    """Elements of a catalog, including those inside (nested) groups"""
    if e is None:
        return []
    out: list[ET.Element] = []
    for c in e:
        if c.tag == tag:
            out.append(c)
        elif c.tag == "Group":
            out.extend(collect(c, tag))
    return out


def table(rows: list[list[str]], head: list[str]) -> str:
    if not rows:
        return "_none_\n"
    z = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    z += ["| " + " | ".join(s.replace("|", "\\|") for s in r) + " |" for r in rows]
    return "\n".join(z) + "\n"


def file_section(f: ET.Element, texts: list[str]) -> str:
    md = [f"## File `{name(f)}`\n"]

    bt = collect(f.find("BaseTableCatalog"), "BaseTable")
    rows = []
    for t in bt:
        fields = t.findall("./FieldCatalog/Field")
        kinds = Counter(x.get("fieldType", "?") for x in fields)
        external = "yes" if t.find("DataSourceRef") is not None else ""
        rows.append(
            [
                name(t),
                t.get("records", ""),
                str(len(fields)),
                ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())),
                external,
            ]
        )
    md.append(f"### Base tables ({len(bt)})\n")
    md.append(table(rows, ["Table", "Records", "Fields", "Field types", "External"]))

    rg = f.find("RelationshipGraph")
    occ = rg.findall("./TableList/Table") if rg is not None else []
    rel = rg.findall("./RelationshipList/Relationship") if rg is not None else []
    md.append(f"\n### Relationship graph\n\n{len(occ)} table occurrences, {len(rel)} relationships.\n")

    sc = collect(f.find("ScriptCatalog"), "Script")
    md.append(f"\n### Scripts ({len(sc)})\n")
    md.append(
        table(
            [[name(s), str(len(s.findall("./StepList/Step")))] for s in sc],
            ["Script", "Steps"],
        )
    )

    la = collect(f.find("LayoutCatalog"), "Layout")
    rows = []
    for lay in la:
        occurrence = lay.find("Table")
        objs = lay.findall(".//Object")
        txt = [
            "".join(d.itertext()).strip()
            for o in objs
            if o.get("type") == "Text"
            for d in o.findall(".//Data")
        ]
        txt = [t for t in txt if t]
        if txt:
            texts.append(f"## {name(f)} - layout `{name(lay)}`\n")
            texts.extend(f"```\n{t}\n```\n" for t in txt)
        rows.append(
            [
                name(lay),
                name(occurrence) if occurrence is not None else "",
                str(len(objs)),
                str(len(txt)),
            ]
        )
    md.append(f"\n### Layouts ({len(la)})\n")
    md.append(table(rows, ["Layout", "Table occurrence", "Objects", "Text objects"]))

    vl = collect(f.find("ValueListCatalog"), "ValueList")
    md.append(f"\n### Value lists ({len(vl)})\n")
    md.append(
        table(
            [
                [name(v), (v.find("Source").get("value", "") if v.find("Source") is not None else "")]
                for v in vl
            ],
            ["Value list", "Source"],
        )
    )

    ps = f.findall("./PrivilegesCatalog/PrivilegeSet")
    md.append(f"\n### Privilege sets ({len(ps)}) - basis for roles\n")
    md.append(table([[name(p), p.get("comment", "")] for p in ps], ["Set", "Comment"]))

    ac = f.findall("./AccountCatalog/Account")
    md.append(f"\n### Accounts ({len(ac)}) - names only\n")
    md.append(
        table(
            [[name(a), a.get("privilegeSet", ""), a.get("status", "")] for a in ac],
            ["Account", "Set", "Status"],
        )
    )

    cf = f.findall("./CustomFunctionCatalog/CustomFunction")
    md.append(f"\n### Custom functions ({len(cf)})\n")
    md.append(", ".join(f"`{name(c)}`" for c in cf) + "\n" if cf else "_none_\n")

    ex = f.find("ExternalDataSourcesCatalog")
    md.append("\n### External data sources\n")
    rows = []
    for q in list(ex) if ex is not None else []:
        rows.append([q.tag, name(q), q.get("pathList") or q.get("DSN") or q.get("dsn", "")])
    md.append(table(rows, ["Kind", "Name", "Path/DSN"]))
    return "\n".join(md)


def findings(root: ET.Element) -> list[str]:
    """Places that hold credentials - location only, never the value"""
    out = []
    for f in root.iter("File"):
        for e in f.iter():
            # Values sit directly in the element or in a <Calculation> below it
            if e.tag in SECRET and "".join(e.itertext()).strip():
                out.append(f"- `{name(f)}`: element `{e.tag}` is filled (value not shown)")
    # merge duplicate locations
    return [f"{z} x{n}" if n > 1 else z for z, n in Counter(out).items()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ddr", type=Path)
    ap.add_argument("--texts", type=Path, help="write the layout texts to this file")
    a = ap.parse_args()
    root = load(a.ddr)
    texts: list[str] = []
    parts = [f"# DDR inventory `{a.ddr.name}`\n"]
    parts += [file_section(f, texts) for f in root.iter("File")]
    found = findings(root)
    parts.append("\n## Security findings\n")
    parts.append(
        "\n".join(found)
        + "\n\n**Never take over or repeat these values - have the credentials rotated.**\n"
        if found
        else "_no filled credentials found_\n"
    )
    sys.stdout.write("\n".join(parts))
    if a.texts:
        a.texts.write_text("# Layout texts (verbatim)\n\n" + "\n".join(texts), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
