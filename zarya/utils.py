import os
import re
import json
import shutil
import zipfile

COLOR_CODE_RE = re.compile(r"(?:\u00a7|(?<![a-zA-Z])ss)([0-9a-fk-orA-FK-OR])")


def normalize_color_codes(text):
    text = str(text or "")
    text = text.replace("\u00a7", "ss")
    return COLOR_CODE_RE.sub(lambda m: "\u00a7" + m.group(1).lower(), text)


def assets_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def load_snapshot(name):
    path = os.path.join(assets_dir(), "data", name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def safe_extract(archive_path, dest):
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(archive_path) as z:
        z.extractall(dest)


def find_pack_root(path):
    if os.path.isfile(os.path.join(path, "pack.mcmeta")) or \
       os.path.isdir(os.path.join(path, "assets", "minecraft")):
        return path
    best = None
    best_score = 0
    best_depth = 9999
    for dirpath, dirnames, files in os.walk(path):
        depth = dirpath[len(path):].count(os.sep)
        if depth > 6:
            dirnames[:] = []
            continue
        score = 0
        if "pack.mcmeta" in files:
            score += 10
        if "assets" in dirnames and os.path.isdir(os.path.join(dirpath, "assets", "minecraft")):
            score += 6
        if "textures" in dirnames:
            score += 4
        if "pack.png" in files:
            score += 1
        if score > best_score or (score == best_score and score > 0 and depth < best_depth):
            best = dirpath
            best_score = score
            best_depth = depth
        if score >= 11:
            dirnames[:] = []
    if best and best_score >= 4:
        return best
    for dirpath, dirnames, _ in os.walk(path):
        for d in list(dirnames):
            sub = os.path.join(dirpath, d)
            inner = os.listdir(sub) if os.path.isdir(sub) else []
            if "assets" in inner or "textures" in inner:
                return sub
    return path


def _strip_json_comments(text):
    out = []
    in_str = False
    esc = False
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            text = f.read()
        try:
            return json.loads(text)
        except Exception:
            cleaned = _strip_json_comments(text)
            cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
            return json.loads(cleaned)
    except Exception:
        return None


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def lowercase_tree(root, log=None):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for name in filenames:
            low = name.lower()
            if name != low:
                src = os.path.join(dirpath, name)
                tmp = os.path.join(dirpath, "~" + low)
                dst = os.path.join(dirpath, low)
                if os.path.exists(dst):
                    os.remove(src)
                else:
                    os.rename(src, tmp)
                    os.rename(tmp, dst)
                count += 1
        for name in dirnames:
            low = name.lower()
            if name != low:
                src = os.path.join(dirpath, name)
                dst = os.path.join(dirpath, low)
                if os.path.exists(dst):
                    shutil.rmtree(src, ignore_errors=True)
                else:
                    tmp = os.path.join(dirpath, "~" + low)
                    os.rename(src, tmp)
                    os.rename(tmp, dst)
                count += 1
    if log and count:
        log("Lowercased %d file/folder names" % count)


def strip_mcmeta(root, log=None):
    count = 0
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.endswith(".mcmeta"):
                try:
                    os.remove(os.path.join(dirpath, name))
                    count += 1
                except OSError:
                    pass
    if log and count:
        log("Removed %d .mcmeta files" % count)


def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def next_power_of_two(value):
    pot = 1
    while pot < value:
        pot *= 2
    return pot


def sanitize_png(path, pad_pot=False, log=None):
    try:
        from PIL import Image
        img = Image.open(path)
        needs_rewrite = img.mode not in ("RGBA",) or img.info.get("interlace")
        w, h = img.size
        if pad_pot:
            pw = next_power_of_two(w)
            ph = next_power_of_two(h)
        else:
            pw, ph = w, h
        img = img.convert("RGBA")
        if (pw, ph) != (w, h):
            canvas = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
            canvas.paste(img, ((pw - w) // 2, (ph - h) // 2))
            img = canvas
            needs_rewrite = True
        if needs_rewrite:
            img.save(path, format="PNG", optimize=False)
            return 1
        return 0
    except Exception:
        return 0


def relative_files(root):
    out = []
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/"))
    return out


def guess_description(mcmeta):
    text = ""
    if isinstance(mcmeta, dict):
        pack_section = mcmeta.get("pack", {})
        if isinstance(pack_section, dict):
            text = pack_section.get("description", "")
        if not text:
            text = mcmeta.get("description", "")
    if isinstance(text, dict):
        text = text.get("text", "") or json.dumps(text)
    text = str(text).replace("\n", " ").strip()
    return text or "Minecraft Java Resource Pack"
