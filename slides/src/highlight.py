"""Semantic Python syntax highlighting -> HTML, used by CodeSnippet.

Tokens are tagged with semantic CSS classes only (``tok-keyword``,
``tok-function``, ...) -- no inline colors. The actual palette lives in
assets/static/code-snippet.css so it can be restyled without touching this
module.

Class/function names are resolved via jedi (so a class is colored correctly
everywhere it's *used*, not just where it's defined); parameter names and
call-site keyword-argument names are found via the ``ast`` module.
"""

from __future__ import annotations

import ast
import html
import textwrap

import jedi
from pygments.lexers import PythonLexer
from pygments.token import Comment, Keyword, Name, Number, String


def _collect_param_positions(code: str) -> set[tuple[int, int]]:
    positions: set[tuple[int, int]] = set()
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return positions

    def add(node: ast.AST) -> None:
        positions.add((node.lineno, node.col_offset))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            args = node.args
            for arg in getattr(args, "posonlyargs", []) + args.args + args.kwonlyargs:
                add(arg)
            if args.vararg:
                add(args.vararg)
            if args.kwarg:
                add(args.kwarg)
        elif isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg is not None:
                    positions.add((kw.lineno, kw.col_offset))

    return positions


def _line_offsets(code: str) -> list[int]:
    offsets = [0]
    for line in code.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _offset_to_line_col(offsets: list[int], offset: int) -> tuple[int, int]:
    for i in range(len(offsets) - 1):
        if offsets[i] <= offset < offsets[i + 1]:
            return i + 1, offset - offsets[i]
    return len(offsets) - 1, offset - offsets[-2]


def render_code_html(code: str) -> str:
    """Render Python source to an HTML ``<pre>`` block with inline line numbers."""
    # A code= argument written as an indented triple-quoted string literal
    # (natural Python style) carries that indentation as literal content,
    # which is invalid syntax at module level -- ast.parse() then silently
    # fails (no parameter coloring) and jedi's error-recovery parsing can
    # misclassify tokens. Normalize it away instead of relying on every
    # caller to remember textwrap.dedent() themselves.
    code = textwrap.dedent(code).strip("\n")
    param_positions = _collect_param_positions(code)
    offsets = _line_offsets(code)

    try:
        script = jedi.Script(code=code)
    except Exception:
        script = None
    infer_cache: dict[tuple[int, int], str | None] = {}

    def resolve_type(line: int, col: int) -> str | None:
        if script is None:
            return None
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

    # Pygments tags definition-site names more specifically than plain Name
    # (e.g. `class Grid:` -> Name.Class, `def __init__` -> Name.Function.Magic)
    # -- `token in Name` alone would also swallow Name.Namespace (imports,
    # handled separately below), so list the exact subtypes instead.
    _resolvable = (Name, Name.Builtin, Name.Class, Name.Function, Name.Function.Magic)

    def classify(token, value: str, line: int, col: int) -> str | None:
        if value.isidentifier() and token in _resolvable:
            if (line, col) in param_positions:
                return "param"
            kind = resolve_type(line, col)
            if kind == "class":
                return "class"
            if kind in ("function", "builtin"):
                return "function"
            return None
        if token in Comment:
            return "comment"
        if token in String:
            return "string"
        if token in Keyword:
            return "keyword"
        if token in Name.Namespace:
            return "import"
        if token in Number:
            return "number"
        return None

    lines: list[list[str]] = [[]]
    offset = 0
    for token, value in PythonLexer().get_tokens(code):
        remaining = value
        while remaining:
            nl_index = remaining.find("\n")
            segment = remaining if nl_index == -1 else remaining[:nl_index]
            remaining = "" if nl_index == -1 else remaining[nl_index + 1 :]
            if segment:
                line, col = _offset_to_line_col(offsets, offset)
                css_class = classify(token, segment, line, col)
                escaped = html.escape(segment)
                lines[-1].append(f'<span class="tok-{css_class}">{escaped}</span>' if css_class else escaped)
                offset += len(segment)
            if nl_index != -1:
                lines.append([])
                offset += 1

    if lines and not lines[-1]:
        lines.pop()

    rows = "".join(
        f'<div class="code-line"><span class="lineno">{i}</span>'
        f'<span class="code-text">{"".join(parts) or " "}</span></div>'
        for i, parts in enumerate(lines, start=1)
    )
    return f'<pre class="code-block">{rows}</pre>'
