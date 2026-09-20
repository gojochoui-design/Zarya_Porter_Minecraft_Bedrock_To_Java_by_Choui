# Zarya Porter by Choui
<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/a3a3076c-3a11-4ad7-954c-c9eb06132649" />


A simple desktop app that turns **Minecraft Java** resource packs into **Minecraft Bedrock** packs. Pick a pack, flip the switches, choose where to save, hit convert.

Made by Choui. This tool does not collect anything, does not need Java, and works fully offline. The interface is a clean dark UI in pure gray and black with square blocks, real animations, glowing square switches in both states, and the window can be resized, maximized or put in fullscreen (F11 or the button in the corner).

## What it does

- **Pure conversion** - the output only contains what your pack actually has. A 10 MB pack gives you roughly a 10 MB pack. Nothing is bundled, no vanilla base is merged in.
- **Version detection that never says unknown** - reads `pack.mcmeta`, the lang files, the folder layout, the model formats and the actual textures in your pack (a netherite ingot means 1.16+, a spyglass means 1.17+, a mace means 1.21+, and so on), and narrows the version down as far as the pack content allows. Packs zipped inside subfolders are found automatically - the app digs through the whole archive to locate the real pack root.
- **Classic menus (ChouiUI)** - my own Java 1.8-style menus for Bedrock: player inventory, crafting table, furnace, chest, dispenser, hopper, brewing stand, anvil, enchanting table. The app copies my menus in untouched, then just swaps the typical Java container texture names (`inventory`, `crafting_table`, `furnace`, `generic_54`, ...) onto my template so your pack's art drives the menus. No rescaling tricks, no broken math - if your pack is a clean 1.8 pack, everything lines up like it should.
- **Creative mode, rebuilt the mathematically clean way** - in creative, Bedrock's own block list fills the standard window exactly like vanilla does (the browser gets the full width - no more crushed half-size grid), and a single H button in the corner swaps the whole thing for the classic 1.8 inventory centered on a solid backdrop. The two modes are true siblings: when one is visible the other is gone, nothing overlaps, nothing floats on top. The classic panel carries its own X to close the screen, and pressing H again puts you back on the block list.
- **Skybox radar with live previews - and skies you can actually use** - the moment you load a pack, the app hunts for every sky your pack carries: OptiFine custom skies (day layers, night layers, sunrise sets, per-dimension folders like world0, world-1, world1), the older MCPatcher skies in their own folder, the cloud and starfield sheets, and the environment textures (sun, moon phases, end sky and any custom sky sheets). Every declared layer gets its own card with a real projected panorama preview (the flat 2:1 texture is rendered through a lens so you see it like a horizon), the fade times read from the `.properties` files, its phase (dawn, day, dusk, night) and whether it rotates - even layers whose texture is missing from the zip are shown with a warning instead of being silently dropped. And they are not just decoration: click any card with a picture and that sky becomes the real Bedrock sky - the converter builds the `overworld_cubemap` (6 faces) Bedrock reads, from a 3x2 strip, a 2:1 panorama or even a single texture. The chip shows `SKY: <file>` while a sky is picked, or `SKY: AUTO` to let the converter choose the best strip itself. Missing textures stay marked as not usable.
- **Clean HUD porting** - crosshair, hearts, armor, bubbles, hunger, XP bar and the whole hotbar are sliced from your pack's `icons.png` and `widgets.png`, each piece pinned to its logical size with proper texture metadata so nothing renders oversized on HD packs. The crosshair is rebuilt on a solid black backing (same trick the classic porters use) so it never shows artifacts, and the XP bar is upscaled the same way the classic porters do it, with the exact base size and end caps Bedrock expects.
- **Animations that actually work** - animated block textures from your pack become real Bedrock flipbooks with your pack's own timing, including water, lava, fire and portal if the pack has them. Nothing vanilla is restored - if your pack has no animations, the output ships none. Water is copied as-is because Bedrock tints it per biome, so colored pack water stays colored. Animated items and environment textures (which Bedrock cannot flipbook) are flattened to their first frame instead of showing garbage.
- **No more black high-res items** - every texture in the output is re-encoded as a safe 8-bit RGBA PNG, and item textures that are not power-of-two get resized to the closest power-of-two, which is what causes the black background on 128x items.
- **Everything else** - blocks, items, entity skins, sounds, fonts, sky (with the moon phase strip rearranged into the Bedrock layout), panorama, title logo, pack icon. Color codes with `§` or the classic `ss` shortcut are converted so Bedrock reads them correctly.
- **A layout that refuses to break** - the window fits itself to your screen before showing anything, and if you shrink it below what the content needs, the app scrolls instead of crushing or overlapping anything. Every card keeps its size on any screen, from 1366x768 laptops up to 4K.

## Settings, themes and languages

The **Settings** button in the header opens a panel where everything applies instantly and is remembered for next time:

- **Color theme** - the app starts in Graphite (pure gray and black, no other colors), and the swatch grid lets you jump between fifty-one themes: grays like Ink, Ash, Slate, Carbon and Void; blues like Ocean, Midnight, Deep Sea, Sky, Periwinkle and Indigo; greens like Cyan Wave, Emerald, Lime, Forest, Pine, Moss, Neon and Toxic; warm ones like Crimson, Rose, Salmon, Coral, Sunset, Tangerine, Amber, Gold, Butter and Rust; purples like Amethyst, Violet, Plum, Magenta and Fuchsia; browns like Coffee and Mocha; and six light themes - Paper, Snow Light, Bone, Sand, Mint Cream, Lavender Mist, Sakura and Ice.
- **Language** - English by default, plus Spanish, Russian and Japanese, for the whole interface.
- **Default save folder** - pick a folder and every converted pack lands there by default; leave it empty to save next to the source pack.
- Your option switches are remembered too.


**The easy way (recommended, ~25 minutes, no tools needed):**
1. Create a free account at [github.com](https://github.com) and create a new repository.
2. Upload this whole project folder to it (on the GitHub site: *Add file > Upload files*, drag everything in, and make sure the `.github` folder is included - it may be hidden in your file explorer, enable "show hidden files").
3. In your repo open the **Actions** tab, click **Build Android APK** and press **Run workflow**.
4. When the run turns green (~25 min), click it and download the **Zarya-Porter-Android-APK** artifact - your APK is inside. Copy it to your phone and install it (allow "install unknown apps" when Android asks).

**The local way (one command):** on Linux or WSL2 run `tools/build_apk_local.sh` - the script fetches the JDK, the SDK and the NDK, applies every python-for-android patch, pre-caches the freetype source from a working mirror and leaves the APK in `bin/`. Give it a folder with ~8 GB free and no spaces in the path (`ZARYA_APK_ROOT=/path ./tools/build_apk_local.sh`).

The Android app is the same porter with the same dark square UI, all fifty-one themes (picked from a scrollable list), the four languages, and it scans your Download/Documents folders for `.zip` and `.mcpack` packs and saves the converted pack back to Downloads. It targets Android 5.0 and newer on arm64 devices (that is virtually every modern phone). The included `.github/workflows/build-apk.yml` encodes every python-for-android patch needed to build it, so the cloud build works unattended.

## How to use

1. Install [Python 3.10+](https://python.org) (check "Add to PATH" on Windows).
2. Double click `Zarya Porter.py` (or `Run Zarya Porter.bat` on Windows).
3. Drop your `.zip` / `.mcpack` Java pack (or click the card to browse - folders work too).
4. Flip the switches you want.
5. Choose where to save the `.mcpack` (or `.zip`).
6. Press **CONVERT**, then double click the generated file to import it into Bedrock.

## First run on Windows

If double clicking the `.py` opens the wrong app: right click it, **Open with**, choose **Python**. Or just use `Run Zarya Porter.bat`.

Dependencies install on demand: `pip install -r requirements.txt` (PySide6 + Pillow).

## Classic menus on modern packs

You can turn on ChouiUI for any pack version. If the pack is newer than 1.8, the app warns you first in plain English: newer Minecraft versions changed how menus are laid out, so some slots may not line up with the pack's own menu textures. Nothing breaks - and creative mode still shows the default block list, just with the H button swapping to a centered classic panel and back.

## Credits

- **ChouiUI** - by Choui (that's me).
- Reference studies on how other open-source pack porters handle liquids, flipbooks and atlas quirks - all conversion code here is original.
- Not affiliated with Mojang or Microsoft.
