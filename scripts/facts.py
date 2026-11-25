"""Funciones cortas para citar cifras en los informes."""
from analysis import *


def sub(pop='todos', grp=None, uni=None):
    d = df[pop_mask(pop)]
    if grp:
        d = d[d['Grupo'] == grp]
    if uni:
        d = d[d['Universidad'] == uni]
    return d


def pc(col, vals, pop='todos', grp=None, uni=None, dec=0):
    d = sub(pop, grp, uni)
    if isinstance(vals, str):
        vals = [vals]
    s = d[col].dropna()
    v = pct(s.isin(vals).sum(), len(s))
    return f'{v:.{dec}f}'.replace('.', ',') + ' %'


def nn(col, vals, pop='todos', grp=None):
    d = sub(pop, grp)
    if isinstance(vals, str):
        vals = [vals]
    return int(d[col].isin(vals).sum())


def base(col, pop='todos', grp=None):
    return int(sub(pop, grp)[col].notna().sum())


def mean(col, pop='todos', grp=None, uni=None, dec=2):
    v = sub(pop, grp, uni)[col].mean()
    return f'{v:.{dec}f}'.replace('.', ',')


def fav(name, pop='todos', grp=None):
    v = sub(pop, grp)[name].dropna()
    return f'{pct((v >= 4).sum(), len(v)):.0f} %'


def multi_pc(code, option_start, grp=None, uni=None):
    m = [x for x in MULTI if x[0] == code][0]
    d = sub(m[3], grp, uni)
    d = d[d[list(m[2])].notna().any(axis=1)]
    for c in m[2]:
        if item_label(c).startswith(option_start):
            return f'{pct(d[c].notna().sum(), len(d)):.0f} %'
    raise KeyError(option_start)


def num(x, dec=1):
    return f'{x:.{dec}f}'.replace('.', ',')
