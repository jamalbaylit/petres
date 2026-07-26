"""
Export a Python source file to a PDF with:
  - Manual, theme-independent syntax colors
  - Correct class/function coloring everywhere they're used (via jedi)
  - Distinct color for import module paths (e.g. petres.grids.cornerpoint)
  - Inline line numbers with adjustable gutter spacing
  - Real, selectable text in the final PDF (renders via headless Chrome)

Dependencies:
    pip install pygments jedi playwright --break-system-packages
    playwright install chromium
"""

import io
import jedi
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.style import Style
from pygments.token import Comment, String, Keyword, Name, Number, Text
from playwright.sync_api import sync_playwright

# ============================================================
# CONFIG — edit these
# ============================================================
SOURCE_FILE = "examples\\grid\\from_rectilinear.py"
OUTPUT_PDF = "code_output.pdf"
FONT_FAMILY = "'Gabarito Regular', Consolas, monospace"
FONT_SIZE = "21pt"
LINE_HEIGHT = "28pt"
NUMBER_CODE_GAP = "30px"   # <-- distance between line numbers and code

COLORS = {
    "comments":  "#4f4f4f",
    "strings":   "#6A3282",
    "keywords":  "#CB04A5",
    "types":     "#0000FF",   # classes
    "functions": "#519E00",
    "variables": "#1b1b1b",
    "numbers":   "#08605F",
    "imports":   "#000066",   # module paths after `from` / `import`
    "background": "#ededed",
    "foreground": "#1b1b1b",
}

# ============================================================
# Load source
# ============================================================
with open(SOURCE_FILE, encoding="utf-8") as f:
    code = f.read()

# ============================================================
# Semantic resolution via jedi (class vs function vs other)
# ============================================================
lines = code.splitlines(keepends=True)
line_start_offsets = [0]
for line in lines:
    line_start_offsets.append(line_start_offsets[-1] + len(line))

def offset_to_line_col(offset):
    for i in range(len(line_start_offsets) - 1):
        if line_start_offsets[i] <= offset < line_start_offsets[i + 1]:
            return i + 1, offset - line_start_offsets[i]
    return len(lines), offset - line_start_offsets[-2]

script = jedi.Script(code=code)
infer_cache = {}

def resolve_type(line, col):
    key = (line, col)
    if key in infer_cache:
        return infer_cache[key]
    try:
        defs = script.infer(line=line, column=col)
        result = defs[0].type if defs else None
    except Exception:
        result = None
    infer_cache[key] = result
    return result

# ============================================================
# Pygments style — manual colors
# ============================================================
class ManualStyle(Style):
    background_color = COLORS["background"]
    styles = {
        Text:            COLORS["foreground"],
        Comment:         f"italic {COLORS['comments']}",
        String:          COLORS["strings"],
        Keyword:         f"{COLORS['keywords']}",
        Name.Class:      COLORS["types"],
        Name.Builtin:    COLORS["types"],
        Name.Function:   COLORS["functions"],
        Name.Namespace:  COLORS["imports"],   # e.g. petres.grids.cornerpoint
        Number:          COLORS["numbers"],
        Name:            COLORS["variables"],
    }

# ============================================================
# Custom lexer: re-tag Name tokens using jedi's resolved type
# ============================================================
class SemanticPythonLexer(PythonLexer):
    def get_tokens_unprocessed(self, text):
        for index, token, value in super().get_tokens_unprocessed(text):
            # Re-tag identifiers (including builtins) based on jedi inference.
            if value.isidentifier() and token in (Name, Name.Builtin):
                line, col = offset_to_line_col(index)
                kind = resolve_type(line, col)
                if kind == "class":
                    token = Name.Class
                elif kind in ("function", "builtin"):
                    token = Name.Function
            yield index, token, value

# ============================================================
# Highlight -> HTML (in-memory string)
# ============================================================
formatter = HtmlFormatter(
    style=ManualStyle,
    linenos="inline",
    full=True,
    cssclass="codebox",
)
html_str = highlight(code, SemanticPythonLexer(), formatter)

custom_css = f"""
<style>
    body {{ background: {COLORS['background']}; margin: 0; padding: 20px; }}
    .codebox pre {{
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE};
        line-height: {LINE_HEIGHT};
    }}
    .codebox .linenos {{
        color: {COLORS['comments']};
        padding-right: {NUMBER_CODE_GAP};
        display: inline-block;
        min-width: 3em;
        text-align: right;
        user-select: none;
    }}
</style>
</head>
"""
html_str = html_str.replace("</head>", custom_css)

# ============================================================
# Render to PDF (real selectable text, not raster) via headless Chrome
# ============================================================
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_content(html_str, wait_until="networkidle")
    pdf_bytes = page.pdf(print_background=True)
    browser.close()

pdf_buffer = io.BytesIO(pdf_bytes)

with open(OUTPUT_PDF, "wb") as f:
    f.write(pdf_buffer.getvalue())

print(f"Done -> {OUTPUT_PDF}")