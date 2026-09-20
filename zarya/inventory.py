import os
import shutil

from .utils import read_json, write_json


CONTAINER_NAMES = (
    "inventory",
    "crafting_table",
    "furnace",
    "generic_54",
    "dispenser",
    "hopper",
    "brewing_stand",
    "anvil",
    "enchanting_table",
)


def _copy_tree(source, bed_root, skip_names):
    count = 0
    for root, dirs, files in os.walk(source):
        rel = os.path.relpath(root, source)
        if rel == ".":
            rel = ""
        for d in dirs:
            os.makedirs(os.path.join(bed_root, rel, d), exist_ok=True)
        for f in files:
            if f in skip_names:
                continue
            src = os.path.join(root, f)
            dst = os.path.join(bed_root, rel, f) if rel else os.path.join(bed_root, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            count += 1
    return count


def inject_chouiui(bed_root, assets_dir, log):
    source = os.path.join(assets_dir, "chouiui")
    if not os.path.isdir(source):
        log("ChouiUI asset is missing from the app folder")
        return 0
    count = _copy_tree(source, bed_root, skip_names={"manifest.json", "pack_icon.png"})
    defs_path = os.path.join(bed_root, "ui", "_ui_defs.json")
    source_defs = read_json(os.path.join(source, "ui", "_ui_defs.json")) or {}
    current = read_json(defs_path) or {}
    entries = current.get("ui_defs", [])
    for entry in source_defs.get("ui_defs", []):
        if entry not in entries:
            entries.append(entry)
    current["ui_defs"] = entries
    write_json(defs_path, current)
    log("ChouiUI injected untouched: %d files (creative mode shows the default Bedrock inventory "
        "plus a 1.8 side panel you can fold away with the burger button)" % count)
    return count


def _find_container_png(gui_dir, name):
    candidates = [
        os.path.join(gui_dir, "container", name + ".png"),
        os.path.join(gui_dir, name + ".png"),
    ]
    for cand in candidates:
        if os.path.isfile(cand):
            return cand
    return None


def port_containers(java_root, bed_root, log):
    gui_dir = os.path.join(java_root, "assets", "minecraft", "textures", "gui")
    if not os.path.isdir(gui_dir):
        gui_dir = os.path.join(java_root, "textures", "gui")
    if not os.path.isdir(gui_dir):
        log("No container textures in this pack - menus keep the ChouiUI template art")
        return 0
    ui_dst = os.path.join(bed_root, "textures", "ui")
    os.makedirs(ui_dst, exist_ok=True)
    count = 0
    for name in CONTAINER_NAMES:
        src = _find_container_png(gui_dir, name)
        if not src:
            continue
        dst = os.path.join(ui_dst, name + ".png")
        shutil.copy2(src, dst)
        try:
            from PIL import Image
            w, h = Image.open(src).size
            log("Container: pack %s.png (%dx%d) now drives the %s menu - ChouiUI layout untouched" % (
                name, w, h, name))
        except Exception:
            log("Container: pack %s.png now drives the %s menu" % (name, name))
        count += 1
    if count == 0:
        log("No matching container textures (menus keep the ChouiUI template art)")
    return count
