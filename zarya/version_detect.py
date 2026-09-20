import os
import re

from .utils import read_json


def _vt(text):
    parts = str(text).split(".")
    nums = []
    for p in parts[:4]:
        digits = re.sub(r"\D", "", p)
        if not digits:
            break
        nums.append(int(digits))
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:4])


FORMAT_RANGES = {
    1: ((1, 6, 1), (1, 8, 9)),
    2: ((1, 9, 0), (1, 10, 2)),
    3: ((1, 11, 0), (1, 12, 2)),
    4: ((1, 13, 0), (1, 14, 4)),
    5: ((1, 15, 0), (1, 16, 1)),
    6: ((1, 16, 2), (1, 16, 5)),
    7: ((1, 17, 0), (1, 17, 1)),
    8: ((1, 18, 0), (1, 18, 2)),
    9: ((1, 19, 0), (1, 19, 2)),
    10: ((1, 19, 3), (1, 19, 3)),
    11: ((1, 19, 3), (1, 19, 3)),
    12: ((1, 19, 4), (1, 19, 4)),
    13: ((1, 20, 0), (1, 20, 1)),
    14: ((1, 20, 0), (1, 20, 1)),
    15: ((1, 20, 0), (1, 20, 1)),
    16: ((1, 20, 2), (1, 20, 2)),
    17: ((1, 20, 2), (1, 20, 2)),
    18: ((1, 20, 2), (1, 20, 2)),
    19: ((1, 20, 3), (1, 20, 3)),
    20: ((1, 20, 3), (1, 20, 3)),
    21: ((1, 20, 3), (1, 20, 3)),
    22: ((1, 20, 4), (1, 20, 4)),
    23: ((1, 20, 4), (1, 20, 4)),
    24: ((1, 20, 4), (1, 20, 4)),
    25: ((1, 20, 4), (1, 20, 4)),
    26: ((1, 20, 4), (1, 20, 4)),
    27: ((1, 20, 4), (1, 20, 4)),
    28: ((1, 20, 5), (1, 20, 6)),
    29: ((1, 20, 5), (1, 20, 6)),
    30: ((1, 20, 5), (1, 20, 6)),
    31: ((1, 20, 5), (1, 20, 6)),
    32: ((1, 20, 5), (1, 20, 6)),
    33: ((1, 21, 0), (1, 21, 1)),
    34: ((1, 21, 0), (1, 21, 1)),
    35: ((1, 21, 2), (1, 21, 2)),
    36: ((1, 21, 2), (1, 21, 2)),
    37: ((1, 21, 2), (1, 21, 2)),
    38: ((1, 21, 2), (1, 21, 2)),
    39: ((1, 21, 2), (1, 21, 2)),
    40: ((1, 21, 2), (1, 21, 2)),
    41: ((1, 21, 2), (1, 21, 2)),
    42: ((1, 21, 2), (1, 21, 2)),
    43: ((1, 21, 2), (1, 21, 2)),
    44: ((1, 21, 2), (1, 21, 2)),
    45: ((1, 21, 4), (1, 21, 4)),
    46: ((1, 21, 4), (1, 21, 4)),
    47: ((1, 21, 4), (1, 21, 4)),
    48: ((1, 21, 4), (1, 21, 4)),
    54: ((1, 21, 5), (1, 21, 5)),
    55: ((1, 21, 5), (1, 21, 5)),
    56: ((1, 21, 5), (1, 21, 5)),
    57: ((1, 21, 5), (1, 21, 5)),
    58: ((1, 21, 5), (1, 21, 5)),
    59: ((1, 21, 5), (1, 21, 5)),
    60: ((1, 21, 5), (1, 21, 5)),
    61: ((1, 21, 5), (1, 21, 5)),
    62: ((1, 21, 5), (1, 21, 5)),
    63: ((1, 21, 5), (1, 21, 5)),
    64: ((1, 21, 6), (1, 21, 6)),
    69: ((1, 21, 7), (1, 21, 7)),
    70: ((1, 21, 7), (1, 21, 7)),
    71: ((1, 21, 7), (1, 21, 7)),
    72: ((1, 21, 7), (1, 21, 7)),
    73: ((1, 21, 7), (1, 21, 7)),
    74: ((1, 21, 7), (1, 21, 7)),
    75: ((1, 21, 7), (1, 21, 7)),
    76: ((1, 21, 7), (1, 21, 7)),
    77: ((1, 21, 7), (1, 21, 7)),
    78: ((1, 21, 7), (1, 21, 7)),
    79: ((1, 21, 7), (1, 21, 7)),
    80: ((1, 21, 7), (1, 21, 7)),
    81: ((1, 21, 8), (1, 21, 8)),
    82: ((1, 21, 8), (1, 21, 8)),
    83: ((1, 21, 8), (1, 21, 8)),
    84: ((1, 21, 8), (1, 21, 8)),
    85: ((1, 21, 8), (1, 21, 8)),
    86: ((1, 21, 8), (1, 21, 8)),
    87: ((1, 21, 8), (1, 21, 8)),
    88: ((1, 21, 8), (1, 21, 8)),
    89: ((1, 21, 8), (1, 21, 8)),
    90: ((1, 21, 8), (1, 21, 8)),
}


CONTENT_MIN_PINS = {
    "item/spyglass": (1, 17, 0),
    "item/amethyst_shard": (1, 17, 0),
    "item/music_disc_pigstep": (1, 16, 0),
    "item/netherite_ingot": (1, 16, 0),
    "item/netherite_scrap": (1, 16, 0),
    "item/echo_shard": (1, 19, 0),
    "item/disc_fragment_5": (1, 19, 0),
    "item/brush": (1, 19, 4),
    "item/netherite_upgrade_smithing_template": (1, 20, 0),
    "item/sentry_armor_trim_smithing_template": (1, 20, 0),
    "item/cherry_boat": (1, 20, 0),
    "item/bamboo_raft": (1, 20, 0),
    "item/mace": (1, 21, 0),
    "item/breeze_rod": (1, 21, 0),
    "item/trial_key": (1, 21, 0),
    "item/wind_charge": (1, 20, 5),
    "item/ominous_bottle": (1, 20, 5),
    "item/wolf_armor": (1, 20, 5),
    "item/armadillo_spawn_egg": (1, 20, 5),
    "item/pale_oak_boat": (1, 21, 4),
    "block/deepslate": (1, 17, 0),
    "block/amethyst_block": (1, 17, 0),
    "block/copper_ore": (1, 17, 0),
    "block/moss_block": (1, 17, 0),
    "block/rooted_dirt": (1, 17, 0),
    "block/mud": (1, 19, 0),
    "block/mangrove_log": (1, 19, 0),
    "block/cherry_log": (1, 20, 0),
    "block/bamboo_block": (1, 20, 0),
    "block/crafter": (1, 21, 0),
    "block/copper_bulb": (1, 21, 0),
    "block/pale_oak_log": (1, 21, 4),
    "block/creaking_heart": (1, 21, 4),
    "block/resin_clump": (1, 21, 4),
    "blocks/end_rod": (1, 9, 0),
    "blocks/chorus_plant": (1, 9, 0),
    "blocks/end_stone": (1, 9, 0),
    "blocks/structure_block": (1, 9, 0),
    "blocks/observer": (1, 11, 0),
    "blocks/shulker_box": (1, 11, 0),
    "blocks/concrete_white": (1, 12, 0),
    "blocks/concrete_powder_white": (1, 12, 0),
    "blocks/glazed_terracotta_white": (1, 12, 0),
    "items/elytra": (1, 9, 0),
    "items/end_crystal": (1, 9, 0),
    "items/shulker_shell": (1, 11, 0),
    "items/totem_of_undying": (1, 11, 0),
    "items/iron_nugget": (1, 11, 0),
    "items/knowledge_book": (1, 12, 0),
    "items/totem": (1, 11, 0),
    "blocks/slime": (1, 8, 0),
    "blocks/coarse_dirt": (1, 8, 0),
    "blocks/red_sandstone": (1, 8, 0),
    "blocks/prismarine": (1, 8, 0),
    "items/prismarine_shard": (1, 8, 0),
    "blocks/packed_ice": (1, 7, 0),
    "blocks/red_sand": (1, 7, 0),
    "blocks/log_acacia": (1, 7, 0),
    "blocks/leaves_acacia": (1, 7, 0),
    "blocks/newlog_spruce": (1, 7, 0),
    "blocks/hay_block": (1, 6, 0),
    "blocks/quartz_ore": (1, 6, 0),
    "items/lead": (1, 6, 0),
    "items/name_tag": (1, 6, 0),
}

STRUCTURE_MAX_PINS = {
    "font/glyph_sizes.bin": (1, 12, 2),
    "textures/items": (1, 12, 2),
}

STRUCTURE_MIN_PINS = {
    "textures/item": (1, 13, 0),
    "font/accented.json": (1, 13, 0),
}

STRUCTURE_EXACT_PINS = {
    "lang/en_US.lang": [("max", (1, 10, 2))],
    "lang/en_us.lang": [("min", (1, 11, 0)), ("max", (1, 12, 2))],
    "lang/en_us.json": [("min", (1, 13, 0))],
}

MAX_CEILING = (1, 21, 8)


def _collect_rel_paths(pack_root):
    found = set()
    found_low = set()
    asset_base = os.path.join(pack_root, "assets", "minecraft")
    tex_base = os.path.join(pack_root, "textures")
    bases = []
    if os.path.isdir(asset_base):
        bases.append(asset_base)
    if os.path.isdir(tex_base):
        bases.append(pack_root)
    for base in bases:
        for dirpath, dirnames, files in os.walk(base):
            rel = os.path.relpath(dirpath, base).replace(os.sep, "/")
            prefix = "" if rel == "." else rel + "/"
            for d in dirnames:
                found.add(prefix + d)
                found_low.add((prefix + d).lower())
            for f in files:
                found.add(prefix + f)
                found_low.add((prefix + f).lower())
            if len(found) > 60000:
                return found, found_low
    return found, found_low


def _tree_bounds(pack_root, rels, rels_low):
    mins = []
    maxs = []
    for path, ver in STRUCTURE_MIN_PINS.items():
        if any(r == path or r.startswith(path + "/") for r in rels_low):
            mins.append(ver)
    for path, ver in STRUCTURE_MAX_PINS.items():
        if any(r == path or r.startswith(path + "/") for r in rels_low):
            maxs.append(ver)
    for path, sides in STRUCTURE_EXACT_PINS.items():
        if path in rels:
            for side, ver in sides:
                if side == "min":
                    mins.append(ver)
                else:
                    maxs.append(ver)
    has_multipart = False
    has_builtin_generated = False
    blockstates = os.path.join(pack_root, "assets", "minecraft", "blockstates")
    if os.path.isdir(blockstates):
        for dirpath, _, files in os.walk(blockstates):
            for f in files:
                if not f.endswith(".json"):
                    continue
                data = read_json(os.path.join(dirpath, f))
                if isinstance(data, dict):
                    if "multipart" in data:
                        has_multipart = True
                    variants = data.get("variants")
                    if isinstance(variants, dict):
                        for v in variants.values():
                            items = v if isinstance(v, list) else [v]
                            for it in items:
                                if isinstance(it, dict) and str(it.get("model", "")).startswith("block/"):
                                    has_builtin_generated = has_builtin_generated or "namespace" not in str(it.get("model", ""))
                    if has_multipart:
                        break
        if has_multipart:
            mins.append((1, 13, 2))
    models_item = None
    for cand in (
        os.path.join(pack_root, "assets", "minecraft", "models", "item"),
        os.path.join(pack_root, "assets", "minecraft", "models"),
    ):
        if os.path.isdir(cand):
            models_item = cand
            break
    if models_item:
        checked = 0
        for dirpath, _, files in os.walk(models_item):
            for f in files:
                if not f.endswith(".json") or checked >= 60:
                    continue
                checked += 1
                data = read_json(os.path.join(dirpath, f))
                if isinstance(data, dict):
                    parent = str(data.get("parent", ""))
                    if "builtin/generated" in parent:
                        maxs.append((1, 8, 9))
            if maxs:
                break
    lo = max(mins) if mins else None
    hi = min(maxs) if maxs else None
    return lo, hi, len(rels)


def _content_pins(pack_root, rels):
    pins = []
    for path, ver in CONTENT_MIN_PINS.items():
        probe = "textures/" + path + ".png"
        if probe not in rels:
            continue
        sub, name = path.split("/", 1)
        if sub == "item":
            real = os.path.join(pack_root, "assets", "minecraft", "textures", "item", name + ".png")
            legacy = os.path.join(pack_root, "assets", "minecraft", "textures", "items", name + ".png")
        elif sub == "block":
            real = os.path.join(pack_root, "assets", "minecraft", "textures", "block", name + ".png")
            legacy = os.path.join(pack_root, "assets", "minecraft", "textures", "blocks", name + ".png")
        elif sub == "blocks":
            real = None
            legacy = os.path.join(pack_root, "assets", "minecraft", "textures", "blocks", name + ".png")
        else:
            real = None
            legacy = None
        if (real and os.path.isfile(real)) or (legacy and os.path.isfile(legacy)):
            pins.append(ver)
    return pins


VERSION_TEXT_RE = re.compile(r"\b1\.(\d{1,2})(?:\.(\d{1,2}))?(?:\.\d{1,2})?\b")


def _version_hits(text, weight, votes, notes):
    if not text:
        return
    hits = VERSION_TEXT_RE.findall(text)
    if not hits:
        return
    versions = []
    for major, minor in hits:
        versions.append(_vt("1.%s.%s" % (major, minor or "0")))
    best = max(versions)
    if best > (1, 8, 8) or len(versions) > 1:
        votes.append({"weight": weight, "exact": best, "lo": None, "hi": None})
        notes.append("version text %s" % _fmt(best))


def _fmt(v):
    out = ".".join(str(x) for x in v[:3])
    if len(v) > 3 and v[3]:
        out += ".%d" % v[3]
    return out


def _label_classic(v):
    return len(v) >= 2 and v[0] == 1 and v[1] in (6, 7, 8)


def detect(pack_root, name_hint=""):
    mcmeta = read_json(os.path.join(pack_root, "pack.mcmeta"))
    fmt = None
    description = ""
    if isinstance(mcmeta, dict):
        pack_section = mcmeta.get("pack", {})
        if not isinstance(pack_section, dict):
            pack_section = {}
        fmt = pack_section.get("pack_format", mcmeta.get("pack_format"))
        if fmt is not None:
            try:
                fmt = int(fmt)
            except (TypeError, ValueError):
                fmt = None
        description = pack_section.get("description", mcmeta.get("description", ""))
        if isinstance(description, dict):
            description = description.get("text", "") or json_text(description)
        description = str(description or "")

    rels, rels_low = _collect_rel_paths(pack_root)
    lo, hi, rel_count = _tree_bounds(pack_root, rels, rels_low)
    pins = _content_pins(pack_root, rels_low)
    pin_max = max(pins) if pins else None

    votes = []
    notes = []

    fmt_range = FORMAT_RANGES.get(fmt)
    if fmt_range:
        votes.append({"weight": 60, "lo": fmt_range[0], "hi": fmt_range[1], "exact": None})

    if pin_max:
        votes.append({"weight": 40 + min(40, 5 * len(pins)), "lo": pin_max, "hi": None, "exact": None})
        notes.append("content first seen in %s" % _fmt(pin_max))

    if lo:
        votes.append({"weight": 25, "lo": lo, "hi": None, "exact": None})
        notes.append("layout needs at least %s" % _fmt(lo))
    if hi:
        votes.append({"weight": 25, "lo": None, "hi": hi, "exact": None})
        notes.append("layout stopped at %s" % _fmt(hi))

    _version_hits(description, 30, votes, notes)
    readme_text = _read_readme(pack_root)
    _version_hits(readme_text, 12, votes, notes)
    pack_name = name_hint or os.path.basename(os.path.normpath(pack_root))
    _version_hits(pack_name, 35, votes, notes)

    window_lo, window_hi = _narrow(votes)

    version = _decide(pack_root, fmt, fmt_range, pin_max, window_lo, window_hi, lo, hi)

    result = {
        "version": version,
        "format": fmt,
        "classic": _label_classic(_vt(version.split(" ")[0]) if version else (1, 8, 9)),
        "has_textures": rel_count > 0,
        "description": description,
        "notes": notes,
    }
    return result


def json_text(value):
    import json as _json

    try:
        return _json.dumps(value)
    except Exception:
        return ""


def _read_readme(pack_root):
    for name in sorted(os.listdir(pack_root)) if os.path.isdir(pack_root) else []:
        low = name.lower()
        if low.startswith("readme") or low in ("credits.txt", "credits.md", "license.txt"):
            try:
                with open(os.path.join(pack_root, name), "r", encoding="utf-8", errors="ignore") as f:
                    return f.read(4000)
            except OSError:
                return ""
    return ""


def _vote_score(vote, version):
    if vote.get("exact") is not None:
        return vote["weight"] if version == vote["exact"] else 0
    score = 0
    lo = vote.get("lo")
    hi = vote.get("hi")
    if lo and version < lo:
        return 0
    if hi and version > hi:
        return 0
    if lo and version >= lo:
        score += vote["weight"]
    if hi and version <= hi:
        score += vote["weight"]
    return score


def _narrow(votes):
    lo = None
    hi = None
    for v in votes:
        if v.get("exact") is not None:
            continue
        if v.get("lo") and (lo is None or v["lo"] > lo):
            lo = v["lo"]
        if v.get("hi") and (hi is None or v["hi"] < hi):
            hi = v["hi"]
    return lo, hi


def _decide(pack_root, fmt, fmt_range, pin_max, window_lo, window_hi, struct_lo, struct_hi):
    if window_lo and window_hi and window_lo == window_hi:
        return _fmt(window_lo)
    if window_lo and window_hi and window_lo < window_hi:
        return "%s - %s" % (_fmt(window_lo), _fmt(window_hi))
    if pin_max:
        return _fmt(pin_max)
    if fmt_range:
        lo, hi = fmt_range
        if window_lo and window_lo > lo:
            lo = window_lo
        if window_hi and window_hi < hi:
            hi = window_hi
        if lo == hi:
            return _fmt(lo)
        return "%s - %s" % (_fmt(lo), _fmt(hi))
    if struct_lo and struct_hi:
        if struct_lo == struct_hi:
            return _fmt(struct_lo)
        return "%s - %s" % (_fmt(struct_lo), _fmt(struct_hi))
    if struct_lo:
        return _fmt(struct_lo) + "+"
    if struct_hi:
        return "up to " + _fmt(struct_hi)
    if os.path.isdir(os.path.join(pack_root, "assets", "minecraft", "textures")):
        return "1.8.9 (assumed classic layout)"
    return "1.8.9 (assumed)"


def detect_with_root(pack_root):
    return detect(pack_root)
