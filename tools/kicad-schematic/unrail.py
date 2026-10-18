"""Break shared power rails that chain parts from different modules.

Wires in a cross-module island are removed. Each module pin that sat on such a
rail gets its own copy of the rail's power symbol (same Value, so same net),
and the rail's old power symbols are removed.
usage: unrail.py in.kicad_sch out.kicad_sch
"""
import re, sys, uuid, collections
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from sexp import top_items, find, first, val

src, dst = sys.argv[1], sys.argv[2]
code = open(__file__.rsplit('/', 1)[0] + '/regroup.py').read().split('islands = collections')[0]
code = code.replace("src, dst = sys.argv[1], sys.argv[2]", "").replace("sys.path.insert(0, __file__.rsplit('/', 1)[0])", "")
exec(code)  # reuses parsing + union-find: text, items, objs, root, at_pt, place, lib

islands = collections.defaultdict(list)
for i in range(len(objs)): islands[root(i)].append(i)

def on_wire(p, w):
    (x1, y1), (x2, y2) = w['pts']
    return (min(x1, x2) - 1e-6 <= p[0] <= max(x1, x2) + 1e-6 and min(y1, y2) - 1e-6 <= p[1] <= max(y1, y2) + 1e-6
            and abs((x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1)) < 1e-6)

drop = set(); add = []
for members in islands.values():
    mods = {objs[i]['module'] for i in members if objs[i]['module']}
    if len(mods) <= 1: continue
    wires = [i for i in members if objs[i]['kind'] == 'wire']
    # wire-level nets
    wp = list(range(len(wires)))
    def r(i):
        while wp[i] != i: i = wp[i]
        return i
    for a in range(len(wires)):
        for b in range(a + 1, len(wires)):
            if any(on_wire(p, objs[wires[b]]) for p in objs[wires[a]]['pts']) or any(on_wire(p, objs[wires[a]]) for p in objs[wires[b]]['pts']):
                wp[r(a)] = r(b)
    nets = collections.defaultdict(list)
    for a in range(len(wires)): nets[r(a)].append(objs[wires[a]])
    for ws in nets.values():
        touching = [o for o in (objs[i] for i in members) if o['kind'] != 'wire' and any(on_wire(p, w) for p in o['pts'] for w in ws)]
        pwr = [o for o in touching if o['kind'] == 'symbol' and not o['module']]
        kinds = {(o['lib'], val(next(p for p in find(items[o['idx']][2], 'property') if val(p[1]) == 'Value')[2])) for o in pwr}
        if len(kinds) != 1: raise SystemExit(f"rail net with power symbols {kinds}")
        other = [o for o in touching if o['kind'] != 'symbol' or o['module']]
        if any(o['kind'] != 'symbol' for o in other): raise SystemExit("label/no-connect on a rail")
        tmpl = pwr[0]
        for o in other:
            for p in o['pts']:
                if any(on_wire(p, w) for w in ws): add.append((tmpl, p))
        drop.update(w['idx'] for w in ws); drop.update(o['idx'] for o in pwr)

num = r'(-?\d+(?:\.\d+)?)'
def fmt(v):
    s = f"{round(v, 4):.4f}".rstrip('0').rstrip('.'); return '0' if s == '-0' else s
def clone(tmpl, p, n):
    s, e, node = items[tmpl['idx']]
    chunk = text[s:e]; ox, oy = tmpl['pts'][0]; dx, dy = p[0] - ox, p[1] - oy
    chunk = re.sub(r'\(at ' + num + ' ' + num, lambda m: f"(at {fmt(float(m.group(1)) + dx)} {fmt(float(m.group(2)) + dy)}", chunk)
    for old in set(re.findall(r'\(uuid "([0-9a-f-]+)"\)', chunk)):
        chunk = chunk.replace(old, str(uuid.uuid5(uuid.NAMESPACE_URL, f'funbit-pwr/{old}/{p}/{n}')))
    ref = val(next(q for q in find(node, 'property') if val(q[1]) == 'Reference')[2])
    new = '#PWR' + uuid.uuid5(uuid.NAMESPACE_URL, f'funbit-pwrref/{p}/{n}').hex
    return chunk.replace(f'"{ref}"', f'"{new}"')

out = []; last = 0; inserted = False
for idx, (s, e, node) in enumerate(items):
    if idx in drop:
        out.append(text[last:s].rstrip('\t')); last = e
        if text[last:last + 1] == '\n': last += 1
        continue
    out.append(text[last:e]); last = e
    if node[0] == 'symbol' and not inserted and idx == max(i for i, (_, _, q) in enumerate(items) if q[0] == 'symbol' and i not in drop):
        for n, (tmpl, p) in enumerate(add): out.append('\n\t' + clone(tmpl, p, n))
        inserted = True
out.append(text[last:])
open(dst, 'w').write(''.join(out))
print(f"removed {sum(1 for i in drop if items[i][2][0]=='wire')} rail wires and {sum(1 for i in drop if items[i][2][0]=='symbol')} rail power symbols; added {len(add)} power symbols")
