import os

from PIL import Image

from .constants import (
    ICONS_SLICES, HUD_COPIES, HOTBAR_SLOTS, HOTBAR_X0, HOTBAR_SLOT_W, HOTBAR_H,
    HOTBAR_Y, SELECTED_SLOT, SELECTED_CANVAS,
)
from .utils import write_json

XP_LOGICAL = (364, 10)


def _open_rgba(path):
    try:
        return Image.open(path).convert("RGBA")
    except Exception:
        return None


def _crop_scaled(sheet, box_256):
    x, y, w, h = box_256
    sx = sheet.width / 256.0
    sy = sheet.height / 256.0
    px = min(max(0, round(x * sx)), sheet.width - 1)
    py = min(max(0, round(y * sy)), sheet.height - 1)
    pw = max(1, min(round(w * sx), sheet.width - px))
    ph = max(1, min(round(h * sy), sheet.height - py))
    return sheet.crop((px, py, px + pw, py + ph))


def _upscale_crisp(img, width, height):
    if (img.width, img.height) == (width, height):
        return img
    rx = width / float(img.width)
    ry = height / float(img.height)
    if abs(rx - round(rx)) < 0.01 and abs(ry - round(ry)) < 0.01:
        method = Image.NEAREST
    else:
        method = Image.LANCZOS
    return img.resize((width, height), method)


def _save_png(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def _write_base_size(png_path, base, nineslice=None):
    data = {"base_size": list(base)}
    if nineslice is not None:
        data["nineslice_size"] = list(nineslice)
    root, _ = os.path.splitext(png_path)
    write_json(root + ".json", data)


def _on_canvas(img, w, h):
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(img, (0, 0))
    return canvas


def _crosshair_swedu(icons):
    size = max(1, icons.width // 16)
    crop = icons.crop((0, 0, size, size))
    out = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    out.alpha_composite(crop)
    return out


def _swedu_xp(icons):
    sy = icons.height / 256.0
    u = icons.width / 256.0
    y = round(icons.height / 4.0)
    length = icons.width - round(icons.width / 3.45945945946)
    bar_h = max(1, round(5 * u))
    empty = icons.crop((0, y, length, y + bar_h))
    full = icons.crop((0, y + bar_h, length, y + 2 * bar_h))
    return empty, full


def port_hud(java_root, bed_root, log):
    gui_dir = os.path.join(java_root, "assets", "minecraft", "textures", "gui")
    if not os.path.isdir(gui_dir):
        gui_dir = os.path.join(java_root, "textures", "gui")
    if not os.path.isdir(gui_dir):
        log("No gui folder found, HUD port skipped")
        return 0
    ui_dst = os.path.join(bed_root, "textures", "ui")
    count = 0

    icons_path = os.path.join(gui_dir, "icons.png")
    icons = _open_rgba(icons_path) if os.path.isfile(icons_path) else None
    if icons is not None:
        cross = _crosshair_swedu(icons)
        _save_png(cross, os.path.join(ui_dst, "cross_hair.png"))
        _write_base_size(os.path.join(ui_dst, "cross_hair.png"), [16, 16])
        count += 1
        for name, box, bw, bh, _n in ICONS_SLICES:
            if name == "cross_hair":
                continue
            crop = _crop_scaled(icons, box)
            _save_png(crop, os.path.join(ui_dst, name + ".png"))
            _write_base_size(os.path.join(ui_dst, name + ".png"), [bw, bh])
            count += 1
            for extra in HUD_COPIES.get(name, []):
                _save_png(crop.copy(), os.path.join(ui_dst, extra + ".png"))
                _write_base_size(os.path.join(ui_dst, extra + ".png"), [bw, bh])
                count += 1
        empty, full = _swedu_xp(icons)
        empty = _upscale_crisp(empty, 728, 20)
        full = _upscale_crisp(full, 728, 20)
        _save_png(empty, os.path.join(ui_dst, "experiencebarempty.png"))
        _write_base_size(os.path.join(ui_dst, "experiencebarempty.png"),
                         list(XP_LOGICAL), [6, 1, 6, 1])
        _save_png(full, os.path.join(ui_dst, "experiencebarfull.png"))
        _write_base_size(os.path.join(ui_dst, "experiencebarfull.png"),
                         list(XP_LOGICAL), [1, 0, 1, 0])
        count += 2
        log("HUD: crosshair rebuilt on a solid black backing (Swim Porter 2.0 style), "
            "%d icon slices pinned to their logical sizes, XP bar upscaled to 728x20 "
            "with base %s exactly like the reference porter" % (count, list(XP_LOGICAL)))

    widgets_path = os.path.join(gui_dir, "widgets.png")
    widgets = _open_rgba(widgets_path) if os.path.isfile(widgets_path) else None
    if widgets is not None:
        sx = widgets.width / 256.0
        sy = widgets.height / 256.0
        slot_w = max(1, round(HOTBAR_SLOT_W * sx))
        x0 = round(HOTBAR_X0 * sx)
        h = max(1, round(HOTBAR_H * sy))
        y = round(HOTBAR_Y * sy)
        for i in range(HOTBAR_SLOTS):
            sx_i = min(x0 + i * slot_w, widgets.width - 1)
            crop = widgets.crop((sx_i, y, min(sx_i + slot_w, widgets.width), y + h))
            _save_png(crop, os.path.join(ui_dst, "hotbar_%d.png" % i))
            _write_base_size(os.path.join(ui_dst, "hotbar_%d.png" % i),
                             [HOTBAR_SLOT_W, HOTBAR_H])
            count += 1
        cap_w = max(1, round(1 * sx))
        cap_l = widgets.crop((0, y, cap_w, y + h))
        _save_png(cap_l, os.path.join(ui_dst, "hotbar_start_cap.png"))
        _write_base_size(os.path.join(ui_dst, "hotbar_start_cap.png"),
                         [1, HOTBAR_H], [1, 1, 1, 1])
        cap_r = widgets.crop((max(0, widgets.width - cap_w), y, widgets.width, y + h))
        _save_png(cap_r, os.path.join(ui_dst, "hotbar_end_cap.png"))
        _write_base_size(os.path.join(ui_dst, "hotbar_end_cap.png"),
                         [1, HOTBAR_H], [1, 1, 1, 1])
        count += 2
        sel = _crop_scaled(widgets, SELECTED_SLOT)
        canvas_w = round(SELECTED_CANVAS[0] * sx)
        canvas_h = round(SELECTED_CANVAS[1] * sy)
        sel_canvas = _on_canvas(sel, canvas_w, canvas_h)
        _save_png(sel_canvas, os.path.join(ui_dst, "selected_hotbar_slot.png"))
        _write_base_size(os.path.join(ui_dst, "selected_hotbar_slot.png"),
                         list(SELECTED_CANVAS))
        count += 1
        log("HUD: sliced hotbar (%d slots, caps, selection) with logical size metadata" % HOTBAR_SLOTS)

    if count == 0:
        log("No icons.png / widgets.png in pack, HUD stays vanilla")
    return count
