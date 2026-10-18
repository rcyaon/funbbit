import sys, re
sys.path.insert(0, __file__.rsplit('/',1)[0])
from sexp import parse, find, first, val
def nets(path):
    t = open(path).read(); root, _ = parse(t, t.index('('))
    res = {}
    for n in find(first(root, 'nets'), 'net'):
        name = val(first(n, 'name')[1])
        nodes = frozenset((val(first(x, 'ref')[1]), val(first(x, 'pin')[1])) for x in find(n, 'node'))
        res[nodes] = name
    comps = sorted(val(first(c,'ref')[1]) for c in find(first(root,'components'),'comp'))
    return res, comps
a, ca = nets(sys.argv[1]); b, cb = nets(sys.argv[2])
print('components equal:', ca == cb, len(ca))
print('net sets equal:', set(a) == set(b), len(a), len(b))
names = [(a[k], b[k]) for k in a if k in b and a[k] != b[k]]
print('renamed nets:', names[:10])
for k in set(a) ^ set(b): print('diff', a.get(k) or b.get(k), sorted(k)[:6])
