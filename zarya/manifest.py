import os
import uuid

from PIL import Image

from .constants import MIN_ENGINE_VERSION, PORTER_TAG
from .utils import write_json, copy_file, normalize_color_codes


def _resize_icon(src, dst, size=256):
    try:
        img = Image.open(src).convert("RGBA")
        img = img.resize((size, size), Image.LANCZOS)
        dst_dir = os.path.dirname(dst)
        if dst_dir:
            os.makedirs(dst_dir, exist_ok=True)
        img.save(dst)
        return True
    except Exception:
        return False


def write_manifest(bed_root, description, pack_name, log):
    header_uuid = str(uuid.uuid4())
    module_uuid = str(uuid.uuid4())
    clean_name = (pack_name or "Ported Pack").strip() or "Ported Pack"
    desc = normalize_color_codes(description or "Java resource pack")
    manifest = {
        "format_version": 2,
        "header": {
            "description": desc + "\n" + PORTER_TAG,
            "name": "Zarya - " + clean_name,
            "uuid": header_uuid,
            "version": [1, 0, 0],
            "min_engine_version": list(MIN_ENGINE_VERSION),
        },
        "modules": [
            {
                "description": "Ported resources",
                "type": "resources",
                "uuid": module_uuid,
                "version": [1, 0, 0],
            }
        ],
    }
    write_json(os.path.join(bed_root, "manifest.json"), manifest)
    log("manifest.json written (fresh UUIDs, min_engine %d.%d.%d, color codes adapted)" % tuple(MIN_ENGINE_VERSION))


def write_pack_icon(java_root, bed_root, assets_dir, log):
    candidates = [
        os.path.join(java_root, "pack.png"),
        os.path.join(java_root, "assets", "minecraft", "pack.png"),
    ]
    bundled = os.path.join(assets_dir, "pack_icon_default.png")
    for cand in candidates:
        if os.path.isfile(cand):
            if _resize_icon(cand, os.path.join(bed_root, "pack_icon.png")):
                log("pack_icon.png generated from pack.png")
                return
    if os.path.isfile(bundled):
        copy_file(bundled, os.path.join(bed_root, "pack_icon.png"))
        log("pack_icon.png set to bundled default")
