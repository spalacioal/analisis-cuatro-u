"""Análisis de subtexto: patrones de respuesta, brechas entre discurso y evidencia, red de socios,
concentración y contexto colombiano."""
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from charts import save, w, C_GRP
from extend import *

NS_VALUES = ['No tengo información suficiente', 'No aplica', 'Todavía no es observable', 'No tengo información.', 'No tengo información',
             'Todavía no es posible valorar', 'No recuerda']

# ------------------------------------------------------------------ contexto (fuentes en SOURCES)
CONTEXT = {
    'id_pib_col': 0.21, 'id_pib_ocde': 2.71,
    'minc_2023': 484961, 'minc_2024': 397875, 'minc_2025': 300000,
    'mujeres_inv_2021': 39.16, 'mujeres_inv_2024': 40.5,
    'monto_4u': 5512, 'proyectos_4u': 23, 'mediana_proy': 255.8,
}
SOURCES = [
    ('Convocatorias conjuntas Alianza 4U (EAFIT)', 'https://www.eafit.edu.co/sistema-ciencia-tecnologia-innovacion/investigacion/convocatorias/convocatorias-conjuntas'),
    ('Alianza 4U: valores compartidos (Icesi)', 'https://www.icesi.edu.co/alianza-4u/'),
    ('Memorando Alianza 4U – Purdue (La República, 2024)', 'https://www.larepublica.co/empresas/icesi-cesa-uninorte-y-eafit-se-aliaron-para-formar-la-universidad-en-red-mas-grande-3950301'),
    ('Inversión en I+D 0,21 % del PIB en 2022 frente a 2,71 % OCDE (Ámbito Jurídico, sobre CONPES 4145)', 'https://www.ambitojuridico.com/noticias/tecnologia/educacion-y-cultura/establecen-lineamientos-para-aumentar-inversion-en'),
    ('Recorte de MinCiencias 2023-2024 (El Tiempo)', 'https://www.eltiempo.com/vida/ciencia/vuelve-y-juega-gobierno-recortaria-un-36-a-los-recursos-de-la-ciencia-para-2025-3332243'),
    ('Presupuesto MinCiencias 2025 (El Espectador)', 'https://www.elespectador.com/ciencia/los-apuros-del-ministerio-de-ciencias-para-2025/'),
    ('Mujeres investigadoras reconocidas 39,16 % (2021) y 40,5 % (2024) (La República)', 'https://www.larepublica.co/analisis/yesenia-olaya-requene-4074989/minciencias-hace-justicia-con-las-mujeres-4089602'),
    ('Mujeres: 38 % de investigadores y menos del 30 % de líderes de grupo (El Colombiano)', 'https://www.elcolombiano.com/colombia/salud/colombia-mujeres-representan-38-por-cuento-poblacion-investigadora-minciencias-EM33486570'),
    ('Modelo de medición de grupos e investigadores (MinCiencias)', 'https://minciencias.gov.co/glosario/modelo-conceptual-del-reconocimiento-y-medicion-grupos-investigacion-y-reconocimiento'),
    ('Condiciones de trabajo de profesores universitarios colombianos (Romero, 2019, Acta Colombiana de Psicología)', 'https://actacolombianapsicologia.ucatolica.edu.co/article/download/1379/2702'),
    ('Bol, de Vaan y van de Rijt (2018). The Matthew effect in science funding. PNAS', 'https://www.pnas.org/content/115/19/4887.abstract'),
    ('Presentación "Informe de resultados Alianza 4U" (Oficina de inteligencia en CTeI, EAFIT, septiembre de 2026)', 'Archivo Presentacion_Alianza_4U_final_v3.pdf del repositorio'),
]


def context_table():
    c = CONTEXT
    return pd.DataFrame([
        ['Inversión en I+D de Colombia (% del PIB, 2022)', '0,21 %', 'Promedio OCDE: 2,71 %. Colombia invierte cerca de 13 veces menos.'],
        ['Presupuesto de MinCiencias 2023 → 2024 → 2025 (COP millones)', '484.961 → 397.875 → ~300.000', 'Caída de 38 % en dos años.'],
        ['Monto comparable Alianza 4U, 4 convocatorias (COP millones)', '5.512', f'Equivale a ~1,8 % del presupuesto anual de MinCiencias en 2025; ~0,5 % por año de convocatoria.'],
        ['Mediana por proyecto 4U (COP millones)', '255,8', 'Rango del programa 2021-2024: 50 a 200 millones según EAFIT.'],
        ['Mujeres entre investigadores reconocidos por MinCiencias', '39,2 % (2021) · 40,5 % (2024)', 'Entre aprobados 4U: 44,8 % (EAFIT); entre financiados encuestados: 56 %.'],
        ['Mujeres líderes de grupos de investigación (Colombia)', '< 30 %', 'Entre investigadores principales financiados encuestados: 9 de 17 son mujeres.'],
    ], columns=['Indicador de contexto', 'Valor', 'Lectura frente a la Alianza'])


# ------------------------------------------------------------------ patrones de respuesta
def straightlining():
    rows = []
    for code, title, cols, sc, pop in MATRIX:
        if sc in ('cant', 'h1', 'h5'):
            continue
        d = df[pop_mask(pop)][list(cols)].dropna(how='all')
        full = d.notna().sum(axis=1) == len(cols)
        sl = (d.nunique(axis=1) == 1) & full
        top = d[sl].iloc[:, 0].value_counts()
        idx = df.loc[d.index, f'IDX_{code}']
        rows.append({'Bloque': code, 'Tema': title, 'Personas': len(d), 'Misma respuesta en todos los ítems': int(sl.sum()),
                     '%': round(100 * sl.mean(), 1), 'Respuesta más repetida': top.index[0] if len(top) else '',
                     'Índice (todos)': round(idx.mean(), 2), 'Índice (sin respuestas uniformes)': round(idx[~sl].mean(), 2),
                     'Diferencia': round(idx[~sl].mean() - idx.mean(), 2)})
    return pd.DataFrame(rows)


def ns_rates():
    rows = []
    for code, title, cols, sc, pop in MATRIX:
        d = df[pop_mask(pop)][list(cols)]
        tot = d.notna().sum().sum()
        ns = d.isin(NS_VALUES).sum().sum()
        rows.append({'Bloque': code, 'Tema': title, 'Respuestas': int(tot), '"No sé / no aplica / no observable"': int(ns),
                     '%': round(100 * ns / tot, 1) if tot else np.nan})
    for code, col, lab in [('E6', 124, 'Retroalimentación'), ('E7', 126, 'Oportunidad de opinar')]:
        s = df.loc[df['Grupo'] != 'No postuló', col].dropna()
        rows.append({'Bloque': code, 'Tema': lab, 'Respuestas': len(s), '"No sé / no aplica / no observable"': int((s == 'No recuerda.').sum()),
                     '%': round(100 * (s == 'No recuerda.').mean(), 1)})
    return pd.DataFrame(rows).sort_values('%', ascending=False)


def duration_profile():
    d = df.copy()
    d['min'] = d[5].astype(float) / 60
    d['nivel'] = pd.cut(d['min'], [0, 10, 20, 40, 1e9], labels=['<10 min', '10-20 min', '20-40 min', '>40 min'])
    t = d.groupby('nivel').agg(Personas=('ID', 'size'), Disposición_C1=('IDX_C1', 'mean'), Condiciones_C3=('IDX_C3', 'mean'),
                               Palabras_J6=(321, lambda s: s.dropna().str.split().str.len().mean())).round(2).reset_index()
    t.columns = ['Duración', 'Personas', 'Índice C1', 'Índice C3', 'Palabras promedio en J6']
    return t


# ------------------------------------------------------------------ brechas discurso / evidencia
def gaps():
    f = df[df['Grupo'] == 'Financiado']
    h3 = f['IDX_H3']
    noev = f[249].notna() | f[250].notna()
    rows = [
        ('Disposición a colaborar (C1 favorable, promedio de ítems)', c_fav_avg('C1'), 'Condiciones institucionales (C3 favorable, promedio de ítems)', c_fav_avg('C3'), 'Todos'),
        ('Se siente preparado para participar en equipos (C1.5)', 92.9, 'Probable volver a colaborar en 2 años (J1)', 64.3, 'Todos'),
        ('Productos de calidad alta o muy alta (H3.1)', 97.5, 'Con evidencia verificable de uso (H8)', 61.9, 'Financiados'),
        ('Pertinencia de productos para Alianza 4U (H3.3)', 94.9, 'Algún actor externo usó un resultado (H5)', round(100 * (f[['H5_3', 'H5_4', 'H5_5', 'H5_6']] == 4).any(axis=1).sum() / f['H5_1'].notna().sum(), 1), 'Financiados'),
        ('Artículos completados según la encuesta (H1)', 38.1, 'Artículos finalizados o sometidos según EAFIT', 60.9, 'Financiados / proyectos'),
        ('Proyecto con estado conocido según la encuesta (F1)', 97.7, 'Proyecto con cierre o estado verificable según EAFIT', 73.9, 'Financiados / proyectos'),
        ('Gobernanza: se sabía quién decidía (F2.2)', 90.7, 'Proyecto con procedimientos institucionales y no solo acuerdos personales (F5.1)', 65.9, 'Financiados'),
    ]
    t = pd.DataFrame(rows, columns=['Lo que se declara', '% A', 'Lo que se evidencia', '% B', 'Base'])
    t['Brecha (pp)'] = (t['% A'] - t['% B']).round(1)
    extra = {'Financiados que valoran sus productos con 4 o más (H3) y a la vez no tienen evidencia o no saben (H8)': f'{int(((h3 >= 4) & noev).sum())} de {int(h3.notna().sum())}'}
    return t, extra


def c_fav_avg(code):
    m = [x for x in MATRIX if x[0] == code][0]
    return round(np.mean([100 * (df[f'{code}_{j + 1}'] >= 4).sum() / df[f'{code}_{j + 1}'].notna().sum() for j in range(len(m[2]))]), 1)


# ------------------------------------------------------------------ red de socios
def partner_matrix():
    four = {'CESA': 81, 'EAFIT': 82, 'ICESI': 83, 'Uninorte': 84}
    sub = df[df['Vinculado_4U'] == 'Sí']
    m = pd.DataFrame({p: [round(100 * sub.loc[sub['Universidad'] == u, four[p]].notna().mean(), 0) for u in UNIS] for p in four}, index=UNIS)
    m.index.name = 'Universidad de quien responde'
    cent = pd.DataFrame({'Universidad': UNIS,
                         'Mencionada como socia por personas de OTRAS universidades (%)':
                             [round(100 * sub.loc[sub['Universidad'] != u, four[u]].notna().mean(), 1) for u in UNIS],
                         'Personas de otras universidades que la mencionan (n)': [int(sub.loc[sub['Universidad'] != u, four[u]].notna().sum()) for u in UNIS]})
    return m, cent


# ------------------------------------------------------------------ concentración (datos EAFIT)
def concentration():
    top5_part = 5 * 4
    rows = [
        ('Aprobados', 96, '100 %'),
        ('Aprobados que repiten (≥2 convocatorias)', 17, '17,7 %'),
        ('Aprobados en las 4 convocatorias', 5, '5,2 %'),
        ('Participaciones proyecto-autor totales', 141, '100 %'),
        ('Participaciones del Top 10', 34, '24,1 %'),
        ('Participaciones de los 5 que ganaron 4 veces', top5_part, '14,2 %'),
        ('Proyectos 8, 9 y 13 con los mismos 4-5 autores principales', 3, '13 % de 23'),
    ]
    return pd.DataFrame(rows, columns=['Indicador (presentación EAFIT)', 'n', '%'])


# ------------------------------------------------------------------ texto abierto: léxico y temas latentes
LEXICON = {
    'Fricción administrativa': r'administrativ|proceso|firma|abogado|burocr|lent|desgast|trámite',
    'Tiempo y carga': r'carga|tiempo|descarga|jubila',
    'Pertenencia y red': r'red\b|redes|socio|perfil|conoc|encuentro|comunidad|match|mesas',
    'Autonomía y libertad temática': r'restring|libertad|ampliar|tema|línea|ventana|diversidad|artes',
    'Recursos': r'presupuesto|recurso|fondo|financ',
    'Equidad y reciprocidad': r'equilibr|distribu|responsabilidad|comprometid|todas las áreas',
    'Comparación entre universidades': r'en la icesi|otras universidades|cuatro universidades|las 4 universidades|entre las universidades|eafit eran',
}


def lexicon_table():
    rows = []
    s = df[321].dropna().str.lower()
    g = df.loc[s.index, 'Grupo']
    for k, pat in LEXICON.items():
        m = s.str.contains(pat)
        rows.append({'Campo semántico (J6)': k, 'Respuestas': int(m.sum()), '% de 54': round(100 * m.mean(), 1),
                     'Financiados': int((m & (g == 'Financiado')).sum()), 'No financiados / no postularon': int((m & (g != 'Financiado')).sum())})
    return pd.DataFrame(rows).sort_values('Respuestas', ascending=False)


FLAGSHIPS = {
    'Economía informal (Cali, Medellín, Barranquilla, Cartagena)': r'informal|vendedor|datos en breve',
    'Cultura política y democracia universitaria': r'democr|cultura política|polític.*estudiant|estallido',
    'IA y aprendizaje (chatbots, RAG, autoexplicaciones)': r'chatbot|\brag\b|edurag|\bia\b|autoexplicaci',
    'Monitoreo de aves / biodiversidad (Humboldt)': r'aves|humboldt|biodiversidad|estación de investigación',
    'Género en ingeniería / exclusión de mujeres': r'género|mujeres',
    'Materiales y construcción': r'cement|polímer|matrices',
    'Transición energética (amoníaco verde)': r'amon',
}


def flagship_table():
    txt = df[[252, 279, 280, 321]].fillna('').agg(' '.join, axis=1).str.lower()
    rows = []
    for k, pat in FLAGSHIPS.items():
        m = txt.str.contains(pat) & (df['Grupo'] == 'Financiado')
        rows.append({'Línea de proyecto reconocible en los textos': k, 'Financiados que la mencionan': int(m.sum()),
                     'Universidades': ', '.join(f'{u} ({n})' for u, n in df.loc[m, 'Universidad'].value_counts().items())})
    t = pd.DataFrame(rows).sort_values('Financiados que la mencionan', ascending=False)
    return t


# ------------------------------------------------------------------ gráficos
def charts():
    P = {}
    sl = straightlining()
    fig, ax = plt.subplots(figsize=(7.2, 4))
    ax.barh([f"{a} {w(b, 40)}" for a, b in zip(sl['Bloque'], sl['Tema'])], sl['%'], color='#7030A0')
    for i, v in enumerate(sl['%']):
        ax.text(v + .5, i, f'{v:.0f}%', va='center', fontsize=7)
    ax.invert_yaxis()
    ax.tick_params(axis='y', labelsize=6.5)
    ax.set_xlabel('% de personas que eligieron la misma respuesta en todos los ítems')
    ax.set_title('Respuestas uniformes por bloque')
    P['straight'] = save(fig, 'sub_straight')

    ns = ns_rates().head(12)
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.barh([f"{a} {w(b, 40)}" for a, b in zip(ns['Bloque'], ns['Tema'])], ns['%'], color='#A5A5A5')
    for i, v in enumerate(ns['%']):
        ax.text(v + .5, i, f'{v:.0f}%', va='center', fontsize=7)
    ax.invert_yaxis()
    ax.tick_params(axis='y', labelsize=6.5)
    ax.set_title('Proporción de "no sé / no recuerdo / no aplica" por bloque')
    P['ns'] = save(fig, 'sub_ns')

    g, _ = gaps()
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    y = np.arange(len(g))
    ax.hlines(y, g['% B'], g['% A'], color='#BFBFBF', lw=3)
    ax.scatter(g['% A'], y, color='#1F3864', s=40, label='Lo que se declara', zorder=3)
    ax.scatter(g['% B'], y, color='#C55A11', s=40, label='Lo que se evidencia', zorder=3)
    for yi, a, b in zip(y, g['% A'], g['% B']):
        ax.text(a + 1.5, yi, f'{a:.0f}', va='center', fontsize=6.5)
        ax.text(b - 1.5, yi, f'{b:.0f}', va='center', ha='right', fontsize=6.5)
    ax.set_yticks(y)
    ax.set_yticklabels([w(f'{a} / {b}', 60) for a, b in zip(g['Lo que se declara'], g['Lo que se evidencia'])], fontsize=5.8)
    ax.invert_yaxis()
    ax.set_xlim(0, 105)
    ax.set_xlabel('%')
    ax.legend(fontsize=7, frameon=False, loc='lower left')
    ax.set_title('Brechas entre lo que se declara y lo que se evidencia')
    P['gaps'] = save(fig, 'sub_gaps')

    m, cent = partner_matrix()
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    im = ax.imshow(m.values, cmap='Blues', vmin=0, vmax=80)
    ax.set_xticks(range(4)); ax.set_xticklabels(UNIS)
    ax.set_yticks(range(4)); ax.set_yticklabels(UNIS)
    ax.set_xlabel('Universidad con la que colaboró desde 2021')
    ax.set_ylabel('Universidad de quien responde')
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f'{m.values[i, j]:.0f}%', ha='center', va='center', fontsize=8, color='white' if m.values[i, j] > 45 else 'black')
    fig.colorbar(im, ax=ax, shrink=.8)
    ax.set_title('Red de colaboración declarada (D5)')
    P['net'] = save(fig, 'sub_net')

    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    ax.bar(cent['Universidad'], cent.iloc[:, 1], color=['#7030A0', '#2E75B6', '#C00000', '#548235'])
    for i, v in enumerate(cent.iloc[:, 1]):
        ax.text(i, v + 1, f'{v:.0f}%', ha='center', fontsize=8)
    ax.set_ylim(0, 80)
    ax.set_ylabel('% de personas de otras universidades')
    ax.set_title('Centralidad: quién es nombrado como socio por las demás')
    P['cent'] = save(fig, 'sub_cent')

    lx = lexicon_table()
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.barh(lx['Campo semántico (J6)'], lx['Financiados'], color=C_GRP['Financiado'], label='Financiados')
    ax.barh(lx['Campo semántico (J6)'], lx['No financiados / no postularon'], left=lx['Financiados'], color='#A5A5A5', label='No financiados / no postularon')
    ax.invert_yaxis()
    ax.legend(fontsize=7, frameon=False)
    ax.set_xlabel('Respuestas abiertas (J6) que usan el campo semántico')
    ax.set_title('Campos semánticos en las propuestas de cambio')
    P['lex'] = save(fig, 'sub_lex')

    st = gaps()[0]
    c = CONTEXT
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.8))
    axes[0].bar(['2023', '2024', '2025'], [c['minc_2023'] / 1000, c['minc_2024'] / 1000, c['minc_2025'] / 1000], color='#C00000')
    for i, v in enumerate([c['minc_2023'], c['minc_2024'], c['minc_2025']]):
        axes[0].text(i, v / 1000 + 8, f'{v / 1000:.0f}', ha='center', fontsize=8)
    axes[0].set_title('Presupuesto MinCiencias (COP miles de millones)', fontsize=8)
    axes[1].bar(['Colombia', 'OCDE'], [c['id_pib_col'], c['id_pib_ocde']], color=['#C55A11', '#A5A5A5'])
    for i, v in enumerate([c['id_pib_col'], c['id_pib_ocde']]):
        axes[1].text(i, v + .05, f'{v:.2f}%'.replace('.', ','), ha='center', fontsize=8)
    axes[1].set_title('Inversión en I+D (% del PIB, 2022)', fontsize=8)
    P['ctx'] = save(fig, 'sub_ctx')

    fig, ax = plt.subplots(figsize=(6.5, 2.8))
    labs = ['Investigadores reconocidos\nColombia 2024', 'Aprobados 4U\n(EAFIT)', 'Financiados\nencuestados', 'Encuestados\n(todos)']
    vals = [40.5, 44.8, 55.6, 50.0]
    ax.bar(labs, vals, color=['#A5A5A5', '#C55A11', '#1F3864', '#2E75B6'])
    for i, v in enumerate(vals):
        ax.text(i, v + 1, f'{v:.1f}%'.replace('.', ','), ha='center', fontsize=8)
    ax.set_ylim(0, 70)
    ax.tick_params(axis='x', labelsize=7)
    ax.set_ylabel('% mujeres')
    ax.set_title('Participación de mujeres: país, programa y encuesta')
    P['gender'] = save(fig, 'sub_gender')

    co = concentration()
    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    ax.bar(['5 aprobados\n(4 victorias)', 'Top 10', 'Resto (86)'], [20, 34 - 20, 141 - 34], color=['#C00000', '#F4B183', '#D9D9D9'])
    ax.set_ylabel('Participaciones proyecto-autor')
    ax.set_title('Concentración de participaciones (141, datos EAFIT)')
    for i, v in enumerate([20, 14, 107]):
        ax.text(i, v + 2, str(v), ha='center', fontsize=8)
    P['conc'] = save(fig, 'sub_conc')
    return P


if __name__ == '__main__':
    pd.set_option('display.width', 250)
    pd.set_option('display.max_colwidth', 60)
    print(straightlining().to_string())
    print(gaps()[0].to_string(), gaps()[1])
    print(c_fav_avg('C1'), c_fav_avg('C3'))
    m, c = partner_matrix(); print(m); print(c)
    print(lexicon_table().to_string())
    print(flagship_table().to_string())
    print(duration_profile().to_string())
    print(len(charts()))
