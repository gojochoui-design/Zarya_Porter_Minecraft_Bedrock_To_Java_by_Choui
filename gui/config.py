import json
import os

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".zarya_porter")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "theme": "Graphite",
    "language": "en",
    "save_dir": "",
    "options": {},
}


def load():
    cfg = json.loads(json.dumps(DEFAULTS))
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key in DEFAULTS:
                if key in data:
                    cfg[key] = data[key]
            if not isinstance(cfg["options"], dict):
                cfg["options"] = {}
    except Exception:
        pass
    return cfg


def save(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
