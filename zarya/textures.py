import os

from .constants import (
    BLOCK_SPECIAL, ITEM_SPECIAL, CORAL_COLORS, FLOWERS, COLORS, EXTRA_BLOCK_COPIES, EGG_NAMES,
)
from .utils import copy_file, load_snapshot, write_json, sanitize_png, next_power_of_two

LIQUID_SOURCES = {
    "water_still": ("water_still_grey", 16),
    "water_flow": ("water_flow_grey", 32),
    "lava_still": ("lava_still", 16),
    "lava_flow": ("lava_flow", 32),
}


def _open_rgba(path):
    try:
        from PIL import Image
        return Image.open(path).convert("RGBA")
    except Exception:
        return None


def _ensure_min_width(img, min_width):
    if img.width >= min_width:
        return img
    factor = min_width / float(img.width)
    return img.resize((min_width, max(min_width, int(round(img.height * factor)))), Image.NEAREST)


def _find_tex_root(java_root):
    candidates = [
        os.path.join(java_root, "assets", "minecraft", "textures"),
        os.path.join(java_root, "textures"),
        os.path.join(java_root, "minecraft", "textures"),
    ]
    for cand in candidates:
        if os.path.isdir(cand):
            return cand
    return None


def _port_liquids(tex_src, tex_dst, log):
    count = 0
    for sub in ("block", "blocks"):
        src_base = os.path.join(tex_src, sub)
        if not os.path.isdir(src_base):
            continue
        for stem, (out_name, min_w) in LIQUID_SOURCES.items():
            src = os.path.join(src_base, stem + ".png")
            if not os.path.isfile(src):
                continue
            img = _open_rgba(src)
            if img is None:
                continue
            img = _ensure_min_width(img, min_w)
            out = os.path.join(tex_dst, "blocks", out_name + ".png")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            img.save(out)
            count += 1
            if stem == "water_still":
                cauldron = os.path.join(tex_dst, "blocks", "cauldron_water.png")
                img.save(cauldron)
                count += 1
            log("Liquid: %s -> blocks/%s.png copied as-is (Bedrock tints water per biome), min width %d" % (
                stem, out_name, min_w))
    return count


def _load_stems():
    data = load_snapshot("bedrock_stems.json")
    return {
        "blocks": set(data.get("blocks", [])),
        "items": set(data.get("items", [])),
    }


def _coral_candidates(name):
    for species, color in CORAL_COLORS.items():
        if name.startswith(species + "_"):
            tail = name[len(species) + 1:]
            if tail == "coral":
                return ["coral_plant_" + color]
            if tail == "coral_block":
                return ["coral_" + color]
            if tail == "coral_fan":
                return ["coral_fan_" + color]
            if tail == "coral_wall_fan":
                return ["coral_fan_" + color]
            if tail == "dead_coral_block":
                return ["coral_" + color + "_dead"]
            if tail == "dead_coral_fan":
                return ["coral_fan_" + color + "_dead"]
            if tail == "dead_coral_wall_fan":
                return ["coral_fan_" + color + "_dead"]
    return []


def _pattern_candidates(name):
    c = []
    if name.endswith("_planks"):
        c.append("planks_" + name[:-7])
    if name.endswith("_log"):
        c.append("log_" + name[:-4])
    if name.endswith("_log_top"):
        c.append("log_" + name[:-8] + "_top")
    if name.endswith("_leaves"):
        c.append("leaves_" + name[:-7])
    if name.endswith("_sapling"):
        c.append("sapling_" + name[:-8])
    if name.endswith("_wool") and name[:-5] in COLORS:
        c.append("wool_colored_" + name[:-5])
    if name.endswith("_carpet") and name[:-7] in COLORS:
        c.append("carpet_colored_" + name[:-7])
    if name.endswith("_terracotta"):
        base = name[:-10]
        if name.endswith("_glazed_terracotta"):
            c.append("glazed_terracotta_" + name[:-21])
        elif base in COLORS:
            c.append("hardened_clay_stained_" + base)
    if name.endswith("_concrete_powder") and name[:-16] in COLORS:
        c.append("concrete_powder_" + name[:-16])
    elif name.endswith("_concrete") and name[:-9] in COLORS:
        c.append("concrete_" + name[:-9])
    if name.endswith("_stained_glass_pane_top") and name[:-23] in COLORS:
        c.append("glass_pane_top_" + name[:-23])
    elif name.endswith("_stained_glass") and name[:-14] in COLORS:
        c.append("glass_" + name[:-14])
    if name.endswith("_door_top"):
        c.append("door_" + name[:-9] + "_upper")
        c.append(name[:-9] + "_door_upper")
    if name.endswith("_door_bottom"):
        c.append("door_" + name[:-12] + "_lower")
        c.append(name[:-12] + "_door_lower")
    if name.endswith("_trapdoor") and name[:-9] not in ("iron", "copper"):
        c.append("trapdoor_" + name[:-9])
    if name.endswith("_terracotta") is False and name.endswith("_candle"):
        c.append("candle_" + name[:-7])
    if name.endswith("_stage") is False:
        for prefix in ("beetroots_stage", "carrots_stage", "potatoes_stage", "wheat_stage",
                       "cocoa_stage", "nether_wart_stage", "sweet_berry_bush_stage"):
            if name.startswith(prefix) and name[len(prefix):].isdigit():
                c.append(prefix + "_" + name[len(prefix):])
    if name in FLOWERS:
        c.append(FLOWERS[name])
    if name.startswith("potted_"):
        c.append(name + "_particle")
        c.append("flower_pot")
    if name.endswith("_bed_head_east") or name.endswith("_bed_head_south") or \
       name.endswith("_bed_head_west") or name.endswith("_bed_head_up"):
        c.append("bed_head_top")
    if name.endswith("_bed_foot_east") or name.endswith("_bed_foot_south") or \
       name.endswith("_bed_foot_west") or name.endswith("_bed_foot_up"):
        c.append("bed_feet_top")
    if name == "smooth_stone_slab_side":
        c.append("stone_slab_side")
    if name.endswith("_slab_top"):
        c.append("double_" + name[:-9] + "_top")
    if name.endswith("_slab_side"):
        c.append("double_" + name[:-10] + "_side")
    return c


def resolve_block(name, bedrock_stems):
    if name in bedrock_stems:
        return name
    if name in BLOCK_SPECIAL:
        for cand in BLOCK_SPECIAL[name]:
            if cand in bedrock_stems:
                return cand
    for cand in _coral_candidates(name):
        if cand in bedrock_stems:
            return cand
    for cand in _pattern_candidates(name):
        if cand in bedrock_stems:
            return cand
    return None


def resolve_item(name, bedrock_stems):
    if name in bedrock_stems:
        return name
    if name in ITEM_SPECIAL:
        for cand in ITEM_SPECIAL[name]:
            if cand in bedrock_stems:
                return cand
    if name.startswith("music_disc_"):
        cand = "record_" + name[len("music_disc_"):]
        if cand in bedrock_stems:
            return cand
    if name.startswith("music_disc_") is False and name.endswith("_door") and name != "iron_door":
        wood = name[:-5]
        for cand in ("door_" + wood, "door_wood" if wood == "oak" else None):
            if cand and cand in bedrock_stems:
                return cand
    if name.endswith("_boat"):
        wood = name[:-5]
        for cand in ("boat_" + wood, "boat_" + wood.replace("_", ""), "boat"):
            if cand in bedrock_stems:
                return cand
    if name.endswith("_chest_boat"):
        wood = name[:-11]
        cand = wood + "_chest_boat"
        if cand in bedrock_stems:
            return cand
    if name.endswith("_hanging_sign"):
        wood = name[:-13]
        for cand in (name, wood + "_hanging_sign"):
            if cand in bedrock_stems:
                return cand
    if name.endswith("_sign"):
        wood = name[:-5]
        for cand in ("sign_" + wood, "sign"):
            if cand in bedrock_stems:
                return cand
    if name.endswith("_dye") and name[:-4] in COLORS:
        for cand in ("dye_powder_" + name[:-4] + "_new", "dye_powder_" + name[:-4]):
            if cand in bedrock_stems:
                return cand
    if name.endswith("_spawn_egg"):
        entity = name[:-10]
        cand_entity = EGG_NAMES.get(entity, entity)
        for cand in ("egg_" + cand_entity,):
            if cand in bedrock_stems:
                return cand
    if name.startswith("clock_") and name[6:].isdigit():
        if "clock_item" in bedrock_stems:
            return "clock_item"
    if name.startswith("compass_") and name[8:].isdigit():
        if "compass_item" in bedrock_stems:
            return "compass_item"
    if name.endswith("_horse_armor"):
        if name in bedrock_stems:
            return name
    return None


def _armor_target(stem):
    if stem.endswith("_layer_1"):
        base = stem[:-8]
        base = {"chainmail": "chain", "leather": "cloth"}.get(base, base)
        return base + "_1"
    if stem.endswith("_layer_2"):
        base = stem[:-8]
        base = {"chainmail": "chain", "leather": "cloth"}.get(base, base)
        return base + "_2"
    return stem


def _entity_target(rel, stem):
    if rel == "chest":
        return {"normal": "normal", "normal_double": "double_normal", "ender": "ender",
                "trapped": "trapped", "christmas": "christmas"}.get(stem, stem)
    if rel == "horse" and stem in ("horse", "donkey", "mule", "skeleton_horse", "zombie_horse"):
        return stem
    if stem.endswith("_layer_1") or stem.endswith("_layer_2"):
        return _armor_target(stem)
    if rel == "armor":
        return _armor_target(stem)
    return stem


def port_textures(java_root, bed_root, options, log, progress):
    tex_src = _find_tex_root(java_root)
    tex_dst = os.path.join(bed_root, "textures")
    if not tex_src:
        log("No Java textures folder found")
        return
    liquids_done = set()
    if options.get("flipbook", True) or options.get("blocks", True):
        n = _port_liquids(tex_src, tex_dst, log)
        if n:
            liquids_done = set(LIQUID_SOURCES.keys())
    stats = {"blocks": 0, "items": 0, "entity": 0, "misc": 0, "renamed": 0, "custom": 0}
    stems = _load_stems()
    bed_blocks = stems["blocks"]
    bed_items = stems["items"]

    block_dir = os.path.join(tex_dst, "blocks")
    item_dir = os.path.join(tex_dst, "items")

    for sub in ("block", "blocks"):
        src = os.path.join(tex_src, sub)
        if not os.path.isdir(src):
            continue
        for dirpath, _, files in os.walk(src):
            rel = os.path.relpath(dirpath, src).replace(os.sep, "/")
            for f in files:
                if not f.lower().endswith(".png"):
                    continue
                stem = f[:-4].lower()
                if stem in liquids_done:
                    continue
                target = resolve_block(stem, bed_blocks)
                dst_dir = os.path.join(block_dir, rel) if rel != "." else block_dir
                if target:
                    copy_file(os.path.join(dirpath, f), os.path.join(dst_dir, target + ".png"))
                    if target != stem:
                        stats["renamed"] += 1
                    stats["blocks"] += 1
                    for extra in EXTRA_BLOCK_COPIES.get(stem, []):
                        if rel == "." and extra in bed_blocks:
                            copy_file(os.path.join(dirpath, f), os.path.join(block_dir, extra + ".png"))
                        elif rel == "." and extra == "flame_atlas":
                            copy_file(os.path.join(dirpath, f), os.path.join(tex_dst, "flame_atlas.png"))
                else:
                    copy_file(os.path.join(dirpath, f), os.path.join(dst_dir, f))
                    stats["custom"] += 1

    for sub in ("item", "items"):
        src = os.path.join(tex_src, sub)
        if not os.path.isdir(src):
            continue
        for dirpath, _, files in os.walk(src):
            rel = os.path.relpath(dirpath, src).replace(os.sep, "/")
            for f in files:
                if not f.lower().endswith(".png"):
                    continue
                stem = f[:-4].lower()
                target = resolve_item(stem, bed_items)
                dst_dir = os.path.join(item_dir, rel) if rel != "." else item_dir
                if target:
                    copy_file(os.path.join(dirpath, f), os.path.join(dst_dir, target + ".png"))
                    if target != stem:
                        stats["renamed"] += 1
                    stats["items"] += 1
                else:
                    copy_file(os.path.join(dirpath, f), os.path.join(dst_dir, f))
                    stats["custom"] += 1

    if options.get("entities", True):
        for sub in ("entity", "entities"):
            src = os.path.join(tex_src, sub)
            if not os.path.isdir(src):
                continue
            for dirpath, _, files in os.walk(src):
                rel = os.path.relpath(dirpath, src).replace(os.sep, "/")
                for f in files:
                    if not f.lower().endswith(".png"):
                        continue
                    stem = f[:-4].lower()
                    target = _entity_target(rel, stem)
                    dst = os.path.join(tex_dst, "entity", rel if rel != "." else "")
                    if target and target != stem:
                        copy_file(os.path.join(dirpath, f), os.path.join(dst, target + ".png"))
                        stats["renamed"] += 1
                    else:
                        copy_file(os.path.join(dirpath, f), os.path.join(dst, f))
                    stats["entity"] += 1

    if options.get("environment", True):
        src = os.path.join(tex_src, "environment")
        if os.path.isdir(src):
            for f in os.listdir(src):
                if f.lower().endswith(".png"):
                    copy_file(os.path.join(src, f), os.path.join(tex_dst, "environment", f))
                    stats["misc"] += 1

    gui_src = os.path.join(tex_src, "gui")
    gui_dst = os.path.join(tex_dst, "gui")
    if os.path.isdir(gui_src):
        skip_dirs = {"container", "title", "achievement", "advancements", "presets"}
        skip_files = {"icons.png"}
        if options.get("hud", True):
            skip_files.add("widgets.png")
        for dirpath, dirnames, files in os.walk(gui_src):
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            rel = os.path.relpath(dirpath, gui_src)
            for f in files:
                if f in skip_files:
                    continue
                dst = os.path.join(gui_dst, rel, f) if rel != "." else os.path.join(gui_dst, f)
                if f == "widgets.png":
                    dst = os.path.join(gui_dst, rel, "gui.png") if rel != "." else os.path.join(gui_dst, "gui.png")
                copy_file(os.path.join(dirpath, f), dst)
                stats["misc"] += 1

    misc_map = {
        "map": "map", "misc": "misc", "models": "models", "painting": "painting",
        "particle": "particle", "colormap": "colormap", "trims": "trims",
    }
    for sub, dst_sub in misc_map.items():
        src = os.path.join(tex_src, sub)
        if not os.path.isdir(src):
            continue
        for dirpath, _, files in os.walk(src):
            rel = os.path.relpath(dirpath, src).replace(os.sep, "/")
            for f in files:
                if not f.lower().endswith(".png"):
                    continue
                stem = f[:-4].lower()
                target = stem
                if sub == "painting" and stem == "paintings_kristoffer_zetterstrand":
                    target = "kz"
                if sub == "models":
                    target = _armor_target(stem)
                dst_dir = os.path.join(tex_dst, dst_sub, rel) if rel != "." else os.path.join(tex_dst, dst_sub)
                if target and target != stem:
                    copy_file(os.path.join(dirpath, f), os.path.join(dst_dir, target + ".png"))
                    stats["renamed"] += 1
                else:
                    copy_file(os.path.join(dirpath, f), os.path.join(dst_dir, f))
                stats["misc"] += 1

    if options.get("effects", True):
        for sub in ("mob_effect", "effect"):
            src = os.path.join(tex_src, sub)
            if not os.path.isdir(src):
                continue
            from .constants import LEGACY_EFFECTS
            for f in os.listdir(src):
                if not f.lower().endswith(".png"):
                    continue
                stem = f[:-4].lower()
                target = LEGACY_EFFECTS.get(stem, stem)
                copy_file(os.path.join(src, f), os.path.join(tex_dst, "mob_effect", target + ".png"))
                stats["misc"] += 1

    log("Textures: %d blocks, %d items, %d entity, %d misc (%d renamed, %d custom kept)" % (
        stats["blocks"], stats["items"], stats["entity"], stats["misc"],
        stats["renamed"], stats["custom"]))
    progress("Textures ported")


def sanitize_output(bed_root, log):
    tex_dst = os.path.join(bed_root, "textures")
    if not os.path.isdir(tex_dst):
        return
    fixed = 0
    padded = 0
    for sub, allow_pot in (("items", True), ("blocks", False), ("entity", False),
                           ("environment", False), ("painting", False), ("particle", False),
                           ("misc", False), ("models", False), ("map", False),
                           ("colormap", False), ("mob_effect", False), ("trims", False)):
        base = os.path.join(tex_dst, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, _, files in os.walk(base):
            for f in files:
                if not f.lower().endswith(".png"):
                    continue
                path = os.path.join(dirpath, f)
                animated = os.path.isfile(path + ".mcmeta")
                if allow_pot and not animated:
                    try:
                        from PIL import Image
                        w, h = Image.open(path).size
                        if next_power_of_two(w) != w or next_power_of_two(h) != h:
                            _rescale_pot(path, w, h)
                            padded += 1
                    except Exception:
                        pass
                fixed += sanitize_png(path, pad_pot=False)
    if fixed or padded:
        log("Texture safety: re-encoded %d pngs as 8-bit RGBA, resized %d items to power-of-two (prevents black/garbled icons)" % (fixed, padded))


def _rescale_pot(path, w, h):
    from PIL import Image
    img = Image.open(path).convert("RGBA")
    pw = next_power_of_two(w)
    ph = next_power_of_two(h)
    rx = pw / float(w)
    ry = ph / float(h)
    if abs(rx - round(rx)) < 0.001 and abs(ry - round(ry)) < 0.001:
        method = Image.NEAREST
    else:
        method = Image.LANCZOS
    img.resize((pw, ph), method).save(path, format="PNG")


def patch_terrain_texture(bed_root, log):
    tex_dst = os.path.join(bed_root, "textures")
    folder = os.path.join(tex_dst, "blocks")
    if not os.path.isdir(folder):
        return
    known = set(load_snapshot("terrain_paths.json"))
    texture_data = {}
    existing_paths = set()
    added = 0
    for dirpath, _, files in os.walk(folder):
        rel = os.path.relpath(dirpath, folder).replace(os.sep, "/")
        for f in files:
            if not f.lower().endswith(".png"):
                continue
            stem = f[:-4].lower()
            path = "textures/blocks" + ("/" + rel if rel != "." else "") + "/" + stem
            if path.lower() in known or path.lower() in existing_paths:
                continue
            key = stem if "/" not in rel else (rel + "/" + stem).replace("/", "_")
            if key in texture_data:
                continue
            texture_data[key] = {"textures": path}
            existing_paths.add(path.lower())
            added += 1
    if added:
        data = {
            "resource_pack_name": "zarya",
            "texture_name": "atlas.terrain",
            "padding": 8,
            "num_mip_levels": 4,
            "texture_data": texture_data,
        }
        write_json(os.path.join(tex_dst, "terrain_texture.json"), data)
        log("terrain_texture.json: %d entries for custom block textures" % added)


def patch_item_texture(bed_root, log):
    tex_dst = os.path.join(bed_root, "textures")
    item_dir = os.path.join(tex_dst, "items")
    if not os.path.isdir(item_dir):
        return
    known = set(load_snapshot("item_paths.json"))
    texture_data = {}
    existing_paths = set()
    added = 0
    for dirpath, _, files in os.walk(item_dir):
        rel = os.path.relpath(dirpath, item_dir).replace(os.sep, "/")
        for f in files:
            if not f.lower().endswith(".png"):
                continue
            stem = f[:-4].lower()
            path = "textures/items" + ("/" + rel if rel != "." else "") + "/" + stem
            if path.lower() in known or path.lower() in existing_paths:
                continue
            key = stem if "/" not in rel else (rel + "/" + stem).replace("/", "_")
            if key in texture_data:
                continue
            texture_data[key] = {"textures": path}
            existing_paths.add(path.lower())
            added += 1
    if added:
        data = {
            "resource_pack_name": "zarya",
            "texture_name": "atlas.items",
            "texture_data": texture_data,
        }
        write_json(os.path.join(tex_dst, "item_texture.json"), data)
        log("item_texture.json: %d entries for custom item textures" % added)
