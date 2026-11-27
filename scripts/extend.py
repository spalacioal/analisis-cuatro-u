"""Ampliación: verificación, armonización con la presentación de EAFIT, representatividad,
efectos ajustados (análogos a las estrategias de EAFIT), corrección por comparaciones múltiples,
intervalos de confianza y segmento de postulantes potenciales."""
import re
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint
from analysis import *
from load import load as load_raw, FILES
import verify

RNG = np.random.default_rng(2026)

# ------------------------------------------------------------------ cifras de la presentación EAFIT
EAFIT = {
    'aprobados': 96, 'proyectos': 23, 'autores': 110, 'participaciones': 141,
    'sexo': {'Mujeres': 44.8, 'Hombres': 52.1, 'No informado': 3.1},
    'sexo_n': {'Mujeres': 43, 'Hombres': 50, 'No informado': 3},
    'uni': {'CESA': 7.3, 'EAFIT': 24.0, 'ICESI': 21.9, 'Uninorte': 46.9},
    'uni_n': {'CESA': 7, 'EAFIT': 23, 'ICESI': 21, 'Uninorte': 45},
    'area': {'C. sociales': 30.2, 'Ingeniería': 29.2, 'Economía': 16.0, 'C. naturales': 7.0, 'Otras / no inf.': 18.0},
    'tray': {'<10 años': 4.0, '10-19 años': 44.0, '20 años o más': 47.0, 'No informado': 5.0},
    'tray_fino': {'<5': 1, '5-9': 3, '10-14': 18, '15-19': 26, '20+': 47, 'No inf.': 5},
    'estado': {'En desarrollo': 9, 'Finalizado con pendientes': 5, 'Finalizado': 3, 'Sin cierre o estado verificable': 6},
    'articulos': {'Finalizados / sometidos': 14, 'Pendientes / incompletos': 9},
    'colab': {'Internacional': 9, 'Interinstitucional académica': 10, 'Multiactor': 4},
    'n_unis': {'2': 10, '3': 2, '4': 11},
    'impacto': [('Probabilidad de publicar (controles sintéticos, t=+2)', '+18,3 pp', '+0,2 a +36,5', 0.047),
                ('Coautor externo (controles sintéticos, t=0)', '+21,7 pp', '+0,3 a +43,0', 0.047),
                ('Probabilidad de publicar (rechazados, t=0)', '+24,1 pp', '+0,2 a +48,1', 0.048),
                ('Probabilidad de publicar (rechazados, t=+2)', '+36,2 pp', '+6,8 a +65,7', 0.016),
                ('Cantidad de productos (controles sintéticos, t=0)', '+0,25', '-2,37 a +2,87', 0.852),
                ('Cantidad de productos (rechazados, t=0)', '+0,86', '-1,71 a +3,43', 0.510)],
}

# ------------------------------------------------------------------ variables armonizadas
OTRA_AREA = {'Computación': 'Ingeniería', 'Diseño, tecnología e innovación': 'Ingeniería', 'Física': 'C. naturales',
             'Matemática': 'C. naturales'}
AREA_MAP = {'Ciencias sociales.': 'C. sociales', 'Ingeniería y tecnología.': 'Ingeniería',
            'Economía, administración y negocios.': 'Economía', 'Ciencias naturales.': 'C. naturales'}
AREAS_E = ['C. sociales', 'Ingeniería', 'Economía', 'C. naturales', 'Otras / no inf.']


def area_e(r):
    if r[41] in AREA_MAP:
        return AREA_MAP[r[41]]
    if r[41] == 'Otra.¿Cuál?' and r[42] in OTRA_AREA:
        return OTRA_AREA[r[42]]
    return 'Otras / no inf.'


df['Área (rangos EAFIT)'] = df.apply(area_e, axis=1)
df['Área (C. sociales + Humanidades)'] = np.where(df[41] == 'Humanidades.', 'C. sociales', df['Área (rangos EAFIT)'])
df['Trayectoria (rangos EAFIT aprox.)'] = df[43].map({'Menos de 3 años.': '<10 años', 'Entre 3 y 5 años.': '<10 años',
                                                       'Entre 6 y 10 años.': '<10 años', 'Entre 11 y 20 años.': '10-19 años',
                                                       'Más de 20 años.': '20 años o más'})
TRAY_E = ['<10 años', '10-19 años', '20 años o más']
SINGLE_ORDER['TR'] = TRAY_E
SINGLE_ORDER['AR'] = AREAS_E
df['Sexo (rangos EAFIT)'] = df['Sexo (estimado)'].map({'Mujer': 'Mujeres', 'Hombre': 'Hombres'}).fillna('No informado')
df['Estado proyecto (rangos EAFIT)'] = df[143].map({'No ha iniciado.': 'En desarrollo', 'Está en etapa de formalización.': 'En desarrollo',
                                                     'Está en ejecución.': 'En desarrollo',
                                                     'Finalizó actividades, pero tiene productos en desarrollo.': 'Finalizado con pendientes',
                                                     'Finalizó y cerró formalmente.': 'Finalizado',
                                                     'No conoce su estado actual.': 'Sin cierre o estado verificable'})
df['Artículos (rangos EAFIT)'] = df[184].map({'Completado': 'Finalizados / sometidos', 'En desarrollo': 'Pendientes / incompletos',
                                               'Previsto, pero no iniciado': 'Pendientes / incompletos'})
four = {'CESA': 81, 'EAFIT': 82, 'ICESI': 83, 'Uninorte': 84}
df['N.º universidades 4U (incluida la propia)'] = [1 + sum(pd.notna(r[four[u]]) for u in four if u != r['Universidad']) for _, r in df.iterrows()]
fin_mask = df['Grupo'] == 'Financiado'
ext = df[list(range(223, 228))].notna().any(axis=1)  # actores externos en identificación, formulación, diseño, desarrollo o validación
df['Tipo de colaboración (aprox. EAFIT)'] = np.where(ext, 'Multiactor', np.where(df[86].notna(), 'Internacional', 'Interinstitucional académica'))


def pct_table(col, cats, mask):
    s = df.loc[mask, col]
    return pd.Series({c: round(100 * (s == c).sum() / len(s), 1) for c in cats}), {c: int((s == c).sum()) for c in cats}, len(s)


def harmonized():
    """Tablas lado a lado: encuesta (financiados) frente a la presentación de EAFIT."""
    out = []

    def block(tema, col, cats, ea, nota, mask=fin_mask, ea_n=None, unidad_e='aprobados', unidad_s='financiados encuestados'):
        p, n, tot = pct_table(col, cats, mask)
        ea_tot = sum(ea_n.values()) if ea_n else None
        for c in cats:
            out.append({'Tema': tema, 'Categoría': c, f'EAFIT %': ea.get(c, np.nan), 'EAFIT n': (ea_n or {}).get(c, np.nan),
                        'Encuesta %': p[c], 'Encuesta n': n[c], 'Diferencia (pp)': round(p[c] - ea.get(c, np.nan), 1) if c in ea else np.nan,
                        'Unidad EAFIT': unidad_e, 'Unidad encuesta': f'{unidad_s} (n={tot})', 'Nota': nota})

    block('Sexo', 'Sexo (rangos EAFIT)', ['Mujeres', 'Hombres', 'No informado'], EAFIT['sexo'],
          'EAFIT: sexo registrado. Encuesta: estimado por nombre.', ea_n=EAFIT['sexo_n'])
    block('Universidad', 'Universidad', UNIS, EAFIT['uni'], 'Encuesta: universidad declarada (B4).', ea_n=EAFIT['uni_n'])
    block('Área de conocimiento', 'Área (rangos EAFIT)', AREAS_E, EAFIT['area'],
          'EAFIT: área del programa del máximo título. Encuesta: área elegida por la persona; Humanidades, Artes, Salud e interdisciplinaria quedan en Otras.')
    block('Área (C. sociales incluye Humanidades)', 'Área (C. sociales + Humanidades)', AREAS_E, EAFIT['area'],
          'Sensibilidad: suma Humanidades a Ciencias sociales.')
    tr = dict(EAFIT['tray'])
    block('Trayectoria', 'Trayectoria (rangos EAFIT aprox.)', TRAY_E, tr,
          'EAFIT: años desde el pregrado (<10 = <5 y 5-9). Encuesta: años de experiencia en investigación (B10: ≤10, 11-20, >20). Conceptos distintos y cortes desplazados un año.')
    block('Estado del proyecto', 'Estado proyecto (rangos EAFIT)', ['En desarrollo', 'Finalizado con pendientes', 'Finalizado', 'Sin cierre o estado verificable'],
          {k: round(100 * v / 23, 1) for k, v in EAFIT['estado'].items()},
          'EAFIT: 23 proyectos con evidencia de cierre. Encuesta: respuesta de cada persona (un proyecto puede tener varias).',
          mask=fin_mask & df[143].notna(), ea_n=EAFIT['estado'], unidad_e='proyectos', unidad_s='personas financiadas')
    block('Artículos científicos', 'Artículos (rangos EAFIT)', ['Finalizados / sometidos', 'Pendientes / incompletos'],
          {k: round(100 * v / 23, 1) for k, v in EAFIT['articulos'].items()},
          'EAFIT: 23 artículos declarados en informes. Encuesta: estado del tipo de producto "artículos" en el proyecto de cada persona, entre quienes lo tenían previsto.',
          mask=fin_mask & df['Artículos (rangos EAFIT)'].notna(), ea_n=EAFIT['articulos'], unidad_e='artículos', unidad_s='personas con artículos previstos')
    block('Tipo de colaboración', 'Tipo de colaboración (aprox. EAFIT)', ['Internacional', 'Interinstitucional académica', 'Multiactor'],
          {k: round(100 * v / 23, 1) for k, v in EAFIT['colab'].items()},
          'Encuesta: Multiactor = actores externos participaron en identificación, formulación, diseño, desarrollo o validación (H6); Internacional = colaboró con universidades internacionales desde 2021 (D5). Aproximación a nivel persona.',
          mask=fin_mask & df[list(range(223, 232))].notna().any(axis=1), ea_n=EAFIT['colab'], unidad_e='proyectos', unidad_s='personas financiadas')
    df['_nu'] = df['N.º universidades 4U (incluida la propia)'].clip(upper=4).astype(str)
    block('N.º de universidades 4U', '_nu', ['1', '2', '3', '4'], {k: round(100 * v / 23, 1) for k, v in EAFIT['n_unis'].items()},
          'EAFIT: universidades 4U en el proyecto. Encuesta: universidades 4U con las que la persona colaboró desde 2021, incluida la propia (D5).',
          ea_n=EAFIT['n_unis'], unidad_e='proyectos')
    return pd.DataFrame(out)


# ------------------------------------------------------------------ representatividad
def coverage():
    rows = []
    f = df[fin_mask]
    for u in UNIS:
        k = int((f['Universidad'] == u).sum())
        rows.append({'Dimensión': 'Universidad', 'Categoría': u, 'Aprobados (EAFIT)': EAFIT['uni_n'][u], 'Financiados encuestados': k,
                     'Cobertura %': round(100 * k / EAFIT['uni_n'][u], 1)})
    for s, lab in [('Mujeres', 'Mujer'), ('Hombres', 'Hombre')]:
        k = int((f['Sexo (estimado)'] == lab).sum())
        rows.append({'Dimensión': 'Sexo', 'Categoría': s, 'Aprobados (EAFIT)': EAFIT['sexo_n'][s], 'Financiados encuestados': k,
                     'Cobertura %': round(100 * k / EAFIT['sexo_n'][s], 1)})
    rows.append({'Dimensión': 'Total', 'Categoría': 'Todos', 'Aprobados (EAFIT)': 96, 'Financiados encuestados': len(f),
                 'Cobertura %': round(100 * len(f) / 96, 1)})
    return pd.DataFrame(rows)


def rake_weights():
    """Pesos por raking (universidad y sexo) para que los financiados encuestados reproduzcan los márgenes de los 96 aprobados."""
    f = df[fin_mask].copy()
    w = np.ones(len(f))
    tu = {u: EAFIT['uni_n'][u] / 96 for u in UNIS}
    ts = {'Mujer': 43 / 93, 'Hombre': 50 / 93}
    for _ in range(100):
        for col, tgt in [('Universidad', tu), ('Sexo (estimado)', ts)]:
            for k, v in tgt.items():
                m = (f[col] == k).values
                w[m] *= v * w.sum() / w[m].sum()
    w = w / w.mean()
    return pd.Series(w, index=f.index)


def weighted_indicators():
    w = rake_weights()
    f = df.loc[w.index]
    defs = [
        ('Balance: beneficios > dificultades (F7)', lambda d: d[166].isin(SINGLE_ORDER['F7'][3:5]), d_valid(166)),
        ('Sin 4U el proyecto no se habría realizado (I5)', lambda d: d[265] == 'Probablemente el proyecto no se habría realizado.', d_valid(265)),
        ('Artículos completados (H1)', lambda d: d[184] == 'Completado', d_valid(184)),
        ('Esfuerzo de coordinación mayor (F6)', lambda d: d[165].isin(['Mayor.', 'Mucho mayor.']), d_valid(165)),
        ('Colaboró con otra universidad 4U desde 2021 (D5)', lambda d: d['D5_n_socios_4U_otras'] > 0, lambda d: d[list(range(81, 89))].notna().any(axis=1)),
        ('Publicaciones conjuntas desde 2021 (D6)', lambda d: d[91].notna(), lambda d: d[list(range(89, 99))].notna().any(axis=1)),
        ('Probable volver a colaborar (J1)', lambda d: d[282].isin(['Probable.', 'Muy probable.']), d_valid(282)),
        ('Probable continuidad sin nueva financiación (I4)', lambda d: d[264].isin(['Probable.', 'Muy probable.']), d_valid(264)),
    ]
    rows = []
    for lab, num, val in defs:
        v = val(f)
        x = num(f)[v].astype(float)
        ww = w[v]
        rows.append({'Indicador (financiados)': lab, 'n': int(v.sum()), 'Sin ponderar %': round(100 * x.mean(), 1),
                     'Ponderado %': round(100 * np.average(x, weights=ww), 1)})
    for code in ['IDX_F2', 'IDX_F3', 'IDX_F4', 'IDX_F5', 'IDX_G1', 'IDX_G2', 'IDX_G3', 'IDX_H3', 'IDX_I1', 'IDX_C3']:
        v = f[code].notna()
        rows.append({'Indicador (financiados)': f'Índice {code[4:]} (1-5)', 'n': int(v.sum()), 'Sin ponderar %': round(f.loc[v, code].mean(), 2),
                     'Ponderado %': round(np.average(f.loc[v, code], weights=w[v]), 2)})
    t = pd.DataFrame(rows)
    t['Diferencia'] = (t['Ponderado %'] - t['Sin ponderar %']).round(2)
    wt = pd.DataFrame({'Universidad': f['Universidad'], 'Sexo': f['Sexo (estimado)'], 'Peso': w.round(3)}).groupby(['Universidad', 'Sexo'])['Peso'].agg(['count', 'mean']).reset_index()
    wt.columns = ['Universidad', 'Sexo', 'n', 'Peso']
    return t, wt


def d_valid(col):
    return lambda d: d[col].notna()


# ------------------------------------------------------------------ efectos ajustados
OUTCOMES = [
    ('Publicaciones o productos conjuntos desde 2021 (D6)', 'bin', lambda d: d[91].notna().astype(float), lambda d: d[list(range(89, 99))].notna().any(axis=1)),
    ('Colaboró con otra universidad 4U desde 2021 (D5)', 'bin', lambda d: (d['D5_n_socios_4U_otras'] > 0).astype(float), lambda d: d[list(range(81, 89))].notna().any(axis=1)),
    ('Al menos un producto con otra universidad (D7.3)', 'bin', lambda d: (d['D7_3'] > 0).astype(float), lambda d: d['D7_3'].notna()),
    ('Al menos un proyecto ejecutado con otra universidad (D7.2)', 'bin', lambda d: (d['D7_2'] > 0).astype(float), lambda d: d['D7_2'].notna()),
    ('Al menos una iniciativa con actores externos (D7.4)', 'bin', lambda d: (d['D7_4'] > 0).astype(float), lambda d: d['D7_4'].notna()),
    ('Al menos una relación nueva activa (D7.5)', 'bin', lambda d: (d['D7_5'] > 0).astype(float), lambda d: d['D7_5'].notna()),
    ('N.º de productos con otra universidad (D7.3, aprox.)', 'num', lambda d: d['D7_3'], lambda d: d['D7_3'].notna()),
    ('N.º total de experiencias interinst. (D7, aprox.)', 'num', lambda d: d['D7_total_experiencias_aprox'], lambda d: d['D7_total_experiencias_aprox'].notna()),
    ('Índice de cambio en capacidades (C4, 1-5)', 'num', lambda d: d['IDX_C4'], lambda d: d['IDX_C4'].notna()),
    ('Probable o muy probable volver a colaborar (J1)', 'bin', lambda d: (d['J1_num'] >= 4).astype(float), lambda d: d['J1_num'].notna()),
    ('Probable o muy probable liderar (J2)', 'bin', lambda d: (d['J2_num'] >= 4).astype(float), lambda d: d['J2_num'].notna()),
]


def covariates(d):
    X = pd.DataFrame(index=d.index)
    X['mujer'] = (d['Sexo (estimado)'] == 'Mujer').astype(float)
    X['experiencia_años'] = d['Experiencia_años_aprox']
    X['dedicacion_pct'] = d['Dedicación_inv_pct_aprox']
    d8 = d['D8_num']
    X['proy_previos_2021'] = d8.fillna(d8.median())
    X['proy_previos_nr'] = d8.isna().astype(float)
    for r in ['Asociado', 'Titular', 'Otro / sin rango', 'Auxiliar']:
        X[f'rango_{r}'] = (d['Rango (agrupado)'] == r).astype(float)
    for a in ['Ingeniería', 'Economía', 'C. naturales', 'Otras / no inf.']:
        X[f'area_{a}'] = (d['Área (rangos EAFIT)'] == a).astype(float)
    for u in ['EAFIT', 'ICESI', 'Uninorte']:
        X[f'uni_{u}'] = (d['Universidad'] == u).astype(float)
    return X


def pscore(d, T):
    X = covariates(d)
    X = X.loc[:, X.std() > 0]
    try:
        m = sm.Logit(T, sm.add_constant(X)).fit_regularized(alpha=1.0, disp=0)
        return pd.Series(m.predict(sm.add_constant(X)), index=d.index)
    except Exception:
        m = sm.GLM(T, sm.add_constant(X), family=sm.families.Binomial()).fit()
        return pd.Series(m.predict(sm.add_constant(X)), index=d.index)


def nn_match(d, T, ps):
    """1 control por tratado, con reemplazo, emparejamiento exacto por universidad (como EAFIT)."""
    pairs = []
    for i in d.index[T == 1]:
        pool = d.index[(T == 0) & (d['Universidad'] == d.at[i, 'Universidad'])]
        if len(pool) == 0:
            pool = d.index[T == 0]
        j = (ps[pool] - ps[i]).abs().idxmin()
        pairs.append((i, j))
    return pairs


def att(y, pairs):
    return float(np.mean([y[i] - y[j] for i, j in pairs]))


def effects(control='todos', B=800):
    """ATT por emparejamiento y coeficiente de MCO con controles."""
    rows = []
    if control == 'todos':
        base = df[df['Grupo'].isin(G3)]
    else:
        base = df[df['Grupo'].isin(['Financiado', 'Postuló, no financiado'])]
    for lab, kind, yf, vf in OUTCOMES:
        d = base[vf(base)].copy()
        y = yf(d)
        T = (d['Grupo'] == 'Financiado').astype(float)
        ps = pscore(d, T)
        pairs = nn_match(d, T, ps)
        est = att(y, pairs)
        # bootstrap: remuestrea tratados y controles, re-estima pscore y pareo
        bs = []
        ti, ci = d.index[T == 1], d.index[T == 0]
        for _ in range(B):
            s = np.concatenate([RNG.choice(ti, len(ti)), RNG.choice(ci, len(ci))])
            db = d.loc[s].reset_index(drop=True)
            Tb = (db['Grupo'] == 'Financiado').astype(float)
            try:
                psb = pscore(db, Tb)
                bs.append(att(yf(db), nn_match(db, Tb, psb)))
            except Exception:
                continue
        lo, hi = np.percentile(bs, [2.5, 97.5])
        p_bs = 2 * min(np.mean(np.array(bs) <= 0), np.mean(np.array(bs) >= 0))
        # MCO con errores robustos HC1
        X = covariates(d)
        X = X.loc[:, X.std() > 0]
        X.insert(0, 'financiado', T)
        ols = sm.OLS(y, sm.add_constant(X)).fit(cov_type='HC1')
        b, se, p = ols.params['financiado'], ols.bse['financiado'], ols.pvalues['financiado']
        mult = 100 if kind == 'bin' else 1
        raw = (y[T == 1].mean() - y[T == 0].mean()) * mult
        rows.append({'Resultado': lab, 'Tipo': 'pp' if kind == 'bin' else 'unidades', 'Financiados n': int(T.sum()), 'Controles n': int((T == 0).sum()),
                     'Controles únicos usados': len(set(j for _, j in pairs)),
                     'Media financiados': round(y[T == 1].mean() * mult, 1 if kind == 'bin' else 2),
                     'Media controles': round(y[T == 0].mean() * mult, 1 if kind == 'bin' else 2),
                     'Diferencia bruta': round(raw, 1 if kind == 'bin' else 2),
                     'ATT emparejamiento': round(est * mult, 1 if kind == 'bin' else 2),
                     'IC95% inf': round(lo * mult, 1 if kind == 'bin' else 2), 'IC95% sup': round(hi * mult, 1 if kind == 'bin' else 2),
                     'p (bootstrap)': round(p_bs, 3),
                     'MCO coef.': round(b * mult, 1 if kind == 'bin' else 2), 'MCO EE robusto': round(se * mult, 1 if kind == 'bin' else 2),
                     'MCO p': round(p, 3)})
    return pd.DataFrame(rows)


def balance(control='todos'):
    base = df[df['Grupo'].isin(G3 if control == 'todos' else ['Financiado', 'Postuló, no financiado'])]
    T = (base['Grupo'] == 'Financiado').astype(float)
    X = covariates(base)
    ps = pscore(base, T)
    pairs = nn_match(base, T, ps)
    ti = [i for i, _ in pairs]
    cj = [j for _, j in pairs]
    rows = []
    for c in X.columns:
        xt, xc = X.loc[T == 1, c], X.loc[T == 0, c]
        sd = np.sqrt((xt.var() + xc.var()) / 2) or 1
        rows.append({'Covariable': c, 'Media financiados': round(xt.mean(), 3), 'Media controles (antes)': round(xc.mean(), 3),
                     'DME antes': round((xt.mean() - xc.mean()) / sd, 3),
                     'Media controles (emparejados)': round(X.loc[cj, c].mean(), 3),
                     'DME después': round((X.loc[ti, c].mean() - X.loc[cj, c].mean()) / sd, 3)})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ comparaciones múltiples
def multiple_testing():
    rows = []
    for dim in ['Grupo', 'Universidad', 'Sexo', 'Experiencia']:
        t = matrix_by(dim)
        t = t[t['p-valor'].notna()].copy()
        rej, q, _, _ = multipletests(t['p-valor'], method='fdr_bh')
        t['q (Benjamini-Hochberg)'] = q.round(4)
        t['Significativo tras corrección (q<0,05)'] = np.where(rej, 'Sí', 'No')
        t['Dimensión'] = dim
        rows.append(t[['Dimensión', 'Ítem', 'Enunciado', 'Prueba', 'p-valor', 'q (Benjamini-Hochberg)', 'Significativo tras corrección (q<0,05)']])
    out = pd.concat(rows)
    return out.sort_values(['Dimensión', 'p-valor'])


# ------------------------------------------------------------------ intervalos de confianza
def ci_table():
    f = df[fin_mask]
    defs = [
        ('Tasa de éxito entre postulantes encuestados', 45, 56),
        ('Mujeres entre encuestados (estimado)', 51, 102),
        ('Mujeres entre financiados encuestados', 25, 45),
        ('Más de 10 años de experiencia', int(df[43].isin(['Entre 11 y 20 años.', 'Más de 20 años.']).sum()), int(df[43].notna().sum())),
        ('Carga de trabajo permite participar (C3.3 favorable)', int((df['C3_3'] >= 4).sum()), int(df['C3_3'].notna().sum())),
        ('Procedimientos facilitan (C3.5 favorable)', int((df['C3_5'] >= 4).sum()), int(df['C3_5'].notna().sum())),
        ('Falta de tiempo como barrera (J4)', int(df[295].notna().sum()), int(df[list(range(295, 310))].notna().any(axis=1).sum())),
        ('Probable volver a colaborar (J1)', int((df['J1_num'] >= 4).sum()), int(df['J1_num'].notna().sum())),
        ('Financiados: beneficios > dificultades (F7)', int(f[166].isin(SINGLE_ORDER['F7'][3:5]).sum()), int(f[166].notna().sum())),
        ('Financiados: sin 4U no se habría realizado (I5)', int((f[265] == 'Probablemente el proyecto no se habría realizado.').sum()), int(f[265].notna().sum())),
        ('Financiados: artículos completados (H1)', int((f[184] == 'Completado').sum()), int(f[184].notna().sum())),
        ('Financiados: uso por entidades públicas (H5)', int((f['H5_3'] == 4).sum()), int(f['H5_3'].notna().sum())),
        ('Retroalimentación detallada (E6)', int((df[124] == 'Sí, suficientemente detallada.').sum()), int(df[124].notna().sum())),
        ('No financiados: el equipo dejó de trabajar (E9)', int(df.loc[df['Grupo'] == 'Postuló, no financiado', 132].notna().sum()),
         int(df.loc[df['Grupo'] == 'Postuló, no financiado', list(range(132, 142))].notna().any(axis=1).sum())),
    ]
    rows = []
    for lab, k, n in defs:
        lo, hi = proportion_confint(k, n, method='wilson')
        rows.append({'Indicador': lab, 'k': k, 'n': n, '%': round(100 * k / n, 1), 'IC95% inf': round(100 * lo, 1), 'IC95% sup': round(100 * hi, 1),
                     'Margen ± (pp)': round(100 * (hi - lo) / 2, 1)})
    for code in ['IDX_C1', 'IDX_C3', 'IDX_C4', 'IDX_F2', 'IDX_F4', 'IDX_G1', 'IDX_I1']:
        pop = [m[4] for m in MATRIX if m[0] == code[4:]][0]
        v = df.loc[pop_mask(pop), code].dropna().values
        bs = [RNG.choice(v, len(v)).mean() for _ in range(2000)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        rows.append({'Indicador': f'Índice {code[4:]} (media 1-5)', 'k': np.nan, 'n': len(v), '%': round(v.mean(), 2),
                     'IC95% inf': round(lo, 2), 'IC95% sup': round(hi, 2), 'Margen ± (pp)': round((hi - lo) / 2, 2)})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ postulantes potenciales
def potential():
    np_ = df[df['Grupo'] == 'No postuló']
    pot = np_[(np_['J1_num'] >= 4)]
    rows = [{'Indicador': 'No postulantes', 'Valor': len(np_)},
            {'Indicador': 'No postulantes con intención probable o muy probable de colaborar (J1)', 'Valor': len(pot)},
            {'Indicador': '…de ellos, con disposición alta (C1 ≥ 4)', 'Valor': int((pot['IDX_C1'] >= 4).sum())},
            {'Indicador': '…de ellos, que conocían poco o nada la Alianza (D2)', 'Valor': int(pot[71].isin(['No los conocía.', 'Los conocía muy poco.']).sum())},
            {'Indicador': '…de ellos, que solo recibieron información o escucharon de la Alianza (D3)', 'Valor': int(pot[72].isin(['Recibí información sobre la Alianza o sus convocatorias, pero no participé.', 'Había escuchado hablar de la Alianza, pero no conocía sus actividades.']).sum())}]
    prof = []
    for lab, col in [('Universidad', 'Universidad'), ('Área (rangos EAFIT)', 'Área (rangos EAFIT)'), ('Sexo', 'Sexo (estimado)'),
                     ('Trayectoria', 'Trayectoria (rangos EAFIT aprox.)'), ('Rango', 'Rango (agrupado)')]:
        for k, v in pot[col].value_counts().items():
            prof.append({'Variable': lab, 'Categoría': k, 'n': int(v), '%': round(100 * v / len(pot), 1)})
    bar = []
    for c in list(range(295, 310)) + list(range(310, 321)):
        lab = item_label(c).rstrip('.')
        bar.append({'Pregunta': 'J4 barrera' if c < 310 else 'J5 prioridad', 'Opción': lab, 'n': int(pot[c].notna().sum()),
                    '%': round(100 * pot[c].notna().sum() / len(pot), 1)})
    bar = pd.DataFrame(bar).sort_values(['Pregunta', 'n'], ascending=[True, False])
    bar = bar[bar['n'] > 0]
    return pd.DataFrame(rows), pd.DataFrame(prof), bar


# ------------------------------------------------------------------ sensibilidad con resúmenes de la plataforma
def platform_profile():
    t = pd.read_pickle('/projects/sandbox/work/verify.pkl') if __import__('os').path.exists('/projects/sandbox/work/verify.pkl') else verify.run()
    rows = []
    for q, code, col in [('Q7', 'B4', 32), ('Q9', 'B6', 35), ('Q11', 'B8', 39), ('Q12', 'B9', 41), ('Q13', 'B10', 43), ('Q14', 'B11', 44), ('Q30', 'E2', 107)]:
        s = t[(t['Pregunta'] == q) & (t['Tipo'] == 'simple')].groupby('Categoría')['n plataforma'].sum()
        tot = s.sum()
        r = df[col].value_counts()
        for cat, n in s.items():
            m = int(r.get(cat, 0))
            rows.append({'Pregunta': code, 'Categoría': cat.rstrip('.'), 'Plataforma n': int(n), 'Plataforma %': round(100 * n / tot, 1),
                         'Base exportada n': m, 'Base exportada %': round(100 * m / r.sum(), 1),
                         'Diferencia (pp)': round(100 * n / tot - 100 * m / r.sum(), 1)})
    return pd.DataFrame(rows)


def verification_summary():
    t = pd.read_pickle('/projects/sandbox/work/verify.pkl') if __import__('os').path.exists('/projects/sandbox/work/verify.pkl') else verify.run()
    ok = t[t['n base exportada'].notna()]
    s = ok.groupby('Universidad (enlace)').agg(Comparaciones=('Diferencia', 'size'), Coinciden=('Diferencia', lambda x: int((x == 0).sum())),
                                               Plataforma_mayor=('Diferencia', lambda x: int((x > 0).sum())),
                                               Base_mayor=('Diferencia', lambda x: int((x < 0).sum()))).reset_index()
    s.columns = ['Enlace', 'Celdas comparadas', 'Coinciden', 'Plataforma > base', 'Base > plataforma']
    per_q = ok[ok['Tipo'] == 'simple'].groupby(['Pregunta', 'Universidad (enlace)'])[['n plataforma', 'n base exportada']].sum()
    per_q['Diferencia'] = per_q['n plataforma'] - per_q['n base exportada']
    pq = per_q['Diferencia'].unstack().fillna(0).astype(int)
    pq = pq.loc[sorted(pq.index, key=lambda x: int(x[1:]))].reset_index()
    return s, pq


# ------------------------------------------------------------------ verificación de cifras publicadas
def claims():
    """Recalcula desde la hoja 'Datos sin procesar' (sin usar prep.py) las cifras citadas en los informes."""
    raw, H = load_raw()
    c = {k: i for i, k in enumerate(H)}
    col = lambda code: [i for i, h in enumerate(H) if h.startswith(f'[{code}]')]
    e2 = raw[107]
    fin = e2 == 'Fue financiada por Alianza 4U.'
    nf = e2.isin(['No fue financiada.', 'Fue declarada elegible, pero no recibió financiación.', 'Fue retirada o no llegó a completar el proceso.'])
    npo = e2.isna()
    lik = {'Nada': 1, 'En pequeña medida': 2, 'En medida moderada': 3, 'En gran medida': 4, 'Completamente': 5}

    def favp(ci, mask=None):
        s = raw[ci] if mask is None else raw.loc[mask, ci]
        v = s.map(lik).dropna()
        return round(100 * (v >= 4).mean(), 1)

    def p(mask_num, mask_den):
        return round(100 * mask_num.sum() / mask_den.sum(), 1)

    j1 = raw[282]
    out = [
        ('Registros analizados', 102, len(raw)),
        ('Financiados', 45, int(fin.sum())),
        ('Postularon, no financiados', 11, int(nf.sum())),
        ('No postularon', 45, int(npo.sum())),
        ('Tasa de éxito entre encuestados %', 80.4, round(100 * fin.sum() / (fin.sum() + nf.sum()), 1)),
        ('Profesores de planta %', 80.4, p(raw[35] == 'Profesor(a) de planta o tiempo completo.', raw[35].notna())),
        ('Más de 10 años de experiencia %', 75.5, p(raw[43].isin(['Entre 11 y 20 años.', 'Más de 20 años.']), raw[43].notna())),
        ('Dedican 40 % o menos %', 75.5, p(raw[44].isin(['Ninguna.', 'Entre 1% y 20%.', 'Entre 21% y 40%.']), raw[44].notna())),
        ('C3.3 carga permite (favorable %)', 26.3, favp(58)),
        ('C3.5 procedimientos facilitan (favorable %)', 33.3, favp(60)),
        ('C1.2 confía en calidad (favorable %)', 94.9, favp(47)),
        ('Índice C1 (media)', 4.41, round(raw[list(range(46, 52))].apply(lambda s: s.map(lik)).mean(axis=1).mean(), 2)),
        ('Índice C3 (media)', 3.36, round(raw[list(range(56, 62))].apply(lambda s: s.map(lik)).mean(axis=1).mean(), 2)),
        ('Había escuchado de 4U %', 95.0, p(raw[70] == 'Sí.', raw[70].notna())),
        ('Sin proyectos interinst. antes de 2021 %', 41.6, p(raw[104] == 'Ninguno.', raw[104].notna())),
        ('E4.1 objetivos claros (favorable %)', 94.4, favp(110)),
        ('E4.3 tiempo suficiente (favorable %)', 54.7, favp(112)),
        ('Retroalimentación detallada %', 12.3, p(raw[124] == 'Sí, suficientemente detallada.', raw[124].notna())),
        ('Pudo opinar sobre la convocatoria (postulantes) %', 6.7, p((raw[126] == 'Sí.') & e2.notna(), raw[126].notna() & e2.notna())),
        ('F7 beneficios > dificultades (financiados) %', 58.1, p(raw.loc[fin, 166].isin(['Los beneficios fueron superiores a las dificultades.', 'Los beneficios fueron muy superiores a las dificultades.']), raw.loc[fin, 166].notna())),
        ('F6 esfuerzo mayor (financiados) %', 53.5, p(raw.loc[fin, 165].isin(['Mayor.', 'Mucho mayor.']), raw.loc[fin, 165].notna())),
        ('H1 artículos completados (financiados) %', 38.1, p(raw.loc[fin, 184] == 'Completado', raw.loc[fin, 184].notna())),
        ('H1 artículos en desarrollo (financiados) %', 54.8, p(raw.loc[fin, 184] == 'En desarrollo', raw.loc[fin, 184].notna())),
        ('H2 artículos conjuntos (financiados) %', 90.5, p(raw.loc[fin, 193].notna(), raw.loc[fin, list(range(193, 203))].notna().any(axis=1))),
        ('I5 sin 4U no se habría realizado %', 47.6, p(raw.loc[fin, 265] == 'Probablemente el proyecto no se habría realizado.', raw.loc[fin, 265].notna())),
        ('I6 financiación atribuida a 4U %', 92.9, p(raw.loc[fin, 270].notna(), raw.loc[fin, list(range(266, 278))].notna().any(axis=1))),
        ('H5 uso por entidades públicas %', 2.9, p(raw.loc[fin, 219] == 'Ha utilizado o incorporado algún resultado', raw.loc[fin, 219].isin(['No hubo interacción', 'Recibió información sobre los resultados', 'Entregó comentarios o participó en discusiones', 'Participó en el diseño, producción o validación', 'Ha utilizado o incorporado algún resultado']))),
        ('J1 probable/muy probable %', 64.3, p(j1.isin(['Probable.', 'Muy probable.']), j1.notna())),
        ('J1 financiados probable/muy probable %', 72.1, p(raw.loc[fin, 282].isin(['Probable.', 'Muy probable.']), raw.loc[fin, 282].notna())),
        ('J4 falta de tiempo %', 76.5, p(raw[295].notna(), raw[list(range(295, 310))].notna().any(axis=1))),
        ('J5 identificar socios %', 51.5, p(raw[311].notna(), raw[list(range(310, 321))].notna().any(axis=1))),
        ('J5 armonizar procedimientos %', 41.2, p(raw[314].notna(), raw[list(range(310, 321))].notna().any(axis=1))),
        ('J7 autoriza contacto %', 76.5, p(raw[322] == 'Sí.', raw[322].notna())),
        ('Financiados: D5 n.º otras universidades 4U (media)', 1.87, round(df.loc[fin_mask, 'D5_n_socios_4U_otras'].mean(), 2)),
        ('No postulantes: D5 n.º otras universidades 4U (media)', 0.49, round(df.loc[df['Grupo'] == 'No postuló', 'D5_n_socios_4U_otras'].mean(), 2)),
        ('E9 no financiados: equipo dejó de trabajar (n)', 5, int(raw.loc[nf, 132].notna().sum())),
        ('Postulantes sin experiencia previa financiados (n de 20)', 18, int((fin & (raw[104] == 'Ninguno.')).sum())),
    ]
    t = pd.DataFrame(out, columns=['Cifra citada en el informe', 'Valor en el informe', 'Recalculado desde los datos crudos'])
    t['Coincide'] = np.where(np.isclose(t['Valor en el informe'].astype(float), t['Recalculado desde los datos crudos'].astype(float), atol=0.051), 'Sí', 'REVISAR')
    return t


if __name__ == '__main__':
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 30)
    pd.set_option('display.max_colwidth', 50)
    print(claims().to_string())
    print(harmonized()[['Tema', 'Categoría', 'EAFIT %', 'Encuesta %', 'Encuesta n', 'Diferencia (pp)']].to_string())
    print(coverage().to_string())
    a, b = weighted_indicators()
    print(a.to_string()); print(b.to_string())
