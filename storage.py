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