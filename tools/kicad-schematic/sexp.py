"""Minimal KiCad s-expression reader that keeps source spans of top-level items."""
import re
TOK = re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()"]+))')

def parse(text, pos=0):
    """Parse one list starting at text[pos]=='('. Returns (node, end). node = list of str|list."""
    stack = []; cur = None
    i = pos
    while True:
        m = TOK.match(text, i)
        if not m: raise ValueError(f"bad token at {i}")
        i = m.end()
        if m.group(1):
            new = []
            if cur is not None: cur.append(new); stack.append(cur)
            cur = new
        elif m.group(2):
            if not stack: return cur, i
            cur = stack.pop()
        elif m.group(3) is not None: cur.append(('S', m.group(3)[1:-1]))
        else: cur.append(m.group(4))

def top_items(text):
    """Yield (start, end, node) for each child of the root list."""
    root_start = text.index('(')
    i = root_start + 1
    # skip root head token
    m = TOK.match(text, i); i = m.end()
    out = []
    while True:
        m = TOK.match(text, i)
        if m.group(2): break
        if m.group(1):
            start = m.start(1)
            node, end = parse(text, start)
            out.append((start, end, node)); i = end
        else: i = m.end()
    return out

def val(x): return x[1] if isinstance(x, tuple) else x
def find(node, key): return [c for c in node if isinstance(c, list) and c and c[0] == key]
def first(node, key):
    r = find(node, key); return r[0] if r else None
