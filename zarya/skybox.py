import os
import re

PROVIDERS = ("optifine", "mcpatcher")

WORLD_LABELS = {
    "world0": "Overworld",
    "world-1": "Nether",
    "world1": "The End",
    "world-2": "Custom Dim -2",
    "world2": "Custom Dim 2",
    "world-3": "Custom Dim -3",
    "world3": "Custom Dim 3",
}

ENV_LABELS = {
    "sun.png": "Sun",
    "moon_phases.png": "Moon Phases",
    "moon.png": "Moon",
    "end_sky.png": "End Sky",
    "rain.png": "Rain",
    "snow.png": "Snow",
    "clouds.png": "Clouds",
    "thunder.png": "Thunder",
}

_LEGACY_ENV_NAMES = re.compile(
    r"^(sky|sun|moon|clouds|cloud|rain|snow|thunder|end_sky)[^/]*\.png$", re.IGNORECASE)

_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")
_SOURCE_KEY_RE = re.compile(r"^(?:source(?:\.(\d+))?)$", re.IGNORECASE)

DAWN_END = 8 * 60
DAY_END = 16 * 60 + 30
DUSK_END = 20 * 60
ALL_DAY_MIN = 21 * 60


def parse_time(value):
    match = _TIME_RE.match(str(value or "").strip())
    if not match:
        return None
    hours = int(match.group(1)) % 24
    minutes = int(match.group(2))
    return "%02d:%02d" % (hours, minutes)


def _minutes(text):
    if not text:
        return None
    parts = text.split(":")
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError):
        return None


def classify_phase(start, fade_in, fade_out_start, fade_out):
    begin = _minutes(start)
    finish = _minutes(fade_out) or _minutes(fade_out_start) or _minutes(fade_in) or begin
    if begin is None or finish is None:
        return "all"
    if finish <= begin:
        finish += 1440
    if finish - begin >= ALL_DAY_MIN:
        return "all"
    middle = (begin + finish) // 2 % 1440
    if middle < DAWN_END:
        return "dawn" if middle >= 4 * 60 - 30 else "night"
    if middle < DAY_END:
        return "day"
    if middle < DUSK_END:
        return "dusk"
    return "night"


def parse_properties(path):
    props = {}
    try:
        with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                props[key.strip()] = value.strip()
    except OSError:
        pass
    return props


def _resolve_source(root, world_dir, value):
    value = str(value or "").strip()
    if not value:
        return None
    candidates = [
        os.path.join(world_dir, value),
        os.path.join(root, value),
        os.path.join(root, "assets", "minecraft", value),
        os.path.join(root, "assets", "minecraft", "optifine", "sky", value),
        os.path.join(root, "assets", "minecraft", "mcpatcher", "sky", value),
        os.path.join(root, "environment", value),
    ]
    for cand in candidates:
        if os.path.isfile(cand):
            return cand
    return None


def _layer_from_props(root, world_dir, props_path):
    props = parse_properties(props_path)
    declared = []
    numbered = []
    plain = None
    for key in props:
        match = _SOURCE_KEY_RE.match(key)
        if not match:
            continue
        if match.group(1) is None:
            plain = props[key]
        else:
            numbered.append((int(match.group(1)), props[key]))
    for _, value in sorted(numbered):
        declared.append(value)
    if plain is not None:
        declared.append(plain)
    sources = []
    missing = []
    for value in declared:
        resolved = _resolve_source(root, world_dir, value)
        if resolved:
            sources.append(resolved)
        else:
            missing.append(value)
    if not declared:
        base = os.path.splitext(props_path)[0]
        for ext in (".png", ".tga"):
            cand = base + ext
            if os.path.isfile(cand):
                sources.append(cand)
                break
    if not sources and not missing:
        return None
    start = parse_time(props.get("startFadeIn")) or "00:00"
    fade_in = parse_time(props.get("endFadeIn")) or start
    fade_out_start = parse_time(props.get("startFadeOut")) or fade_in
    fade_out = parse_time(props.get("endFadeOut")) or start
    layer = {
        "name": os.path.basename(props_path)[:-len(".properties")],
        "file": os.path.basename(props_path),
        "start": start,
        "fade_in": fade_in,
        "fade_out_start": fade_out_start,
        "fade_out": fade_out,
        "rotate": str(props.get("rotate", "true")).lower() != "false",
        "speed": props.get("speed"),
        "axis": props.get("axis"),
        "weather": props.get("weather"),
        "days": props.get("days"),
        "blend": props.get("blend"),
        "sources": sources,
        "missing_sources": missing,
        "missing": not sources,
    }
    layer["phase"] = classify_phase(start, fade_in, fade_out_start, fade_out)
    return layer


def _layer_from_png(png_path, start="00:00"):
    return {
        "name": os.path.basename(png_path)[:-4],
        "file": os.path.basename(png_path),
        "start": start,
        "fade_in": start,
        "fade_out_start": start,
        "fade_out": start,
        "rotate": True,
        "speed": None,
        "axis": None,
        "weather": None,
        "days": None,
        "blend": None,
        "sources": [png_path],
        "missing_sources": [],
        "missing": False,
        "phase": "all",
    }


def _scan_world(root, provider, world):
    world_dir = os.path.join(root, "assets", "minecraft", provider, "sky", world)
    if not os.path.isdir(world_dir):
        return None
    entries = sorted(os.listdir(world_dir))
    pngs = []
    props_files = []
    for name in entries:
        low = name.lower()
        if low.endswith(".png"):
            pngs.append(os.path.join(world_dir, name))
        elif low.endswith(".properties"):
            props_files.append(os.path.join(world_dir, name))
    claimed = set()
    layers = []
    for props_path in props_files:
        layer = _layer_from_props(root, world_dir, props_path)
        if layer:
            layers.append(layer)
            for src in layer["sources"]:
                claimed.add(os.path.normcase(os.path.abspath(src)))
    for png_path in pngs:
        if os.path.normcase(os.path.abspath(png_path)) not in claimed:
            layers.append(_layer_from_png(png_path))
    if not layers:
        return None
    layers.sort(key=lambda item: (item["start"], item["name"]))
    folder_rel = os.path.relpath(world_dir, root).replace(os.sep, "/")
    for i, layer in enumerate(layers):
        layer["key"] = "%s#%d" % (folder_rel, i)
        layer["usable"] = bool(layer["sources"])
    return {
        "provider": provider,
        "world": world,
        "world_label": WORLD_LABELS.get(world, world.replace("world", "Dim ")),
        "layers": layers[:24],
        "layer_count": len(layers),
        "folder": folder_rel,
    }


def _scan_clouds(root, provider):
    base = os.path.join(root, "assets", "minecraft", provider)
    if not os.path.isdir(base):
        return None
    for name in sorted(os.listdir(base)):
        low = name.lower()
        if low in ("cloud", "clouds") and os.path.isdir(os.path.join(base, name)):
            cloud_dir = os.path.join(base, name)
            layers = []
            for entry in sorted(os.listdir(cloud_dir)):
                if entry.lower().endswith(".png"):
                    layers.append(_layer_from_png(os.path.join(cloud_dir, entry)))
            if layers:
                folder_rel = os.path.relpath(cloud_dir, root).replace(os.sep, "/")
                for i, layer in enumerate(layers):
                    layer["key"] = "%s#%d" % (folder_rel, i)
                    layer["usable"] = bool(layer["sources"])
                return {
                    "provider": provider,
                    "world": "clouds",
                    "world_label": "Clouds",
                    "layers": layers[:8],
                    "layer_count": len(layers),
                    "folder": folder_rel,
                }
    return None


def _scan_environment(root):
    found = []
    seen = set()
    candidates = [
        (os.path.join(root, "assets", "minecraft", "textures", "environment"), True),
        (os.path.join(root, "textures", "environment"), True),
        (os.path.join(root, "environment"), False),
    ]
    for env_dir, vanilla in candidates:
        norm = os.path.normcase(os.path.abspath(env_dir))
        if not os.path.isdir(env_dir) or norm in seen:
            continue
        seen.add(norm)
        for name in sorted(os.listdir(env_dir)):
            if not name.lower().endswith(".png"):
                continue
            if not vanilla and not _LEGACY_ENV_NAMES.match(name):
                continue
            found.append({
                "file": name,
                "label": ENV_LABELS.get(name.lower(), name[:-4]),
                "path": os.path.join(env_dir, name),
                "kind": ENV_LABELS.get(name.lower(), "custom"),
                "legacy": not vanilla,
            })
    return found


def detect(root):
    skies = []
    for provider in PROVIDERS:
        sky_base = os.path.join(root, "assets", "minecraft", provider, "sky")
        if os.path.isdir(sky_base):
            for world in sorted(os.listdir(sky_base)):
                if not world.lower().startswith("world"):
                    continue
                group = _scan_world(root, provider, world)
                if group:
                    skies.append(group)
        cloud_group = _scan_clouds(root, provider)
        if cloud_group:
            skies.append(cloud_group)
    environment = _scan_environment(root)
    total_layers = sum(group["layer_count"] for group in skies)
    missing_layers = sum(
        1 for group in skies for layer in group["layers"] if layer.get("missing"))
    return {
        "skies": skies,
        "environment": environment,
        "total_layers": total_layers,
        "missing_layers": missing_layers,
        "total": len(skies) + len(environment),
    }


def find_layer(info, key):
    key = str(key or "").strip()
    if not key or not info:
        return None
    for group in info.get("skies", []):
        for layer in group["layers"]:
            if layer.get("key") == key and layer.get("usable"):
                return layer
    return None


def summarize(info):
    if not info:
        return ""
    parts = []
    if info["skies"]:
        worlds = ", ".join(group["world_label"] for group in info["skies"])
        total = info["total_layers"]
        missing = info.get("missing_layers", 0)
        line = "%d custom sky group(s) across %s - %d sky layer(s)" % (
            len(info["skies"]), worlds, total)
        if missing:
            line += " (%d without texture in the pack)" % missing
        parts.append(line)
    if info["environment"]:
        parts.append("%d environment texture(s)" % len(info["environment"]))
    return " + ".join(parts)
