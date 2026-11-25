"""Verificación independiente: compara los conteos calculados desde 'Datos sin procesar'
con las tablas resumen que generó la plataforma en cada archivo."""
import re
import numpy as np
import pandas as pd
from load import FILES

SUMMARY_SHEETS = ['Q1 - Q4', 'Q8 - Q61', 'Q63 - Q70', 'Q73 - Q78', 'Q80 - Q82']


def norm(s):
    return re.sub(r'\s+', ' ', str(s)).strip().rstrip('.').lower()


def raw_table(f):
    d = pd.read_excel(f, sheet_name='Datos sin procesar', header=None)
    hdr = [str(x) for x in d.iloc[0]]
    return d.iloc[1:].reset_index(drop=True), hdr


def parse_summary(f):
    """Devuelve lista de dicts: {q, tipo, item, categoria, n}."""
    out = []
    for s in SUMMARY_SHEETS:
        d = pd.read_excel(f, sheet_name=s, header=None)
        q = None
        i = 0
        while i < len(d):
            c0 = d.iat[i, 0]
            if isinstance(c0, str) and re.fullmatch(r'Q\d+', c0.strip()):
                q = c0.strip()
                i += 1
                continue
            if isinstance(c0, str) and c0.strip() == 'Statement':
                cats = [str(x) for x in d.iloc[i, 1:] if pd.notna(x)]
                cats = [c for c in cats if c != 'Overall']
                j = i + 1
                while j < len(d) and pd.notna(d.iat[j, 0]) or (j < len(d) and pd.isna(d.iat[j, 0]) and pd.notna(d.iat[j, 1])):
                    if pd.notna(d.iat[j, 0]):
                        item = str(d.iat[j, 0])
                        for k, cat in enumerate(cats):
                            v = d.iat[j, 1 + k]
                            out.append({'q': q, 'tipo': 'matriz', 'item': item, 'categoria': cat, 'n': float(v)})
                    j += 1
                i = j
                continue
            # tabla simple: fila con categoría y número, hasta 'Total'
            if q and isinstance(c0, str) and i + 1 < len(d) and pd.isna(d.iat[i, 1]):
                j = i + 1
                rows = []
                while j < len(d) and isinstance(d.iat[j, 0], str) and d.iat[j, 0] != 'Total' and isinstance(d.iat[j, 1], (int, float, np.integer, np.floating)) and pd.notna(d.iat[j, 1]):
                    rows.append((d.iat[j, 0], float(d.iat[j, 1])))
                    j += 1
                if rows and j < len(d) and d.iat[j, 0] == 'Total':
                    for cat, n in rows:
                        out.append({'q': q, 'tipo': 'simple', 'item': str(c0), 'categoria': cat, 'n': n})
                    i = j + 1
                    continue
            i += 1
    return pd.DataFrame(out)


def raw_counts(d, hdr, q, tipo, item, cat):
    cols = [j for j, h in enumerate(hdr) if h.startswith(f'[{q}]')]
    if tipo == 'matriz':
        it = norm(item.replace('...', ''))[:40]
        cols = [j for j in cols if ' - ' in hdr[j] and norm(hdr[j].split(' - ')[-1]).startswith(it)]
    else:
        main = [j for j in cols if not re.search(r'- Otr[ao]', hdr[j])]
        if len(main) > 1:  # selección múltiple: una columna por opción
            sel = [j for j in main if ' - ' in hdr[j] and norm(hdr[j].split(' - ')[-1]) == norm(cat)]
            if sel:
                return int(d[sel[0]].notna().sum()), 'multi'
            return None, 'sin columna'
        cols = main
    if len(cols) != 1:
        return None, f'{len(cols)} columnas'
    s = d[cols[0]].dropna().astype(str).map(norm)
    return int((s == norm(cat)).sum()), 'ok'


def run():
    rows = []
    for uni, f in FILES.items():
        d, hdr = raw_table(f)
        sm = parse_summary(f)
        for _, r in sm.iterrows():
            n_raw, how = raw_counts(d, hdr, r['q'], r['tipo'], r['item'], r['categoria'])
            rows.append({'Universidad (enlace)': uni, 'Pregunta': r['q'], 'Tipo': r['tipo'], 'Ítem': r['item'][:70],
                         'Categoría': r['categoria'], 'n plataforma': r['n'], 'n base exportada': n_raw, 'método': how})
    t = pd.DataFrame(rows)
    t['Diferencia'] = t['n plataforma'] - t['n base exportada']
    return t


if __name__ == '__main__':
    t = run()
    ok = t[t['n base exportada'].notna()]
    print('comparaciones', len(t), 'emparejadas', len(ok))
    print('coinciden', (ok['Diferencia'] == 0).sum(), 'difieren', (ok['Diferencia'] != 0).sum())
    print(ok.groupby('Universidad (enlace)')['Diferencia'].agg(['count', lambda s: (s == 0).sum(), 'sum', 'min', 'max']))
    print(t[t['n base exportada'].isna()]['método'].value_counts())
    print(ok[ok['Diferencia'] != 0].groupby(['Universidad (enlace)', 'Pregunta']).size().head(60))
    t.to_pickle('/projects/sandbox/work/verify.pkl')
