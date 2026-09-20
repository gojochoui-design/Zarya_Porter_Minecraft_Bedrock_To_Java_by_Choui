import math
import os

from PIL import Image

from .constants import SOUND_CATEGORIES, HOSTILE_ENTITIES
from .utils import copy_file, read_json, write_json


BLOCK_VERB_MAP = [
    ("break", ["dig", "break"]),
    ("step", ["step"]),
    ("place", ["place"]),
    ("hit", ["hit"]),
    ("fall", ["fall"]),
    ("item.use.on", ["step"]),
]

ENTITY_VERB_MAP = {
    "ambient": ["say", "ambient"],
    "hurt": ["hurt"],
    "death": ["death"],
    "step": ["step"],
    "eat": ["eat"],
    "ambient_in_water": ["ambient"],
    "hurt_in_water": ["hurt"],
    "death_in_water": ["death"],
}


def _category(event_id):
    root = event_id.split(".")[0]
    if root in SOUND_CATEGORIES:
        return SOUND_CATEGORIES[root]
    if root == "entity":
        parts = event_id.split(".")
        if len(parts) > 1 and parts[1] in HOSTILE_ENTITIES:
            return "hostile"
        return "neutral"
    if root == "music_disc":
        return "record"
    return "neutral"


def _definition_id(event_id):
    if event_id.startswith("music_disc."):
        return "record." + event_id[len("music_disc."):]
    return event_id


def _convert_java_sound(entry):
    if isinstance(entry, str):
        return {"name": entry, "volume": 1.0, "pitch": 1.0, "weight": 1, "stream": False}
    if isinstance(entry, dict):
        return {
            "name": entry.get("name", ""),
            "volume": entry.get("volume", 1.0),
            "pitch": entry.get("pitch", 1.0),
            "weight": entry.get("weight", 1),
            "stream": bool(entry.get("stream", False)),
        }
    return None


def _sound_def(java_entry, event_id):
    sounds = java_entry.get("sounds", []) if isinstance(java_entry, dict) else []
    out_sounds = []
    for s in sounds:
        conv = _convert_java_sound(s)
        if not conv or not conv["name"]:
            continue
        name = conv["name"]
        if name.startswith("minecraft:"):
            name = name[len("minecraft:"):]
        if name.endswith(".ogg"):
            name = name[:-4]
        out_def = {"name": "sounds/" + name, "volume": conv["volume"], "pitch": conv["pitch"]}
        if conv["stream"] or _category(event_id) in ("music", "record"):
            out_def["stream"] = True
        weight = max(1, min(4, int(conv["weight"])))
        for _ in range(weight):
            out_sounds.append(dict(out_def))
    if not out_sounds:
        return None
    return {"category": _category(event_id), "sounds": out_sounds}


def _copy_oggs(java_root, bed_root, log):
    src_base = os.path.join(java_root, "assets", "minecraft", "sounds")
    dst_base = os.path.join(bed_root, "sounds")
    if not os.path.isdir(src_base):
        log("No Java sounds folder")
        return 0
    count = 0
    for dirpath, _, files in os.walk(src_base):
        rel = os.path.relpath(dirpath, src_base).replace(os.sep, "/")
        for f in files:
            if f.lower().endswith((".ogg", ".fsb", ".wav")):
                dst = os.path.join(dst_base, rel, f) if rel != "." else os.path.join(dst_base, f)
                copy_file(os.path.join(dirpath, f), dst)
                count += 1
    log("Copied %d sound files" % count)
    return count


def _material_from_event(event_id):
    parts = event_id.split(".")
    if len(parts) >= 3:
        return parts[1]
    return None


def _entity_from_event(event_id):
    parts = event_id.split(".")
    if len(parts) >= 3:
        return parts[1]
    return None


def port_sounds(java_root, bed_root, log, progress):
    java_sounds_path = os.path.join(java_root, "assets", "minecraft", "sounds.json")
    java_sounds = read_json(java_sounds_path) or {}
    _copy_oggs(java_root, bed_root, log)

    definitions = {}
    music_defs = {}

    for event_id, java_entry in java_sounds.items():
        if not isinstance(event_id, str):
            continue
        if event_id.startswith("block."):
            material = _material_from_event(event_id)
            verb = event_id.split(".")[-1]
            def_ids = None
            for jv, bvs in BLOCK_VERB_MAP:
                if verb == jv:
                    def_ids = bvs
                    break
            if not def_ids:
                continue
            snd = _sound_def(java_entry, event_id)
            if snd:
                for did in def_ids:
                    definitions.setdefault(did + "." + (material or "stone"), dict(snd))
        elif event_id.startswith("entity."):
            entity = _entity_from_event(event_id)
            verb = event_id.split(".")[-1]
            mapped = ENTITY_VERB_MAP.get(verb)
            if not mapped:
                continue
            snd = _sound_def(java_entry, event_id)
            if not snd:
                continue
            for did in mapped:
                definitions.setdefault("mob.%s.%s" % (entity, did), dict(snd))
        elif event_id.startswith("music."):
            snd = _sound_def(java_entry, event_id)
            if snd:
                group = music_defs.setdefault(event_id, {"category": "music", "sounds": []})
                group["sounds"].extend(snd["sounds"])
        else:
            snd = _sound_def(java_entry, event_id)
            if snd:
                definitions.setdefault(_definition_id(event_id), snd)

    if definitions:
        out = {"format_version": "1.14.0", "sound_definitions": definitions}
        write_json(os.path.join(bed_root, "sounds", "sound_definitions.json"), out)
        log("sound_definitions.json: %d events wired to pack sounds" % len(definitions))

    if music_defs:
        out = {"format_version": "1.14.0"}
        for key, group in music_defs.items():
            out[key] = group
        write_json(os.path.join(bed_root, "sounds", "music_definitions.json"), out)
        log("music_definitions.json: %d music groups replaced" % len(music_defs))

    progress("Sounds ported")


def port_fonts(java_root, bed_root, log):
    font_srcs = [
        os.path.join(java_root, "assets", "minecraft", "textures", "font"),
        os.path.join(java_root, "assets", "minecraft", "font"),
    ]
    font_dst = os.path.join(bed_root, "font")
    found = None
    for src in font_srcs:
        if os.path.isdir(src):
            found = src
            break
    if not found:
        log("No Java font folder")
        return
    count = 0
    for f in os.listdir(found):
        low = f.lower()
        src = os.path.join(found, f)
        if not os.path.isfile(src):
            continue
        if low == "glyph_sizes.bin" or low.endswith(".json"):
            continue
        if low == "ascii.png":
            copy_file(src, os.path.join(font_dst, "default8.png"))
            count += 1
        elif low.startswith("unicode_page_") and low.endswith(".png"):
            copy_file(src, os.path.join(font_dst, "glyph_" + low[len("unicode_page_"):]))
            count += 1
        elif low.endswith(".png"):
            copy_file(src, os.path.join(font_dst, f))
            count += 1
    log("Fonts: ported %d files (ascii.png -> default8.png, unicode pages -> glyph sheets)" % count)


def port_panorama(java_root, bed_root, log):
    src = os.path.join(java_root, "assets", "minecraft", "textures", "gui", "title", "background")
    if not os.path.isdir(src):
        log("No panorama folder")
        return
    count = 0
    for f in sorted(os.listdir(src)):
        if f.lower().startswith("panorama") and f.lower().endswith(".png"):
            copy_file(os.path.join(src, f), os.path.join(bed_root, "textures", "gui", "background", f))
            copy_file(os.path.join(src, f), os.path.join(bed_root, "textures", f))
            count += 1
    log("Panorama: ported %d images to both legacy and modern paths" % count)


def _compose_weather(rain_path, snow_path, out_path):
    try:
        rain = Image.open(rain_path).convert("RGBA")
        snow = Image.open(snow_path).convert("RGBA")
        if rain.width != snow.width:
            return False
        scale = rain.width / 64.0
        side = round(32 * scale)
        out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        band = round(5 * scale)
        rain_band = rain.crop((0, 0, rain.width, band)).resize((side, band), Image.NEAREST)
        out.paste(rain_band, (0, band))
        snow_band = snow.crop((0, 0, snow.width, round(3 * scale))).resize((side, round(3 * scale)), Image.NEAREST)
        out.paste(snow_band, (0, 0))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        out.save(out_path)
        return True
    except Exception:
        return False


_STRIP_TILES = [(2, 0, False), (0, 1, False), (1, 1, False), (2, 1, False),
                (1, 0, True), (0, 0, True)]

_FACE_DIRS = [
    (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0), (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0), (0.0, 0.0, -1.0),
]

_FACE_UPS = [
    (0.0, -1.0, 0.0), (0.0, -1.0, 0.0),
    (0.0, 0.0, -1.0), (0.0, 0.0, 1.0),
    (0.0, -1.0, 0.0), (0.0, -1.0, 0.0),
]


def _strip_to_cubemap(strip_path, bed_root):
    try:
        img = Image.open(strip_path).convert("RGBA")
    except Exception:
        return False
    if img.width // 3 != img.height // 2:
        return False
    side = img.height // 2
    out_dir = os.path.join(bed_root, "textures", "environment", "overworld_cubemap")
    os.makedirs(out_dir, exist_ok=True)
    for i, (cx, cy, flip) in enumerate(_STRIP_TILES):
        tile = img.crop((cx * side, cy * side, (cx + 1) * side, (cy + 1) * side))
        if flip:
            tile = tile.rotate(180)
        tile.save(os.path.join(out_dir, "cubemap_%d.png" % i))
    return True


def _face_mesh(img, face_dir, face_up, face_size, cells=24):
    fx, fy, fz = face_dir
    ux, uy, uz = face_up
    rx, ry, rz = uy * fz - uz * fy, uz * fx - ux * fz, ux * fy - uy * fx
    src_w, src_h = img.size
    step = 2.0 / cells
    mesh = []

    def uv(nx, ny):
        dx = fx + rx * nx + ux * ny
        dy = fy + ry * nx + uy * ny
        dz = fz + rz * nx + uz * ny
        length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
        yaw = math.atan2(dx, dz)
        pitch = math.asin(max(-1.0, min(1.0, dy / length)))
        u = (yaw / (2.0 * math.pi) + 0.5) % 1.0
        v = 0.5 - pitch / math.pi
        return (u * src_w, v * src_h)

    for cy in range(cells):
        for cx in range(cells):
            nx0 = -1.0 + cx * step
            ny0 = 1.0 - cy * step
            box = (int(cx * face_size / cells), int(cy * face_size / cells),
                   int((cx + 1) * face_size / cells), int((cy + 1) * face_size / cells))
            ul = uv(nx0, ny0)
            ll = uv(nx0, ny0 - step)
            lr = uv(nx0 + step, ny0 - step)
            ur = uv(nx0 + step, ny0)
            quad = (ul[0], ul[1], ll[0], ll[1], lr[0], lr[1], ur[0], ur[1])
            mesh.append((box, quad))
    return img.transform((face_size, face_size), Image.MESH, mesh, Image.BILINEAR)


def _equirect_to_cubemap(path, bed_root):
    try:
        img = Image.open(path).convert("RGBA")
    except Exception:
        return False
    if img.width < img.height * 2 - max(8, img.height // 8):
        return False
    face_size = max(128, min(1024, img.width // 4))
    out_dir = os.path.join(bed_root, "textures", "environment", "overworld_cubemap")
    os.makedirs(out_dir, exist_ok=True)
    for i, (direction, up) in enumerate(zip(_FACE_DIRS, _FACE_UPS)):
        face = _face_mesh(img, direction, up, face_size)
        face.save(os.path.join(out_dir, "cubemap_%d.png" % i))
    return True


def _single_to_cubemap(path, bed_root):
    try:
        img = Image.open(path).convert("RGBA")
    except Exception:
        return False
    side = max(128, min(1024, max(img.width, img.height)))
    face = img.resize((side, side), Image.NEAREST if side >= img.width else Image.BILINEAR)
    out_dir = os.path.join(bed_root, "textures", "environment", "overworld_cubemap")
    os.makedirs(out_dir, exist_ok=True)
    for i in range(6):
        face.save(os.path.join(out_dir, "cubemap_%d.png" % i))
    return True


def _texture_to_cubemap(path, bed_root):
    if not path or not os.path.isfile(path):
        return False
    if _strip_to_cubemap(path, bed_root):
        return True
    if _equirect_to_cubemap(path, bed_root):
        return True
    return _single_to_cubemap(path, bed_root)


def _port_selected_sky(java_root, bed_root, log, sky_key):
    from . import skybox as skybox_mod
    layer = skybox_mod.find_layer(skybox_mod.detect(java_root), sky_key)
    if not layer:
        return False
    source = (layer.get("sources") or [None])[0]
    if not source or not os.path.isfile(source):
        return False
    if not _texture_to_cubemap(source, bed_root):
        return False
    log("Selected sky %s -> Bedrock overworld sky (6 cubemap faces)" % os.path.basename(source))
    return True


def _port_mcpatcher_sky(java_root, bed_root, log):
    sky_dirs = [
        os.path.join(java_root, "assets", "minecraft", "mcpatcher", "sky", "world0"),
        os.path.join(java_root, "assets", "minecraft", "optifine", "sky", "world0"),
    ]
    names = ["cloud1.png", "cloud2.png", "starfield03.png", "starfield.png", "skybox.png", "skybox2.png"]
    strip = None
    for d in sky_dirs:
        if not os.path.isdir(d):
            continue
        for n in names:
            cand = os.path.join(d, n)
            if os.path.isfile(cand):
                strip = cand
                break
        if strip:
            break
    if not strip:
        return 0
    if not _strip_to_cubemap(strip, bed_root):
        return 0
    log("McPatcher sky: 3x2 strip -> overworld cubemap (6 faces)")
    return 1


def _relayout_moon(src, out_path):
    try:
        img = Image.open(src).convert("RGBA")
        frame = img.height
        phases = max(1, img.width // frame)
        out_frame = max(8, int(round(32 * (frame / 20.0))))
        canvas = Image.new("RGBA", (out_frame * 4, out_frame * 2), (0, 0, 0, 0))
        for i in range(min(8, phases)):
            tile = img.crop((i * frame, 0, (i + 1) * frame, frame))
            if tile.size != (out_frame, out_frame):
                tile = tile.resize((out_frame, out_frame), Image.NEAREST)
            col = i % 4
            row = i // 4
            canvas.paste(tile, (col * out_frame, row * out_frame))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        canvas.save(out_path)
        return True
    except Exception:
        return False


def _fit_size(src, out_path, width, height):
    try:
        img = Image.open(src).convert("RGBA")
        if img.size == (width, height):
            img.save(out_path)
            return True
        img = img.resize((width, height), Image.NEAREST)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        img.save(out_path)
        return True
    except Exception:
        return False


def port_sky(java_root, bed_root, log, sky_key=""):
    env_src = os.path.join(java_root, "assets", "minecraft", "textures", "environment")
    if not os.path.isdir(env_src):
        env_src = os.path.join(java_root, "textures", "environment")
    env_dst = os.path.join(bed_root, "textures", "environment")
    count = 0
    if os.path.isdir(env_src):
        for f in list(os.listdir(env_src)):
            low = f.lower()
            if low in ("rain.png", "snow.png"):
                continue
            if not low.endswith(".png"):
                continue
            src = os.path.join(env_src, f)
            dst = os.path.join(env_dst, f)
            if low == "moon_phases.png":
                if _relayout_moon(src, dst):
                    count += 1
                    log("Moon: relaid the phase strip out as 2 rows x 4 phases (Bedrock layout)")
                continue
            if low == "end_sky.png":
                if _fit_size(src, dst, 128, 128):
                    count += 1
                continue
            copy_file(src, dst)
            count += 1
        rain = os.path.join(env_src, "rain.png")
        snow = os.path.join(env_src, "snow.png")
        if os.path.isfile(rain) and os.path.isfile(snow):
            if _compose_weather(rain, snow, os.path.join(env_dst, "weather.png")):
                log("Weather: composed rain.png + snow.png -> weather.png")
                count += 1
    if sky_key:
        selected = _port_selected_sky(java_root, bed_root, log, sky_key)
    else:
        selected = False
    if not selected:
        count += _port_mcpatcher_sky(java_root, bed_root, log)
    blocks_dir = os.path.join(bed_root, "textures", "blocks")
    if os.path.isdir(blocks_dir):
        for i in range(10):
            src = os.path.join(blocks_dir, "destroy_stage_%d.png" % i)
            if os.path.isfile(src):
                copy_file(src, os.path.join(env_dst, "destroy_stage_%d.png" % i))
                count += 1
    log("Sky/environment: ported %d textures" % count)


def port_title_logo(java_root, bed_root, log):
    srcs = [
        os.path.join(java_root, "assets", "minecraft", "textures", "gui", "title", "minecraft.png"),
        os.path.join(java_root, "assets", "minecraft", "textures", "gui", "title", "logo.png"),
    ]
    src = next((p for p in srcs if os.path.isfile(p)), None)
    if not src:
        log("No title logo")
        return
    try:
        img = Image.open(src).convert("RGBA")
        u = img.width / 256.0
        if img.width >= round(260 * u) and img.height <= round(60 * u):
            out = img.resize((img.width * 4, img.height * 4), Image.NEAREST)
            dst = os.path.join(bed_root, "textures", "ui", "title.png")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            out.save(dst)
            log("Title logo: single-sheet logo saved 4x pixel-perfect as textures/ui/title.png (%dx%d)" % out.size)
            return
        h = round(44 * u)
        if img.height < h + round(45 * u):
            h = img.height // 2
        left = img.crop((0, 0, round(155 * u), h))
        right = img.crop((0, round(45 * u), round(119 * u), round(45 * u) + h))
        out = Image.new("RGBA", (round(274 * u), h), (0, 0, 0, 0))
        out.paste(left, (0, 0))
        out.paste(right, (round(155 * u), 0))
        out = out.resize((out.width * 4, out.height * 4), Image.NEAREST)
        dst = os.path.join(bed_root, "textures", "ui", "title.png")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        out.save(dst)
        log("Title logo: minecraft.png halves joined at the seam and saved 4x pixel-perfect "
            "as textures/ui/title.png (%dx%d)" % out.size)
    except Exception as exc:
        log("Title logo failed: %s" % exc)
