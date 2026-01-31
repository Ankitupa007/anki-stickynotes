from aqt import mw, gui_hooks, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QTextEdit, QWebEngineView, QTimer, QMessageBox, qtmajor, QLineEdit, QMenuBar
from aqt.utils import tooltip, showText
from aqt.qt import QToolBar, QAction, QTextCursor, Qt, QIcon, QSize, QFont, QFontDatabase, QPixmap, QPainter, QColor, QFileDialog, QBuffer, QIODevice, QByteArray, QUrl, QWebEngineSettings, QFrame
from .storage import get_stickies, save_stickies, get_default_settings, save_default_settings, get_presets, save_presets, get_templates, save_templates
from .renderer import markdown_to_html
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


# Removed local markdown_to_html, now imported from .renderer


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
        self._is_applying_preset = False
        
        # Load existing sticky or fall back to defaults
        if idx is not None and idx < len(self.data):
            self.sticky = self.data[idx]
        else:
            defaults = get_default_settings()
            self.sticky = {
                "data": "",
                "color": defaults["color"],
                "font_size": defaults["font_size"],
                "font_family": defaults["font_family"],
                "width": defaults["width"],
                "height": defaults["height"],
                "bold": defaults["bold"],
                "italic": defaults["italic"],
                "preset": defaults.get("preset")
            }
            
        self.current_color = self.sticky.get("color", "yellow")
        self.setWindowTitle("Edit Sticky Note" if idx is not None else "New Sticky Note")
        self.resize(900, 700)
        self.current_preset_name = self.sticky.get("preset")
        
        # If no explicit preset saved, try to identify by style match
        if not self.current_preset_name:
            presets = get_presets()
            for name, p in presets.items():
                if (p.get("color") == self.current_color and 
                    p.get("font_size") == self.sticky.get("font_size") and
                    p.get("font_family") == self.sticky.get("font_family") and
                    p.get("bold") == self.sticky.get("bold") and
                    p.get("italic") == self.sticky.get("italic") and
                    p.get("width") == self.sticky.get("width") and
                    p.get("height") == self.sticky.get("height")):
                    self.current_preset_name = name
                    break
                
        self.setup_ui()
        gui_hooks.reviewer_did_show_question.append(self.on_card_change)

    def on_card_change(self):
        """Automatically switch target card when user moves in the reviewer"""
        card = mw.reviewer.card
        if not card or card.note().id == self.note_id:
            return
        
        # If user has unsaved text, maybe we should warn? 
        # For bulk creation, it's usually better to just refresh.
        self.card = card
        self.note_id = card.note().id
        self.prepare_new_note()

    def prepare_new_note(self):
        """Resets the editor state for a fresh note on the current card"""
        self.idx = None
        self.data = get_stickies(self.note_id)
        
        # Reset to defaults
        defaults = get_default_settings()
        self.sticky = {
            "data": "",
            "color": defaults["color"],
            "font_size": defaults["font_size"],
            "font_family": defaults["font_family"],
            "width": defaults["width"],
            "height": defaults["height"],
            "bold": defaults["bold"],
            "italic": defaults["italic"],
            "preset": defaults.get("preset")
        }
        self.current_preset_name = self.sticky.get("preset")
        
        # Update widgets to reflect defaults
        self._is_applying_preset = True
        try:
            self.set_color(self.sticky["color"])
            self.fs.setValue(self.sticky["font_size"])
            self.ff.setCurrentText(self.sticky["font_family"])
            self.w.setValue(self.sticky["width"])
            self.h.setValue(self.sticky["height"])
            self.bold_btn.setChecked(self.sticky["bold"])
            self.italic_btn.setChecked(self.sticky["italic"])
        finally:
            self._is_applying_preset = False
            
        self.editor.clear()
        self.setWindowTitle("New Sticky Note")
        if hasattr(self, "delete_btn"):
            self.delete_btn.setVisible(False)
        if hasattr(self, "save_btn"):
            self.save_btn.setText("Save (Ctrl+S)")
        self.update_preview()
        self.update_presets_menu()

    def closeEvent(self, event):
        """Cleanup hooks when the window is closed"""
        try:
            gui_hooks.reviewer_did_show_question.remove(self.on_card_change)
        except:
            pass
        event.accept()

    def setup_ui(self):
        font_path = os.path.join(os.path.dirname(__file__), "icomoon.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
            
        # Use a main layout with zero margins for the menubar, then a content layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.menubar = self.create_menu_bar()
        self.main_layout.setMenuBar(self.menubar)

        # Content area with padding
        from aqt.qt import QWidget
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(24, 20, 24, 24)
        self.main_layout.addWidget(content_widget)

        # SYSTEMATIC TOP SETTINGS SECTION
        top_settings = QHBoxLayout()
        top_settings.setSpacing(32)

        # 1. COLOR PALETTE GROUP
        color_box = QVBoxLayout()
        color_box.setSpacing(10)
        label_color = QLabel("PALETTE")
        label_color.setStyleSheet("font-weight:bold; font-size:10px; color:#888; letter-spacing:1px;")
        color_box.addWidget(label_color)
        
        color_swatches = QHBoxLayout()
        color_swatches.setSpacing(14)
        
        self.color_map = {
            "yellow": "#fff9c4", "green": "#dcfce7", "blue": "#dbeafe",
            "purple": "#e0d6ff", "pink": "#fce7f3", "orange": "#fed7aa",
        }
        self.color_buttons = {}
        self.color_indicators = {}
        
        for name, hex_color in self.color_map.items():
            swatch_container = QVBoxLayout()
            swatch_container.setSpacing(4)
            swatch_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            btn = QPushButton()
            btn.setFixedSize(28, 28)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Use hyper-robust CSS to force roundness on Windows
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_color};
                    border: 1px solid rgba(0,0,0,0.1);
                    border-radius: 14px;
                    border-style: solid;
                    outline: none;
                    margin: 0;
                    padding: 0;
                }}
                QPushButton:hover {{
                    border: 1px solid rgba(0,0,0,0.3);
                }}
                QPushButton:checked {{
                    border: 2px solid rgba(0,0,0,0.2);
                    background-color: {hex_color};
                }}
                QPushButton:pressed {{
                    background-color: {hex_color};
                    border: 1px solid rgba(0,0,0,0.4);
                }}
            """)
            btn.clicked.connect(lambda checked, n=name: self.set_color(n))
            swatch_container.addWidget(btn)
            
            # Using a more robust dot indicator
            indicator = QFrame()
            indicator.setFixedSize(6, 6)
            indicator.setStyleSheet(f"""
                background-color: #ffffff;
                border-radius: 3px;
                margin: 0;
            """)
            indicator.setVisible(name == self.current_color)
            
            # Center the indicator in a container to manage its layout better
            ind_container = QHBoxLayout()
            ind_container.setContentsMargins(0, 0, 0, 0)
            ind_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ind_container.addWidget(indicator)
            swatch_container.addLayout(ind_container)
            
            color_swatches.addLayout(swatch_container)
            self.color_buttons[name] = btn
            self.color_indicators[name] = indicator
        
        self.color_buttons[self.current_color].setChecked(True)
        color_box.addLayout(color_swatches)
        top_settings.addLayout(color_box)

        # Vertical Separator
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.VLine)
        line1.setStyleSheet("color: rgba(0,0,0,0.1);")
        top_settings.addWidget(line1)

        # 2. TYPOGRAPHY GROUP
        typo_box = QVBoxLayout()
        typo_box.setSpacing(10)
        label_typo = QLabel("TYPOGRAPHY")
        label_typo.setStyleSheet("font-weight:bold; font-size:10px; color:#888; letter-spacing:1px;")
        typo_box.addWidget(label_typo)
        
        typo_controls = QHBoxLayout()
        typo_controls.setSpacing(12)
        
        self.ff = QComboBox()
        self.ff.addItems(["Inter, Arial, sans-serif", "Arial", "Georgia", "Verdana", "Courier New", "Trebuchet MS", "Comic Sans MS"])
        self.ff.setCurrentText(self.sticky.get("font_family", "Comic Sans MS"))
        self.ff.setFixedWidth(180)
        self.ff.setStyleSheet("border-radius:8px; padding:6px; background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.1);")
        
        self.fs = QSpinBox()
        self.fs.setRange(10, 48)
        self.fs.setValue(self.sticky.get("font_size", 16))
        self.fs.setFixedWidth(70)
        self.fs.setSuffix("px")
        self.fs.setStyleSheet("border-radius:8px; padding:6px; background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.1);")

        typo_controls.addWidget(self.ff)
        typo_controls.addWidget(self.fs)

        self.bold_btn = QPushButton()
        self.bold_btn.setIcon(create_icon_from_font(0xe905, 20, "#fff")) # Bold icon
        self.bold_btn.setCheckable(True)
        self.bold_btn.setFixedSize(32, 32)
        self.bold_btn.setChecked(self.sticky.get("bold", False))
        self.bold_btn.setStyleSheet("""
            QPushButton { border-radius:6px; background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.1); }
            QPushButton:checked { background:#007bff; border:none; }
        """)
        
        self.italic_btn = QPushButton()
        self.italic_btn.setIcon(create_icon_from_font(0xe904, 20, "#fff")) # Italic icon
        self.italic_btn.setCheckable(True)
        self.italic_btn.setFixedSize(32, 32)
        self.italic_btn.setChecked(self.sticky.get("italic", False))
        self.italic_btn.setStyleSheet("""
            QPushButton { border-radius:6px; background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.1); }
            QPushButton:checked { background:#007bff; border:none; }
        """)

        typo_controls.addWidget(self.bold_btn)
        typo_controls.addWidget(self.italic_btn)
        typo_box.addLayout(typo_controls)
        top_settings.addLayout(typo_box)

        # Vertical Separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.VLine)
        line2.setStyleSheet("color: rgba(0,0,0,0.1);")
        top_settings.addWidget(line2)

        # 3. DIMENSIONS GROUP
        dim_box = QVBoxLayout()
        dim_box.setSpacing(10)
        label_dim = QLabel("CANVAS")
        label_dim.setStyleSheet("font-weight:bold; font-size:10px; color:#888; letter-spacing:1px;")
        dim_box.addWidget(label_dim)
        
        dim_controls = QHBoxLayout()
        dim_controls.setSpacing(12)
        
        self.w = QSpinBox()
        self.w.setRange(150, 800)
        self.w.setValue(self.sticky.get("width", 300))
        self.w.setPrefix("W: ")
        self.w.setSuffix(" px")
        self.w.setFixedWidth(100)
        self.w.setStyleSheet("border-radius:8px; padding:6px; background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.1);")

        self.h = QSpinBox()
        self.h.setRange(100, 800)
        self.h.setValue(self.sticky.get("height", 150))
        self.h.setPrefix("H: ")
        self.h.setSuffix(" px")
        self.h.setFixedWidth(100)
        self.h.setStyleSheet("border-radius:8px; padding:6px; background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.1);")

        dim_controls.addWidget(self.w)
        dim_controls.addWidget(self.h)
        dim_box.addLayout(dim_controls)
        top_settings.addLayout(dim_box)

        top_settings.addStretch()
        content_layout.addLayout(top_settings)

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

        content_layout.addWidget(toolbar)

        split = QHBoxLayout()
        split.setSpacing(20)

        self.editor = MarkdownTextEdit()
        self.editor.setPlainText(self.sticky.get("data", ""))
        self.editor.setStyleSheet("""
            QTextEdit {
                background: #333333;
                color: #ffffff;
                border-radius:8px;
                padding:18px; font-size:16px; font-family:'Segoe UI',sans-serif;
                border:1px solid rgba(0,0,0,0.1);
            }
        """)
        self.editor.setPlaceholderText("Start writing here...")
        split.addWidget(self.editor, 1)

        self.preview = QWebEngineView()
        self.preview.setStyleSheet("border-radius:14px; border:1px solid rgba(0,0,0,0.05);")
        
        settings = self.preview.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        split.addWidget(self.preview, 1)
        content_layout.addLayout(split, 1)

        bottom = QHBoxLayout()
        bottom.addStretch()

        btn_text = "Update (Ctrl+S)" if self.idx is not None else "Save (Ctrl+S)"
        self.save_btn = QPushButton(btn_text)
        self.save_btn.clicked.connect(self.save)
        self.save_btn.setStyleSheet("background:#4caf50; color:white; padding:8px 38px; border-radius:12px; font-weight:bold; font-size:14px;")
        bottom.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_)
        self.delete_btn.setVisible(self.idx is not None)
        self.delete_btn.setStyleSheet("background:#f44336; color:white; padding:8px 38px; border-radius:12px; font-weight:bold; font-size:14px;")
        bottom.addWidget(self.delete_btn)

        self.cancel_btn = QPushButton("Close")
        self.cancel_btn.clicked.connect(self.close)
        self.cancel_btn.setStyleSheet("background:#555; color:white; padding:8px 38px; border-radius:12px; font-weight:bold; font-size:14px;")
        bottom.addWidget(self.cancel_btn)

        content_layout.addLayout(bottom)

        # Shortcut hint in bottom left
        hint_label = QLabel("Tip: <b>Ctrl+S</b> to save and close")
        hint_label.setStyleSheet("color: #888; font-size: 11px; margin-left: 24px; margin-bottom: 10px;")
        self.main_layout.addWidget(hint_label)

        # Track last rendered HTML to prevent unnecessary updates that cause flickering

        # Track last rendered HTML to prevent unnecessary updates that cause flickering
        self.last_preview_html = ""

        # Connect signals - instant preview with smart HTML change detection
        self.editor.textChanged.connect(self.update_preview)
        self.editor.cursorPositionChanged.connect(self.update_buttons)
        self.editor.selectionChanged.connect(self.update_buttons)
        self.fs.valueChanged.connect(lambda: (self.clear_preset_indicator(), self.update_preview()))
        self.ff.currentTextChanged.connect(lambda: (self.clear_preset_indicator(), self.update_preview()))
        self.w.valueChanged.connect(lambda: (self.clear_preset_indicator(), self.update_preview()))
        self.h.valueChanged.connect(lambda: (self.clear_preset_indicator(), self.update_preview()))
        self.bold_btn.clicked.connect(lambda: (self.clear_preset_indicator(), self.update_preview()))
        self.italic_btn.clicked.connect(lambda: (self.clear_preset_indicator(), self.update_preview()))

        QTimer.singleShot(100, lambda: (self.update_preview(), self.update_buttons()))

    def clear_preset_indicator(self):
        """Clears the active preset name when a manual style change occurs"""
        if self._is_applying_preset: return
        if self.current_preset_name:
            self.current_preset_name = None
            self.update_presets_menu()

    def set_color(self, color_name: str):
        self.clear_preset_indicator()
        self.current_color = color_name
        for name, btn in self.color_buttons.items():
            is_active = (name == color_name)
            btn.setChecked(is_active)
            if name in self.color_indicators:
                self.color_indicators[name].setVisible(is_active)
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
                font-weight:{'bold' if self.bold_btn.isChecked() else 'normal'};
                font-style:{'italic' if self.italic_btn.isChecked() else 'normal'};
                line-height:1.33;
            }}
            .sticky-content-empty {{ padding:10px 0; margin:8px 0; color:#aaaaaa;}}
            code {{ background:rgba(0,0,0,0.1); padding:2px 4px; border-radius:3px; font-family:monospace; }}
            pre {{ background:rgba(0,0,0,0.1); padding:10px; border-radius:5px; overflow-x:auto; }}
            blockquote {{ 
                border-left: 4px solid rgba(0, 0, 0, 0.2);
                margin: 8px 0;
                padding-left: 12px;
                color: rgba(0, 0, 0, 0.6);
                font-style: italic;
            }}
            table {{ border-collapse: collapse; width: 100%; margin: 12px 0; border-radius: 4px; overflow: hidden; }}
            th, td {{ border: 1px solid rgba(0, 0, 0, 0.1); padding: 8px 12px; text-align: left; }}
            th {{ background-color: rgba(0, 0, 0, 0.05); font-weight: 600; }}
            pre {{ background: rgba(0, 0, 0, 0.05); padding: 12px; border-radius: 8px; overflow-x: auto; margin: 12px 0; }}
            code {{ background: rgba(0, 0, 0, 0.05); padding: 2px 4px; border-radius: 4px; font-family: monospace; }}
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
            "height": self.h.value(),
            "bold": self.bold_btn.isChecked(),
            "italic": self.italic_btn.isChecked(),
            "preset": self.current_preset_name
        }
        if self.idx is not None:
            self.data[self.idx] = new_sticky
            self.sticky = new_sticky # Update state for next save's image cleanup
            save_stickies(self.note_id, self.data)
            mw.reviewer._redraw_current_card()
            tooltip("Sticky note updated!")
            self.close() # Close dialog after updating
        else:
            self.data.append(new_sticky)
            save_stickies(self.note_id, self.data)
            mw.reviewer._redraw_current_card()
            tooltip("Sticky note added!")
            self.editor.clear() # Clear for bulk creation

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

    def save_as_default(self):
        settings = {
            "color": self.current_color,
            "font_size": self.fs.value(),
            "font_family": self.ff.currentText(),
            "width": self.w.value(),
            "height": self.h.value(),
            "bold": self.bold_btn.isChecked(),
            "italic": self.italic_btn.isChecked()
        }
        save_default_settings(settings)
        tooltip("✓ Settings saved as default for new notes!")

    def create_menu_bar(self):
        menubar = QMenuBar(self)
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export as Image...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_as_image)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save Note", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)
        
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

        # Presets Menu
        self.presets_menu = menubar.addMenu("Presets")
        self.update_presets_menu()

        # Insert Menu
        insert_menu = menubar.addMenu("Insert")
        
        timestamp_action = QAction("Timestamp", self)
        timestamp_action.setShortcut("Ctrl+T")
        timestamp_action.triggered.connect(self.insert_timestamp)
        insert_menu.addAction(timestamp_action)
        
        insert_menu.addSeparator()
        
        self.templates_menu = insert_menu.addMenu("Templates")
        self.update_templates_menu()

        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        return menubar

    def update_presets_menu(self):
        self.presets_menu.clear()
        
        # 1. Global Default Management Section
        defaults = get_default_settings()
        default_name = defaults.get("preset") or "Wide"
        
        default_sub_menu = self.presets_menu.addMenu(f"Default Preset: {default_name}")
        presets = get_presets()
        for name in presets:
            act = QAction(name, self)
            act.triggered.connect(lambda checked, n=name: self.set_global_default(n))
            default_sub_menu.addAction(act)
            
        self.presets_menu.addSeparator()

        save_preset_action = QAction("Save/Update Preset...", self)
        save_preset_action.triggered.connect(self.save_current_as_preset)
        self.presets_menu.addAction(save_preset_action)
        
        manage_presets_action = QAction("Manage Presets...", self)
        manage_presets_action.triggered.connect(self.manage_presets)
        self.presets_menu.addAction(manage_presets_action)
        
        self.presets_menu.addSeparator()
        
        header = QAction("APPLY PRESET TO THIS NOTE", self)
        header.setEnabled(False)
        self.presets_menu.addAction(header)
        
        for name in presets:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, n=name: self.apply_preset(n))
            self.presets_menu.addAction(action)

    def apply_preset(self, name):
        presets = get_presets()
        if name not in presets: return
        p = presets[name]
        
        self._is_applying_preset = True
        try:
            self.current_preset_name = name
            self.set_color(p.get("color", "yellow"))
            self.fs.setValue(p.get("font_size", 16))
            self.ff.setCurrentText(p.get("font_family", "Comic Sans MS"))
            self.w.setValue(p.get("width", 300))
            self.h.setValue(p.get("height", 150))
            self.bold_btn.setChecked(p.get("bold", False))
            self.italic_btn.setChecked(p.get("italic", False))
        finally:
            self._is_applying_preset = False
        
        self.update_preview()
        self.update_presets_menu()
        tooltip(f"Preset applied: {name}")

    def set_global_default(self, name):
        presets = get_presets()
        if name not in presets: return
        p = presets[name].copy()
        p["preset_name"] = name
        save_default_settings(p)
        self.apply_preset(name)  # Apply it to the current note as well
        self.update_presets_menu()
        tooltip(f"✓ New Global Default: {name}")

    def save_current_as_preset(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Save Preset")
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Select an existing preset to overwrite or type a new name:"))
        
        from aqt.qt import QComboBox
        combo = QComboBox()
        combo.setEditable(True)
        presets = get_presets()
        combo.addItems(presets.keys())
        if self.current_preset_name:
            combo.setCurrentText(self.current_preset_name)
        layout.addWidget(combo)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        def do_save():
            name = combo.currentText().strip()
            if not name: return
            presets[name] = {
                "color": self.current_color,
                "font_size": self.fs.value(),
                "font_family": self.ff.currentText(),
                "width": self.w.value(),
                "height": self.h.value(),
                "bold": self.bold_btn.isChecked(),
                "italic": self.italic_btn.isChecked()
            }
            save_presets(presets)
            self.current_preset_name = name
            self.update_presets_menu()
            dialog.accept()
            tooltip(f"Preset '{name}' saved!")
            
        save_btn.clicked.connect(do_save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        dialog.exec()

    def manage_presets(self):
        presets = get_presets()
        if not presets:
            tooltip("No presets to manage.")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Presets")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout(dialog)
        
        from aqt import QListWidget
        list_widget = QListWidget()
        list_widget.addItems(presets.keys())
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        
        rename_btn = QPushButton("Rename")
        def rename_selected():
            item = list_widget.currentItem()
            if not item: return
            old_name = item.text()
            from aqt.utils import getOnlyText
            new_name = getOnlyText(f"Rename '{old_name}' to:", default=old_name)
            if new_name and new_name != old_name:
                presets[new_name] = presets.pop(old_name)
                save_presets(presets)
                item.setText(new_name)
                if self.current_preset_name == old_name:
                    self.current_preset_name = new_name
                self.update_presets_menu()
                tooltip(f"Renamed to: {new_name}")
        
        delete_btn = QPushButton("Delete")
        def delete_selected():
            item = list_widget.currentItem()
            if item:
                name = item.text()
                if name in presets:
                    del presets[name]
                    save_presets(presets)
                    list_widget.takeItem(list_widget.row(item))
                    if self.current_preset_name == name:
                        self.current_preset_name = None
                    self.update_presets_menu()
                    tooltip(f"Deleted preset: {name}")
        
        rename_btn.clicked.connect(rename_selected)
        delete_btn.clicked.connect(delete_selected)
        btn_layout.addWidget(rename_btn)
        btn_layout.addWidget(delete_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec()

    def export_as_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Sticky Note as Image", "sticky_note.png", "PNG (*.png)")
        if not path: return
        
        def on_grab(pixmap):
            pixmap.save(path, "PNG")
            tooltip("✓ Exported as image!")
            
        self.preview.grab().save(path, "PNG") # Simple grab for now

    def insert_timestamp(self):
        from datetime import datetime
        now = datetime.now().strftime("%I:%M %p")
        self.editor.insertPlainText(now)
        tooltip(f"Inserted: {now}")

    def update_templates_menu(self):
        self.templates_menu.clear()
        
        save_tmpl_action = QAction("Save Selection as Template...", self)
        save_tmpl_action.triggered.connect(self.save_selection_as_template)
        self.templates_menu.addAction(save_tmpl_action)
        
        manage_tmpl_action = QAction("Manage Templates...", self)
        manage_tmpl_action.triggered.connect(self.manage_templates)
        self.templates_menu.addAction(manage_tmpl_action)
        
        self.templates_menu.addSeparator()
        
        header = QAction("AVAILABLE TEMPLATES", self)
        header.setEnabled(False)
        self.templates_menu.addAction(header)
        
        templates = get_templates()
        for name in templates:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, n=name: self.insert_template(n))
            self.templates_menu.addAction(action)

    def insert_template(self, name):
        templates = get_templates()
        content = templates.get(name, "")
        if content:
            self.editor.insertPlainText(content)
            tooltip(f"Inserted: {name}")

    def save_selection_as_template(self):
        cursor = self.editor.textCursor()
        content = cursor.selectedText()
        if not content:
            tooltip("Please select some text first!")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Save Content Template")
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Select an existing template to overwrite or type a new name:"))
        
        from aqt.qt import QComboBox
        combo = QComboBox()
        combo.setEditable(True)
        templates = get_templates()
        combo.addItems(templates.keys())
        layout.addWidget(combo)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        def do_save():
            name = combo.currentText().strip()
            if not name: return
            templates[name] = content
            save_templates(templates)
            self.update_templates_menu()
            dialog.accept()
            tooltip(f"Template '{name}' saved!")
            
        save_btn.clicked.connect(do_save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        dialog.exec()

    def manage_templates(self):
        templates = get_templates()
        if not templates:
            tooltip("No templates to manage.")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Content Templates")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout(dialog)
        
        from aqt import QListWidget
        list_widget = QListWidget()
        list_widget.addItems(templates.keys())
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        
        rename_btn = QPushButton("Rename")
        def rename_selected():
            item = list_widget.currentItem()
            if not item: return
            old_name = item.text()
            from aqt.utils import getOnlyText
            new_name = getOnlyText(f"Rename template '{old_name}' to:", default=old_name)
            if new_name and new_name != old_name:
                templates[new_name] = templates.pop(old_name)
                save_templates(templates)
                item.setText(new_name)
                self.update_templates_menu()
                tooltip(f"Renamed to: {new_name}")
        
        delete_btn = QPushButton("Delete")
        def delete_selected():
            item = list_widget.currentItem()
            if item:
                name = item.text()
                if name in templates:
                    del templates[name]
                    save_templates(templates)
                    list_widget.takeItem(list_widget.row(item))
                    self.update_templates_menu()
                    tooltip(f"Deleted template: {name}")
        
        rename_btn.clicked.connect(rename_selected)
        delete_btn.clicked.connect(delete_selected)
        btn_layout.addWidget(rename_btn)
        btn_layout.addWidget(delete_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec()

    def show_shortcuts(self):
        shortcuts_text = """
        <div style="min-width: 450px;">
        <h3 style="color: #007BFF; border-bottom: 1px solid #ddd; padding-bottom: 5px;">Sticky Note Master Cheat Sheet</h3>
        
        <p style="font-weight: bold; color: #555; margin-top: 15px; margin-bottom: 5px;">✍️ CORE EDITING</p>
        <table border="0" cellpadding="4" style="width: 100%;">
          <tr><td><b>Ctrl+B</b></td><td>Bold</td><td style="color: #888; font-size: 11px;">Emphasis</td></tr>
          <tr><td><b>Ctrl+I</b></td><td>Italic</td><td style="color: #888; font-size: 11px;">Emphasis</td></tr>
          <tr><td><b>Ctrl+Shift+X</b></td><td>Strikethrough</td><td style="color: #888; font-size: 11px;">Deletions</td></tr>
          <tr><td><b>Alt+1/2/3</b></td><td>H1, H2, H3</td><td style="color: #888; font-size: 11px;">Headings</td></tr>
          <tr><td><b>Ctrl+Shift+L</b></td><td>Bullet List</td><td style="color: #888; font-size: 11px;">Bullet points</td></tr>
        </table>

        <p style="font-weight: bold; color: #555; margin-top: 15px; margin-bottom: 5px;">🛠️ TOOLS & INSERT</p>
        <table border="0" cellpadding="4" style="width: 100%;">
          <tr><td><b>Ctrl+T</b></td><td><b>Insert Timestamp</b></td><td style="color: #888; font-size: 11px;">Time logs</td></tr>
          <tr><td><b>Ctrl+Shift+I</b></td><td>Insert Image</td><td style="color: #888; font-size: 11px;">Local images</td></tr>
          <tr><td><b>Ctrl+Shift+G</b></td><td>Insert GIF</td><td style="color: #888; font-size: 11px;">Tenor lookup</td></tr>
          <tr><td><b>Ctrl+K</b></td><td>Link</td><td style="color: #888; font-size: 11px;">Web URLs</td></tr>
          <tr><td><b>Ctrl+`</b></td><td>Code</td><td style="color: #888; font-size: 11px;">Code snippets</td></tr>
        </table>

        <p style="font-weight: bold; color: #555; margin-top: 15px; margin-bottom: 5px;">💾 FILE & APPLICATION</p>
        <table border="0" cellpadding="4" style="width: 100%;">
          <tr><td><b>Ctrl+S</b></td><td><b>Save Note</b></td><td style="color: #888; font-size: 11px;">Commit changes</td></tr>
          <tr><td><b>Ctrl+E</b></td><td><b>Export Image</b></td><td style="color: #888; font-size: 11px;">Save as PNG</td></tr>
          <tr><td><b>Ctrl+Shift+S</b></td><td>Open Editor</td><td style="color: #888; font-size: 11px;">Quick access</td></tr>
          <tr><td><b>F1</b></td><td>Help</td><td style="color: #888; font-size: 11px;">Show guide</td></tr>
        </table>

        <p style="font-weight: bold; color: #555; margin-top: 15px; margin-bottom: 5px;">🎨 STYLE & OTHERS</p>
        <table border="0" cellpadding="4" style="width: 100%;">
          <tr><td><b>Ctrl+Shift+Q</b></td><td>Blockquote</td><td style="color: #888; font-size: 11px;">Quotes</td></tr>
          <tr><td><b>Ctrl+Shift+H</b></td><td>Horizontal Rule</td><td style="color: #888; font-size: 11px;">Divider line</td></tr>
        </table>
        </div>
        """
        showText(shortcuts_text, parent=self, type=1)

def extract_image_filenames(text):
    """Extract all image filenames from markdown text"""
    return set(re.findall(r'!\[.*?\]\((.*?)\)', text))