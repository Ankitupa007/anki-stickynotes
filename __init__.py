# __init__.py
from aqt import mw, gui_hooks, QAction, QMenu, QShortcut, QKeySequence, QFileDialog, QDialog, QListWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QBoxLayout
from aqt.qt import QAction
from aqt.utils import  getOnlyText, showInfo, tooltip, askUser
import json
import time
from .dialog import StickyDialog
from .renderer import render_stickies_for_card
from .storage import init_storage, get_stickies as get, save_stickies as put
import os, shutil

def copy_assets():
    src = os.path.join(os.path.dirname(__file__), "web")
    dst = mw.col.media.dir()
    for f in ["packery.min.js", "sticky.css"]:
        if os.path.exists(os.path.join(src, f)):
            shutil.copy2(os.path.join(src, f), os.path.join(dst, "_" + f))

gui_hooks.profile_did_open.append(lambda: (init_storage(), copy_assets()))

def inject(html, card, kind):
    if kind == "reviewAnswer":
        return html + render_stickies_for_card(card)
    return html

gui_hooks.card_will_show.append(inject)

def menu(reviewer, menu):
    a = QAction("Add Sticky Note\tCtrl+Shift+S", mw)
    a.triggered.connect(lambda: StickyDialog(reviewer.card).show())
    menu.addAction(a)

gui_hooks.reviewer_will_show_context_menu.append(menu)

def js(handled, msg, ctx):
    if msg.startswith("stickyEdit:") or msg.startswith("stickyDelete:"):
        idx = int(msg.split(":")[1])
        card = mw.reviewer.card
        if msg.startswith("stickyEdit:"):
            StickyDialog(card, idx).show()
        else:
            data = get(card.note().id)
            if 0 <= idx < len(data):
                data.pop(idx)
                put(card.note().id, data)
                mw.reviewer._redraw_current_card()
        return (True, None)
    return handled

def setup_shortcuts(reviewer):
    # Only create once (bulletproof GC protection)
    if hasattr(reviewer.web, "_sticky_shortcut"):
        return
    
    def open_dialog():
        if not reviewer.card:
            return
        from .dialog import StickyDialog
        dialog = StickyDialog(reviewer.card)
        dialog.show()
    
    # Attach to reviewer.web (the QWebEngineView) — fixes PyQt6 TypeError
    shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), reviewer.web)
    shortcut.activated.connect(open_dialog)
    reviewer.web._sticky_shortcut = shortcut  # Prevent garbage collection


def add_export_import_menu():
    # Create submenu
    menu = QMenu("Sticky Notes", mw)
    mw.form.menuTools.addMenu(menu)

    # Export action
    export_act = QAction("Export Sticky Notes from Deck…", mw)
    export_act.triggered.connect(choose_deck_and_export)
    menu.addAction(export_act)

    # Import action
    import_act = QAction("Import Sticky Notes into Deck…", mw)
    import_act.triggered.connect(choose_deck_and_import)
    menu.addAction(import_act)

# ——— EXPORT & IMPORT WITH DECK SELECTION DIALOG ———

def choose_deck_and_export():
    # Get all deck names (all_names_and_ids() already excludes dynamic decks)
    deck_names = [d.name for d in mw.col.decks.all_names_and_ids()]

    if not deck_names:
        showInfo("No decks found!")
        return

    dialog = QDialog(mw)
    dialog.setWindowTitle("Export Sticky Notes — Select Deck")
    dialog.resize(420, 520)
    layout = QVBoxLayout(dialog)

    layout.addWidget(QLabel("Choose a deck to export all sticky notes from:"))
    
    listw = QListWidget()
    listw.addItems(sorted(deck_names))
    listw.setCurrentRow(0)
    layout.addWidget(listw)

    btns = QHBoxLayout()
    ok = QPushButton("Export")
    cancel = QPushButton("Cancel")
    btns.addStretch()
    btns.addWidget(ok)
    btns.addWidget(cancel)
    layout.addLayout(btns)

    def on_ok():
        item = listw.currentItem()
        if item:
            dialog.accept()
            perform_export(item.text())

    ok.clicked.connect(on_ok)
    cancel.clicked.connect(dialog.reject)
    dialog.exec()

def perform_export(deck_name: str):
    did = mw.col.decks.id_for_name(deck_name)
    note_ids = mw.col.db.list(f"SELECT id FROM notes WHERE id IN (SELECT nid FROM cards WHERE did = {did})")

    data = {}
    for nid in note_ids:
        stickies = get(nid)
        if stickies:
            data[str(nid)] = stickies

    if not data:
        showInfo(f"No sticky notes found in deck:\n{deck_name}")
        return

    path, _ = QFileDialog.getSaveFileName(
        mw, "Export Sticky Notes",
        f"{deck_name.replace('::', '_')}_stickynotes.json",
        "Sticky Notes (*.stickynotes *.json)"
    )
    if path:
        export_data = {
            "exported_from": deck_name,
            "exported_at": time.strftime("%Y-%m-%d %H:%M"),
            "notes": data
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        tooltip(f"Exported {len(data)} note(s) from '{deck_name}'!")

# ——— IMPORT: Deck selection dialog (Anki 25.09+ compatible) ———
def choose_deck_and_import():
    path, _ = QFileDialog.getOpenFileName(
        mw, "Import Sticky Notes", "", "Sticky Notes (*.stickynotes *.json)"
    )
    if not path:
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            export_data = json.load(f)
    except Exception as e:
        showInfo(f"Failed to read file:\n{e}")
        return

    # Get all deck names (all_names_and_ids() already excludes dynamic decks)
    deck_names = [d.name for d in mw.col.decks.all_names_and_ids()]
    if not deck_names:
        showInfo("No decks to import into!")
        return

    dialog = QDialog(mw)
    dialog.setWindowTitle("Import Sticky Notes — Select Target Deck")
    dialog.resize(420, 520)
    layout = QVBoxLayout(dialog)

    layout.addWidget(QLabel(f"Import {len(export_data.get('notes', {}))} sticky note set(s) into:"))
    
    listw = QListWidget()
    listw.addItems(sorted(deck_names))
    listw.setCurrentRow(0)
    layout.addWidget(listw)

    btns = QHBoxLayout()
    ok = QPushButton("Import")
    cancel = QPushButton("Cancel")
    btns.addStretch()
    btns.addWidget(ok)
    btns.addWidget(cancel)
    layout.addLayout(btns)

    def on_ok():
        item = listw.currentItem()
        if item:
            dialog.accept()
            perform_import(export_data, item.text())

    ok.clicked.connect(on_ok)
    cancel.clicked.connect(dialog.reject)
    dialog.exec()


def perform_import(export_data: dict, deck_name: str):
    did = mw.col.decks.id_for_name(deck_name)
    if not did:
        showInfo("Target deck no longer exists!")
        return

    note_ids = mw.col.db.list(f"SELECT id FROM notes WHERE id IN (SELECT nid FROM cards WHERE did = {did})")
    if not note_ids:
        showInfo("Target deck has no notes!")
        return

    imported = 0
    notes_data = export_data.get("notes", {})
    for i, (old_nid, stickies) in enumerate(notes_data.items()):
        if i >= len(note_ids):
            break
        target_nid = note_ids[i]
        put(target_nid, stickies)
        imported += 1

    mw.reset()
    tooltip(f"Successfully imported {imported} sticky note(s) into\n'{deck_name}'!")


add_export_import_menu()

gui_hooks.reviewer_did_init.append(setup_shortcuts)
gui_hooks.webview_did_receive_js_message.append(js)