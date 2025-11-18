# __init__.py
from aqt import mw, gui_hooks, QAction, QMenu, QShortcut, QKeySequence, QFileDialog, QDialog, QListWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QBoxLayout, QTextBrowser, QDesktopServices, QUrl, Qt, QTextEdit, QApplication, QPixmap
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


def add_top_level_menu():
    # Create a top-level menu called "Sticky Notes"
    sticky_menu = QMenu("&Sticky Notes", mw)  # &S makes Alt+S the shortcut
    mw.form.menubar.addMenu(sticky_menu)

    # About action
    about_act = QAction("About Sticky Notes…", mw)
    about_act.triggered.connect(show_about_dialog)
    sticky_menu.addAction(about_act)

    sticky_menu.addSeparator()

    # Export action
    export_act = QAction("Export Sticky Notes from Deck…", mw)
    export_act.setShortcut("Ctrl+Alt+E")  # optional shortcut
    export_act.triggered.connect(choose_deck_and_export)
    sticky_menu.addAction(export_act)

    # Import action
    import_act = QAction("Import Sticky Notes into Deck…", mw)
    import_act.setShortcut("Ctrl+Alt+I")  # optional shortcut
    import_act.triggered.connect(choose_deck_and_import)
    sticky_menu.addAction(import_act)

    # Optional: Add a link to documentation or GitHub
    sticky_menu.addSeparator()
    docs_act = QAction("Documentation & GitHub", mw)
    docs_act.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Ankitupa007/anki-stickynotes")))
    sticky_menu.addAction(docs_act)


def show_upi_info():
    
    upi_dialog = QDialog(mw)
    upi_dialog.setWindowTitle("UPI Payment Details")
    upi_dialog.resize(500, 620)
    
    layout = QVBoxLayout(upi_dialog)
    layout.setSpacing(15)
    
    title = QLabel("<h2>💰 Support via UPI</h2>")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
    layout.addWidget(title)
    
    # QR Code Section
    qr_label_title = QLabel("<b>Scan QR Code:</b>")
    qr_label_title.setStyleSheet("font-size: 13px;")
    layout.addWidget(qr_label_title)
    
    # QR Code Image - Save your QR code as "upi_qr.jpg" in addon folder
    qr_path = os.path.join(os.path.dirname(__file__), "upi_qr.jpg")
    
    qr_container = QLabel()
    if os.path.exists(qr_path):
        pixmap = QPixmap(qr_path)
        scaled_pixmap = pixmap.scaled(
            280, 280,
            Qt.AspectRatioMode.KeepAspectRatio if hasattr(Qt, 'AspectRatioMode') else Qt.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation if hasattr(Qt, 'TransformationMode') else Qt.SmoothTransformation
        )
        qr_container.setPixmap(scaled_pixmap)
        qr_container.setStyleSheet("padding: 10px; border-radius: 8px;")
    else:
        qr_container.setText("⚠️ QR Code not found\nPlace 'upi_qr.jpg' in addon folder")
        qr_container.setStyleSheet("padding: 30px;  border: 2px dashed #ccc; border-radius: 8px; color: #666;")
    
    qr_container.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
    layout.addWidget(qr_container)
    
    # Divider
    divider = QLabel("<center>— OR —</center>")
    divider.setStyleSheet("color: #999; font-size: 12px; margin: 10px 0;")
    layout.addWidget(divider)
    
    # UPI ID Section
    upi_label = QLabel("<b>Copy UPI ID:</b>")
    upi_label.setStyleSheet("font-size: 13px;")
    layout.addWidget(upi_label)
    
    instruction = QLabel("Use in any UPI app (PhonePe, Google Pay, Paytm, etc.)")
    instruction.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 5px;")
    layout.addWidget(instruction)

    # NAME display
    upi_id_name = "Ankit Upadhyay"
    
    upi_box_name = QTextEdit()
    upi_box_name.setPlainText(upi_id_name)
    upi_box_name.setMaximumHeight(50)
    upi_box_name.setStyleSheet("""
        QTextEdit {
            font-size: 16px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            padding: 10px;
            border-radius: 5px;
        }
    """)
    upi_box_name.setReadOnly(True)
    upi_box_name.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
    layout.addWidget(upi_box_name)
    
    # UPI ID display - REPLACE WITH YOUR ACTUAL UPI ID
    upi_id = "ankit.upa007@oksbi"
    
    upi_box = QTextEdit()
    upi_box.setPlainText(upi_id)
    upi_box.setMaximumHeight(50)
    upi_box.setStyleSheet("""
        QTextEdit {
            font-size: 16px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            padding: 10px;
            border: 2px solid #5f259f;
            border-radius: 5px;
        }
    """)
    upi_box.setReadOnly(True)
    upi_box.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
    layout.addWidget(upi_box)
    
    # Copy button
    copy_btn = QPushButton("📋 Copy UPI ID to Clipboard")
    copy_btn.setStyleSheet("""
        QPushButton {
            padding: 10px 20px;
            background: #5f259f;
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton:hover {
            background: #4a1d7f;
        }
    """)
    copy_btn.setCursor(Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else Qt.PointingHandCursor)
    
    def copy_to_clipboard():
        QApplication.clipboard().setText(upi_id)
        tooltip("✓ UPI ID copied to clipboard!")
    
    copy_btn.clicked.connect(copy_to_clipboard)
    layout.addWidget(copy_btn)
    
    layout.addStretch()
    
    # Thank you note
    thanks = QLabel("Thank you for supporting this project! 💜")
    thanks.setStyleSheet("font-size: 12px; color: #666; font-style: italic;")
    thanks.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
    layout.addWidget(thanks)
    
    # Close button
    close_btn = QPushButton("Close")
    close_btn.setStyleSheet("""
        QPushButton {
            padding: 8px 24px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: #1976D2;
        }
    """)
    close_btn.clicked.connect(upi_dialog.accept)
    
    close_layout = QHBoxLayout()
    close_layout.addStretch()
    close_layout.addWidget(close_btn)
    close_layout.addStretch()
    layout.addLayout(close_layout)
    
    upi_dialog.exec()

def show_about_dialog():
    
    dialog = QDialog(mw)
    dialog.setWindowTitle("About Sticky Notes Add-on")
    dialog.resize(800, 600)
    
    layout = QVBoxLayout(dialog)
    layout.setSpacing(15)
    
    # Title and version
    title = QLabel("<h2>Sticky Notes for Anki</h2>")
    title.setStyleSheet("font-weight: bold;")
    layout.addWidget(title)
    
    version = QLabel("Version 1.7.3")
    version.setStyleSheet("font-size: 13px; color: #aaa;")
    layout.addWidget(version)
    
    # Description
    desc = QTextBrowser()
    desc.setMaximumHeight(120)
    desc.setOpenExternalLinks(True)
    desc.setHtml("""
        <p style='font-size: 13px; line-height: 1.6;'>
        A powerful Markdown-enabled sticky notes add-on with an intuitive live preview editor.
        Add beautiful formatted stickies to your cards without editing templates.
        </p>
    """)
    layout.addWidget(desc)
    
    
    # Links section
    links_label = QLabel("<b>Resources:</b>")
    links_label.setStyleSheet("font-size: 13px; margin-top: 10px;")
    layout.addWidget(links_label)
    
    links_layout = QHBoxLayout()
    links_layout.setSpacing(8)
    
    def create_link_button(text, url):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 20px 20px;
                # border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #2196F3;
            }
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else Qt.PointingHandCursor)
        btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        return btn
    
    github_btn = create_link_button("📦 View on AnkiWeb / GitHub", "https://github.com/Ankitupa007/anki-stickynotes")
    links_layout.addWidget(github_btn)
    
    docs_btn = create_link_button("📖 Documentation & Guide", "https://github.com/Ankitupa007/anki-stickynotes")
    links_layout.addWidget(docs_btn)

    docs_btn = create_link_button("📽️ Watch a tutorial", "https://github.com/Ankitupa007/anki-stickynotes")
    links_layout.addWidget(docs_btn)
    
    issues_btn = create_link_button("🐛 Report Issues", "https://github.com/Ankitupa007/anki-stickynotes/issues")
    links_layout.addWidget(issues_btn)
    
    layout.addLayout(links_layout)
    
    # Support section
    support_label = QLabel("<b>Support Development:</b>")
    support_label.setStyleSheet("font-size: 13px; margin-top: 10px;")
    layout.addWidget(support_label)
    
    # Support Description
    desc = QTextBrowser()
    desc.setMaximumHeight(120)
    desc.setOpenExternalLinks(True)
    desc.setHtml("""
        <p style='font-size: 13px; line-height: 1.6;'>
        I am a solo developer dedicating my time to create and maintain this add-on for the Anki community.
        If you find this add-on useful, please consider supporting its development through donations. Indian patrons can use UPI, while international users can use PayPal.
        Your support helps me continue improving and updating the add-on. Thank you for using this Add-on!✨
        </p>
    """)
    layout.addWidget(desc)

    support_layout = QHBoxLayout()
    support_layout.setSpacing(10)
    
    def create_donate_button(text, url, color):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                background: {color};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {color}dd;
            }}
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else Qt.PointingHandCursor)
        btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        return btn
    
    # UPI button - shows UPI ID in a dialog
    upi_btn = create_donate_button("💰 UPI (India)", "", "#5f259f")
    upi_btn.clicked.disconnect()
    upi_btn.clicked.connect(show_upi_info)
    support_layout.addWidget(upi_btn)
    
    paypal_btn = create_donate_button("💝 PayPal (International)", "https://paypal.me/thisisankitupadhyay", "#0138A5")
    support_layout.addWidget(paypal_btn)
    
    layout.addLayout(support_layout)
    
    # Update check info
    update_info = QLabel(
        "💡 <i>Check AnkiWeb regularly for updates</i>"
    )
    update_info.setStyleSheet("font-size: 11px; color: #666; margin-top: 5px;")
    layout.addWidget(update_info)
    
    layout.addStretch()
    
    # Footer
    footer = QLabel(
        "Made with ❤️ for the Anki community<br>"
        "© 2025 — Free and open source"
    )
    footer.setStyleSheet("font-size: 11px; color: #999; text-align: center;")
    footer.setAlignment(Qt.AlignmentFlag.AlignCenter if hasattr(Qt, 'AlignmentFlag') else Qt.AlignCenter)
    layout.addWidget(footer)
    
    # Close button
    close_btn = QPushButton("Close")
    close_btn.setStyleSheet("""
        QPushButton {
            padding: 8px 24px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: #1976D2;
        }
    """)
    close_btn.clicked.connect(dialog.accept)
    
    close_layout = QHBoxLayout()
    close_layout.addStretch()
    close_layout.addWidget(close_btn)
    close_layout.addStretch()
    layout.addLayout(close_layout)
    
    dialog.exec()

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


add_top_level_menu()

gui_hooks.reviewer_did_init.append(setup_shortcuts)
gui_hooks.webview_did_receive_js_message.append(js)