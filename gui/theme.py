from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

DEFAULT_THEME = "Graphite"


def _rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _pal(bg, grad_top, grad_bottom, card, card_hover, input_bg, border,
         border_strong, text, muted, faint, accent, accent_2,
         success=None, success_dark=None, warn=None, error=None,
         track_off=None, knob_top="#ffffff", knob_bottom=None,
         btn_disabled=None, btn_border=None, dots=None, shadow_alpha=120):
    mono = _rgb(accent)[0] == _rgb(accent)[1] == _rgb(accent)[2]
    if success is None:
        success = accent_2 if mono else accent
    if success_dark is None:
        success_dark = text if mono else accent
    if warn is None:
        warn = muted if mono else "#fbbf24"
    if error is None:
        error = faint if mono else "#f87171"
    if track_off is None:
        track_off = border_strong
    if knob_bottom is None:
        knob_bottom = muted if mono else "#e6e9f2"
    if btn_disabled is None:
        btn_disabled = input_bg
    if btn_border is None:
        btn_border = border_strong
    if dots is None:
        dots = [accent, accent_2, muted, faint, border_strong]
    return {
        "BG": bg,
        "BG_GRADIENT_TOP": grad_top,
        "BG_GRADIENT_BOTTOM": grad_bottom,
        "CARD": card,
        "CARD_HOVER": card_hover,
        "INPUT": input_bg,
        "BORDER": border,
        "BORDER_STRONG": border_strong,
        "TEXT": text,
        "TEXT_MUTED": muted,
        "TEXT_FAINT": faint,
        "ACCENT": accent,
        "ACCENT_2": accent_2,
        "SUCCESS": success,
        "SUCCESS_DARK": success_dark,
        "WARN": warn,
        "ERROR": error,
        "DANGER": error,
        "GLOW_ACCENT": _rgb(accent),
        "GLOW_SUCCESS": _rgb(accent_2),
        "GLOW_OFF": _rgb(border_strong),
        "GLOW_CYAN": _rgb(muted),
        "TRACK_OFF": track_off,
        "KNOB_TOP": knob_top,
        "KNOB_BOTTOM": knob_bottom,
        "BTN_DISABLED": btn_disabled,
        "BTN_BORDER": btn_border,
        "DOTS": dots,
        "SHADOW_ALPHA": shadow_alpha,
    }


THEMES = {}
THEME_ORDER = []

def _register(name, palette):
    THEMES[name] = palette
    THEME_ORDER.append(name)


_register("Graphite", _pal(
    bg="#0a0a0a", grad_top="#101010", grad_bottom="#070707",
    card="#141414", card_hover="#191919", input_bg="#0f0f0f",
    border="#272727", border_strong="#343434",
    text="#e8e8e8", muted="#9a9a9a", faint="#5f5f5f",
    accent="#c9c9c9", accent_2="#a3a3a3",
    track_off="#2c2c2c", knob_top="#ffffff", knob_bottom="#c9c9c9",
    btn_disabled="#1d1d1d", btn_border="#3a3a3a",
))

_register("Ink", _pal(
    bg="#000000", grad_top="#050505", grad_bottom="#000000",
    card="#0d0d0d", card_hover="#131313", input_bg="#080808",
    border="#1f1f1f", border_strong="#2e2e2e",
    text="#f5f5f5", muted="#a8a8a8", faint="#666666",
    accent="#ffffff", accent_2="#d0d0d0",
    track_off="#242424", knob_top="#ffffff", knob_bottom="#d8d8d8",
    btn_disabled="#161616", btn_border="#333333",
))

_register("Paper", _pal(
    bg="#eceef1", grad_top="#f4f5f7", grad_bottom="#e4e6ea",
    card="#ffffff", card_hover="#f5f6f8", input_bg="#f0f1f4",
    border="#d4d7dd", border_strong="#bcbfc7",
    text="#17181b", muted="#5d6169", faint="#8f939b",
    accent="#5f636b", accent_2="#7c8087",
    track_off="#c9ccd3", knob_top="#ffffff", knob_bottom="#dfe2e7",
    btn_disabled="#e2e4e8", btn_border="#aeb1b9",
    shadow_alpha=60,
))

_register("Ocean", _pal(
    bg="#0a0f16", grad_top="#0e1622", grad_bottom="#070b11",
    card="#121a26", card_hover="#16202e", input_bg="#0d141e",
    border="#233246", border_strong="#31455f",
    text="#e6edf5", muted="#93a6bc", faint="#5b6d82",
    accent="#4fa3ff", accent_2="#38bdf8",
    track_off="#26333f", knob_top="#ffffff", knob_bottom="#cfe6ff",
))

_register("Cyan Wave", _pal(
    bg="#081114", grad_top="#0c181d", grad_bottom="#050d10",
    card="#0f1d23", card_hover="#132529", input_bg="#0a161b",
    border="#1f3a42", border_strong="#2b505a",
    text="#e4f2f5", muted="#8fadb5", faint="#587278",
    accent="#2dd4bf", accent_2="#22d3ee",
    track_off="#22373d", knob_top="#ffffff", knob_bottom="#c9f2ec",
))

_register("Emerald", _pal(
    bg="#0a120c", grad_top="#0e1a10", grad_bottom="#060b07",
    card="#111f14", card_hover="#152718", input_bg="#0c1710",
    border="#1f3a26", border_strong="#2b5034",
    text="#e4f2e7", muted="#8fbc9a", faint="#587a61",
    accent="#3ddc84", accent_2="#7ee2a8",
    track_off="#22392a", knob_top="#ffffff", knob_bottom="#ccf2dc",
))

_register("Lime", _pal(
    bg="#0d1108", grad_top="#131a0c", grad_bottom="#080b05",
    card="#161d10", card_hover="#1c2414", input_bg="#10150b",
    border="#2c3a1c", border_strong="#3d5228",
    text="#eef4e6", muted="#a8bd8f", faint="#6a7a58",
    accent="#a3e635", accent_2="#c8f06e",
    track_off="#2b3520", knob_top="#ffffff", knob_bottom="#e7f7c6",
))

_register("Crimson", _pal(
    bg="#120a0b", grad_top="#1a0d0f", grad_bottom="#0c0607",
    card="#1d1113", card_hover="#241518", input_bg="#150c0d",
    border="#3a2024", border_strong="#502c31",
    text="#f5e6e8", muted="#bd8f95", faint="#7a5a5f",
    accent="#ff5a5a", accent_2="#ff8a7a",
    track_off="#332023", knob_top="#ffffff", knob_bottom="#ffd2d2",
))

_register("Rose", _pal(
    bg="#120a0f", grad_top="#1a0e16", grad_bottom="#0c060a",
    card="#1d1119", card_hover="#241521", input_bg="#150c11",
    border="#3a2030", border_strong="#502c43",
    text="#f5e6f0", muted="#bd8fab", faint="#7a5a71",
    accent="#ff7ab8", accent_2="#ffa5cf",
    track_off="#33202c", knob_top="#ffffff", knob_bottom="#ffd9ec",
))

_register("Amethyst", _pal(
    bg="#0e0a14", grad_top="#140f1e", grad_bottom="#080510",
    card="#171126", card_hover="#1d1530", input_bg="#110c1c",
    border="#2c2044", border_strong="#3d2c5e",
    text="#ece6f5", muted="#a394bd", faint="#665a7a",
    accent="#a78bfa", accent_2="#c4b0fd",
    track_off="#2a2038", knob_top="#ffffff", knob_bottom="#e3d9fd",
))

_register("Sunset", _pal(
    bg="#120e08", grad_top="#1a140b", grad_bottom="#0b0805",
    card="#1d1710", card_hover="#241d14", input_bg="#150f0a",
    border="#3a2e1c", border_strong="#504027",
    text="#f5efe6", muted="#bda78f", faint="#7a6a5a",
    accent="#ff9950", accent_2="#ffbe7a",
    track_off="#332a1c", knob_top="#ffffff", knob_bottom="#ffe3c9",
))

_register("Gold", _pal(
    bg="#111008", grad_top="#18160b", grad_bottom="#0a0905",
    card="#1a1810", card_hover="#211e14", input_bg="#131207",
    border="#332f1c", border_strong="#474127",
    text="#f4f2e6", muted="#b5ad8f", faint="#736e5a",
    accent="#e6b93f", accent_2="#f0d07a",
    track_off="#2f2b1c", knob_top="#ffffff", knob_bottom="#f7e9c4",
))

_register("Steel", _pal(
    bg="#0c0f14", grad_top="#11151d", grad_bottom="#080a0e",
    card="#141a24", card_hover="#19202c", input_bg="#0e1219",
    border="#242e3e", border_strong="#314054",
    text="#e8edf5", muted="#94a3b8", faint="#5b6878",
    accent="#7c9cf3", accent_2="#a3bcf7",
    track_off="#262f3b", knob_top="#ffffff", knob_bottom="#d6e2fc",
))

_register("Blood Moon", _pal(
    bg="#0d0708", grad_top="#130a0c", grad_bottom="#070404",
    card="#170d0f", card_hover="#1d1013", input_bg="#10090a",
    border="#2e1a1d", border_strong="#412529",
    text="#f2e6e8", muted="#b18d92", faint="#6e5558",
    accent="#e04848", accent_2="#ff6b5e",
    track_off="#2b1a1d", knob_top="#ffffff", knob_bottom="#f6cfcf",
))

_register("Snow Light", _pal(
    bg="#e8edf3", grad_top="#f2f6fa", grad_bottom="#dfe5ec",
    card="#ffffff", card_hover="#f3f6fa", input_bg="#eef2f7",
    border="#cdd6e0", border_strong="#b3bfcd",
    text="#1a2230", muted="#5a6a7e", faint="#8b99ab",
    accent="#3b82f6", accent_2="#6ea8ff",
    track_off="#c4cedb", knob_top="#ffffff", knob_bottom="#dbe7ff",
    shadow_alpha=60,
))

_register("Ash", _pal(
    bg="#0b0a09", grad_top="#111009", grad_bottom="#070605",
    card="#16140f", card_hover="#1c1a15", input_bg="#100e0c",
    border="#2b2820", border_strong="#3c382e",
    text="#eeeae2", muted="#b0a898", faint="#6e675c",
    accent="#b5aca0", accent_2="#cfc6ba",
    track_off="#2e2a24", knob_top="#ffffff", knob_bottom="#d8d2c8",
))
_register("Slate", _pal(
    bg="#0b0e13", grad_top="#10141c", grad_bottom="#070a0e",
    card="#141924", card_hover="#19202e", input_bg="#0e121b",
    border="#242e3e", border_strong="#32405a",
    text="#e8edf5", muted="#9aabc4", faint="#5e6c82",
    accent="#8fa8c8", accent_2="#b0c6de",
    track_off="#28303e", knob_top="#ffffff", knob_bottom="#d4e0ee",
))
_register("Carbon", _pal(
    bg="#0a0c0e", grad_top="#0f1216", grad_bottom="#06080a",
    card="#14171b", card_hover="#191d22", input_bg="#0e1114",
    border="#252a31", border_strong="#333a44",
    text="#e9edf1", muted="#9aa5b1", faint="#5f6a76",
    accent="#9aa5b1", accent_2="#bcc6d0",
    track_off="#2a3038", knob_top="#ffffff", knob_bottom="#d5dce4",
))
_register("Void", _pal(
    bg="#050508", grad_top="#0a0a10", grad_bottom="#030305",
    card="#0e0e15", card_hover="#13131c", input_bg="#090910",
    border="#1e1e2c", border_strong="#2c2c40",
    text="#ececf5", muted="#8f8fa8", faint="#575770",
    accent="#7d7d95", accent_2="#a0a0b8",
    track_off="#23233a", knob_top="#ffffff", knob_bottom="#c9c9dc",
))
_register("Midnight", _pal(
    bg="#070b18", grad_top="#0c1224", grad_bottom="#040712",
    card="#101730", card_hover="#151d3c", input_bg="#0b1122",
    border="#1f2a4c", border_strong="#2c3c68",
    text="#e7ecf8", muted="#8fa0c8", faint="#57668e",
    accent="#5b7bd5", accent_2="#88a2e8",
    track_off="#242e4c", knob_top="#ffffff", knob_bottom="#ccd8f5",
))
_register("Deep Sea", _pal(
    bg="#061013", grad_top="#0a181c", grad_bottom="#040a0c",
    card="#0c1a1f", card_hover="#10222a", input_bg="#081419",
    border="#1b343c", border_strong="#264952",
    text="#e2f2f4", muted="#84aab2", faint="#516c72",
    accent="#14b8a6", accent_2="#5ad4c6",
    track_off="#1e3438", knob_top="#ffffff", knob_bottom="#c2ece6",
))
_register("Teal", _pal(
    bg="#081211", grad_top="#0c1a18", grad_bottom="#050b0a",
    card="#0f1d1b", card_hover="#132523", input_bg="#0a1614",
    border="#1e3a36", border_strong="#2b524c",
    text="#e3f2f0", muted="#8cb8b0", faint="#56736e",
    accent="#2ab7a9", accent_2="#66d3c8",
    track_off="#203a36", knob_top="#ffffff", knob_bottom="#c5ebe5",
))
_register("Aqua", _pal(
    bg="#071015", grad_top="#0b181f", grad_bottom="#040a0e",
    card="#0c1a22", card_hover="#10222c", input_bg="#08141b",
    border="#173444", border_strong="#214a5e",
    text="#e2f1f8", muted="#83aebf", faint="#506c7a",
    accent="#22d3ee", accent_2="#67e2f4",
    track_off="#1d3644", knob_top="#ffffff", knob_bottom="#c0ecf7",
))
_register("Sky", _pal(
    bg="#091018", grad_top="#0d1724", grad_bottom="#060a10",
    card="#0e1928", card_hover="#122032", input_bg="#0a131f",
    border="#1b2e48", border_strong="#264062",
    text="#e4eef8", muted="#8aa8c4", faint="#54687e",
    accent="#38bdf8", accent_2="#7cd4fa",
    track_off="#20334a", knob_top="#ffffff", knob_bottom="#c5e7fb",
))
_register("Periwinkle", _pal(
    bg="#0b0d18", grad_top="#101224", grad_bottom="#070810",
    card="#131630", card_hover="#191c3c", input_bg="#0d1024",
    border="#242a52", border_strong="#323a70",
    text="#e9eaf8", muted="#9ba0cc", faint="#60648c",
    accent="#818cf8", accent_2="#a8b0fb",
    track_off="#282c4c", knob_top="#ffffff", knob_bottom="#d3d7fb",
))
_register("Indigo", _pal(
    bg="#0a0c1a", grad_top="#0f1226", grad_bottom="#060810",
    card="#121531", card_hover="#171b3e", input_bg="#0c0f24",
    border="#22264e", border_strong="#303668",
    text="#e8eaf8", muted="#98a0cc", faint="#5d648c",
    accent="#6366f1", accent_2="#8f92f5",
    track_off="#262a4c", knob_top="#ffffff", knob_bottom="#ccd0fa",
))
_register("Violet", _pal(
    bg="#0d0a18", grad_top="#130f22", grad_bottom="#080610",
    card="#161130", card_hover="#1c163c", input_bg="#100c22",
    border="#282050", border_strong="#372c6c",
    text="#ebe8f8", muted="#a49cc8", faint="#665e8a",
    accent="#8b5cf6", accent_2="#b088fa",
    track_off="#2a2244", knob_top="#ffffff", knob_bottom="#dcd0fb",
))
_register("Plum", _pal(
    bg="#0e0814", grad_top="#140c1e", grad_bottom="#080410",
    card="#170f28", card_hover="#1e1332", input_bg="#110a1e",
    border="#2a1c44", border_strong="#3a285c",
    text="#ede7f5", muted="#a894c4", faint="#68587e",
    accent="#a855f7", accent_2="#c488fa",
    track_off="#2c2044", knob_top="#ffffff", knob_bottom="#e3d0fb",
))
_register("Magenta", _pal(
    bg="#130811", grad_top="#1a0c18", grad_bottom="#0c040a",
    card="#1d0f1b", card_hover="#251423", input_bg="#150a13",
    border="#381c33", border_strong="#4e2847",
    text="#f5e8f2", muted="#c08fab", faint="#78586c",
    accent="#e04fc4", accent_2="#ef85da",
    track_off="#32202e", knob_top="#ffffff", knob_bottom="#f7cdec",
))
_register("Fuchsia", _pal(
    bg="#120812", grad_top="#190c19", grad_bottom="#0b040b",
    card="#1c0f1c", card_hover="#241424", input_bg="#140a14",
    border="#341a34", border_strong="#482548",
    text="#f5e8f5", muted="#bd8fbd", faint="#755875",
    accent="#f055d4", accent_2="#f685e2",
    track_off="#30202f", knob_top="#ffffff", knob_bottom="#f9cff0",
))
_register("Salmon", _pal(
    bg="#140a0c", grad_top="#1c0e11", grad_bottom="#0d0607",
    card="#1e1214", card_hover="#251719", input_bg="#160c0e",
    border="#382024", border_strong="#4e2c31",
    text="#f5e9ea", muted="#c08f94", faint="#785a5e",
    accent="#fb7185", accent_2="#fb98a7",
    track_off="#322023", knob_top="#ffffff", knob_bottom="#fecfd7",
))
_register("Coral", _pal(
    bg="#140a08", grad_top="#1c0e0b", grad_bottom="#0d0604",
    card="#1e1210", card_hover="#251815", input_bg="#160d0b",
    border="#38221c", border_strong="#4e2f26",
    text="#f5ebe6", muted="#c09284", faint="#785c52",
    accent="#ff7f66", accent_2="#ff9c8a",
    track_off="#32221c", knob_top="#ffffff", knob_bottom="#fed6cb",
))
_register("Tangerine", _pal(
    bg="#130c07", grad_top="#1a110a", grad_bottom="#0c0704",
    card="#1d1410", card_hover="#241a14", input_bg="#150e0a",
    border="#37261a", border_strong="#4d3524",
    text="#f5ede4", muted="#c0a088", faint="#786554",
    accent="#ff8c42", accent_2="#ffab6e",
    track_off="#332619", knob_top="#ffffff", knob_bottom="#fedcc4",
))
_register("Amber", _pal(
    bg="#120d06", grad_top="#191309", grad_bottom="#0b0703",
    card="#1c150c", card_hover="#231b10", input_bg="#140f07",
    border="#332815", border_strong="#47381d",
    text="#f5efe2", muted="#bfae8a", faint="#776a52",
    accent="#f5a623", accent_2="#f8c05e",
    track_off="#322a17", knob_top="#ffffff", knob_bottom="#fde9bd",
))
_register("Butter", _pal(
    bg="#101008", grad_top="#16160b", grad_bottom="#0a0a04",
    card="#1a1a0e", card_hover="#212115", input_bg="#131309",
    border="#30301a", border_strong="#434325",
    text="#f5f4e2", muted="#b8b58a", faint="#706e54",
    accent="#fde047", accent_2="#feea80",
    track_off="#2e2e1c", knob_top="#ffffff", knob_bottom="#fef7c3",
))
_register("Olive", _pal(
    bg="#0d0f08", grad_top="#12160c", grad_bottom="#070804",
    card="#151a10", card_hover="#1b2115", input_bg="#0e120a",
    border="#27301c", border_strong="#364227",
    text="#eef2e2", muted="#a8b88a", faint="#677454",
    accent="#a8b545", accent_2="#c4cf6e",
    track_off="#2a331d", knob_top="#ffffff", knob_bottom="#e6eec3",
))
_register("Forest", _pal(
    bg="#081009", grad_top="#0c160e", grad_bottom="#040a05",
    card="#0e1c12", card_hover="#122418", input_bg="#091309",
    border="#183420", border_strong="#22482c",
    text="#e4f2e6", muted="#8ab894", faint="#526e58",
    accent="#34c759", accent_2="#6bdc84",
    track_off="#1e3624", knob_top="#ffffff", knob_bottom="#c7f0d0",
))
_register("Pine", _pal(
    bg="#071010", grad_top="#0b1818", grad_bottom="#040a0a",
    card="#0c1c1a", card_hover="#102422", input_bg="#081414",
    border="#173430", border_strong="#204842",
    text="#e2f1ee", muted="#84b0a8", faint="#506c66",
    accent="#1fa885", accent_2="#5cc9a8",
    track_off="#1c3630", knob_top="#ffffff", knob_bottom="#c1ece2",
))
_register("Moss", _pal(
    bg="#0b0f09", grad_top="#10160e", grad_bottom="#070a05",
    card="#121a10", card_hover="#172115", input_bg="#0c120a",
    border="#212e1a", border_strong="#2e4024",
    text="#ecf2e2", muted="#9cb88a", faint="#5e7254",
    accent="#7fb069", accent_2="#a3cd90",
    track_off="#26331e", knob_top="#ffffff", knob_bottom="#dcefce",
))
_register("Coffee", _pal(
    bg="#100c09", grad_top="#16110d", grad_bottom="#0a0705",
    card="#1a1410", card_hover="#211a15", input_bg="#120d0a",
    border="#30241c", border_strong="#433226",
    text="#f2ece4", muted="#b89c88", faint="#6e5c50",
    accent="#b08968", accent_2="#cba98c",
    track_off="#302620", knob_top="#ffffff", knob_bottom="#e8d7c6",
))
_register("Mocha", _pal(
    bg="#100d0b", grad_top="#161311", grad_bottom="#0a0807",
    card="#1a1614", card_hover="#211d1a", input_bg="#120f0d",
    border="#302a25", border_strong="#433a33",
    text="#f2eee9", muted="#b8a698", faint="#6e635a",
    accent="#c4a484", accent_2="#d8bfa4",
    track_off="#302a24", knob_top="#ffffff", knob_bottom="#efe1d0",
))
_register("Wine", _pal(
    bg="#100810", grad_top="#160c16", grad_bottom="#0a040a",
    card="#190f19", card_hover="#201420", input_bg="#120a12",
    border="#2e1a2e", border_strong="#402540",
    text="#f2e6f0", muted="#b88fb4", faint="#6e5870",
    accent="#c7365f", accent_2="#e06085",
    track_off="#2e202c", knob_top="#ffffff", knob_bottom="#f3c9d9",
))
_register("Neon", _pal(
    bg="#0a0f06", grad_top="#0f160a", grad_bottom="#050803",
    card="#101a0c", card_hover="#152210", input_bg="#0a1207",
    border="#1c3012", border_strong="#28431a",
    text="#eaf5e0", muted="#8fbc7c", faint="#567050",
    accent="#ccff00", accent_2="#e2ff66",
    track_off="#20341a", knob_top="#ffffff", knob_bottom="#eefbb8",
))
_register("Toxic", _pal(
    bg="#0c0f05", grad_top="#121608", grad_bottom="#070903",
    card="#131a0a", card_hover="#192210", input_bg="#0d1206",
    border="#223012", border_strong="#2f441a",
    text="#eef5e0", muted="#9cb87c", faint="#5e7050",
    accent="#84cc16", accent_2="#a8e03e",
    track_off="#24331a", knob_top="#ffffff", knob_bottom="#ddf5b8",
))
_register("Rust", _pal(
    bg="#100a07", grad_top="#16100b", grad_bottom="#0a0604",
    card="#1a120e", card_hover="#211813", input_bg="#120c09",
    border="#302218", border_strong="#432e21",
    text="#f2ebe4", muted="#b89880", faint="#6e5c4e",
    accent="#c96f4a", accent_2="#dc9470",
    track_off="#30241c", knob_top="#ffffff", knob_bottom="#eed4c2",
))
_register("Bone", _pal(
    bg="#f0ede8", grad_top="#f7f5f1", grad_bottom="#e6e2da",
    card="#ffffff", card_hover="#f6f4f0", input_bg="#f1eee9",
    border="#ddd7cc", border_strong="#c4bcb0",
    text="#1d1a16", muted="#6b6459", faint="#9b938a",
    accent="#8a8177", accent_2="#a89f94",
    track_off="#cfc8bd", knob_top="#ffffff", knob_bottom="#e8e2d9",
    shadow_alpha=60,
))
_register("Sand", _pal(
    bg="#f2ecdf", grad_top="#f9f5ea", grad_bottom="#e8e0cf",
    card="#ffffff", card_hover="#f7f3e8", input_bg="#f2ede0",
    border="#ded4bd", border_strong="#c5b89e",
    text="#211c12", muted="#6e6350", faint="#9d917c",
    accent="#a08a5f", accent_2="#bcaa80",
    track_off="#d2c8b0", knob_top="#ffffff", knob_bottom="#eae1cb",
    shadow_alpha=60,
))
_register("Mint Cream", _pal(
    bg="#e9f4ec", grad_top="#f1f9f3", grad_bottom="#dcebe0",
    card="#ffffff", card_hover="#f2f8f4", input_bg="#ebf4ee",
    border="#cfe2d5", border_strong="#b2cdbd",
    text="#14231a", muted="#5a7264", faint="#8a9f92",
    accent="#34a86a", accent_2="#62c48d",
    track_off="#c3dccd", knob_top="#ffffff", knob_bottom="#d9f0e1",
    shadow_alpha=60,
))
_register("Lavender Mist", _pal(
    bg="#efeef7", grad_top="#f6f5fb", grad_bottom="#e5e3f0",
    card="#ffffff", card_hover="#f4f3fa", input_bg="#efeef7",
    border="#d9d7e8", border_strong="#bcb9d4",
    text="#1c1a2e", muted="#635e84", faint="#948fb0",
    accent="#7c6fd0", accent_2="#9c92e0",
    track_off="#cdc9e2", knob_top="#ffffff", knob_bottom="#e2dff4",
    shadow_alpha=60,
))
_register("Sakura", _pal(
    bg="#f9eef2", grad_top="#fcf4f7", grad_bottom="#f2e3e9",
    card="#ffffff", card_hover="#fbf2f5", input_bg="#f9eef2",
    border="#ecd4dd", border_strong="#d8b3c1",
    text="#2a1620", muted="#7d5a68", faint="#a88895",
    accent="#d4699b", accent_2="#e390b8",
    track_off="#e0c3cf", knob_top="#ffffff", knob_bottom="#f6dbe5",
    shadow_alpha=60,
))
_register("Ice", _pal(
    bg="#e8f1f6", grad_top="#f1f8fb", grad_bottom="#dce9f0",
    card="#ffffff", card_hover="#f1f6f9", input_bg="#eaf2f6",
    border="#d0dfe8", border_strong="#b3c8d4",
    text="#14202c", muted="#5a6e7c", faint="#8a9ba6",
    accent="#2f8fc4", accent_2="#64b0d9",
    track_off="#c5d8e2", knob_top="#ffffff", knob_bottom="#d9ecf5",
    shadow_alpha=60,
))

_current = dict(THEMES[DEFAULT_THEME])

FONT_FAMILY = "Segoe UI Variable Display"
FONT_FALLBACK = "Segoe UI"
MONO_FAMILY = "Cascadia Mono"

DROP_SHADOW = {
    "color": QColor(0, 0, 0, 120),
    "blur": 24,
    "offset": (0, 8),
}


def __getattr__(name):
    try:
        return _current[name]
    except KeyError:
        raise AttributeError(name)


def current_name():
    for name, pal in THEMES.items():
        if pal == _current:
            return name
    return DEFAULT_THEME


def names():
    return list(THEME_ORDER)


def is_dark(name):
    pal = THEMES.get(name, THEMES[DEFAULT_THEME])
    c = QColor(pal["BG"])
    return c.lightness() < 128


def qss():
    return """
    QWidget {{ background-color: transparent; color: {text};
               font-family: "{family}", "{fallback}"; font-size: 13px; }}
    QMainWindow, QDialog {{ background-color: {bg}; }}
    QWidget#central {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                      stop:0 {grad_top}, stop:1 {grad_bottom}); }}
    QFrame#card {{ background-color: {card}; border: 1px solid {border}; border-radius: 0px; }}
    QLabel {{ background: transparent; border: none; }}
    QLabel#brand {{ font-size: 27px; font-weight: 800; letter-spacing: 8px; color: {text}; }}
    QLabel#brandSub {{ font-size: 10px; font-weight: 700; letter-spacing: 5px; color: {faint}; }}
    QLabel#section {{ font-size: 10px; font-weight: 800; letter-spacing: 3px; color: {faint}; }}
    QLabel#secHead {{ font-size: 11px; font-weight: 800; letter-spacing: 3px;
                      color: {accent}; background: transparent; }}
    QLabel#muted {{ color: {muted}; font-size: 12px; }}
    QFrame#hline {{ background-color: {border}; border: none; max-height: 1px; }}
    QWidget#optInner {{ background: transparent; }}
    QScrollArea {{ background: transparent; border: none; }}
    QLabel#chip {{ background-color: {input}; border: 1px solid {border}; border-radius: 0px;
                   padding: 5px 13px; font-size: 12px; font-weight: 700; color: {muted}; }}
    QLabel#drop {{ border: 2px dashed {border_strong}; border-radius: 0px; background: {card}; }}
    QPushButton#pathEdit {{ background-color: {input}; border: 1px solid {border}; border-radius: 0px;
                            padding: 10px 14px; color: {muted}; font-size: 12px; text-align: left; }}
    QPushButton#pathEdit:hover {{ border-color: {accent}; color: {text}; }}
    QPushButton#ghost {{ background-color: {input}; color: {text}; border: 1px solid {border};
                         border-radius: 0px; padding: 9px 18px; font-weight: 700; }}
    QPushButton#ghost:hover {{ border-color: {accent}; color: {accent}; background-color: {card}; }}
    QPushButton#ghost:pressed {{ background-color: {input}; }}
    QPushButton#footer {{ background: transparent; color: {faint}; border: none; font-size: 12px; }}
    QPushButton#footer:hover {{ color: {muted}; }}
    QTextEdit#log {{ background-color: {input}; border: 1px solid {border}; border-radius: 0px;
                     color: {muted}; font-family: "{mono}"; font-size: 12px; padding: 10px; }}
    QScrollBar:vertical {{ background: transparent; width: 8px; margin: 4px 2px 4px 0; }}
    QScrollBar::handle:vertical {{ background: {border_strong}; border-radius: 0px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {muted}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
    QToolTip {{ background-color: {card}; color: {text}; border: 1px solid {border}; padding: 6px;
                border-radius: 0px; }}
    """.format(bg=_current["BG"], grad_top=_current["BG_GRADIENT_TOP"],
               grad_bottom=_current["BG_GRADIENT_BOTTOM"], card=_current["CARD"],
               border=_current["BORDER"], border_strong=_current["BORDER_STRONG"],
               text=_current["TEXT"], muted=_current["TEXT_MUTED"],
               faint=_current["TEXT_FAINT"], input=_current["INPUT"],
               accent=_current["ACCENT"], family=FONT_FAMILY,
               fallback=FONT_FALLBACK, mono=MONO_FAMILY)


def _repaint_all():
    for w in QApplication.allWidgets():
        w.update()


def switch(name):
    global _current
    if name not in THEMES:
        name = DEFAULT_THEME
    _current = dict(THEMES[name])
    DROP_SHADOW["color"] = QColor(0, 0, 0, _current["SHADOW_ALPHA"])


def apply(app, name=None):
    app.setStyle("Fusion")
    if name:
        switch(name)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(_current["BG"]))
    palette.setColor(QPalette.WindowText, QColor(_current["TEXT"]))
    palette.setColor(QPalette.Base, QColor(_current["CARD"]))
    palette.setColor(QPalette.Text, QColor(_current["TEXT"]))
    palette.setColor(QPalette.Button, QColor(_current["CARD"]))
    palette.setColor(QPalette.ButtonText, QColor(_current["TEXT"]))
    palette.setColor(QPalette.Highlight, QColor(_current["ACCENT"]))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
    app.setStyleSheet(qss())
    f = QApplication.font()
    f.setFamily(FONT_FALLBACK)
    app.setFont(f)
    _repaint_all()
