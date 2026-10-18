#!/usr/bin/env python3
"""
Prints a markdown report of entries that are listed under more than one ID (nothing if there are none).
Same rule as Iris with debug options enabled (IdMap.java / DuplicateTracker, 26.2 branch). Angelica (1.7.10) has no
check, so the old "name:meta" block files use: same block + meta + blockstate + NBT filters.
Branches of the same #if / #elif / #else chain are never active together, so entries in different branches don't clash.
Only reads the files, never executes anything from them.

Usage: check_duplicates.py <repo root>      (env HEAD_REPO and HEAD_SHA are used for the links in the report)
"""
import glob
import os
import re
import sys
from itertools import combinations

# Files that end up in one properties file in the shaderpack
GROUPS = {
    "item.properties": ["item.properties"],
    "entity.properties": ["entity.properties"],
    "blockProperties/1.13+": ["blockProperties/tags/tags.properties", "blockProperties/1.13+/*.properties",
                              "blockProperties/renderlayers/renderlayers.properties"],
    "blockProperties/1.7.10": ["blockProperties/1.7.10/block.properties"],
    "blockProperties/1.8+": ["blockProperties/1.8+/block.properties"],
}
DIRECTIVE = re.compile(r"#(ifdef|ifndef|if|elif|else|endif|define)\b\s*(.*)")
TOKEN = re.compile(r'(?:"[^"]*"|\[[^\]]*\]|[^\s"\[])+')  # a name, "quoted name" or name[nbt filter]
META = re.compile(r"\d+(,\d+)*")
BLOB = "https://github.com/{}/blob/{}/".format(os.environ.get("HEAD_REPO", "EuphoriaPatches/propertiesFiles"),
                                                os.environ.get("HEAD_SHA", "main"))


def read_entries(root, paths):
    """Yields (key, tokens, path, line number, conditions); conditions = {#if chain: branch that is active}."""
    macros, stack, text = {}, [], ""  # an #if can span several of the block files
    for path in paths:
        with open(os.path.join(root, path), encoding="iso-8859-1") as f:
            for number, line in enumerate(f, start=1):
                line = line.strip()
                directive = DIRECTIVE.match(line)
                if directive:
                    name, arg = directive.groups()
                    if name == "define":
                        macros[arg.partition(" ")[0]] = arg.partition(" ")[2].strip()
                    elif name in ("if", "ifdef", "ifndef"):
                        stack.append([(path, number), 0])
                    elif stack:
                        if name == "endif":
                            stack.pop()
                        else:  # elif / else: the next branch of the chain
                            stack[-1][1] += 1
                    continue
                if not line or line.startswith("#"):
                    continue
                if not text:
                    start, conditions = number, dict(stack)
                text += line
                if text.endswith("\\"):  # the entry continues on the next line
                    text = text[:-1]
                    continue
                key, _, value = text.partition("=")
                text = ""
                yield key.strip(), [t for v in TOKEN.findall(value) for t in TOKEN.findall(macros.get(v, v))], path, start, conditions


def block_ids(token):
    """One identity per meta: name, mod:name, name:1,2, mod:name:prop=value, mod:name[nbt=value]"""
    base, bracket, nbt = token.replace('"', "").partition("[")
    parts = [p for p in base.split(":") if p]
    if not parts:
        return []
    rest = parts[1:]
    if rest and "=" not in rest[0] and not META.fullmatch(rest[0]):
        block, rest = f"{parts[0]}:{rest[0]}", rest[1:]
    else:
        block = "minecraft:" + parts[0]
    block += "".join(":" + p for p in sorted(p for p in rest if "=" in p)) + bracket + nbt
    metas = sorted({m for p in rest if META.fullmatch(p) for m in p.split(",")}, key=int)
    return [f"{block}:{m}" for m in metas] or [block]


def identities(kind, token):
    if token.startswith("%"):  # tags are not tracked
        return []
    if kind == "block":
        return block_ids(token)
    return [] if "=" in token else [token]  # Iris skips item/entity entries with blockstates


def find_duplicates(root, paths):
    """{(kind, identity): [(key, path, line)]} for entries that are active together more than once."""
    seen = {}
    for key, tokens, path, number, conditions in read_entries(root, paths):
        kind = key.split(".")[0]
        if kind not in ("item", "entity", "block", "layer"):
            continue
        for token in tokens:
            for identity in identities(kind, token):
                seen.setdefault((kind, identity), []).append((key, path, number, conditions))
    duplicates = {}
    for identity, places in seen.items():
        hits = {k for (i, a), (j, b) in combinations(enumerate(places), 2)
                if not any(b[3].get(chain, branch) != branch for chain, branch in a[3].items()) for k in (i, j)}
        if hits:
            duplicates[identity] = [places[k][:3] for k in sorted(hits)]
    return duplicates


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    root = sys.argv[1]
    for name, patterns in GROUPS.items():
        duplicates = find_duplicates(root, [p for pattern in patterns for p in sorted(glob.glob(pattern, root_dir=root))])
        if duplicates:
            print(f"#### `{name}`\n\n| Entry | Found in |\n| --- | --- |")
            for (_, identity), places in duplicates.items():
                print(f"| `{identity}` | " + "<br>".join(
                    f"`{key}` ([{os.path.basename(path)}:{number}]({BLOB}{path.replace(' ', '%20')}#L{number}))" for key, path, number in places) + " |")
            print()


if __name__ == "__main__":
    main()
