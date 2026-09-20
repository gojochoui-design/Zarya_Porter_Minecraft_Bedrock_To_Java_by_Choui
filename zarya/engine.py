import os
import shutil
import zipfile
import tempfile

from . import version_detect
from . import textures as textures_mod
from . import hud as hud_mod
from . import animations as animations_mod
from . import media as media_mod
from . import manifest as manifest_mod
from . import inventory as inventory_mod
from .utils import (
    safe_extract, find_pack_root, lowercase_tree, strip_mcmeta, relative_files,
    assets_dir, guess_description, read_json,
)


class Porter:
    def __init__(self):
        self.assets = assets_dir()

    def run(self, source_path, out_path, options, log, progress, finished):
        try:
            self._run(source_path, out_path, options, log, progress)
            finished(True, None)
        except Exception as exc:
            log("ERROR: %s" % exc)
            finished(False, str(exc))

    def _run(self, source_path, out_path, options, log, progress):
        progress("Preparing...")
        if not os.path.exists(source_path):
            raise RuntimeError("Input file does not exist")
        work = tempfile.mkdtemp(prefix="zarya_")
        try:
            base = os.path.join(work, "src")
            if os.path.isdir(source_path):
                shutil.copytree(source_path, base)
                src_root = find_pack_root(base)
            else:
                safe_extract(source_path, base)
                src_root = find_pack_root(base)
            log("Source pack: %s" % os.path.basename(os.path.normpath(source_path)))

            hint = os.path.splitext(os.path.basename(source_path))[0] if os.path.isfile(source_path) \
                else ""
            info = version_detect.detect(src_root, name_hint=hint)
            log("Detected Java version: %s" % info["version"])
            if info["format"] is not None:
                log("pack.mcmeta pack_format: %d" % info["format"])
            for note in info.get("notes", []):
                log("Detection: %s" % note)

            pack_name = os.path.splitext(os.path.basename(source_path))[0] if os.path.isfile(source_path) \
                else os.path.basename(os.path.normpath(source_path))
            pack_name = "".join(c for c in pack_name if c.isalnum() or c in "-_ .").strip().rstrip(".") or "PortedPack"

            bed_root = os.path.join(work, "out", pack_name)
            os.makedirs(bed_root, exist_ok=True)
            log("Pure conversion: only converted files go into the output")

            progress("Porting textures...")
            textures_mod.port_textures(src_root, bed_root, options, log, progress)

            if options.get("flipbook", True):
                progress("Converting animations...")
                animations_mod.port_flipbooks(src_root, bed_root, log)
            else:
                animations_mod.flatten_strips(bed_root, log)

            if options.get("hud", True):
                progress("Slicing HUD elements...")
                hud_mod.port_hud(src_root, bed_root, log)

            if options.get("environment", True):
                progress("Porting sky...")
                media_mod.port_sky(src_root, bed_root, log, options.get("sky_key") or "")

            if options.get("panorama", True):
                progress("Porting panorama...")
                media_mod.port_panorama(src_root, bed_root, log)

            if options.get("title", True):
                media_mod.port_title_logo(src_root, bed_root, log)

            if options.get("sounds", True):
                progress("Porting sounds...")
                media_mod.port_sounds(src_root, bed_root, log, progress)

            if options.get("fonts", True):
                progress("Porting fonts...")
                media_mod.port_fonts(src_root, bed_root, log)

            textures_mod.patch_terrain_texture(bed_root, log)
            textures_mod.patch_item_texture(bed_root, log)
            textures_mod.sanitize_output(bed_root, log)

            if options.get("lowercase", True):
                progress("Normalizing filenames...")
                lowercase_tree(bed_root, log)
            strip_mcmeta(os.path.join(bed_root, "textures"), log)

            if options.get("chouiui", False):
                progress("Building classic menus (ChouiUI)...")
                inventory_mod.inject_chouiui(bed_root, self.assets, log)
                inventory_mod.port_containers(src_root, bed_root, log)
            else:
                log("Classic menus (ChouiUI) left off - Bedrock default menus will show")

            mcmeta = read_json(os.path.join(src_root, "pack.mcmeta"))
            manifest_mod.write_manifest(bed_root, guess_description(mcmeta), pack_name, log)
            if options.get("pack_icon", True):
                manifest_mod.write_pack_icon(src_root, bed_root, self.assets, log)

            progress("Packaging...")
            out_path = os.path.abspath(out_path)
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            ext = os.path.splitext(out_path)[1].lower()
            if ext not in (".mcpack", ".zip"):
                out_path = out_path + ".mcpack"
            if os.path.exists(out_path):
                os.remove(out_path)
            with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
                for rel in relative_files(bed_root):
                    z.write(os.path.join(bed_root, rel), os.path.join(pack_name, rel))
            total = len(relative_files(bed_root))
            in_size = _size_of(source_path)
            out_size = os.path.getsize(out_path)
            log("Output: %s" % out_path)
            log("Packaging: %d files, %.1f MB in -> %.1f MB out" % (
                total, in_size / 1048576.0, out_size / 1048576.0))
            progress("Done")
            log("PORT COMPLETE - double click the file to import it into Minecraft Bedrock")
        finally:
            shutil.rmtree(work, ignore_errors=True)


def _size_of(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for dirpath, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass
    return total
