# renderer.py
from .storage import get_stickies
import html, re

def markdown_to_html(text: str) -> str:
    if not text:
        return ""

    text = html.escape(text).strip()

    # === Headers ===
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.M)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.M)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.M)

    # === Bold / Italic / Bold-Italic ===
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'___(.*?)___', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)

    # === Strikethrough ===
    text = re.sub(r'~~(.*?)~~', r'<del>\1</del>', text)

    # === Inline Code ===
    text = re.sub(r'`([^`]+)`', r'<code style="background:#171717;color:#fff;padding:2px 6px;border-radius:4px;font-family:monospace;">\1</code>', text)

    # === Links ===
    text = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#1976d2;text-decoration:underline;" target="_blank">\1</a>', text)

    # === Horizontal Rule ===
    text = re.sub(r'^---\s*$', r'<hr style="border:0;border-top:1px solid #171717;margin:10px 0;">', text, flags=re.M)

    # === Lists (unordered) ===
    lines = text.split('\n')
    in_list = False
    result = []

    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped.startswith(('- ', '* ', '• ')):
            item = stripped[2:].strip()
            if not in_list:
                result.append('<ul style="margin:8px 0;padding-left:20px;">')
                in_list = True
            result.append(f'<li>{item}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    
    if in_list:
        result.append('</ul>')

    text = '\n'.join(result)

    # === Final line breaks (but preserve list spacing) ===
    text = re.sub(r'(?<!>)\n(?!\s*(</ul>|</?li>))', '<br>', text)

    return text


def render_stickies_for_card(card):
    stickies = get_stickies(card.note().id)
    if not stickies:
        return ""

    html = '''
    <link rel="stylesheet" href="_sticky.css">
    <script src="_packery.min.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", () => {
        const grid = document.querySelector("#anki-sticky-container");
        if (grid) new Packery(grid, {itemSelector: ".anki-sticky", gutter: 8});
    });
    function edit(i){pycmd("stickyEdit:"+i)}
    function del(i){confirm("Delete?") && pycmd("stickyDelete:"+i)}
    </script>

    <div class="container-header">
        <h2 class="container-title" style="">Sticky Notes</h2>
    </div>
    <div id="anki-sticky-container" data-packery='{ "itemSelector": ".anki-sticky", "gutter": 8 }'>
    '''

    colors = {"yellow":"anki-yellow","green":"anki-green","blue":"anki-blue","pink":"anki-pink","purple":"anki-purple","orange":"anki-orange"}

    for i, s in enumerate(stickies):
        color = colors.get(s.get("color","yellow"),"anki-yellow")
        w = s.get("width",300)
        h = s.get("height",150)
        fs = s.get("font_size",16)
        ff = s.get("font_family","Verdana")
        content = markdown_to_html(s.get("data",""))

        html += f'''
        <div class="anki-sticky {color}" style="width:{w}px;min-height:{h}px;">
            <div class="sticky-content" style="font-size:{fs}px;font-family:'{ff}'">
                {content}
            </div>
            <div class="sticky-controls">
                <button class="sticky-btn" onclick="edit({i})">Edit</button>
                <button class="sticky-btn" onclick="del({i})">Delete</button>
            </div>
        </div>
        '''

    return html + "</div>"