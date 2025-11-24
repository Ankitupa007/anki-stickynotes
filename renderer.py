# renderer.py
from aqt import mw
from .storage import get_stickies
from . import markdown2
import html, re
from pathlib import Path

def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    # Use markdown2 with extras for better compatibility
    return markdown2.markdown(text, extras=["fenced-code-blocks", "tables", "break-on-newline", "cuddled-lists", "strike"]).strip()


def render_stickies_for_card(card):
    stickies = get_stickies(card.note().id)
    if not stickies:
        return ""

    addon_package = mw.addonManager.addonFromModule(__name__)

    html = f'''
    <link rel="stylesheet" href="/_addons/{addon_package}/web/sticky.css">
    <script src="/_addons/{addon_package}/web/packery.min.js"></script>
    <script type="text/javascript">
    (function() {{
        document.addEventListener("DOMContentLoaded", function() {{
            var grid = document.querySelector("#anki-sticky-container");
            if (grid) {{
                new Packery(grid, {{
                    itemSelector: ".anki-sticky",
                    gutter: 8
                }});
            }}
        }});
        
        window.edit = function(i) {{
            pycmd("stickyEdit:" + i);
        }};
        
        window.del = function(i) {{
            if (confirm("Delete this sticky note?")) {{
                pycmd("stickyDelete:" + i);
            }}
        }};
    }})();
    </script>
    <div id="anki-sticky-container" data-packery='{{"itemSelector": ".anki-sticky", "gutter": 8}}'>
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