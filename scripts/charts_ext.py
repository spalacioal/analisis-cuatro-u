"""Gráficos de la ampliación."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from charts import save, w
from extend import *


def ch_harmonized(H):
    temas = ['Sexo', 'Universidad', 'Área de conocimiento', 'Trayectoria', 'Estado del proyecto', 'Artículos científicos']
    fig, axes = plt.subplots(3, 2, figsize=(7.4, 8.2))
    for ax, tema in zip(axes.flat, temas):
        t = H[H['Tema'] == tema]
        y = np.arange(len(t))
        ax.barh(y - .2, t['EAFIT %'], .4, color='#C55A11', label='Presentación EAFIT')
        ax.barh(y + .2, t['Encuesta %'], .4, color='#1F3864', label='Encuesta (financiados)')
        for yi, a, b in zip(y, t['EAFIT %'], t['Encuesta %']):
            if pd.notna(a):
                ax.text(a + 1, yi - .2, f'{a:.0f}', va='center', fontsize=6)
            ax.text(b + 1, yi + .2, f'{b:.0f}', va='center', fontsize=6)
        ax.set_yticks(y)
        ax.set_yticklabels([w(c, 18) for c in t['Categoría']], fontsize=6.5)
        ax.invert_yaxis()
        ax.set_xlim(0, 80)
        ax.set_title(tema, fontsize=8)
        ax.tick_params(axis='x', labelsize=6)
    axes[0, 0].legend(fontsize=6.5, frameon=False, loc='lower right')
    fig.suptitle('Encuesta frente a presentación de EAFIT, con rangos armonizados (%)', fontsize=9)
    return save(fig, 'ext_harmonized')


def ch_coverage(C):
    t = C[C['Dimensión'] != 'Total']
    fig, ax = plt.subplots(figsize=(7, 2.6))
    y = np.arange(len(t))
    ax.barh(y, t['Cobertura %'], color='#548235')
    for yi, v, k, n in zip(y, t['Cobertura %'], t['Financiados encuestados'], t['Aprobados (EAFIT)']):
        ax.text(v + 1, yi, f'{v:.0f}% ({k} de {n})', va='center', fontsize=7)
    ax.axvline(46.9, color='grey', ls='--', lw=.8)
    ax.text(47.5, len(t) - .4, 'Total 47%', fontsize=7, color='grey')
    ax.set_yticks(y)
    ax.set_yticklabels(t['Categoría'])
    ax.invert_yaxis()
    ax.set_xlim(0, 80)
    ax.set_title('Cobertura: financiados que respondieron / aprobados según EAFIT')
    return save(fig, 'ext_coverage')


def ch_effects(E1, E2):
    t1 = E1[E1['Tipo'] == 'pp'].reset_index(drop=True)
    t2 = E2[E2['Tipo'] == 'pp'].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    y = np.arange(len(t1))
    for t, off, col, lab in [(t1, -.17, '#1F3864', 'Control: todos los no financiados (n≈55)'), (t2, .17, '#C55A11', 'Control: postulantes rechazados (n=11)')]:
        ax.errorbar(t['ATT emparejamiento'], y + off, xerr=[t['ATT emparejamiento'] - t['IC95% inf'], t['IC95% sup'] - t['ATT emparejamiento']],
                    fmt='o', color=col, ecolor=col, elinewidth=1, capsize=2, label=lab, ms=4)
    ax.axvline(0, color='black', lw=.7)
    ax.set_yticks(y)
    ax.set_yticklabels([w(r, 42) for r in t1['Resultado']], fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xlabel('Diferencia emparejada financiados − controles (puntos porcentuales, IC 95 %)')
    ax.legend(fontsize=6.5, frameon=False, loc='upper center', bbox_to_anchor=(0.4, -0.12), ncol=2)
    ax.set_title('Efecto ajustado de ser financiado (emparejamiento por puntaje de propensión)')
    return save(fig, 'ext_effects')


def ch_potential(prof):
    t = prof[prof['Variable'] == 'Universidad']
    fig, ax = plt.subplots(figsize=(6, 2.2))
    ax.barh(t['Categoría'], t['n'], color='#7030A0')
    for i, v in enumerate(t['n']):
        ax.text(v + .2, i, str(v), va='center', fontsize=7)
    ax.invert_yaxis()
    ax.set_title('No postulantes con intención probable de colaborar, por universidad (n=27)')
    return save(fig, 'ext_potential')


def build(E1, E2):
    H = harmonized()
    P = {'harm': ch_harmonized(H), 'cov': ch_coverage(coverage()), 'eff': ch_effects(E1, E2)}
    a, prof, bar = potential()
    P['pot'] = ch_potential(prof)
    return P
