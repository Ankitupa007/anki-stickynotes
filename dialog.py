# dialog.py — FINAL, FLAWLESS, OBSIDIAN-LEVEL MARKDOWN EDITOR
from aqt import mw, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QTextEdit, QWebEngineView, QTimer, QMessageBox, qtmajor, QLineEdit
from aqt.utils import tooltip
from aqt.qt import QToolBar, QAction, QTextCursor, Qt, QIcon, QSize, QFont, QFontDatabase, QPixmap, QPainter, QColor, QFileDialog, QBuffer, QIODevice, QByteArray, QUrl, QWebEngineSettings
from .storage import get_stickies, save_stickies
from . import markdown2
import html, re, os, time, json, urllib.parse, urllib.request, urllib.error

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


def create_text_icon(text, size=20, color="#919191"):
    """Create a QIcon from text"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    font = QFont("Arial")
    font.setPixelSize(10)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(color))
    
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
    painter.end()
    
    return QIcon(pixmap)


class TenorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Tenor GIFs")
        self.resize(600, 600)
        self.selected_url = None
        self.next_pos = None
        self.current_results = []
        self.current_query = ""
        
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for GIFs...")
        self.search_input.returnPressed.connect(lambda: self.do_search(new_search=True))
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(lambda: self.do_search(new_search=True))
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Web view for results
        self.web = QWebEngineView()
        self.web.titleChanged.connect(self.on_title_changed)
        layout.addWidget(self.web)
        
        # Load More button
        self.load_more_btn = QPushButton("Load More")
        self.load_more_btn.clicked.connect(lambda: self.do_search(new_search=False))
        self.load_more_btn.setVisible(False)
        layout.addWidget(self.load_more_btn)
        
        # Initial trending search
        self.do_search(new_search=True)

    def do_search(self, new_search=False):
        if new_search:
            self.current_query = self.search_input.text()
            self.next_pos = None
            self.current_results = []
            
        api_key = "LIVDSRZULELA"  # Public Tenor API Key
        limit = 20
        
        url = "https://g.tenor.com/v1/"
        if self.current_query:
            url += f"search?q={urllib.parse.quote(self.current_query)}&"
        else:
            url += "trending?"
            
        url += f"key={api_key}&limit={limit}"
        
        if self.next_pos:
            url += f"&pos={self.next_pos}"
            
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            self.next_pos = data.get("next", None)
            self.current_results.extend(data.get('results', []))
            
            self.render_results()
            self.load_more_btn.setVisible(bool(self.next_pos))
            
        except urllib.error.URLError as e:
            # Network-related errors (no internet, DNS failure, etc.)
            error_html = """
            <html>
            <head>
                <style>
                    body { 
                        background-color: #333; 
                        color: white; 
                        font-family: sans-serif; 
                        padding: 40px; 
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .error-container {
                        text-align: center;
                        max-width: 400px;
                    }
                    h2 { color: #ff6b6b; margin-bottom: 20px; }
                    p { line-height: 1.6; color: #ddd; }
                    .icon { font-size: 48px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <div class="icon">🌐❌</div>
                    <h2>No Internet Connection</h2>
                    <p>Unable to connect to Tenor GIF service.</p>
                    <p>Please check your internet connection and try again.</p>
                </div>
            </body>
            </html>
            """
            self.web.setHtml(error_html)
            self.load_more_btn.setVisible(False)
        except Exception as e:
            # Other errors (API errors, parsing errors, etc.)
            error_html = f"""
            <html>
            <head>
                <style>
                    body {{ 
                        background-color: #333; 
                        color: white; 
                        font-family: sans-serif; 
                        padding: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                    }}
                    .error-container {{
                        text-align: center;
                        max-width: 400px;
                    }}
                    h2 {{ color: #ffa500; margin-bottom: 20px; }}
                    p {{ line-height: 1.6; color: #ddd; }}
                    .error-details {{ 
                        background: rgba(0,0,0,0.3); 
                        padding: 10px; 
                        border-radius: 5px; 
                        margin-top: 15px;
                        font-size: 12px;
                        color: #aaa;
                    }}
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h2>⚠️ Error Loading GIFs</h2>
                    <p>Something went wrong while fetching GIFs from Tenor.</p>
                    <div class="error-details">Error: {str(e)}</div>
                </div>
            </body>
            </html>
            """
            self.web.setHtml(error_html)
            self.load_more_btn.setVisible(False)

    def render_results(self):
        html_content = """
        <html>
        <head>
            <style>
                body { background-color: #333; color: white; font-family: sans-serif; padding: 10px; }
                .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
                .item { cursor: pointer; border-radius: 8px; overflow: hidden; position: relative; }
                .item img { width: 100%; height: 120px; object-fit: cover; display: block; }
                .item:hover { opacity: 0.8; }
            </style>
            <script>
                function selectGif(url) {
                    document.title = "SELECTED:" + url;
                }
            </script>
        </head>
        <body>
            <div class="grid">
        """
        
        for result in self.current_results:
            media = result['media'][0]
            thumb_url = media['tinygif']['url']
            full_url = media['gif']['url']
            html_content += f"""
                <div class="item" onclick="selectGif('{full_url}')">
                    <img src="{thumb_url}">
                </div>
            """
            
        html_content += """
            </div>
        </body>
        </html>
        """
        self.web.setHtml(html_content)

    def on_title_changed(self, title):
        if title.startswith("SELECTED:"):
            self.selected_url = title[9:]
            self.accept()


def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    return markdown2.markdown(text, extras=["fenced-code-blocks", "tables", "break-on-newline", "cuddled-lists", "strike"]).strip()


class MarkdownTextEdit(QTextEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            match = re.match(r'^(\s*)([-*•])\s', text)
            if match:
                indent, marker = match.groups()
                if text.strip() == marker:
                    cursor.beginEditBlock()
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.insertBlock()
                    cursor.endEditBlock()
                else:
                    super().keyPressEvent(event)
                    self.insertPlainText(f"{indent}{marker} ")
                return
        super().keyPressEvent(event)

    def canInsertFromMimeData(self, source):
        if source.hasImage():
            return True
        return super().canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        if source.hasFormat("image/gif"):
            data = source.data("image/gif")
            self.save_and_insert_bytes(data, ".gif")
            return
        if source.hasImage():
            image = source.imageData()
            if image:
                self.save_and_insert_image(image)
                return
        if source.hasUrls():
            for url in source.urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp')):
                        self.save_and_insert_file(path)
                        return
        super().insertFromMimeData(source)

    def save_and_insert_image(self, image):
        if isinstance(image, QPixmap):
            image = image.toImage()
        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        data = ba.data()
        filename = f"_sticky_paste_{int(time.time()*1000)}.png"
        mw.col.media.write_data(filename, data)
        self.insertPlainText(f"![image]({filename})")

    def save_and_insert_bytes(self, data: QByteArray, ext: str):
        filename = f"_sticky_paste_{int(time.time()*1000)}{ext}"
        mw.col.media.write_data(filename, data.data())
        self.insertPlainText(f"![image]({filename})")

    def save_and_insert_file(self, file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        ext = os.path.splitext(file_path)[1]
        filename = f"_sticky_import_{int(time.time()*1000)}{ext}"
        mw.col.media.write_data(filename, data)
        self.insertPlainText(f"![image]({filename})")


class StickyDialog(QDialog):
    def __init__(self, card, idx=None):
        super().__init__(mw)
        self.card = card
        self.note_id = card.note().id
        self.idx = idx
        self.data = get_stickies(self.note_id)
        self.sticky = self.data[idx] if idx is not None and idx < len(self.data) else {
            "data": "", "color": "yellow", "font_size": 16, "font_family": "Comic Sans MS",
            "width": 300, "height": 150
        }
        self.current_color = self.sticky.get("color", "yellow")
        self.setWindowTitle("Edit Sticky Note" if idx is not None else "New Sticky Note")
        self.resize(1180, 760)

        font_path = os.path.join(os.path.dirname(__file__), "icomoon.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        top_row = QHBoxLayout()
        top_row.setSpacing(48)

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

        self.color_buttons[self.current_color].setChecked(True)
        colors_group.addLayout(color_swatch_row)
        top_row.addLayout(colors_group)

        font_group = QVBoxLayout()
        font_group.setSpacing(14)

        ff_row = QHBoxLayout()
        ff_row.addWidget(QLabel("Font family"))
        self.ff = QComboBox()
        self.ff.addItems(["Inter, Arial, sans-serif", "Arial", "Georgia", "Verdana", "Courier New", "Trebuchet MS", "Comic Sans MS"])
        self.ff.setCurrentText(self.sticky.get("font_family", "Comic Sans MS"))
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
        
        MATERIAL_ICONS = {
            "bold": 0xe905,
            "italic": 0xe904,
            "strikethrough": 0xe906,
            "h1": 0xe90a,
            "h2": 0xe909,
            "h3": 0xe908,
            "list": 0xe903,
            "code": 0xe901,
            "link": 0xe902,
            "quote": 0xe900,
            "hr": 0xe907,
            "image": 0xe90b,
            "gif": 0xe90d,
        }
        
        def add_btn(text, tip, open_tag="", close_tag="", prefix="", shortcut=None, icon_code=None, handler=None, checkable=True):
            if icon_code and icon_code in MATERIAL_ICONS:
                icon = create_icon_from_font(MATERIAL_ICONS[icon_code], 20, "#919191")
                act = QAction(icon, "", self)
            else:
                act = QAction(text, self)
            
            act.setToolTip(tip + (f" ({shortcut})" if shortcut else ""))
            act.setCheckable(checkable)
            if shortcut:
                act.setShortcut(shortcut)
            if handler:
                act.triggered.connect(handler)
            else:
                act.triggered.connect(lambda: self.toggle_format(open_tag, close_tag, prefix))
            toolbar.addAction(act)
            self.buttons[text] = act

        add_btn("B", "Bold", "**", "**", shortcut="Ctrl+B", icon_code="bold")
        add_btn("I", "Italic", "*", "*", shortcut="Ctrl+I", icon_code="italic")
        add_btn("S", "Strikethrough", "~~", "~~", shortcut="Ctrl+Shift+X", icon_code="strikethrough")
        add_btn("H1", "Heading 1", prefix="# ", shortcut="Alt+1", icon_code="h1")
        add_btn("H2", "Heading 2", prefix="## ", shortcut="Alt+2", icon_code="h2")
        add_btn("H3", "Heading 3", prefix="### ", shortcut="Alt+3", icon_code="h3")
        add_btn("List", "Bullet List", prefix="- ", shortcut="Ctrl+Shift+L", icon_code="list")
        add_btn("`", "Inline Code", "`", "`", shortcut="Ctrl+`", icon_code="code")
        add_btn("Link", "Insert Link", "[link", "](url here)", shortcut="Ctrl+K", icon_code="link")
        add_btn("Image", "Insert Image", shortcut="Ctrl+Shift+I", icon_code="image", handler=self.insert_image, checkable=False)
        add_btn("Qt", "Blockquote", prefix="> ", shortcut="Ctrl+Shift+Q", icon_code="quote")
        add_btn("---", "Horizontal Rule", "\n---\n", "", shortcut="Ctrl+Shift+H", icon_code="hr")
        add_btn("GIF", "Insert GIF", shortcut="Ctrl+Shift+G", icon_code="gif", handler=self.insert_gif, checkable=False)

        main_layout.addWidget(toolbar)

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
        
        settings = self.preview.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        split.addWidget(self.preview, 1)
        main_layout.addLayout(split, 1)

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

        # Track last rendered HTML to prevent unnecessary updates that cause flickering
        self.last_preview_html = ""

        # Connect signals - instant preview with smart HTML change detection
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

    def insert_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp)"
        )
        if file_path:
            self.editor.save_and_insert_file(file_path)

    def insert_gif(self):
        dialog = TenorDialog(self)
        if dialog.exec():
            url = dialog.selected_url
            if url:
                self.editor.insertPlainText(f"![gif]({url})")

    def update_buttons(self):
        if not hasattr(self, "buttons"):
            return
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        block = cursor.block()
        text = block.text()
        pos = cursor.position() - block.position()
        line_start = text[:pos].lstrip()

        self.buttons["B"].setChecked(bool(selected.startswith("**") and selected.endswith("**")))
        self.buttons["I"].setChecked(bool(selected.startswith("*") and selected.endswith("*") and not (selected.startswith("**") or selected.startswith("***"))))
        self.buttons["S"].setChecked(bool(selected.startswith("~~") and selected.endswith("~~")))
        self.buttons["`"].setChecked(bool(selected.startswith("`") and selected.endswith("`")))
        
        self.buttons["H1"].setChecked(line_start.startswith("# ") and not line_start.startswith("##"))
        self.buttons["H2"].setChecked(line_start.startswith("## ") and not line_start.startswith("###"))
        self.buttons["H3"].setChecked(line_start.startswith("### "))
        self.buttons["List"].setChecked(any(line_start.startswith(p) for p in ["- ", "* ", "• "]))
        self.buttons["Qt"].setChecked(line_start.startswith("> "))
        
        link_pattern = r'(?<!!)\[([^\]]+)\]\(([^\)]+)\)'
        is_in_link = False
        if selected:
            is_in_link = bool(re.match(link_pattern, selected))
        else:
            line_text = block.text()
            for match in re.finditer(link_pattern, line_text):
                start, end = match.span()
                cursor_pos_in_line = cursor.position() - block.position()
                if start <= cursor_pos_in_line <= end:
                    is_in_link = True
                    break
        self.buttons["Link"].setChecked(is_in_link)
        
        is_hr = text.strip() in ["---", "___"]
        self.buttons["---"].setChecked(is_hr)

    def update_preview(self):
        raw = self.editor.toPlainText()
        rendered = markdown_to_html(raw)
        bg = self.color_map.get(self.current_color, "#fff9c4")

        html = f"""
        <html><head><style>
            body {{background:#333333; border-radius:12px; display:flex; justify-content:center; align-items:center; padding:50px; margin:0;}}
            .note {{
                background:{bg};
                color:#1a1a1a; 
                border-radius:18px;
                padding:0px 14px;
                width:{self.w.value()}px; 
                min-height:{self.h.value()}px;
                font-family:'{self.ff.currentText()}';
                font-size:{self.fs.value()}px;
                line-height:1.33;
            }}
            .sticky-content-empty {{ padding:10px 0; margin:8px 0;}}
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
            img {{ max-width: 100%; height: auto; border-radius: 8px; margin-top:0px; }}
        </style></head><body>
            <div class="note">{rendered or "<p class='sticky-content-empty'>This is your sticky note preview</p>"}</div>
        </body></html>
        """
        
        # Only update HTML if it has actually changed to prevent image flickering
        if html != self.last_preview_html:
            base_url = QUrl.fromLocalFile(mw.col.media.dir() + "/")
            self.preview.setHtml(html, baseUrl=base_url)
            self.last_preview_html = html

    def save(self):
        new_text = self.editor.toPlainText()
        
        if self.idx is not None:
            old_text = self.sticky.get("data", "")
            old_images = extract_image_filenames(old_text)
            new_images = extract_image_filenames(new_text)
            
            removed_images = old_images - new_images
            to_delete = [img for img in removed_images if img.startswith("_sticky_")]
            if to_delete:
                mw.col.media.trash_files(to_delete)
        
        new_sticky = {
            "data": new_text,
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
            text = self.sticky.get("data", "")
            images = extract_image_filenames(text)
            to_delete = [img for img in images if img.startswith("_sticky_")]
            if to_delete:
                mw.col.media.trash_files(to_delete)
            
            self.data.pop(self.idx)
            save_stickies(self.note_id, self.data)
            tooltip("Sticky deleted")
            mw.reviewer._redraw_current_card()
            self.close()

def extract_image_filenames(text):
    """Extract all image filenames from markdown text"""
    return set(re.findall(r'!\[.*?\]\((.*?)\)', text))