# dialog.py — FINAL, FLAWLESS, OBSIDIAN-LEVEL MARKDOWN EDITOR
from aqt import mw, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QTextEdit, QWebEngineView, QTimer, QMessageBox, qtmajor
from aqt.utils import tooltip
from aqt.qt import QToolBar, QAction, QTextCursor, Qt, QIcon, QSize, QFont, QFontDatabase, QPixmap, QPainter, QColor
from .storage import get_stickies, save_stickies
from . import markdown2
import html, re, os

def create_icon_from_font(char_code, size=20, color="#919191"):
    """Create a QIcon from Material Icons font character"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    font = QFont("icomoon")
    font.setPixelSize(size)
    painter.setFont(font)
    painter.setPen(QColor(color))
    
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, chr(char_code))
    painter.end()
    
    return QIcon(pixmap)


def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    # Use markdown2 with extras for better compatibility
    return markdown2.markdown(text, extras=["fenced-code-blocks", "tables", "break-on-newline", "cuddled-lists", "strike"]).strip()


class MarkdownTextEdit(QTextEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            # Check for list markers
            match = re.match(r'^(\s*)([-*•])\s', text)
            if match:
                indent, marker = match.groups()
                # If line is just the marker, remove it (exit list)
                if text.strip() == marker:
                    cursor.beginEditBlock()
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.insertBlock()
                    cursor.endEditBlock()
                else:
                    # Continue list
                    super().keyPressEvent(event)
                    self.insertPlainText(f"{indent}{marker} ")
                return
        
        super().keyPressEvent(event)


class StickyDialog(QDialog):
    def __init__(self, card, idx=None):
        super().__init__(mw)
        self.card = card
        self.note_id = card.note().id
        self.idx = idx
        self.data = get_stickies(self.note_id)
        self.sticky = self.data[idx] if idx is not None and idx < len(self.data) else {
            "data": "", "color": "yellow", "font_size": 16, "font_family": "Verdana",
            "width": 300, "height": 150
        }

        self.current_color = self.sticky.get("color", "yellow")

        self.setWindowTitle("Edit Sticky Note" if idx is not None else "New Sticky Note")
        self.resize(1180, 760)

        # Load Material Icons font
        font_path = os.path.join(os.path.dirname(__file__), "icomoon.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

        # === MAIN LAYOUT ===
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # === TOP CONTROLS ROW ===
        top_row = QHBoxLayout()
        top_row.setSpacing(48)

        # — Colors Section —
        colors_group = QVBoxLayout()
        colors_group.setSpacing(20)
        QLabel("Colors", self).setStyleSheet("font-weight:600; font-size:13px; padding-left:8px;")

        color_swatch_row = QHBoxLayout()
        color_swatch_row.setSpacing(14)

        self.color_map = {
            "yellow": "#fff9c4", "green": "#dcfce7", "blue": "#dbeafe",
            "purple": "#e0d6ff", "pink": "#fce7f3", "orange": "#fed7aa",
        }

        self.color_buttons = {}
        for name, hex_color in self.color_map.items():
            btn = QPushButton()
            btn.setFixedSize(42, 42)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{hex_color};
                    width:12px; height:12px;
                    border: none;
                    border-radius: 6px;
                }}
                QPushButton:checked {{
                    border: 2px solid #007bff;
                    width:24px; height:24px;
                    box-shadow: 0 0 0 3px rgba(255,255,255,0.3);
                    border-radius: 12px;
                }}
                QPushButton:hover:!checked {{   
                    border-radius: 6px;
                    width:12px; height:12px;
                    border:none;
                }}
            """)
            btn.clicked.connect(lambda checked, n=name: self.set_color(n))
            color_swatch_row.addWidget(btn)
            self.color_buttons[name] = btn

        # Select current
        self.color_buttons[self.current_color].setChecked(True)

        colors_group.addLayout(color_swatch_row)
        top_row.addLayout(colors_group)

        # — Font Family & Size —
        font_group = QVBoxLayout()
        font_group.setSpacing(14)

        ff_row = QHBoxLayout()
        ff_row.addWidget(QLabel("Font family"))
        self.ff = QComboBox()
        self.ff.addItems(["Inter, Arial, sans-serif", "Arial", "Georgia", "Verdana", "Courier New", "Trebuchet MS", "Comic Sans MS"])
        self.ff.setCurrentText(self.sticky.get("font_family", "Verdana"))
        self.ff.setStyleSheet("""
            QComboBox {
                border-radius:10px; padding:9px 14px; font-size:13px;
            }
            QComboBox::drop-down { border:none; width:30px; }
        """)
        ff_row.addWidget(self.ff, 1)
        font_group.addLayout(ff_row)

        fs_row = QHBoxLayout()
        fs_row.addWidget(QLabel("Font Size"))
        self.fs = QSpinBox()
        self.fs.setRange(10, 40)
        self.fs.setValue(self.sticky.get("font_size", 16))
        self.fs.setSuffix(" px")
        self.fs.setStyleSheet("border-radius:10px; padding:6px;")
        fs_row.addWidget(self.fs)
        font_group.addLayout(fs_row)
        top_row.addLayout(font_group)

        # — Width & Height —
        size_group = QVBoxLayout()
        size_group.setSpacing(14)

        w_row = QHBoxLayout()
        w_row.addWidget(QLabel("Width"))
        self.w = QSpinBox()
        self.w.setRange(150, 650)
        self.w.setValue(self.sticky.get("width", 300))
        self.w.setSuffix(" px")
        self.w.setStyleSheet("border-radius:10px; padding:6px;")
        w_row.addWidget(self.w)
        size_group.addLayout(w_row)

        h_row = QHBoxLayout()
        h_row.addWidget(QLabel("Height"))
        self.h = QSpinBox()
        self.h.setRange(100, 550)
        self.h.setValue(self.sticky.get("height", 150))
        self.h.setSuffix(" px")
        self.h.setStyleSheet("border-radius:10px; padding:6px;")
        h_row.addWidget(self.h)
        size_group.addLayout(h_row)
        top_row.addLayout(size_group)

        top_row.addStretch()
        main_layout.addLayout(top_row)

        # === TOOLBAR — Material Icons Font ===
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet("""
            QToolBar {
                padding: 6px;
                spacing: 6px;
                background: transparent;
                border: none;
            }


            QToolButton {
                color: palette(window-text);
                background: transparent;
                border-radius: 6px;
                padding: 6px 8px;
                border: none;
            }

            QToolButton:hover {
                background: rgba(128, 128, 128, 0.12);
            }

            QToolButton:checked {
                background: rgba(0, 123, 255, 0.20);
                border: none;
                color: #007BFF;
            }

            QToolButton:focus {
                outline: none;
                border: none;
            }

        """)

        self.buttons = {}
        
        # Material Icons Unicode codepoints
        MATERIAL_ICONS = {
            "bold": 0xe905,           # format_bold
            "italic": 0xe904,         # format_italic
            "strikethrough": 0xe906,  # strikethrough_s
            "h1": 0xe90a,             # looks_one (number 1)
            "h2": 0xe909,             # looks_two (number 2)
            "h3": 0xe908,             # looks_3 (number 3)
            "list": 0xe903,           # format_list_bulleted
            "code": 0xe901,           # code
            "link": 0xe902,           # link
            "quote": 0xe900,          # format_quote
            "hr": 0xe907,             # horizontal_rule
        }
        
        def add_btn(text, tip, open_tag="", close_tag="", prefix="", shortcut=None, icon_code=None):
            if icon_code and icon_code in MATERIAL_ICONS:
                # Create icon with normal color
                icon = create_icon_from_font(MATERIAL_ICONS[icon_code], 20, "#919191")
                act = QAction(icon, "", self)
            else:
                # Fallback to text
                act = QAction(text, self)
            
            act.setToolTip(tip + (f" ({shortcut})" if shortcut else ""))
            act.setCheckable(True)
            if shortcut:
                act.setShortcut(shortcut)
            act.triggered.connect(lambda: self.toggle_format(open_tag, close_tag, prefix))
            toolbar.addAction(act)
            self.buttons[text] = act

        # Add toolbar buttons with Material Icons
        add_btn("B", "Bold", "**", "**", shortcut="Ctrl+B", icon_code="bold")
        add_btn("I", "Italic", "*", "*", shortcut="Ctrl+I", icon_code="italic")
        add_btn("S", "Strikethrough", "~~", "~~", shortcut="Ctrl+Shift+X", icon_code="strikethrough")
        add_btn("H1", "Heading 1", prefix="# ", shortcut="Alt+1", icon_code="h1")
        add_btn("H2", "Heading 2", prefix="## ", shortcut="Alt+2", icon_code="h2")
        add_btn("H3", "Heading 3", prefix="### ", shortcut="Alt+3", icon_code="h3")
        add_btn("List", "Bullet List", prefix="- ", shortcut="Ctrl+Shift+L", icon_code="list")
        add_btn("`", "Inline Code", "`", "`", shortcut="Ctrl+`", icon_code="code")
        add_btn("Link", "Insert Link", "[link", "](url here)", shortcut="Ctrl+K", icon_code="link")
        add_btn("Qt", "Blockquote", prefix="> ", shortcut="Ctrl+Shift+Q", icon_code="quote")
        add_btn("---", "Horizontal Rule", "\n---\n", "", shortcut="Ctrl+Shift+H", icon_code="hr")

        main_layout.addWidget(toolbar)

        # === Editor + Preview Split ===
        split = QHBoxLayout()
        split.setSpacing(20)

        self.editor = MarkdownTextEdit()
        self.editor.setPlainText(self.sticky.get("data", ""))
        self.editor.setStyleSheet("""
            QTextEdit {
                border-radius:6px;
                padding:18px; font-size:16px; font-family:'Segoe UI',sans-serif;
                border:1px solid transparent;
            }
        """)
        self.editor.setPlaceholderText("Start writing here...")
        split.addWidget(self.editor, 1)

        self.preview = QWebEngineView()
        self.preview.setStyleSheet("border-radius:14px;")
        split.addWidget(self.preview, 1)

        main_layout.addLayout(split, 1)

        # === Bottom Buttons ===
        bottom = QHBoxLayout()
        bottom.addStretch()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("background:#4caf50; color:white; padding:12px 38px; border-radius:12px; font-weight:bold; font-size:14px;")
        bottom.addWidget(save_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_)
        delete_btn.setVisible(idx is not None)
        delete_btn.setStyleSheet("background:#f44336; color:white; padding:12px 38px; border-radius:12px; font-weight:bold; font-size:14px;")
        bottom.addWidget(delete_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setStyleSheet("background:#555; color:white; padding:12px 38px; border-radius:12px; font-weight:bold; font-size:14px;")
        bottom.addWidget(cancel_btn)

        main_layout.addLayout(bottom)

        # === Connections ===
        self.editor.textChanged.connect(self.update_preview)
        self.editor.cursorPositionChanged.connect(self.update_buttons)
        self.editor.selectionChanged.connect(self.update_buttons)
        self.fs.valueChanged.connect(self.update_preview)
        self.ff.currentTextChanged.connect(self.update_preview)
        self.w.valueChanged.connect(self.update_preview)
        self.h.valueChanged.connect(self.update_preview)

        QTimer.singleShot(100, lambda: (self.update_preview(), self.update_buttons()))

    def set_color(self, color_name: str):
        self.current_color = color_name
        for name, btn in self.color_buttons.items():
            btn.setChecked(name == color_name)
        self.update_preview()

    def toggle_format(self, open_tag="", close_tag="", prefix=""):
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()

        if selected:
            if selected.startswith(open_tag) and selected.endswith(close_tag):
                cursor.insertText(selected[len(open_tag):-len(close_tag)] if close_tag else selected[len(open_tag):])
            else:
                cursor.insertText(f"{open_tag}{selected}{close_tag}")
        elif prefix:
            block = cursor.block()
            text = block.text()
            start_pos = block.position()
            indent_len = len(text) - len(text.lstrip())
            cursor.setPosition(start_pos + indent_len)
            if text.lstrip().startswith(prefix.strip()):
                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, len(prefix.strip()))
                cursor.removeSelectedText()
            else:
                cursor.setPosition(start_pos)
                cursor.insertText(prefix)
        else:
            cursor.insertText(f"{open_tag}{close_tag}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(close_tag))

        self.editor.setTextCursor(cursor)
        self.update_buttons()

    def update_buttons(self):
        if not hasattr(self, "buttons"):
            return
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        block = cursor.block()
        text = block.text()
        pos = cursor.position() - block.position()
        line_start = text[:pos].lstrip()

        # Check for inline formatting
        self.buttons["B"].setChecked(bool(selected.startswith("**") and selected.endswith("**")))
        self.buttons["I"].setChecked(bool(selected.startswith("*") and selected.endswith("*") and not (selected.startswith("**") or selected.startswith("***"))))
        self.buttons["S"].setChecked(bool(selected.startswith("~~") and selected.endswith("~~")))
        self.buttons["`"].setChecked(bool(selected.startswith("`") and selected.endswith("`")))
        
        # Check for block-level formatting
        self.buttons["H1"].setChecked(line_start.startswith("# ") and not line_start.startswith("##"))
        self.buttons["H2"].setChecked(line_start.startswith("## ") and not line_start.startswith("###"))
        self.buttons["H3"].setChecked(line_start.startswith("### "))
        self.buttons["List"].setChecked(any(line_start.startswith(p) for p in ["- ", "* ", "• "]))
        self.buttons["Qt"].setChecked(line_start.startswith("> "))
        
        # Link button: check if cursor is within a markdown link
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        is_in_link = False
        if selected:
            is_in_link = bool(re.match(link_pattern, selected))
        else:
            # Check if cursor is within a link in the current line
            line_text = block.text()
            for match in re.finditer(link_pattern, line_text):
                start, end = match.span()
                cursor_pos_in_line = cursor.position() - block.position()
                if start <= cursor_pos_in_line <= end:
                    is_in_link = True
                    break
        self.buttons["Link"].setChecked(is_in_link)
        
        # Horizontal rule button: check if current line is a horizontal rule
        is_hr = text.strip() in ["---", "***", "___"]
        self.buttons["---"].setChecked(is_hr)

    def update_preview(self):
        raw = self.editor.toPlainText()
        rendered = markdown_to_html(raw)
        bg = self.color_map.get(self.current_color, "#fff9c4")

        html = f"""
        <html><head><style>
            body {{background:#333333; border-radius:12px; display:flex; justify-content:center; align-items:center; padding:50px; margin:0;}}
            .note {{
                background:{bg}; color:#1a1a1a; padding:24px; border-radius:18px;
                width:{self.w.value()}px; 
                min-height:{self.h.value()}px;
                font-family:'{self.ff.currentText()}';
                font-size:{self.fs.value()}px; 
                line-height:1.33;
            }}
            .note:empty:before {{ content:"This is your note preview"; color:#aaa; font-style:italic; }}
            
            /* Markdown2 specific styles */
            code {{ background:rgba(0,0,0,0.1); padding:2px 4px; border-radius:3px; font-family:monospace; }}
            pre {{ background:rgba(0,0,0,0.1); padding:10px; border-radius:5px; overflow-x:auto; }}
            blockquote {{ 
                border-left: 4px solid rgba(0, 0, 0, 0.2);
                margin: 8px 0;
                padding-left: 12px;
                color: rgba(0, 0, 0, 0.6);
                font-style: italic;
            }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: rgba(0,0,0,0.05); }}
        </style></head><body>
            <div class="note">{rendered or "<em>This is your note preview</em>"}</div>
        </body></html>
        """
        self.preview.setHtml(html)

    def save(self):
        new_sticky = {
            "data": self.editor.toPlainText(),
            "color": self.current_color,
            "font_size": self.fs.value(),
            "font_family": self.ff.currentText(),
            "width": self.w.value(),
            "height": self.h.value()
        }
        if self.idx is not None:
            self.data[self.idx] = new_sticky
        else:
            self.data.append(new_sticky)
        save_stickies(self.note_id, self.data)
        tooltip("Sticky note saved!")
        mw.reviewer._redraw_current_card()
        self.close()

    def delete_(self):
        if QMessageBox.question(self, "Delete", "Delete this sticky note permanently?") == QMessageBox.StandardButton.Yes:
            self.data.pop(self.idx)
            save_stickies(self.note_id, self.data)
            tooltip("Sticky deleted")
            mw.reviewer._redraw_current_card()
            self.close()