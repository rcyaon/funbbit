"""Regroup an auto-placed Diode/KiCad schematic into titled blocks, one per Zener module.

Each symbol with its wire stubs, net labels, no-connect flags and power flags
forms an island. Islands move rigidly (translation only, on a 1.27 mm grid),
so pin-to-wire-to-label connectivity is unchanged.
usage: regroup.py in.kicad_sch out.kicad_sch [zener_root]
With zener_root, parts inside a block follow declaration order in modules/*.zen (signal flow).
"""
import re, sys, uuid, collections
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from sexp import top_items, find, first, val

G = 1.27
src, dst = sys.argv[1], sys.argv[2]
ZEN = sys.argv[3] if len(sys.argv) > 3 else None
text = open(src).read()
items = top_items(text)

# ---- library pin positions -------------------------------------------------
lib = {}
libnode = next(n for _, _, n in items if n[0] == 'lib_symbols')
for sym in find(libnode, 'symbol'):
    name = val(sym[1]); pins = []; pts = []
    def walk(n):
        for c in n:
            if isinstance(c, list) and c:
                if c[0] == 'pin':
                    a = first(c, 'at'); pins.append((float(a[1]), float(a[2])))
                    L = float(first(c, 'length')[1]); ang = float(a[3]) if len(a) > 3 else 0
                    import math
                    pts.append((float(a[1]) + L * math.cos(math.radians(ang)), float(a[2]) + L * math.sin(math.radians(ang))))
                elif c[0] in ('xy', 'start', 'end', 'center'):
                    pts.append((float(c[1]), float(c[2])))
                walk(c)
    walk(sym)
    lib[name] = (pins, pins + pts)

def place(sx, sy, rot, p):
    px, py = p
    if rot == 0: return (round(sx + px, 3), round(sy - py, 3))
    if rot == 180: return (round(sx - px, 3), round(sy + py, 3))
    raise SystemExit(f"unsupported rotation {rot}")

# ---- nodes ------------------------------------------------------------------
objs = []  # dict(kind, idx, pts(connection points), bbox_pts, module)
for idx, (s, e, n) in enumerate(items):
    k = n[0]
    if k == 'symbol':
        at = first(n, 'at'); sx, sy, rot = float(at[1]), float(at[2]), float(at[3])
        lid = val(first(n, 'lib_id')[1])
        props = {val(p[1]): p for p in find(n, 'property')}
        path = val(props['Path'][2]) if 'Path' in props else None
        ref = val(props['Reference'][2])
        pins, gpts = lib[lid]
        bb = [place(sx, sy, rot, p) for p in gpts] + [(sx, sy)]
        for nm, p in props.items():
            if first(p, 'hide') is None and nm in ('Reference', 'Value'):
                a = first(p, 'at'); txt = val(p[2])
                x, y = float(a[1]), float(a[2])
                j = first(first(p, 'effects'), 'justify')
                w = len(txt) * 1.1
                bb += [(x, y - 1), (x + (w if j and 'left' in [val(q) for q in j] else -w if j and 'right' in [val(q) for q in j] else w / 2), y + 1)]
                if not (j and ('left' in [val(q) for q in j] or 'right' in [val(q) for q in j])): bb.append((x - w / 2, y))
        objs.append(dict(kind=k, idx=idx, pts=[place(sx, sy, rot, p) for p in pins], bb=bb,
                         module=(path.split('.')[0] if path else None), ref=ref, path=path, lib=lid, pos=(sx, sy)))
    elif k == 'wire':
        p = [(float(x[1]), float(x[2])) for x in find(first(n, 'pts'), 'xy')]
        objs.append(dict(kind=k, idx=idx, pts=p, bb=p, module=None))
    elif k in ('label', 'no_connect'):
        a = first(n, 'at'); x, y = float(a[1]), float(a[2])
        bb = [(x, y)]
        if k == 'label':
            ang = float(a[3]); w = len(val(n[1])) * 1.1 + 1
            ends = {0: [(x + w, y - 1.5), (x, y + 1.5)], 180: [(x - w, y - 1.5), (x, y + 1.5)],
                    90: [(x - 1.5, y - w), (x + 1.5, y)], 270: [(x - 1.5, y + w), (x + 1.5, y)]}
            bb += ends[ang]
        objs.append(dict(kind=k, idx=idx, pts=[(x, y)], bb=bb, module=None))

# ---- union-find on shared connection points -----------------------------------
parent = list(range(len(objs)))
def root(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
at_pt = collections.defaultdict(list)
for i, o in enumerate(objs):
    for p in o['pts']: at_pt[p].append(i)
for js in at_pt.values():
    for j in js[1:]: parent[root(j)] = root(js[0])
for i, o in enumerate(objs):
    if o['kind'] == 'wire':
        (x1, y1), (x2, y2) = o['pts']
        for p, js in at_pt.items():  # endpoints or T-joins on this wire
            on = (min(x1, x2) - 1e-6 <= p[0] <= max(x1, x2) + 1e-6 and min(y1, y2) - 1e-6 <= p[1] <= max(y1, y2) + 1e-6
                  and abs((x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1)) < 1e-6)
            if on:
                for j in js: parent[root(j)] = root(i)
islands = collections.defaultdict(list)
for i in range(len(objs)): islands[root(i)].append(i)

MECH = 'MECHANICAL'
isl = []
for members in islands.values():
    mods = {objs[i]['module'] for i in members if objs[i]['module']}
    if len(mods) > 1: raise SystemExit(f"island spans modules {mods}")
    if not mods: raise SystemExit("island with no owning module: " + str([objs[i]['kind'] for i in members]))
    m = mods.pop()
    if m.startswith(('H_MOUNT', 'FID_')): m = MECH
    pts = [p for i in members for p in objs[i]['bb']]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    syms = [objs[i] for i in members if objs[i]['kind'] == 'symbol' and objs[i]['module']]
    isl.append(dict(members=members, module=m, bbox=(min(xs), min(ys), max(xs), max(ys)), syms=syms))

# ---- ordering inside a block: main parts, then R, C, other, test points -------
def natkey(r):
    m = re.match(r'([A-Z#]+)(\d+)', r); return (m.group(1), int(m.group(2))) if m else (r, 0)
decl = {}  # (module instance, part name) -> declaration index
if ZEN:
    import os
    top = open(os.path.join(ZEN, 'funbit.zen')).read()
    files = dict(re.findall(r'(\w+) = Module\("\./(modules/\w+\.zen)"\)', top))
    for typ, inst in re.findall(r'^(\w+)\(\s*name="(\w+)"', top, re.M):
        if typ in files:
            names = re.findall(r'name="(\w+)"', open(os.path.join(ZEN, files[typ])).read())
            for k, nm in enumerate(names): decl[(inst, nm)] = k
def order_of(sym):
    path = sym.get('path') or ''
    parts = path.split('.')
    if len(parts) < 2: return 999
    for k in range(len(parts[1]), 0, -1):  # 'C_BULK1' falls back to 'C_BULK'
        if (parts[0], parts[1][:k]) in decl: return decl[(parts[0], parts[1][:k])]
    return 999
def cat(island):
    s0 = island['syms'][0]; r = s0['ref']
    group = {'U': 0, 'J': 0, 'BT': 0, 'Q': 0, 'SW': 0, 'TP': 7, 'H': 8, 'FID': 8}.get(natkey(r)[0], 4)
    return (group, order_of(s0), natkey(r))
def area(i): b = i['bbox']; return (b[2] - b[0]) * (b[3] - b[1])

def snap(v): return round(round(v / G) * G, 4)

PAD = 2.54; HEAD = 12.7
def pack(blocks_islands, max_w):
    """Shelf-pack islands in order; rows break when a category changes or width runs out."""
    x = y = 0; row_h = 0; placed = []; prev = None; W = 0
    for it in blocks_islands:
        b = it['bbox']; w = b[2] - b[0]; h = b[3] - b[1]
        c = cat(it)[0]
        brk = (prev is not None and ((c >= 4) != (prev >= 4) or (c == 7) != (prev == 7))) or x + w > max_w
        if brk and x > 0:
            x = 0; y += row_h + 2 * PAD; row_h = 0
        placed.append((it, x, y)); x += w + 2 * PAD; row_h = max(row_h, h); W = max(W, x); prev = c
    return placed, W - 2 * PAD, y + row_h

DESC = {
    'POWER': 'CR2032 cell, reverse-polarity P-FET, >=100 uF bulk. No regulator: everything runs from VBAT.',
    'AUDIO_PASSTHROUGH': 'Fully passive stereo path, jack to jack. Works with a dead cell or MCU in reset.',
    'AUDIO_SENSE': 'Non-loading 100k tap, precision half-wave envelope detector (U1A), music-present comparator (U1B). Option B direct-ADC parts are DNP.',
    'MCU': 'STM32U083KCU6, decoupling, 32.768 kHz LSE, BOOT0 pull-down, NRST filter.',
    'DISPLAY': 'Sharp LS013B7DH03 memory LCD on 10-pin 0.5 mm FPC (J4). EXTMODE strap selects EXTCOMIN mode.',
    'HMI': 'Select, Dance A, Dance B (internal pull-ups) and the pinhole reset switch.',
    'DEBUG': '10-pin Cortex SWD header and probe pads. Probe VTref only senses VBAT.',
    MECH: 'M2 mounting holes and fiducials.',
}
LAYOUT = [  # rows of blocks (signal flow left to right), with max inner width per block (mm)
    [('POWER', 95), ('AUDIO_PASSTHROUGH', 95), ('AUDIO_SENSE', 330)],
    [('MCU', 130), ('DISPLAY', 115), ('HMI', 70), ('DEBUG', 95), (MECH, 55)],
]
by_mod = collections.defaultdict(list)
for i in isl: by_mod[i['module']].append(i)
assert set(by_mod) == {m for r in LAYOUT for m, _ in r}, set(by_mod)

moves = {}  # item idx -> (dx, dy)
frames = []
X0, Y0 = 15.24, 15.24; GAP = 7.62
y = Y0; page_w = 0
for row in LAYOUT:
    x = X0; rh = 0
    for m, maxw in row:
        isls = sorted(by_mod[m], key=lambda i: (cat(i), -area(i)))
        placed, w, h = pack(isls, maxw)
        w = max(w, len(DESC[m]) * 1.05 if len(DESC[m]) * 1.05 < maxw else maxw)
        ix, iy = x + PAD * 2, y + HEAD
        for it, ox, oy in placed:
            dx = snap(ix + ox - it['bbox'][0]); dy = snap(iy + oy - it['bbox'][1])
            for k in it['members']: moves[objs[k]['idx']] = (dx, dy)
        bw = snap(w + PAD * 4); bh = snap(h + HEAD + PAD * 2)
        frames.append((m, x, y, bw, bh))
        x = snap(x + bw + GAP); rh = max(rh, bh)
    page_w = max(page_w, x); y = snap(y + rh + GAP)
page_h = y

# ---- rewrite -------------------------------------------------------------------
num = r'(-?\d+(?:\.\d+)?)'
def shift(chunk, dx, dy):
    chunk = re.sub(r'\(at ' + num + ' ' + num, lambda m: f"(at {fmt(float(m.group(1)) + dx)} {fmt(float(m.group(2)) + dy)}", chunk)
    return re.sub(r'\(xy ' + num + ' ' + num, lambda m: f"(xy {fmt(float(m.group(1)) + dx)} {fmt(float(m.group(2)) + dy)}", chunk)
def fmt(v):
    s = f"{round(v, 4):.4f}".rstrip('0').rstrip('.'); return '0' if s == '-0' else s

out = []; last = 0
for idx, (s, e, n) in enumerate(items):
    out.append(text[last:s]); chunk = text[s:e]
    if idx in moves: chunk = shift(chunk, *moves[idx])
    elif n[0] in ('symbol', 'wire', 'label', 'no_connect'): raise SystemExit(f"unmoved {n[0]}")
    if n[0] == 'paper':
        W = max(594, snap(page_w + X0)); H = max(420, snap(page_h + X0))
        chunk = '(paper "A2")' if (W, H) == (594, 420) else f'(paper "User" {fmt(W)} {fmt(H)})'
        chunk += ('\n\t(title_block\n\t\t(title "funbit: Sony PET-F7 Funbbit recreation")\n\t\t(date "2026-10-17")\n'
                  '\t\t(rev "0.1")\n\t\t(comment 1 "Generated by Diode pcb from funbit.zen; blocks follow modules/*.zen")\n'
                  '\t\t(comment 2 "Grouped by module. Nets connect by label name across blocks.")\n\t)')
    out.append(chunk); last = e
    if n[0] == 'no_connect' and idx == max(i for i, (_, _, q) in enumerate(items) if q[0] == 'no_connect'):
        for m, x, y, bw, bh in frames:
            u = lambda: str(uuid.uuid5(uuid.NAMESPACE_URL, f'funbit-block/{m}/{len(out)}'))
            out.append(f'\n\t(rectangle\n\t\t(start {fmt(x)} {fmt(y)})\n\t\t(end {fmt(x + bw)} {fmt(y + bh)})\n'
                       f'\t\t(stroke\n\t\t\t(width 0.254)\n\t\t\t(type dash)\n\t\t)\n\t\t(fill\n\t\t\t(type none)\n\t\t)\n\t\t(uuid "{u()}")\n\t)')
            out.append(f'\n\t(text "{m.replace("_", " ")}"\n\t\t(exclude_from_sim no)\n\t\t(at {fmt(x + 2.54)} {fmt(y + 5.08)} 0)\n'
                       f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 2.54 2.54)\n\t\t\t\t(thickness 0.508)\n\t\t\t\t(bold yes)\n\t\t\t)\n'
                       f'\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{u()}")\n\t)')
            out.append(f'\n\t(text "{DESC[m]}"\n\t\t(exclude_from_sim no)\n\t\t(at {fmt(x + 2.54)} {fmt(y + 8.89)} 0)\n'
                       f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t\t(italic yes)\n\t\t\t)\n'
                       f'\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{u()}")\n\t)')
out.append(text[last:])
open(dst, 'w').write(''.join(out))
print(f"{len(isl)} islands, page {fmt(max(594, snap(page_w + X0)))} x {fmt(max(420, snap(page_h + X0)))} mm")
for f in frames: print(f)
