"""Gráficos para los informes Word."""
import os
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from analysis import *

OUTD = '/projects/sandbox/work/charts'
os.makedirs(OUTD, exist_ok=True)
C_GRP = {'Financiado': '#1F3864', 'Postuló, no financiado': '#C55A11', 'No postuló': '#A5A5A5'}
C_UNI = {'CESA': '#7030A0', 'EAFIT': '#2E75B6', 'ICESI': '#C00000', 'Uninorte': '#548235'}
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.dpi': 150})


def w(s, n=45):
    return '\n'.join(textwrap.wrap(str(s).rstrip('.'), n))


def save(fig, name):
    p = os.path.join(OUTD, name + '.png')
    fig.tight_layout()
    fig.savefig(p, bbox_inches='tight')
    plt.close(fig)
    return p


def stacked_pct(ax, table, cats, colors, labels=None, wrapn=35):
    left = np.zeros(len(table))
    for c, col in zip(cats, colors):
        v = table[c].values if c in table else np.zeros(len(table))
        ax.barh(range(len(table)), v, left=left, color=col, label=c, edgecolor='white')
        for i, (l, x) in enumerate(zip(left, v)):
            if x >= 7:
                ax.text(l + x / 2, i, f'{x:.0f}', ha='center', va='center', color='white', fontsize=7)
        left += v
    ax.set_yticks(range(len(table)))
    ax.set_yticklabels([w(x, wrapn) for x in (labels or table.index)])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel('%')


def ch_profile():
    out = {}
    # Grupos por universidad
    ct = pd.crosstab(df['Universidad'], df['Grupo'])[G3]
    fig, ax = plt.subplots(figsize=(7, 3))
    ct.plot.bar(ax=ax, color=[C_GRP[g] for g in G3], width=.75)
    for p in ax.patches:
        if p.get_height():
            ax.annotate(int(p.get_height()), (p.get_x() + p.get_width() / 2, p.get_height()), ha='center', va='bottom', fontsize=7)
    ax.set_xlabel('')
    ax.set_ylabel('Personas')
    ax.set_title('Encuestados por universidad y grupo de vinculación')
    ax.legend(frameon=False, fontsize=8)
    plt.xticks(rotation=0)
    out['grupos_uni'] = save(fig, 'grupos_uni')

    # experiencia, rango, dedicación por grupo
    for key, col, order, title in [('exp', 43, SINGLE_ORDER['B10'][1:], 'Años de experiencia en investigación por grupo'),
                                   ('rango', 'Rango (agrupado)', ['Auxiliar', 'Asistente', 'Asociado', 'Titular', 'Otro / sin rango'], 'Rango académico por grupo'),
                                   ('ded', 44, SINGLE_ORDER['B11'], 'Dedicación a investigación por grupo'),
                                   ('sexo', 'Sexo (estimado)', ['Mujer', 'Hombre'], 'Sexo (estimado por nombre) por grupo')]:
        sub = df[df['Grupo'].isin(G3)]
        t = (pd.crosstab(sub['Grupo'], sub[col], normalize='index') * 100).reindex(G3)
        t = t.reindex(columns=[o for o in order if o in t.columns]).fillna(0)
        t.loc['Total'] = (df[col].value_counts(normalize=True) * 100).reindex(t.columns).fillna(0)
        fig, ax = plt.subplots(figsize=(7, 2.6))
        cmap = plt.get_cmap('Blues', len(t.columns) + 2)
        stacked_pct(ax, t, list(t.columns), [cmap(i + 2) for i in range(len(t.columns))])
        ax.legend([str(c).rstrip('.') for c in t.columns], ncol=min(len(t.columns), 3), frameon=False, fontsize=7,
                  bbox_to_anchor=(0.5, -0.35), loc='upper center')
        ax.set_title(title)
        out[key] = save(fig, f'perfil_{key}')

    # área de conocimiento
    t = df[41].value_counts()
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.barh([w(x, 40) for x in t.index], t.values, color='#2E75B6')
    for i, v in enumerate(t.values):
        ax.text(v + .3, i, f'{v} ({v / len(df) * 100:.0f}%)', va='center', fontsize=7)
    ax.invert_yaxis()
    ax.set_title('Área principal de conocimiento (B9)')
    out['area'] = save(fig, 'perfil_area')
    return out


def ch_likert(code, title_override=None, pop=None, fname=None, by_group=False):
    m = [x for x in MATRIX if x[0] == code][0]
    _, title, cols, sc, popd = m
    d = df[pop_mask(pop or popd)]
    cats = [c for c in ORD[sc] if c in SCALES[sc]]
    rows = {}
    for c in cols:
        s = d[c].dropna()
        s = s[s.isin(cats)]
        rows[item_label(c)] = [(s == k).mean() * 100 if len(s) else 0 for k in cats]
    t = pd.DataFrame(rows, index=cats).T
    colors = ['#C00000', '#F4B183', '#D9D9D9', '#9DC3E6', '#1F3864']
    fig, ax = plt.subplots(figsize=(7.2, 0.45 * len(t) + 1.2))
    stacked_pct(ax, t, cats, colors, wrapn=48)
    ax.legend(cats, ncol=5, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.12 - 0.6 / len(t)), loc='upper center')
    ax.set_title(title_override or f'{code}. {title}')
    return save(fig, fname or f'likert_{code}')


def ch_index_groups():
    codes = ['C1', 'C2', 'C3', 'C4', 'E4', 'E5', 'E8']
    names = {'C1': 'C1 Disposición', 'C2': 'C2 Valor percibido', 'C3': 'C3 Condiciones inst.', 'C4': 'C4 Cambio capacidades',
             'E4': 'E4 Diseño convocatoria', 'E5': 'E5 Proceso', 'E8': 'E8 Aportes formulación'}
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    x = np.arange(len(codes))
    for i, g in enumerate(G3):
        vals = [np.nan if (g == 'No postuló' and c.startswith('E')) else df.loc[df['Grupo'] == g, f'IDX_{c}'].mean() for c in codes]
        ax.bar(x + (i - 1) * 0.27, vals, 0.27, color=C_GRP[g], label=g)
        for xi, v in zip(x, vals):
            if pd.notna(v):
                ax.text(xi + (i - 1) * 0.27, v + .03, f'{v:.2f}', ha='center', fontsize=6, rotation=90)
    ax.set_xticks(x)
    ax.set_xticklabels([w(names[c], 14) for c in codes], fontsize=7)
    ax.set_ylim(1, 5.3)
    ax.set_ylabel('Media (1-5)')
    ax.legend(frameon=False, fontsize=7, ncol=3, loc='upper center', bbox_to_anchor=(0.5, -0.18))
    ax.set_title('Índices compuestos por grupo de vinculación')
    return save(fig, 'idx_grupos')


def ch_index_uni():
    codes = list(INDEX)
    t = pd.DataFrame({u: [df[(df['Universidad'] == u) & pop_mask([m[4] for m in MATRIX if m[0] == c][0])][f'IDX_{c}'].mean() for c in codes] for u in UNIS},
                     index=[f'{c} {INDEX[c][0][:38]}' for c in codes])
    fig, ax = plt.subplots(figsize=(7.2, 5.5))
    im = ax.imshow(t.values, cmap='RdYlBu', vmin=2.5, vmax=5, aspect='auto')
    ax.set_xticks(range(len(UNIS)))
    ax.set_xticklabels(UNIS)
    ax.set_yticks(range(len(t)))
    ax.set_yticklabels(t.index, fontsize=7)
    for i in range(t.shape[0]):
        for j in range(t.shape[1]):
            v = t.values[i, j]
            if pd.notna(v):
                ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=7)
    fig.colorbar(im, ax=ax, shrink=.6, label='Media (1-5)')
    ax.set_title('Índices por universidad (C-E: todos o postulantes; F-I: financiados)')
    return save(fig, 'idx_uni')


def ch_d7():
    labs = ['Propuestas con otra universidad', 'Proyectos ejecutados con otra universidad', 'Productos con otra universidad',
            'Iniciativas con actores externos', 'Relaciones nuevas aún activas']
    fig, ax = plt.subplots(figsize=(7.2, 3))
    x = np.arange(5)
    for i, g in enumerate(G3):
        vals = [df.loc[df['Grupo'] == g, f'D7_{j}'].mean() for j in range(1, 6)]
        ax.bar(x + (i - 1) * .27, vals, .27, color=C_GRP[g], label=g)
        for xi, v in zip(x, vals):
            ax.text(xi + (i - 1) * .27, v + .04, f'{v:.1f}', ha='center', fontsize=6)
    ax.set_xticks(x)
    ax.set_xticklabels([w(l, 16) for l in labs], fontsize=7)
    ax.set_ylabel('Promedio aprox. por persona')
    ax.set_title('Experiencias interinstitucionales desde 2021 (D7)')
    ax.legend(frameon=False, fontsize=7)
    return save(fig, 'd7_grupos')


def ch_multi(code, by='Grupo', top=None, fname=None, title=None):
    m = [x for x in MULTI if x[0] == code][0]
    t = multi_table(*m, by=by if m[3] == 'todos' else None)
    t = t.iloc[:-1]
    t = t[t['Total n'] > 0]
    if top:
        t = t.head(top)
    fig, ax = plt.subplots(figsize=(7.2, 0.38 * len(t) + 1.1))
    y = np.arange(len(t))
    if m[3] == 'todos' and by == 'Grupo':
        for i, g in enumerate(G3):
            ax.barh(y + (i - 1) * .27, t[f'{g} %'], .27, color=C_GRP[g], label=g)
        ax.legend(frameon=False, fontsize=7, loc='lower right')
    else:
        ax.barh(y, t['Total %'], color='#1F3864')
        for yi, v, n in zip(y, t['Total %'], t['Total n']):
            ax.text(v + 1, yi, f'{v:.0f}% (n={n})', va='center', fontsize=7)
    ax.set_yticks(y)
    ax.set_yticklabels([w(o, 45) for o in t['Opción']], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel('% de personas')
    ax.set_xlim(0, 110)
    ax.set_title(title or f'{code}. {m[1]}')
    return save(fig, fname or f'multi_{code}')


def ch_single(code, col, pop, order=None, fname=None, by=None, title=None):
    d = df[pop_mask(pop)]
    order = order or SINGLE_ORDER.get(code) or list(d[col].value_counts().index)
    order = [o for o in order if (d[col] == o).any()]
    if by == 'Grupo':
        t = (pd.crosstab(d['Grupo'], d[col], normalize='index') * 100).reindex(G3)
    else:
        t = pd.DataFrame([(d[col].value_counts(normalize=True) * 100)])
        t.index = ['Total']
    t = t.reindex(columns=order).fillna(0)
    cmap = plt.get_cmap('RdYlBu', len(order) + 1)
    fig, ax = plt.subplots(figsize=(7.2, 0.5 * len(t) + 1.6))
    stacked_pct(ax, t, order, [cmap(i) for i in range(len(order))])
    ax.legend([w(o, 28) for o in order], ncol=3, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.25), loc='upper center')
    lab = [s for s in SINGLE if s[0] == code][0][2]
    ax.set_title(title or f'{code}. {lab}')
    return save(fig, fname or f'single_{code}')


def ch_bar_single(code, col, pop, fname=None, title=None):
    d = df[pop_mask(pop)]
    order = SINGLE_ORDER.get(code) or list(d[col].value_counts().index)
    t = d[col].value_counts().reindex([o for o in order if (d[col] == o).any()])
    if code not in SINGLE_ORDER:
        t = t.sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7.2, 0.38 * len(t) + 1))
    ax.barh([w(x, 50) for x in t.index], t.values, color='#2E75B6')
    for i, v in enumerate(t.values):
        ax.text(v + .2, i, f'{v} ({v / t.sum() * 100:.0f}%)', va='center', fontsize=7)
    ax.invert_yaxis()
    lab = [s for s in SINGLE if s[0] == code][0][2]
    ax.set_title(title or f'{code}. {lab} (n={t.sum()})')
    return save(fig, fname or f'bar_{code}')


def ch_h1():
    cats = ORD['h1']
    d = df[df['Grupo'] == 'Financiado']
    rows = {}
    for c in range(184, 193):
        s = d[c].dropna()
        rows[item_label(c)] = [(s == k).mean() * 100 for k in cats]
    t = pd.DataFrame(rows, index=cats).T
    t = t.sort_values('Completado', ascending=False)
    fig, ax = plt.subplots(figsize=(7.2, 4))
    stacked_pct(ax, t, ['Completado', 'En desarrollo', 'Previsto, pero no iniciado', 'No estaba previsto', 'No tengo información.'],
                ['#1F3864', '#2E75B6', '#9DC3E6', '#E7E6E6', '#BFBFBF'], wrapn=40)
    ax.legend(['Completado', 'En desarrollo', 'Previsto, no iniciado', 'No estaba previsto', 'Sin información'], ncol=5,
              frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.12), loc='upper center')
    ax.set_title('H1. Estado de los productos en los proyectos financiados (n=42)')
    return save(fig, 'h1')


def ch_h5():
    cats = ORD['h5']
    d = df[df['Grupo'] == 'Financiado']
    rows = {}
    for c in range(217, 223):
        s = d[c].dropna()
        rows[item_label(c)] = [(s == k).mean() * 100 for k in cats]
    t = pd.DataFrame(rows, index=cats).T
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    stacked_pct(ax, t, cats, ['#E7E6E6', '#DEEBF7', '#9DC3E6', '#2E75B6', '#1F3864', '#BFBFBF'], wrapn=40)
    ax.legend(['Sin interacción', 'Recibió información', 'Comentó/discutió', 'Co-diseñó/validó', 'Usó resultados', 'Sin información'],
              ncol=3, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.15), loc='upper center')
    ax.set_title('H5. Nivel más avanzado de interacción por tipo de actor (financiados)')
    return save(fig, 'h5')


def ch_success():
    s = success_rate()
    s = s[s['Variable'].isin(['Universidad', 'Sexo (estimado)', 'Experiencia', 'Rango', 'Rol en la propuesta (E3)'])]
    s = s[s['Postulantes'] >= 3]
    fig, ax = plt.subplots(figsize=(7.2, 4))
    y = np.arange(len(s))
    ax.barh(y, s['Tasa de éxito %'], color='#548235')
    for yi, v, n in zip(y, s['Tasa de éxito %'], s['Postulantes']):
        ax.text(v + 1, yi, f'{v:.0f}% (n={n})', va='center', fontsize=7)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{a}: {b}" for a, b in zip(s['Variable'].str.replace(' (estimado)', '').str.replace(' (E3)', ''), s['Categoría'])], fontsize=7)
    ax.axvline(80.4, color='grey', ls='--', lw=.8)
    ax.text(80.4, -0.8, 'Promedio 80%', fontsize=7, color='grey')
    ax.invert_yaxis()
    ax.set_xlim(0, 115)
    ax.set_title('Tasa de éxito de las postulaciones por perfil (n=56)')
    return save(fig, 'exito')


def ch_e_compare():
    rows = []
    for code in ['E4', 'E5', 'E8']:
        m = [x for x in MATRIX if x[0] == code][0]
        for j, c in enumerate(m[2]):
            rows.append((f'{code}.{j + 1} {item_label(c)}',
                         df.loc[df['Grupo'] == 'Financiado', f'{code}_{j + 1}'].mean(),
                         df.loc[df['Grupo'] == 'Postuló, no financiado', f'{code}_{j + 1}'].mean()))
    t = pd.DataFrame(rows, columns=['Ítem', 'F', 'NF'])
    fig, ax = plt.subplots(figsize=(7.2, 6.5))
    y = np.arange(len(t))
    ax.hlines(y, t['NF'], t['F'], color='#BFBFBF')
    ax.scatter(t['F'], y, color=C_GRP['Financiado'], label='Financiado', zorder=3)
    ax.scatter(t['NF'], y, color=C_GRP['Postuló, no financiado'], label='Postuló, no financiado', zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([w(x, 55) for x in t['Ítem']], fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xlim(1, 5)
    ax.set_xlabel('Media (1-5)')
    ax.legend(frameon=False, fontsize=7, loc='lower left')
    ax.set_title('Valoración de la convocatoria: financiados vs. no financiados')
    return save(fig, 'e_compare')


def ch_j12():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.8), sharey=True)
    for ax, col, lab in [(axes[0], 'J1_num', 'J1. Participar con otra universidad 4U'), (axes[1], 'J2_num', 'J2. Liderar una iniciativa')]:
        vals = [(df.loc[df['Grupo'] == g, col] >= 4).sum() / df.loc[df['Grupo'] == g, col].notna().sum() * 100 for g in G3]
        ax.bar(range(3), vals, color=[C_GRP[g] for g in G3])
        for i, v in enumerate(vals):
            ax.text(i, v + 1, f'{v:.0f}%', ha='center', fontsize=8)
        ax.set_xticks(range(3))
        ax.set_xticklabels([w(g, 12) for g in G3], fontsize=7)
        ax.set_title(lab, fontsize=8)
        ax.set_ylim(0, 100)
    axes[0].set_ylabel('% probable o muy probable')
    return save(fig, 'j12')


def ch_text(col, themes, name, title):
    t, q = code_text(col, themes)
    t = t.iloc[:-1]
    t = t[t['Menciones'] > 0]
    fig, ax = plt.subplots(figsize=(7.2, 0.38 * len(t) + 1))
    ax.barh([w(x, 45) for x in t['Tema']], t['Menciones'], color='#7030A0')
    for i, (v, p) in enumerate(zip(t['Menciones'], t['% de respuestas'])):
        ax.text(v + .2, i, f'{v} ({p:.0f}%)', va='center', fontsize=7)
    ax.invert_yaxis()
    ax.set_title(title + f' (n={len(q)} respuestas)')
    return save(fig, name)


def build_all():
    P = {}
    P.update(ch_profile())
    for code in ['C1', 'C2', 'C3', 'C4', 'E4', 'E5', 'F2', 'F3', 'F4', 'F5', 'G1', 'G2', 'G3', 'I1', 'H3', 'E8']:
        P[f'lk_{code}'] = ch_likert(code)
    P['idx_grupos'] = ch_index_groups()
    P['idx_uni'] = ch_index_uni()
    P['d7'] = ch_d7()
    for code in ['D4', 'D5', 'D6', 'J3', 'J4', 'J5']:
        P[f'mu_{code}'] = ch_multi(code)
    for code in ['H2', 'H4', 'H6', 'H7', 'H8', 'I6', 'E9']:
        P[f'mu_{code}'] = ch_multi(code)
    P['d2'] = ch_single('D2', 71, 'todos', by='Grupo')
    P['d8'] = ch_single('D8', 104, 'todos', by='Grupo')
    for code, col in [('F1', 143), ('F6', 165), ('F7', 166), ('I2', 262), ('I3', 263), ('I4', 264), ('I5', 265), ('I7', 278),
                      ('E6', 124), ('E3', 108)]:
        pop = [s for s in SINGLE if s[0] == code][0][3]
        P[f'bar_{code}'] = ch_bar_single(code, col, pop)
    P['h1'] = ch_h1()
    P['h5'] = ch_h5()
    P['exito'] = ch_success()
    P['e_compare'] = ch_e_compare()
    P['j12'] = ch_j12()
    P['txt_J6'] = ch_text(321, THEMES_J6, 'txt_J6', 'J6. Cambio propuesto – temas')
    P['txt_I8'] = ch_text(280, THEMES_I8, 'txt_I8', 'I8. Resultado más significativo – temas')
    return P


if __name__ == '__main__':
    P = build_all()
    print(len(P), 'charts')
