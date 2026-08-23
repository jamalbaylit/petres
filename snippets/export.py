"""
Export a Python source file to an SVG with:
  - Manual, theme-independent syntax colors
  - Correct class/function coloring everywhere they're used (via jedi)
  - Distinct color for import module paths (e.g. petres.grids.cornerpoint)
  - Distinct color for function/class PARAMETER names (def f(a=1, b=3))
    and keyword-argument names at call sites (f(a=1, b=3))
  - Inline line numbers with adjustable gutter spacing
  - Real, selectable vector text (native SVG <text>/<tspan>, no rasterization)
  - Transparent background (text only)

Dependencies:
    pip install pygments jedi --break-system-packages
"""

import ast
import html
import jedi
from pygments.lexers import PythonLexer
from pygments.token import Comment, String, Keyword, Name, Number

# ============================================================
# CONFIG — edit these
# ============================================================
SOURCE_FILE = "layering.py"
OUTPUT_SVG = "code_output.svg"
FONT_FAMILY = "'Gabarito Regular', Consolas, monospace"
FONT_SIZE = 33               # pt

# All spacing below is defined relative to FONT_SIZE (in "em" units, i.e.
# multiples of FONT_SIZE) so the layout keeps its proportions automatically
# when FONT_SIZE changes -- no need to retune gaps by hand.
LINE_HEIGHT_EM = 1.4        # em, line-to-line spacing
LEFT_MARGIN_EM = 0           # em, left edge of the line-number column
NUMBER_CODE_GAP_EM = 0.95    # em, distance between line numbers and code
RIGHT_PADDING_EM = 0         # em, extra canvas width beyond the longest line
CHAR_WIDTH_FACTOR = 0.6      # em, monospace advance width; only used to size the canvas
LINENO_CHARS = 3             # digits reserved for the line-number column

LINE_HEIGHT = LINE_HEIGHT_EM * FONT_SIZE               # pt
LEFT_MARGIN = LEFT_MARGIN_EM * FONT_SIZE               # pt
NUMBER_CODE_GAP = NUMBER_CODE_GAP_EM * FONT_SIZE       # pt
RIGHT_PADDING = RIGHT_PADDING_EM * FONT_SIZE           # pt
CHAR_WIDTH_ESTIMATE = FONT_SIZE * CHAR_WIDTH_FACTOR    # pt
LINENO_WIDTH = LINENO_CHARS * CHAR_WIDTH_ESTIMATE      # pt

COLORS = {
    "comments":  "#4f4f4f",
    "strings":   "#6A3282",
    "keywords":  "#CB04A5",
    "types":     "#0000FF",   # classes
    "functions": "#519E00",
    "variables": "#1b1b1b",
    "numbers":   "#08605F",
    "imports":   "#000066",   # module paths after `from` / `import`
    "params":    "#9C4807",   # function/class parameter & kwarg names
    "foreground": "#1b1b1b",
    "linenos":   "#4f4f4f",
}

# ============================================================
# Load source
# ============================================================
with open(SOURCE_FILE, encoding="utf-8") as f:
    code = f.read()

# ============================================================
# Semantic resolution via jedi (class vs function vs other)
# ============================================================
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
# Positions of function/class PARAMETER names and call-site
# KEYWORD ARGUMENT names, via the `ast` module (line, 0-based col)
# ============================================================
def collect_param_positions(source):
    positions = set()
    tree = ast.parse(source)

    def add(node):
        positions.add((node.lineno, node.col_offset))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            a = node.args
            for arg in (getattr(a, "posonlyargs", []) + a.args + a.kwonlyargs):
                add(arg)
            if a.vararg:
                add(a.vararg)
            if a.kwarg:
                add(a.kwarg)
        elif isinstance(node, ast.Call):
            for kw in node.keywords:
                # kw.arg is None for **kwargs unpacking -> skip
                if kw.arg is not None:
                    positions.add((kw.lineno, kw.col_offset))

    return positions

PARAM_POSITIONS = collect_param_positions(code)

# ============================================================
# Color a single token, resolving Name/Name.Builtin via the
# ast-derived parameter positions and jedi
# ============================================================
def token_style(token, value, line, col):
    if value.isidentifier() and token in (Name, Name.Builtin):
        # 1) Parameter name in a def/lambda, or kwarg name at a call
        if (line, col) in PARAM_POSITIONS:
            return COLORS["params"], False
        # 2) Otherwise fall back to jedi-based class/function detection
        kind = resolve_type(line, col)
        if kind == "class":
            return COLORS["types"], False
        if kind in ("function", "builtin"):
            return COLORS["functions"], False
    if token in Comment:
        return COLORS["comments"], True
    if token in String:
        return COLORS["strings"], False
    if token in Keyword:
        return COLORS["keywords"], False
    if token in Name.Namespace:
        return COLORS["imports"], False
    if token in Number:
        return COLORS["numbers"], False
    return COLORS["foreground"], False

# ============================================================
# Tokenize and group into per-line runs of (text, color, italic)
# ============================================================
line_runs = [[]]
current_line, current_col = 1, 0

for token, value in PythonLexer().get_tokens(code):
    remaining = value
    while remaining:
        nl_index = remaining.find("\n")
        segment = remaining if nl_index == -1 else remaining[:nl_index]
        remaining = "" if nl_index == -1 else remaining[nl_index + 1:]
        if segment:
            color, italic = token_style(token, segment, current_line, current_col)
            line_runs[-1].append((segment, color, italic))
            current_col += len(segment)
        if nl_index != -1:
            line_runs.append([])
            current_line += 1
            current_col = 0

if line_runs and not line_runs[-1]:
    line_runs.pop()

# ============================================================
# Build SVG
# ============================================================
code_x = LEFT_MARGIN + LINENO_WIDTH + NUMBER_CODE_GAP
max_chars = max((sum(len(seg) for seg, _, _ in run) for run in line_runs), default=0)
svg_width = code_x + max_chars * CHAR_WIDTH_ESTIMATE + RIGHT_PADDING
svg_height = len(line_runs) * LINE_HEIGHT + LINE_HEIGHT * 0.5

body_lines = []
for i, run in enumerate(line_runs):
    y = (i + 1) * LINE_HEIGHT
    lineno_x = LEFT_MARGIN + LINENO_WIDTH
    body_lines.append(
        f'<text x="{lineno_x:.1f}" y="{y:.1f}" text-anchor="end" '
        f'fill="{COLORS["linenos"]}">{i + 1}</text>'
    )
    tspans = "".join(
        f'<tspan fill="{color}"{" font-style=\"italic\"" if italic else ""}>'
        f'{html.escape(text)}</tspan>'
        for text, color, italic in run
    )
    body_lines.append(f'<text x="{code_x:.1f}" y="{y:.1f}">{tspans}</text>')

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width:.1f}" height="{svg_height:.1f}"
     viewBox="0 0 {svg_width:.1f} {svg_height:.1f}" xml:space="preserve">
<style>
    text {{ font-family: {FONT_FAMILY}; font-size: {FONT_SIZE}pt; }}
</style>
{chr(10).join(body_lines)}
</svg>
'''

with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"Done -> {OUTPUT_SVG}")
