"""Cálculo de todas las tablas estadísticas a partir de prep.df."""
import re
import numpy as np
import pandas as pd
from scipy import stats
from prep import *
from load import FILES

G3 = GROUPS  # Financiado, Postuló no financiado, No postuló
SEXOS = ['Mujer', 'Hombre']
EXPS = ['≤10 años', '11-20 años', '>20 años']


def pct(a, b):
    return np.nan if not b else 100.0 * a / b


# ---------------------------------------------------------------- respuesta única
def single_table(code, col, by=None, pop='todos', order=None):
    m = pop_mask(pop)
    d = df[m]
    cats = list(order or SINGLE_ORDER.get(code, []))
    for v in d[col].dropna().unique():
        if v not in cats:
            cats.append(v)
    cats = [c for c in cats if (d[col] == c).any()]
    rows = []
    groups = [('Total', d)]
    if by == 'Grupo':
        groups += [(g, d[d['Grupo'] == g]) for g in G3]
    elif by == 'Universidad':
        groups += [(u, d[d['Universidad'] == u]) for u in UNIS]
    elif by == 'Sexo':
        groups += [(s, d[d['Sexo (estimado)'] == s]) for s in SEXOS]
    elif by == 'Experiencia':
        groups += [(s, d[d['Experiencia (agrupada)'] == s]) for s in EXPS]
    for c in cats:
        r = {'Categoría': str(c).rstrip('.')}
        for g, sub in groups:
            n = sub[col].notna().sum()
            k = (sub[col] == c).sum()
            r[f'{g} n'] = int(k)
            r[f'{g} %'] = round(pct(k, n), 1)
        rows.append(r)
    r = {'Categoría': 'Total respuestas válidas'}
    for g, sub in groups:
        r[f'{g} n'] = int(sub[col].notna().sum())
        r[f'{g} %'] = 100.0 if sub[col].notna().sum() else np.nan
    rows.append(r)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- matrices Likert
def item_stats(series, scale):
    s = series.dropna()
    v = s.map(SCALES[scale]).dropna() if scale in SCALES else pd.Series(dtype=float)
    out = {'Respuestas': int(len(s)), 'n válido (escala)': int(len(v)),
           'NS/NA/NR': int(len(s) - len(v))}
    if scale == 'h1':
        out['n válido (escala)'] = int((s != 'No tengo información.').sum())
        out['NS/NA/NR'] = int((s == 'No tengo información.').sum())
    if scale in SCALES and scale not in ('cant', 'h5'):
        out.update({'Media (1-5)': round(v.mean(), 2) if len(v) else np.nan,
                    'Desv. est.': round(v.std(), 2) if len(v) > 1 else np.nan,
                    'Mediana': v.median() if len(v) else np.nan,
                    '% favorable (4-5)': round(pct((v >= 4).sum(), len(v)), 1),
                    '% desfavorable (1-2)': round(pct((v <= 2).sum(), len(v)), 1)})
    elif scale == 'cant':
        out.update({'Media aprox. (n.º)': round(v.mean(), 2) if len(v) else np.nan,
                    'Total estimado (n.º)': round(v.sum(), 0),
                    '% con al menos una': round(pct((v > 0).sum(), len(v)), 1),
                    '% con 4 o más': round(pct((v >= 4).sum(), len(v)), 1)})
    elif scale == 'h5':
        out.update({'Nivel medio (0-4)': round(v.mean(), 2) if len(v) else np.nan,
                    '% con alguna interacción': round(pct((v >= 1).sum(), len(v)), 1),
                    '% con participación activa (≥3)': round(pct((v >= 3).sum(), len(v)), 1),
                    '% uso efectivo (4)': round(pct((v == 4).sum(), len(v)), 1)})
    if scale == 'h1':
        out.update({'% completado': round(pct((s == 'Completado').sum(), len(s)), 1),
                    '% en desarrollo': round(pct((s == 'En desarrollo').sum(), len(s)), 1),
                    '% previsto (cualquier estado)': round(pct(s.isin(['Previsto, pero no iniciado', 'En desarrollo', 'Completado']).sum(), len(s)), 1),
                    'n completados': int((s == 'Completado').sum())})
    return out


def matrix_overall():
    rows = []
    for code, title, cols, sc, pop in MATRIX:
        d = df[pop_mask(pop)]
        for j, c in enumerate(cols):
            r = {'Bloque': code, 'Tema': title, 'Ítem': f'{code}.{j + 1}', 'Enunciado': item_label(c),
                 'Población': pop}
            r.update(item_stats(d[c], sc))
            rows.append(r)
    return pd.DataFrame(rows)


def matrix_dist():
    rows = []
    for code, title, cols, sc, pop in MATRIX:
        d = df[pop_mask(pop)]
        for j, c in enumerate(cols):
            s = d[c].dropna()
            r = {'Bloque': code, 'Ítem': f'{code}.{j + 1}', 'Enunciado': item_label(c), 'n': len(s)}
            for cat in ORD[sc]:
                k = (s == cat).sum()
                r[f'{cat} (n)'] = int(k)
            for cat in ORD[sc]:
                r[f'{cat} (%)'] = round(pct((s == cat).sum(), len(s)), 1)
            rows.append((sc, r))
    out = {}
    for sc, r in rows:
        out.setdefault(sc, []).append(r)
    return {k: pd.DataFrame(v) for k, v in out.items()}


def matrix_by(dim):
    if dim == 'Grupo':
        levels, key = G3, 'Grupo'
    elif dim == 'Universidad':
        levels, key = UNIS, 'Universidad'
    elif dim == 'Sexo':
        levels, key = SEXOS, 'Sexo (estimado)'
    else:
        levels, key = EXPS, 'Experiencia (agrupada)'
    rows = []
    for code, title, cols, sc, pop in MATRIX:
        if sc in ('h1',):
            continue
        if dim == 'Grupo' and pop == 'financiados':
            continue
        d = df[pop_mask(pop)]
        for j, c in enumerate(cols):
            name = f'{code}_{j + 1}'
            r = {'Bloque': code, 'Ítem': f'{code}.{j + 1}', 'Enunciado': item_label(c)}
            samples = []
            for lv in levels:
                v = d.loc[d[key] == lv, name].dropna()
                r[f'{lv} n'] = len(v)
                r[f'{lv} media'] = round(v.mean(), 2) if len(v) else np.nan
                if sc == 'cant':
                    r[f'{lv} % ≥1'] = round(pct((v > 0).sum(), len(v)), 1)
                elif sc == 'h5':
                    r[f'{lv} % uso'] = round(pct((v == 4).sum(), len(v)), 1)
                else:
                    r[f'{lv} % 4-5'] = round(pct((v >= 4).sum(), len(v)), 1)
                if len(v) >= 3:
                    samples.append(v)
            r.update(test_groups(samples))
            rows.append(r)
    return pd.DataFrame(rows)


def test_groups(samples):
    out = {'Prueba': '', 'Estadístico': np.nan, 'p-valor': np.nan, 'Significativo (p<0,05)': ''}
    if len(samples) < 2:
        return out
    try:
        if len(samples) == 2:
            st, p = stats.mannwhitneyu(samples[0], samples[1], alternative='two-sided')
            out['Prueba'] = 'Mann-Whitney U'
        else:
            st, p = stats.kruskal(*samples)
            out['Prueba'] = 'Kruskal-Wallis H'
        out['Estadístico'] = round(float(st), 3)
        out['p-valor'] = round(float(p), 4)
        out['Significativo (p<0,05)'] = 'Sí' if p < 0.05 else ('Tendencia (p<0,10)' if p < 0.10 else 'No')
    except ValueError:
        pass
    return out


# ---------------------------------------------------------------- índices
def cronbach(items):
    x = df[items].dropna()
    k = len(items)
    if len(x) < 3 or k < 2:
        return np.nan, len(x)
    var_sum = x.var(axis=0, ddof=1).sum()
    tot = x.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - var_sum / tot) if tot else np.nan, len(x)


def index_table():
    rows = []
    for code, (title, items) in INDEX.items():
        pop = [m[4] for m in MATRIX if m[0] == code][0]
        d = df[pop_mask(pop)]
        v = d[f'IDX_{code}'].dropna()
        a, nc = cronbach(items)
        r = {'Índice': f'IDX_{code}', 'Dimensión': title, 'Población': pop, 'N.º ítems': len(items),
             'n': len(v), 'Media': round(v.mean(), 2), 'Desv. est.': round(v.std(), 2), 'Mínimo': round(v.min(), 2),
             'P25': round(v.quantile(.25), 2), 'Mediana': round(v.median(), 2), 'P75': round(v.quantile(.75), 2),
             'Máximo': round(v.max(), 2), '% índice ≥4': round(pct((v >= 4).sum(), len(v)), 1),
             'Alfa de Cronbach': round(a, 3) if pd.notna(a) else np.nan, 'n casos completos (alfa)': nc}
        rows.append(r)
    return pd.DataFrame(rows)


def index_by(dim):
    levels, key = {'Grupo': (G3, 'Grupo'), 'Universidad': (UNIS, 'Universidad'),
                   'Sexo': (SEXOS, 'Sexo (estimado)'), 'Experiencia': (EXPS, 'Experiencia (agrupada)'),
                   'Rango': (['Auxiliar', 'Asistente', 'Asociado', 'Titular', 'Otro / sin rango'], 'Rango (agrupado)')}[dim]
    rows = []
    for code, (title, items) in INDEX.items():
        pop = [m[4] for m in MATRIX if m[0] == code][0]
        if dim == 'Grupo' and pop == 'financiados':
            continue
        d = df[pop_mask(pop)]
        r = {'Índice': f'IDX_{code}', 'Dimensión': title}
        samples = []
        for lv in levels:
            v = d.loc[d[key] == lv, f'IDX_{code}'].dropna()
            r[f'{lv} n'] = len(v)
            r[f'{lv} media'] = round(v.mean(), 2) if len(v) else np.nan
            if len(v) >= 3:
                samples.append(v)
        r.update(test_groups(samples))
        rows.append(r)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- selección múltiple
def multi_table(code, title, cols, pop, by=None):
    d = df[pop_mask(pop)]
    answered = d[list(cols)].notna().any(axis=1)
    d = d[answered]
    levels = []
    if by == 'Grupo':
        levels = G3
        key = 'Grupo'
    elif by == 'Universidad':
        levels = UNIS
        key = 'Universidad'
    elif by == 'Sexo':
        levels, key = SEXOS, 'Sexo (estimado)'
    rows = []
    for c in cols:
        lab = item_label(c).rstrip('.')
        if re.match(r'^Otr[ao]\.?\s*¿', lab):
            lab = 'Otra'
        r = {'Opción': lab, 'Total n': int(d[c].notna().sum()), 'Total %': round(pct(d[c].notna().sum(), len(d)), 1)}
        for lv in levels:
            sub = d[d[key] == lv]
            r[f'{lv} n'] = int(sub[c].notna().sum())
            r[f'{lv} %'] = round(pct(sub[c].notna().sum(), len(sub)), 1)
        rows.append(r)
    r = {'Opción': 'Base (personas que respondieron)', 'Total n': len(d), 'Total %': 100.0}
    for lv in levels:
        r[f'{lv} n'] = int((d[key] == lv).sum())
        r[f'{lv} %'] = 100.0
    rows.append(r)
    t = pd.DataFrame(rows)
    body = t.iloc[:-1].sort_values('Total n', ascending=False)
    return pd.concat([body, t.iloc[[-1]]], ignore_index=True)


# ---------------------------------------------------------------- pruebas de asociación categórica
def cramers_v(ct):
    chi2, p, dof, exp = stats.chi2_contingency(ct)
    n = ct.values.sum()
    r, k = ct.shape
    v = np.sqrt(chi2 / (n * (min(r, k) - 1))) if min(r, k) > 1 else np.nan
    low = (exp < 5).mean() * 100
    return chi2, p, dof, v, low


def assoc_table():
    vars_ = [('Universidad', 'Universidad'), ('Sexo (estimado)', 'Sexo (estimado)'), ('B6 Tipo de vinculación', 35),
             ('B7 Función principal', 37), ('Rango (agrupado)', 'Rango (agrupado)'), ('B9 Área de conocimiento', 41),
             ('Experiencia (agrupada)', 'Experiencia (agrupada)'), ('B11 Dedicación a investigación', 44),
             ('D2 Conocimiento de Alianza 4U', 71), ('D8 Proyectos interinstitucionales antes de 2021', 104),
             ('J1 Prob. de participar', 282), ('J2 Prob. de liderar', 283)]
    rows = []
    for against_lab, filt in [('Grupo (3 categorías)', df['Grupo'].isin(G3)),
                              ('Financiado vs. resto', pd.Series(True, index=df.index))]:
        for lab, col in vars_:
            d = df[filt]
            y = d['Grupo'] if against_lab.startswith('Grupo') else np.where(d['Grupo'] == 'Financiado', 'Financiado', 'Resto')
            ct = pd.crosstab(d[col], y)
            if ct.shape[0] < 2 or ct.shape[1] < 2:
                continue
            chi2, p, dof, v, low = cramers_v(ct)
            try:
                if ct.shape == (2, 2):
                    _, pf = stats.fisher_exact(ct.values)
                else:
                    pf = np.nan
            except Exception:
                pf = np.nan
            rows.append({'Variable': lab, 'Contra': against_lab, 'n': int(ct.values.sum()), 'Chi²': round(chi2, 3),
                         'gl': dof, 'p-valor (chi²)': round(p, 4), 'p exacto Fisher (2x2)': round(pf, 4) if pd.notna(pf) else '',
                         'V de Cramér': round(v, 3), '% celdas esperadas <5': round(low, 1),
                         'Lectura': ('Asociación significativa' if p < 0.05 else 'Tendencia' if p < 0.10 else 'Sin asociación significativa')
                         + (' (interpretar con cautela: muchas celdas pequeñas)' if low > 20 else '')})
    return pd.DataFrame(rows)


def success_rate():
    post = df[df['Grupo'].isin(['Financiado', 'Postuló, no financiado'])]
    rows = []
    for lab, key, levels in [('Universidad', 'Universidad', UNIS), ('Sexo (estimado)', 'Sexo (estimado)', SEXOS),
                             ('Experiencia', 'Experiencia (agrupada)', EXPS),
                             ('Rango', 'Rango (agrupado)', ['Auxiliar', 'Asistente', 'Asociado', 'Titular', 'Otro / sin rango']),
                             ('Área de conocimiento', 41, sorted(post[41].dropna().unique())),
                             ('Rol en la propuesta (E3)', 108, sorted(post[108].dropna().unique())),
                             ('Participación en la postulación (E1)', 106, sorted(post[106].dropna().unique())),
                             ('Proyectos interinst. antes de 2021 (D8)', 104, SINGLE_ORDER['D8'])]:
        for lv in levels:
            sub = post[post[key] == lv]
            if len(sub) == 0:
                continue
            f = (sub['Grupo'] == 'Financiado').sum()
            rows.append({'Variable': lab, 'Categoría': str(lv).rstrip('.'), 'Postulantes': len(sub), 'Financiados': int(f),
                         'No financiados': int(len(sub) - f), 'Tasa de éxito %': round(pct(f, len(sub)), 1)})
    f = (post['Grupo'] == 'Financiado').sum()
    rows.append({'Variable': 'TOTAL', 'Categoría': 'Todos los postulantes con resultado conocido', 'Postulantes': len(post),
                 'Financiados': int(f), 'No financiados': int(len(post) - f), 'Tasa de éxito %': round(pct(f, len(post)), 1)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- correlaciones
CORR_VARS = {'Experiencia (años aprox.)': 'Experiencia_años_aprox', 'Dedicación a investigación (% aprox.)': 'Dedicación_inv_pct_aprox',
             'Conocimiento de Alianza 4U (D2)': 'D2_num', 'Proyectos interinst. antes de 2021 (D8)': 'D8_num',
             'N.º instituciones con las que colabora (D5)': 'D5_n_instituciones',
             'N.º actividades interinst. (D6)': 'D6_n_actividades',
             'Experiencias interinst. desde 2021 (D7 total)': 'D7_total_experiencias_aprox',
             'IDX C1 Disposición': 'IDX_C1', 'IDX C2 Valor percibido': 'IDX_C2', 'IDX C3 Condiciones institucionales': 'IDX_C3',
             'IDX C4 Cambio en capacidades': 'IDX_C4', 'J1 Prob. participar': 'J1_num', 'J2 Prob. liderar': 'J2_num',
             'Financiado (1/0)': 'FIN'}


def corr_table():
    d = df.copy()
    d['FIN'] = (d['Grupo'] == 'Financiado').astype(int)
    cols = list(CORR_VARS.values())
    names = list(CORR_VARS)
    rho = pd.DataFrame(index=names, columns=names, dtype=float)
    pv = pd.DataFrame(index=names, columns=names, dtype=float)
    for i, a in enumerate(cols):
        for j, b in enumerate(cols):
            if i == j:
                rho.iat[i, j] = 1.0
                continue
            x = d[[a, b]].dropna()
            if len(x) > 5 and x[a].nunique() > 1 and x[b].nunique() > 1:
                r, p = stats.spearmanr(x[a], x[b])
                rho.iat[i, j] = round(r, 3)
                pv.iat[i, j] = round(p, 4)
    return rho, pv


def corr_fin():
    """Correlaciones en financiados: índices de gobernanza vs resultados."""
    d = df[df['Grupo'] == 'Financiado']
    v = {'IDX F2 Decisiones': 'IDX_F2', 'IDX F3 Coordinación': 'IDX_F3', 'IDX F4 Relaciones': 'IDX_F4',
         'IDX F5 Consolidación': 'IDX_F5', 'IDX G1 Cap. científicas': 'IDX_G1', 'IDX G2 Cap. institucionales': 'IDX_G2',
         'IDX G3 Aprendizaje': 'IDX_G3', 'IDX H3 Valor productos': 'IDX_H3', 'IDX I1 Contribuciones': 'IDX_I1',
         'F6 Esfuerzo coordinación': 'F6_num', 'F7 Balance': 'F7_num', 'I4 Continuidad': 'I4_num',
         'H1 N.º tipos de producto completados': 'H1_n_completados', 'J1 Prob. participar': 'J1_num',
         'Experiencia (años aprox.)': 'Experiencia_años_aprox'}
    names, cols = list(v), list(v.values())
    rho = pd.DataFrame(index=names, columns=names, dtype=float)
    pv = pd.DataFrame(index=names, columns=names, dtype=float)
    for i, a in enumerate(cols):
        for j, b in enumerate(cols):
            if i == j:
                rho.iat[i, j] = 1.0
                continue
            x = d[[a, b]].dropna()
            if len(x) > 5 and x[a].nunique() > 1 and x[b].nunique() > 1:
                r, p = stats.spearmanr(x[a], x[b])
                rho.iat[i, j] = round(r, 3)
                pv.iat[i, j] = round(p, 4)
    return rho, pv


# ---------------------------------------------------------------- producción / productos
def production_table():
    rows = []
    for lab, col in [('D5 N.º de tipos de institución con que colaboró', 'D5_n_instituciones'),
                     ('D5 N.º de otras universidades 4U con que colaboró', 'D5_n_socios_4U_otras'),
                     ('D6 N.º de tipos de actividad interinstitucional', 'D6_n_actividades'),
                     ('D7 Experiencias interinst. desde 2021 (suma aprox.)', 'D7_total_experiencias_aprox'),
                     ('D7.1 Propuestas con otra universidad (aprox.)', 'D7_1'),
                     ('D7.2 Proyectos ejecutados con otra universidad (aprox.)', 'D7_2'),
                     ('D7.3 Productos con otra universidad (aprox.)', 'D7_3'),
                     ('D7.4 Iniciativas con actores externos (aprox.)', 'D7_4'),
                     ('D7.5 Relaciones nuevas activas (aprox.)', 'D7_5'),
                     ('D8 Proyectos interinst. antes de 2021 (aprox.)', 'D8_num'),
                     ('Experiencia investigativa (años aprox.)', 'Experiencia_años_aprox'),
                     ('Dedicación a investigación (% aprox.)', 'Dedicación_inv_pct_aprox')]:
        r = {'Indicador': lab}
        samples = []
        for g in ['Total'] + G3:
            sub = df if g == 'Total' else df[df['Grupo'] == g]
            v = sub[col].dropna()
            r[f'{g} n'] = len(v)
            r[f'{g} media'] = round(v.mean(), 2) if len(v) else np.nan
            r[f'{g} mediana'] = v.median() if len(v) else np.nan
            if g != 'Total' and len(v) >= 3:
                samples.append(v)
        r.update(test_groups(samples))
        rows.append(r)
    return pd.DataFrame(rows)


def production_fin():
    d = df[df['Grupo'] == 'Financiado']
    rows = []
    for lab, col in [('H1 Tipos de producto completados por proyecto', 'H1_n_completados'),
                     ('H1 Tipos de producto en desarrollo', 'H1_n_en_desarrollo'),
                     ('H1 Tipos de producto previstos', 'H1_n_previstos'),
                     ('H2 Tipos de producto conjuntos (≥2 universidades)', 'H2_n_tipos_conjuntos'),
                     ('H4 N.º de mecanismos de movilización', 'H4_n_mecanismos')]:
        r = {'Indicador': lab}
        for u in ['Total'] + UNIS:
            sub = d if u == 'Total' else d[d['Universidad'] == u]
            ok = sub[list(range(184, 193))].notna().any(axis=1)
            v = sub.loc[ok, col]
            r[f'{u} n'] = len(v)
            r[f'{u} media'] = round(v.mean(), 2) if len(v) else np.nan
            r[f'{u} suma'] = int(v.sum()) if len(v) else 0
        rows.append(r)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- texto abierto
THEMES_J6 = {
    'Simplificar y armonizar procesos administrativos': r'administrativ|proceso|firma|unific|simplific|burocr|facilidad administrativa',
    'Tiempo y carga académica (descargas)': r'carga|descarga|tiempo|docencia|facilidad de personal',
    'Identificar socios y conocer perfiles / red de investigadores': r'perfil|socio|red |redes|match|identific|plataforma|encuentro|mesas|dossier|emparejamiento|combinar capacidades|conozcan|conocer que tiene|intercambio de info',
    'Ampliar temas, áreas e interdisciplinariedad': r'tema|línea|lineas|áreas|areas|artes|ejes|diversidad|interdisciplin|restringir|otras universidades',
    'Más recursos y autonomía presupuestal': r'presupuesto|recursos|fondos|financ',
    'Difusión y comunicación de oportunidades': r'divulga|difusi|comunicaci|información|informacón',
    'Incentivos y reconocimiento institucional': r'incentiv|reconocimiento',
    'Diseño de convocatorias (calendario, claridad, exigencias)': r'calendario|fechas|retroalimentaci|claridad|estrategia|sencill|artículos|productos de investigación',
    'Gestión del proyecto (dirección, roles, control)': r'director|responsabilidad|control de gastos|comprometid|espacio ejecutivo|confianza',
}
THEMES_I8 = {
    'Publicaciones científicas': r'public|artícul|articul|capítulo|capitulo|citacion|libro|conferenc|ponencia|congreso',
    'Comparación entre regiones, ciudades o universidades': r'compar|regiones|ciudades|tres universidades|3 universidades|cuatro ciudades|cada una de las universidades|distintas instituciones',
    'Colaboración, redes e integración interinstitucional': r'colabora|red |articulaci|interinstitucional|integraci|interdisciplin|grupo',
    'Incidencia en políticas públicas y decisiones': r'polític|decisiones|hoja de ruta|instancias',
    'Formación de estudiantes e investigadores': r'estudiante|tesis|posgrado|maestr|doctor|postdoctoral|formativ',
    'Desarrollos tecnológicos, datos y herramientas': r'prototipo|software|base de datos|página web|pagina web|sistema|rag|\bia\b|plataforma|juego|instrumento|metodolog',
    'Divulgación y apropiación social': r'divulga|apropiaci|radial|exposici|audiovisual|periodíst',
    'Impacto en comunidades o actores externos': r'comunidad|vulnerable|sociedad civil|empresas|discapacidad',
    'Financiación adicional o nuevos proyectos': r'financiación externa|otro proyecto|otra propuesta|nuevo proyecto|financiación interna',
    'Hallazgos científicos o técnicos específicos': r'proteínas|cemento|heterogeneidad|socioemocional|valor científico|hallazgo|eficacia|diferencias de género|exclusión de mujeres|amoníaco|bioeconom|autoexplicaciones|conocimiento',
    'Aún sin resultados verificables': r'todavía no|aún no|no es posible',
}
THEMES_I7 = {
    'Nuevas conexiones, colaboraciones y proyectos': r'integración de capacidades|conexi|colabora|alianza|relacion|nuevo proyecto|nuevas investig|oportunidades|conocí|conocer|cooperación|ideas',
    'Hallazgos o productos no previstos': r'plataforma|rag|estación|página web|caracterizaci|evaluación|chatbot|análisis|metodolog|programa',
    'Impacto social / con organizaciones': r'comunidad|sociedad civil|gubernamental|empresarial|mujeres',
    'Dificultades o efectos negativos': r'no fue posible|termino|exclusión|no se considero',
}
NAMES_RE = re.compile(r'(Nicolas Pita|Alexander Villarraga Orjuela|José Luis de la Hoz|Dario\b|Prof\. [A-Z][a-z]+ [A-Z][a-z]+)')


def anonymize(t):
    t = NAMES_RE.sub('[nombre omitido]', str(t))
    t = re.sub(r'user=[\w-]+', 'user=[omitido]', t)
    return t


def code_text(col, themes):
    d = df[df[col].notna()]
    d = d[~d[col].astype(str).str.strip().isin(['.', 'si', 'Otro. ¿Cuál?', 'Otra. ¿Cuál?'])]
    rows, quotes = [], []
    for _, r in d.iterrows():
        t = str(r[col]).lower()
        hits = [k for k, pat in themes.items() if re.search(pat, t)]
        quotes.append({'ID': r['ID'], 'Universidad': r['Universidad'], 'Grupo': r['Grupo'],
                       'Temas': '; '.join(hits) if hits else 'Otro / sin clasificar', 'Texto (anonimizado)': anonymize(r[col])})
    q = pd.DataFrame(quotes)
    for k in list(themes) + ['Otro / sin clasificar']:
        m = q['Temas'].str.contains(re.escape(k)) if len(q) else pd.Series(dtype=bool)
        rows.append({'Tema': k, 'Menciones': int(m.sum()), '% de respuestas': round(pct(m.sum(), len(q)), 1),
                     'Financiados': int((m & (q['Grupo'] == 'Financiado')).sum()),
                     'No financiados / no postularon': int((m & (q['Grupo'] != 'Financiado')).sum())})
    t = pd.DataFrame(rows).sort_values('Menciones', ascending=False)
    t = pd.concat([t, pd.DataFrame([{'Tema': 'Base: respuestas con contenido', 'Menciones': len(q), '% de respuestas': 100.0}])])
    return t, q


# ---------------------------------------------------------------- participación
def participation():
    rows = []
    for k, f in FILES.items():
        g = pd.read_excel(f, sheet_name='Estadísticas generales', header=None)
        vals = {str(a).strip(): b for a, b in g.iloc[4:8, :2].values}
        sub = df[df['Encuesta'] == k]
        rows.append({'Encuesta (enlace)': k, 'Respuestas totales (plataforma)': int(vals.get('Total Responses', 0)),
                     'Terminadas (plataforma)': int(vals.get('Terminado', 0)),
                     'Incompletas (plataforma)': int(vals.get('Incompletes', 0)),
                     'Tasa de finalización % (plataforma)': round(100 * float(g.iat[4, 2]), 1),
                     'Registros en base exportada': len(sub),
                     'Completos en base': int((sub[1] == 'Completed').sum()),
                     'Parciales en base': int((sub[1] == 'Started').sum()),
                     'Primera respuesta': pd.to_datetime(sub[3]).min().strftime('%Y-%m-%d'),
                     'Última respuesta': pd.to_datetime(sub[3]).max().strftime('%Y-%m-%d'),
                     'Mediana duración (min)': round(sub[5].astype(float).median() / 60, 1)})
    t = pd.DataFrame(rows)
    tot = t.sum(numeric_only=True)
    tot['Encuesta (enlace)'] = 'TOTAL'
    tot['Tasa de finalización % (plataforma)'] = round(100 * tot['Terminadas (plataforma)'] / tot['Respuestas totales (plataforma)'], 1)
    tot['Primera respuesta'] = pd.to_datetime(df[3]).min().strftime('%Y-%m-%d')
    tot['Última respuesta'] = pd.to_datetime(df[3]).max().strftime('%Y-%m-%d')
    tot['Mediana duración (min)'] = round(df[5].astype(float).median() / 60, 1)
    return pd.concat([t, pd.DataFrame([tot])], ignore_index=True)


def anonymized_base():
    keep = {'ID': 'ID', 'Encuesta': 'Encuesta (enlace)', 'Universidad': 'Universidad (B4)', 'Vinculado_4U': 'Vinculado a 4U',
            'Grupo': 'Grupo de vinculación', 'Sexo (estimado)': 'Sexo (estimado por nombre)', 1: 'Estado de respuesta',
            5: 'Duración (s)', 3: 'Fecha de respuesta', 'Experiencia_años_aprox': 'Experiencia (años aprox.)',
            'Dedicación_inv_pct_aprox': 'Dedicación inv. (% aprox.)', 'Rango (agrupado)': 'Rango (agrupado)'}
    out = pd.DataFrame({v: df[k] for k, v in keep.items()})
    skip = {0, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 45, 69,
            105, 142, 167, 183, 253, 281, 324, 1, 3, 5}
    cols = {}
    for c in range(len(H)):
        if c in skip:
            continue
        m = re.match(r'\[Q\d+\]\s*([A-Z]\d+b?)\.?', H[c])
        code = m.group(1) if m else f'col{c}'
        lab = item_label(c) if ' - ' in H[c] else re.sub(r'^\[Q\d+\]\s*', '', H[c])[:80]
        name = f'{code} | {lab[:70]}'
        while name in cols or name in out.columns:
            name += ' '
        s = df[c]
        if c in TEXT_COLS.values():
            s = s.map(lambda x: anonymize(x) if pd.notna(x) else x)
        cols[name] = s
    out = pd.concat([out, pd.DataFrame(cols)], axis=1)
    idx = [c for c in df.columns if isinstance(c, str) and (c.startswith('IDX_') or c.endswith('_num') or c.startswith(('D5_n', 'D6_n', 'D7_', 'H1_n', 'H2_n', 'H4_n', 'H8_', 'J4_n')))]
    out = pd.concat([out, df[idx].round(3)], axis=1)
    return out
