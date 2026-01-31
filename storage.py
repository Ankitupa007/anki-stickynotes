# storage.py
import json
import os
from aqt import mw

FILENAME = "_stickynotes.json"

def _path():
    return os.path.join(mw.col.media.dir(), FILENAME)

def init_storage():
    path = _path()
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_all():
    try:
        with open(_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all(data):
    with open(_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 100% compatible way to mark media as changed in Anki 25.09+
    try:
        # Newest way (25.09+)
        mw.col.media.mark_file_modified()
    except AttributeError:
        try:
            # Slightly older 25.09 builds
            mw.col.media._changed = True
        except AttributeError:
            # Fallback – just trigger a harmless media check
            mw.col.media.check()

def get_stickies(note_id):
    return load_all().get(str(note_id), [])

def save_stickies(note_id, stickies):
    data = load_all()
    data[str(note_id)] = stickies
    save_all(data)

def get_default_settings():
    """Get default sticky note settings from Anki config"""
    config = mw.addonManager.getConfig(__name__) or {}
    preset_name = config.get("last_preset_name")
    presets = config.get("presets", {})
    
    # If a named preset is set as default, pull values dynamically from its definition
    if preset_name and preset_name in presets:
        p = presets[preset_name]
        return {
            "color": p.get("color", "yellow"),
            "font_size": p.get("font_size", 16),
            "font_family": p.get("font_family", "Comic Sans MS"),
            "width": p.get("width", 300),
            "height": p.get("height", 150),
            "bold": p.get("bold", False),
            "italic": p.get("italic", False),
            "preset": preset_name
        }
    
    # Fallback to loose default values if no preset is selected or it was deleted
    return {
        "color": config.get("default_color", "yellow"),
        "font_size": config.get("default_font_size", 16),
        "font_family": config.get("default_font_family", "Comic Sans MS"),
        "width": config.get("default_width", 300),
        "height": config.get("default_height", 150),
        "bold": config.get("default_bold", False),
        "italic": config.get("default_italic", False),
        "preset": None
    }

def save_default_settings(settings):
    """Save default sticky note settings to Anki config"""
    config = mw.addonManager.getConfig(__name__) or {}
    config.update({
        "default_color": settings.get("color", "yellow"),
        "default_font_size": settings.get("font_size", 16),
        "default_font_family": settings.get("font_family", "Comic Sans MS"),
        "default_width": settings.get("width", 300),
        "default_height": settings.get("height", 150),
        "default_bold": settings.get("bold", False),
        "default_italic": settings.get("italic", False),
        "last_preset_name": settings.get("preset_name")
    })
    mw.addonManager.writeConfig(__name__, config)

def get_presets():
    """Get all saved sticky note presets"""
    config = mw.addonManager.getConfig(__name__) or {}
    return config.get("presets", {
        "Standard": {
            "color": "yellow",
            "font_size": 16,
            "font_family": "Comic Sans MS",
            "width": 300,
            "height": 150,
            "bold": False,
            "italic": False
        }
    })

def save_presets(presets):
    """Save all sticky note presets"""
    config = mw.addonManager.getConfig(__name__) or {}
    config["presets"] = presets
    mw.addonManager.writeConfig(__name__, config)

def get_templates():
    """Get saved content templates (snippets)"""
    config = mw.addonManager.getConfig(__name__) or {}
    return config.get("templates", {
        "Checklist": "- [ ] Item 1\n- [ ] Item 2",
        "Med Table": "| Symptom | Sign | Treatment |\n| --- | --- | --- |\n| | | |"
    })

def save_templates(templates):
    """Save content templates"""
    config = mw.addonManager.getConfig(__name__) or {}
    config["templates"] = templates
    mw.addonManager.writeConfig(__name__, config)