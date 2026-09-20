import os

from PIL import Image

from .utils import read_json, write_json, load_snapshot
from .textures import resolve_block, resolve_item, LIQUID_SOURCES, _load_stems


def _collect(java_root):
    tex = os.path.join(java_root, "assets", "minecraft", "textures")
    if not os.path.isdir(tex):
        tex = os.path.join(java_root, "textures")
    out = []
    if not os.path.isdir(tex):
        return out
    for dirpath, _, files in os.walk(tex):
        for f in files:
            if not f.lower().endswith(".png"):
                continue
            path = os.path.join(dirpath, f)
            mcmeta = path + ".mcmeta"
            anim = _parse_mcmeta(mcmeta) if os.path.isfile(mcmeta) else {}
            strip = _strip_frames(path) is not None
            if anim or strip:
                rel = os.path.relpath(dirpath, tex).replace(os.sep, "/")
                top = rel.split("/")[0] if rel != "." else ""
                out.append((path, top, anim))
    return out


def _strip_frames(path):
    try:
        w, h = Image.open(path).size
    except Exception:
        return None
    if w > 0 and h > w and h % w == 0:
        return h // w
    return None


def _vanilla_tile_map():
    data = load_snapshot("vanilla_flipbook.json")
    tiles = {}
    if isinstance(data, list):
        for e in data:
            if isinstance(e, dict) and e.get("flipbook_texture") and e.get("atlas_tile"):
                tiles[str(e["flipbook_texture"]).lower()] = str(e["atlas_tile"])
    return tiles


def _parse_mcmeta(path):
    anim = read_json(path) or {}
    if isinstance(anim, dict) and isinstance(anim.get("animation"), dict):
        anim = anim["animation"]
    if not isinstance(anim, dict):
        return {}
    return anim


def _clean_frames(anim):
    frames = anim.get("frames")
    if not isinstance(frames, list) or not frames:
        return None
    clean = []
    for fr in frames:
        if isinstance(fr, dict) and "index" in fr:
            idx = fr["index"]
            if isinstance(idx, int):
                clean.append(idx)
        elif isinstance(fr, int):
            clean.append(fr)
    return clean or None


def _ticks(anim):
    ticks = anim.get("frametime", 1)
    try:
        return max(1, int(ticks))
    except (TypeError, ValueError):
        return 1


def _output_stems(stem, top, bed_blocks, bed_items):
    stems = [stem]
    if top in ("block", "blocks"):
        target = resolve_block(stem, bed_blocks)
        if target:
            stems.append(target)
        if stem in LIQUID_SOURCES:
            stems.append(LIQUID_SOURCES[stem][0])
    elif top in ("item", "items"):
        target = resolve_item(stem, bed_items)
        if target:
            stems.append(target)
    seen = []
    for s in stems:
        if s not in seen:
            seen.append(s)
    return seen


def _terrain_key(out_rel, out_stem):
    if out_rel == "blocks":
        return out_stem
    if out_rel.startswith("blocks/"):
        sub = out_rel[len("blocks/"):]
        return (sub + "/" + out_stem).replace("/", "_")
    return out_stem


def port_flipbooks(java_root, bed_root, log):
    entries = _collect(java_root)
    tex_dst = os.path.join(bed_root, "textures")
    if not entries:
        log("Animations: no animated textures in your pack - Bedrock's own flipbook list stays untouched")
        return 0
    if not os.path.isdir(tex_dst):
        log("Animations: pack has %d animated textures but nothing was ported for them" % len(entries))
        return 0

    stems = _load_stems()
    vanilla_tiles = _vanilla_tile_map()

    output_index = {}
    for dirpath, _, files in os.walk(tex_dst):
        rel = os.path.relpath(dirpath, tex_dst).replace(os.sep, "/")
        for f in files:
            if f.lower().endswith(".png"):
                stem = f[:-4].lower()
                output_index.setdefault(stem, []).append(
                    (rel, os.path.join(dirpath, f)))

    flipbook = []
    converted = 0
    collapsed = 0
    missed = 0
    names = []

    for png_path, top, anim in entries:
        stem = os.path.splitext(os.path.basename(png_path))[0].lower()
        candidates = _output_stems(stem, top, stems["blocks"], stems["items"])
        targets = []
        for cand in candidates:
            for out_rel, out_path in output_index.get(cand, []):
                if (out_rel, out_path) not in targets:
                    targets.append((out_rel, out_path))
        if not targets:
            missed += 1
            continue

        if top in ("block", "blocks"):
            for out_rel, out_path in targets:
                frames = _strip_frames(out_path)
                if frames is None:
                    try:
                        img = Image.open(out_path)
                        if img.height <= img.width:
                            continue
                        if _collapse(out_path, log):
                            collapsed += 1
                    except Exception:
                        pass
                    continue
                out_stem = os.path.splitext(os.path.basename(out_path))[0].lower()
                path_key = "textures/" + out_rel + "/" + out_stem
                tile = vanilla_tiles.get(path_key) or _terrain_key(out_rel, out_stem)
                entry = {
                    "flipbook_texture": path_key,
                    "atlas_tile": tile,
                    "ticks_per_frame": _ticks(anim) if anim else 1,
                }
                if anim:
                    frames_list = _clean_frames(anim)
                    if frames_list:
                        entry["frames"] = frames_list
                flipbook.append(entry)
                converted += 1
                if len(names) < 6:
                    names.append(stem)
        else:
            for out_rel, out_path in targets:
                if _strip_frames(out_path) is not None:
                    if _collapse(out_path, log):
                        collapsed += 1
                    break

    if converted:
        write_json(os.path.join(tex_dst, "flipbook_textures.json"), flipbook)
        label = (", ".join(names) + (", ..." if converted > len(names) else "")) if names else ""
        log("Animations: %d of your pack's animations converted with their own timing (%s)" % (converted, label))
        log("Animations: flipbook_textures.json holds only your pack's entries - no vanilla animation data shipped")
    else:
        log("Animations: none of your animated textures land in the block atlas - no flipbook file written")
    if collapsed:
        log("Animations: %d strips flattened to frame 1 (Bedrock cannot animate item, entity or HUD slots)" % collapsed)
    if missed:
        log("Animations: %d animated textures had no Bedrock slot and were skipped" % missed)
    return converted


def flatten_strips(bed_root, log):
    tex_dst = os.path.join(bed_root, "textures")
    if not os.path.isdir(tex_dst):
        return 0
    count = 0
    for dirpath, _, files in os.walk(tex_dst):
        rel = os.path.relpath(dirpath, tex_dst).replace(os.sep, "/")
        top = rel.split("/")[0] if rel != "." else ""
        if top == "ui":
            continue
        for f in files:
            if not f.lower().endswith(".png"):
                continue
            path = os.path.join(dirpath, f)
            if _strip_frames(path) is not None:
                if _collapse(path, log):
                    count += 1
    if count:
        log("Animations: option off - %d texture strips flattened to frame 1 so nothing renders glitched" % count)
    return count


def _collapse(path, log):
    try:
        img = Image.open(path).convert("RGBA")
        crop = img.crop((0, 0, img.width, img.width))
        crop.save(path, format="PNG")
        log("Animated %s: kept frame 1 (Bedrock renders this slot static)" % os.path.basename(path))
        return True
    except Exception:
        return False
