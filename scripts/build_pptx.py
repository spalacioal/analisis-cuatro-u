"""Presentación PowerPoint con gráficas de todos los hallazgos y el análisis de subtexto."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import charts as CH
import charts_ext
import subtext as ST
from extend import *

OUT = '/projects/sandbox/analisis-cuatro-u/resultados/Presentacion_hallazgos_Alianza_4U.pptx'
NAVY = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x2E, 0x75, 0xB6)
GREY = RGBColor(0x59, 0x59, 0x59)
ORANGE = RGBColor(0xC5, 0x5A, 0x11)
LIGHT = RGBColor(0xEA, 0xF0, 0xF8)
W, Hh = Inches(13.333), Inches(7.5)


# ------------------------------------------------------------------ gráficos adicionales de detalle
def extra_charts():
    P = {}
    save, w = CH.save, CH.w
    for key, col, title in [('b6', 35, 'B6. Tipo de vinculación'), ('b7', 37, 'B7. Función principal'), ('b8', 39, 'B8. Rango o categoría académica'),
                            ('d3', 72, 'D3. Relación previa con Alianza 4U'), ('e1', 106, 'E1. Participación en la postulación'),
                            ('e2', 107, 'E2. Resultado de la postulación'), ('b11', 44, 'B11. Dedicación a investigación')]:
        s = df[col].dropna().value_counts()
        order = SINGLE_ORDER.get({'b8': 'B8', 'b11': 'B11'}.get(key, ''), None)
        if order:
            s = s.reindex([o for o in order if o in s.index])
        fig, ax = plt.subplots(figsize=(7.2, 0.36 * len(s) + 1))
        ax.barh([w(x, 55) for x in s.index], s.values, color='#2E75B6')
        for i, v in enumerate(s.values):
            ax.text(v + .3, i, f'{v} ({100 * v / s.sum():.0f}%)', va='center', fontsize=7)
        ax.invert_yaxis()
        ax.tick_params(axis='y', labelsize=7)
        ax.set_title(f'{title} (n={s.sum()})')
        P[key] = save(fig, f'x_{key}')
    # sexo por área y por rol
    for key, col, title, sub in [('sx_area', 41, 'Sexo estimado por área de conocimiento', df),
                                 ('sx_rol', 108, 'Sexo estimado por rol en la propuesta', df[df[108].notna()]),
                                 ('sx_func', 37, 'Sexo estimado por función principal', df)]:
        ct = pd.crosstab(sub[col].str.rstrip('.'), sub['Sexo (estimado)'])[['Mujer', 'Hombre']]
        ct = ct.loc[ct.sum(axis=1).sort_values(ascending=False).index]
        fig, ax = plt.subplots(figsize=(7.2, 0.36 * len(ct) + 1.1))
        y = np.arange(len(ct))
        ax.barh(y - .2, ct['Mujer'], .4, color='#C00000', label='Mujeres')
        ax.barh(y + .2, ct['Hombre'], .4, color='#1F3864', label='Hombres')
        ax.set_yticks(y)
        ax.set_yticklabels([w(x, 45) for x in ct.index], fontsize=7)
        ax.invert_yaxis()
        ax.legend(fontsize=7, frameon=False)
        ax.set_title(title)
        P[key] = save(fig, f'x_{key}')
    # duración
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    for u, c in CH.C_UNI.items():
        ax.hist(df.loc[df['Encuesta'] == u, 5].astype(float) / 60, bins=np.arange(0, 140, 5), alpha=.55, color=c, label=u)
    ax.set_xlabel('Minutos')
    ax.set_ylabel('Personas')
    ax.legend(fontsize=7, frameon=False)
    ax.set_title('Duración de la encuesta por enlace')
    P['dur'] = save(fig, 'x_dur')
    # fechas
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    d = pd.to_datetime(df[3])
    for u, c in CH.C_UNI.items():
        s = d[df['Encuesta'] == u].sort_values()
        ax.plot(s, range(1, len(s) + 1), color=c, label=u)
    ax.set_ylabel('Respuestas acumuladas')
    ax.legend(fontsize=7, frameon=False)
    ax.set_title('Ritmo de respuesta (sep-nov 2026)')
    fig.autofmt_xdate()
    P['fechas'] = save(fig, 'x_fechas')
    # J1/J2 por universidad
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    x = np.arange(4)
    for i, (col, lab, c) in enumerate([('J1_num', 'Participar (J1)', '#1F3864'), ('J2_num', 'Liderar (J2)', '#C55A11')]):
        v = [100 * (df.loc[df['Universidad'] == u, col] >= 4).sum() / df.loc[df['Universidad'] == u, col].notna().sum() for u in UNIS]
        ax.bar(x + (i - .5) * .38, v, .38, color=c, label=lab)
        for xi, vi in zip(x, v):
            ax.text(xi + (i - .5) * .38, vi + 1, f'{vi:.0f}%', ha='center', fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(UNIS)
    ax.set_ylim(0, 100)
    ax.set_ylabel('% probable o muy probable')
    ax.legend(fontsize=7, frameon=False)
    ax.set_title('Intención futura por universidad')
    P['j12u'] = save(fig, 'x_j12u')
    # tasa de éxito por área
    s = success_rate()
    s = s[s['Variable'] == 'Área de conocimiento'].sort_values('Postulantes', ascending=False)
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    ax.barh(s['Categoría'], s['Tasa de éxito %'], color='#548235')
    for i, (v, n) in enumerate(zip(s['Tasa de éxito %'], s['Postulantes'])):
        ax.text(v + 1, i, f'{v:.0f}% (n={n})', va='center', fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 120)
    ax.set_title('Éxito entre postulantes encuestados, por área autodeclarada')
    P['exito_area'] = save(fig, 'x_exito_area')
    # índices por sexo y experiencia
    for key, dim, levels, cols in [('idx_sexo', 'Sexo', ['Mujer', 'Hombre'], ['#C00000', '#1F3864']),
                                   ('idx_exp', 'Experiencia', ['≤10 años', '11-20 años', '>20 años'], ['#9DC3E6', '#2E75B6', '#1F3864'])]:
        t = index_by(dim)
        fig, ax = plt.subplots(figsize=(7.4, 3.2))
        x = np.arange(len(t))
        wd = .8 / len(levels)
        for i, (lv, c) in enumerate(zip(levels, cols)):
            ax.bar(x + (i - (len(levels) - 1) / 2) * wd, t[f'{lv} media'], wd, color=c, label=lv)
        ax.set_xticks(x)
        ax.set_xticklabels(t['Índice'].str.replace('IDX_', ''), fontsize=7)
        ax.set_ylim(1, 5)
        ax.set_ylabel('Media (1-5)')
        ax.legend(fontsize=7, frameon=False, ncol=3)
        ax.set_title(f'Índices por {dim.lower()}')
        P[key] = save(fig, f'x_{key}')
    # correlaciones financiados (heatmap)
    rf, pf = corr_fin()
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(rf.values.astype(float), cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_xticks(range(len(rf))); ax.set_xticklabels(rf.columns, rotation=90, fontsize=6)
    ax.set_yticks(range(len(rf))); ax.set_yticklabels(rf.index, fontsize=6)
    for i in range(len(rf)):
        for j in range(len(rf)):
            v = rf.values[i, j]
            if pd.notna(v) and i != j:
                ax.text(j, i, f'{v:.1f}', ha='center', va='center', fontsize=5)
    fig.colorbar(im, ax=ax, shrink=.7)
    ax.set_title('Correlaciones de Spearman entre resultados (financiados)')
    P['corr'] = save(fig, 'x_corr')
    return P


# ------------------------------------------------------------------ utilidades de diapositiva
class Deck:
    def __init__(self):
        self.p = Presentation()
        self.p.slide_width, self.p.slide_height = W, Hh
        self.blank = self.p.slide_layouts[6]
        self.n = 0

    def _bar(self, s, color=NAVY, h=Inches(0.12)):
        r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, h)
        r.fill.solid(); r.fill.fore_color.rgb = color; r.line.fill.background()

    def _text(self, s, txt, l, t, w, h, size=14, bold=False, color=None, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
        tb = s.shapes.add_textbox(l, t, w, h)
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        lines = txt if isinstance(txt, list) else [txt]
        for i, ln in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            r = p.add_run()
            r.text = ln
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.name = 'Calibri'
            if color:
                r.font.color.rgb = color
        return tb

    def _footer(self, s, src):
        self.n += 1
        self._text(s, src, Inches(0.5), Inches(7.05), Inches(10.5), Inches(0.35), size=9, color=GREY)
        self._text(s, str(self.n), Inches(12.3), Inches(7.05), Inches(0.6), Inches(0.35), size=9, color=GREY, align=PP_ALIGN.RIGHT)

    def cover(self, title, sub, lines):
        s = self.p.slides.add_slide(self.blank)
        bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Hh)
        bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
        self._text(s, title, Inches(0.8), Inches(2.2), Inches(11.7), Inches(1.4), size=38, bold=True, color=RGBColor(255, 255, 255))
        self._text(s, sub, Inches(0.8), Inches(3.6), Inches(11.7), Inches(0.8), size=20, color=RGBColor(0x9D, 0xC3, 0xE6))
        self._text(s, lines, Inches(0.8), Inches(5.2), Inches(11.7), Inches(1.5), size=14, color=RGBColor(255, 255, 255))
        self.n += 1

    def section(self, num, title, sub=''):
        s = self.p.slides.add_slide(self.blank)
        bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(4.2), Hh)
        bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
        self._text(s, num, Inches(0.6), Inches(2.6), Inches(3.2), Inches(1.6), size=72, bold=True, color=RGBColor(255, 255, 255))
        self._text(s, title, Inches(4.8), Inches(2.7), Inches(8), Inches(1.2), size=34, bold=True, color=NAVY)
        if sub:
            self._text(s, sub, Inches(4.8), Inches(3.9), Inches(8), Inches(1.5), size=16, color=GREY)
        self.n += 1

    def chart(self, title, img, bullets, src='Fuente: encuesta Alianza 4U (n=102).', layout='right'):
        s = self.p.slides.add_slide(self.blank)
        self._bar(s)
        self._text(s, title, Inches(0.5), Inches(0.3), Inches(12.3), Inches(1.0), size=24, bold=True, color=NAVY)
        if layout == 'right':
            box = (Inches(0.4), Inches(1.35), Inches(8.3), Inches(5.6))
            tx = (Inches(8.9), Inches(1.5), Inches(4.1), Inches(5.4))
        else:
            box = (Inches(0.6), Inches(1.3), Inches(12.1), Inches(4.4))
            tx = (Inches(0.6), Inches(5.75), Inches(12.1), Inches(1.25))
        self._img(s, img, *box)
        if bullets:
            tb = s.shapes.add_textbox(*tx)
            tf = tb.text_frame
            tf.word_wrap = True
            for i, b in enumerate(bullets):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                r = p.add_run()
                r.text = '• ' + b
                r.font.size = Pt(13 if layout == 'right' else 12)
                r.font.color.rgb = RGBColor(0x26, 0x26, 0x26)
                p.space_after = Pt(8)
        self._footer(s, src)

    def two(self, title, img1, img2, bullets=None, src='Fuente: encuesta Alianza 4U (n=102).'):
        s = self.p.slides.add_slide(self.blank)
        self._bar(s)
        self._text(s, title, Inches(0.5), Inches(0.3), Inches(12.3), Inches(1.0), size=24, bold=True, color=NAVY)
        h = Inches(4.6) if bullets else Inches(5.6)
        self._img(s, img1, Inches(0.3), Inches(1.35), Inches(6.3), h)
        self._img(s, img2, Inches(6.75), Inches(1.35), Inches(6.3), h)
        if bullets:
            self._text(s, ['• ' + b for b in bullets], Inches(0.6), Inches(6.05), Inches(12.1), Inches(1.0), size=12)
        self._footer(s, src)

    def _img(self, s, path, l, t, bw, bh):
        iw, ih = Image.open(path).size
        r = min(bw / iw, bh / ih)
        w_, h_ = int(iw * r), int(ih * r)
        s.shapes.add_picture(path, l + (bw - w_) // 2, t + (bh - h_) // 2, w_, h_)

    def kpis(self, title, items, src):
        s = self.p.slides.add_slide(self.blank)
        self._bar(s)
        self._text(s, title, Inches(0.5), Inches(0.3), Inches(12.3), Inches(1.0), size=24, bold=True, color=NAVY)
        cols = 4
        for k, (v, lab) in enumerate(items):
            r, c = divmod(k, cols)
            l, t = Inches(0.5 + c * 3.15), Inches(1.45 + r * 1.85)
            box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, Inches(2.95), Inches(1.65))
            box.fill.solid(); box.fill.fore_color.rgb = LIGHT; box.line.fill.background()
            self._text(s, v, l, t + Inches(0.1), Inches(2.95), Inches(0.75), size=28, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
            self._text(s, lab, l + Inches(0.1), t + Inches(0.85), Inches(2.75), Inches(0.8), size=11, color=GREY, align=PP_ALIGN.CENTER)
        self._footer(s, src)

    def table(self, title, df_, src, colw=None, size=10, note=None):
        s = self.p.slides.add_slide(self.blank)
        self._bar(s)
        self._text(s, title, Inches(0.5), Inches(0.3), Inches(12.3), Inches(1.0), size=24, bold=True, color=NAVY)
        rows, cols = df_.shape[0] + 1, df_.shape[1]
        th = Inches(0.36) * rows
        maxh = Inches(5.2) if note else Inches(5.6)
        shp = s.shapes.add_table(rows, cols, Inches(0.5), Inches(1.35), Inches(12.3), min(th, maxh))
        tb = shp.table
        if colw:
            for j, cw in enumerate(colw):
                tb.columns[j].width = Inches(cw)
        for j, c in enumerate(df_.columns):
            cell = tb.cell(0, j)
            cell.text = str(c)
            cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
            for p in cell.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
        for i, row in enumerate(df_.itertuples(index=False), 1):
            for j, v in enumerate(row):
                cell = tb.cell(i, j)
                if isinstance(v, float):
                    v = '–' if np.isnan(v) else (f'{v:.1f}' if not float(v).is_integer() else f'{int(v)}').replace('.', ',')
                cell.text = str(v)
                cell.fill.solid(); cell.fill.fore_color.rgb = LIGHT if i % 2 else RGBColor(255, 255, 255)
                for p in cell.text_frame.paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(size)
        if note:
            self._text(s, note, Inches(0.5), Inches(6.55), Inches(12.3), Inches(0.5), size=11, color=GREY)
        self._footer(s, src)

    def text(self, title, bullets, src='', size=16):
        s = self.p.slides.add_slide(self.blank)
        self._bar(s)
        self._text(s, title, Inches(0.5), Inches(0.3), Inches(12.3), Inches(1.0), size=24, bold=True, color=NAVY)
        tb = s.shapes.add_textbox(Inches(0.7), Inches(1.45), Inches(12), Inches(5.5))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            if isinstance(b, tuple):
                r = p.add_run(); r.text = b[0]; r.font.bold = True; r.font.size = Pt(size); r.font.color.rgb = NAVY
                r = p.add_run(); r.text = b[1]; r.font.size = Pt(size)
            else:
                r = p.add_run(); r.text = '• ' + b; r.font.size = Pt(size)
            p.space_after = Pt(10)
        self._footer(s, src)

    def save(self, path):
        self.p.save(path)


# ------------------------------------------------------------------ contenido
def build():
    E1 = pd.read_pickle('/projects/sandbox/work/eff_todos.pkl')
    E2 = pd.read_pickle('/projects/sandbox/work/eff_rechazados.pkl')
    P = CH.build_all()
    P.update(charts_ext.build(E1, E2))
    P.update(ST.charts())
    P.update(extra_charts())
    D = Deck()
    SRC = 'Fuente: encuesta Alianza 4U, 102 personas (sep-nov 2026).'
    SRCF = 'Fuente: encuesta Alianza 4U, financiados (n=43-45).'
    SRCP = 'Fuente: encuesta Alianza 4U, postulantes (n=57).'
    SRCE = 'Fuentes: encuesta Alianza 4U y presentación de la oficina de inteligencia en CTeI de EAFIT (sep. 2026).'

    D.cover('Alianza 4U: lo que dicen los datos', 'Hallazgos de la encuesta a docentes e investigadores y análisis de subtexto',
            ['CESA · EAFIT · Icesi · Universidad del Norte', '102 personas encuestadas · septiembre a noviembre de 2026', 'Noviembre de 2026'])
    D.text('Contenido', [('1. ', 'Resumen y método'), ('2. ', 'Quiénes respondieron'), ('3. ', 'Colaboración en general'),
                         ('4. ', 'Trayectoria y relación con la Alianza'), ('5. ', 'Convocatorias'), ('6. ', 'Proyectos financiados'),
                         ('7. ', 'Capacidades, productos y uso'), ('8. ', 'Impacto y adicionalidad'), ('9. ', 'Futuro y barreras'),
                         ('10. ', 'Comparación con EAFIT, verificación y efecto ajustado'), ('11. ', 'Análisis de subtexto'),
                         ('12. ', 'Conclusiones y recomendaciones')], size=15)

    # 1 -----------------------------------------------------------------
    D.section('1', 'Resumen y método', 'Cifras clave, grupos de comparación y cómo leer los datos')
    D.kpis('Cifras clave', [('102', 'personas encuestadas'), ('45 / 11 / 45', 'financiados / no financiados / no postularon'),
                            ('47 %', 'de los 96 aprobados respondió'), ('50 / 50', '% mujeres / hombres (estimado)'),
                            ('4,41', 'disposición a colaborar (1-5)'), ('3,36', 'condiciones institucionales (1-5)'),
                            ('48 %', 'financiados: sin 4U no habría proyecto'), ('77 %', 'barrera: falta de tiempo')], SRC)
    D.text('Cómo leer esta presentación', [
        ('Grupos. ', 'Financiado (E2 = financiada por 4U, 45), postuló sin financiación (11) y no postuló (45). Un caso no recuerda su resultado.'),
        ('Escalas. ', 'Las escalas de 5 puntos van de 1 (más bajo) a 5 (más alto). "Favorable" = 4 o 5. "No sé" y "No aplica" no entran en medias.'),
        ('Sexo y edad. ', 'La encuesta no pregunta ninguno de los dos. El sexo se estimó por el primer nombre; la edad no se puede reportar.'),
        ('Muestra. ', 'Pequeña y voluntaria: márgenes de error de ±9 puntos (toda la muestra) y ±14 (financiados). Solo 2 diferencias de ítems resisten la corrección por comparaciones múltiples.'),
        ('Verificación. ', '37 cifras recalculadas desde los datos crudos y 3.640 celdas contrastadas con la plataforma.'),
    ], SRC, size=15)
    D.two('La encuesta llegó a las cuatro universidades, con más peso de Uninorte', P['grupos_uni'], P['fechas'],
          ['Uninorte aporta 42 personas; CESA 12. Las respuestas llegaron entre el 22 de septiembre y el 14 de noviembre de 2026.'], SRC)
    D.two('Responder tomó 24 minutos en la mediana; en ICESI, 36', P['dur'], P['ns'],
          ['ICESI tuvo la menor finalización (55 %). Los bloques con más "no sé" son E5, H5 e I1: lo que pasa fuera del proyecto se conoce poco.'], SRC)

    # 2 -----------------------------------------------------------------
    D.section('2', 'Quiénes respondieron', 'Sexo, trayectoria, vinculación, rango, área y dedicación')
    D.two('Paridad por sexo en la muestra; más mujeres entre financiados y rechazados', P['sexo'], P['sub_gender'] if 'sub_gender' in P else P['gender'],
          ['Las mujeres son el 56 % de los financiados encuestados, frente a 44,8 % de los aprobados según EAFIT y 40,5 % de los investigadores reconocidos en Colombia.'], SRC)
    D.chart('Las diferencias por sexo aparecen en el área y la función, no en el rango', P['sx_area'],
            ['Hombres: 18 de 24 en Ingeniería y 5 de 6 en Ciencias naturales.', 'Mujeres: 17 de 26 en Economía y 10 de 14 en Humanidades.',
             'Titulares: 10 mujeres y 10 hombres.'], SRC)
    D.two('Las mujeres ocupan más funciones de gestión y todos los roles de "integrante del equipo"', P['sx_func'], P['sx_rol'],
          ['12 de 19 personas en dirección o gestión académica son mujeres. En los proyectos, el liderazgo está repartido por igual (10 y 10).'], SRC)
    D.chart('Tres de cada cuatro tienen más de 10 años investigando', P['exp'],
            ['44 % tiene entre 11 y 20 años; 31 % más de 20; nadie menos de 3.', 'Los no financiados son los más veteranos: 45 % con más de 20 años.',
             'Promedio aproximado: 16,4 años.'], SRC)
    D.two('Predominan profesores de planta que combinan docencia e investigación', P['b6'], P['b7'],
          ['80 % de planta; 62 % docencia e investigación; solo 4 % se dedica principalmente a investigar.'], SRC)
    D.two('El rango más común es asistente; los asociados son los que menos ganan', P['b8'], P['rango'],
          ['Entre financiados, 51 % son asistentes. Los asociados tienen 62 % de éxito entre los encuestados (8 de 13), sin diferencia significativa.'], SRC)
    D.chart('Economía e Ingeniería dominan la muestra', P['area'],
            ['26 en Economía y negocios, 24 en Ingeniería.', 'EAFIT, clasificando por título, encuentra 30 % de Ciencias sociales entre los aprobados: la gente se ubica en áreas distintas a su título.'], SRC)
    D.two('La investigación ocupa una fracción pequeña de la jornada', P['b11'], P['ded'],
          ['73 % dedica 40 % o menos; promedio aproximado 29 %. A más dedicación, más socios y más experiencias interinstitucionales (rho≈0,31-0,33).'], SRC)

    # 3 -----------------------------------------------------------------
    D.section('3', 'Colaboración en general', 'Disposición, valor percibido, condiciones institucionales y cambio en capacidades')
    D.chart('La disposición a colaborar es casi unánime', P['lk_C1'],
            ['93-95 % confía en otras universidades, cree útil colaborar y se siente preparado.', 'Lo más bajo: sentirse parte de una comunidad 4U (75 %) y sentirse capaz de coordinar (79 %).',
             'CESA tiene los valores más bajos en utilidad y comunidad.'], SRC)
    D.chart('Los proyectos conjuntos se ven más visibles, no necesariamente de más calidad', P['lk_C2'],
            ['91 % ve mayor alcance y visibilidad; 85 % mayor integración de conocimientos.', 'Solo 64 % cree que la calidad científica es mayor; 34 % la ve similar.'], SRC)
    D.chart('Las condiciones institucionales son lo peor evaluado de toda la encuesta', P['lk_C3'],
            ['Solo 26 % dice que su carga permite participar y 33 % que los trámites ayudan.', 'Es igual en financiados y no financiados, y en las cuatro universidades: es estructural.'], SRC)
    D.chart('Las capacidades de colaboración crecieron desde 2021', P['lk_C4'],
            ['81 % aumentó su capacidad de producir conocimiento colaborativo.', 'Lo que menos creció: gestionar proyectos con reglas administrativas distintas (64 %).',
             'Los más veteranos reportan menos cambio.'], SRC)
    D.chart('Entre grupos, las mayores diferencias están en la evaluación de la convocatoria', P['idx_grupos'],
            ['C1-C4 casi no cambian entre grupos.', 'E4 y E8 separan a financiados de rechazados (p<0,05 sin corregir).'], SRC)

    # 4 -----------------------------------------------------------------
    D.section('4', 'Trayectoria y relación con la Alianza', 'Conocimiento, canales, socios, actividades y producción declarada')
    D.two('Casi todos conocen la Alianza, pero pocos de quienes no se postularon la conocen a fondo', P['d2'], P['mu_D4'],
          ['64 % de financiados conoce bastante o a fondo la Alianza, frente a 21 % de los no postulantes. El canal principal es la comunicación institucional (83 %).'], SRC)
    D.chart('Una parte de quienes no se postularon solo recibió información', P['d3'],
            ['15 personas recibieron información y no participaron; 12 solo habían oído hablar de la Alianza.', 'Es la reserva de nuevos postulantes.'], SRC)
    D.chart('Uninorte es el socio más mencionado', P['mu_D5'],
            ['61 % colaboró con Uninorte, 47 % con ICESI, 44 % con EAFIT, 20 % con CESA.', 'Ningún financiado declara cero colaboración; 18 % de los no postulantes sí.'], SRC)
    D.chart('Los financiados ejecutan, publican y formulan con otras universidades mucho más', P['mu_D6'],
            ['Ejecución de proyectos: 93 % frente a 25 % de los no postulantes.', 'Desarrollo tecnológico: raro en todos (14 %).'], SRC)
    D.chart('Desde 2021: ~210 propuestas, ~140 proyectos y ~212 productos con otra universidad', P['d7'],
            ['Estimación por puntos medios de rangos; puede contar dos veces productos con varios coautores encuestados.', 'Financiados: 12,3 experiencias; no postulantes: 6,2.'], SRC)
    D.chart('La Alianza financió también a quienes no tenían experiencia interinstitucional', P['d8'],
            ['42 % no había hecho proyectos interinstitucionales antes de 2021.', '18 de 20 postulantes sin esa experiencia fueron financiados.'], SRC)

    # 5 -----------------------------------------------------------------
    D.section('5', 'Convocatorias', 'Postulación, diseño, proceso, retroalimentación y aprendizajes')
    D.two('La mayoría participó directamente; un tercio fue investigador principal', P['e1'], P['bar_E3'],
          ['79 % participó directamente en la propuesta; 35 % fue IP y 56 % coinvestigador.'], SRCP)
    D.two('80 % de los postulantes encuestados fue financiado; no es la tasa del programa', P['e2'], P['exito'],
          ['Intervalo de 68 % a 89 %. La encuesta incluye solo 11 rechazados. Los IP tienen 90 % de éxito; los integrantes de equipo 60 %.'], SRCP)
    D.chart('Por área, el éxito varía, pero con muy pocos casos', P['exito_area'],
            ['Ciencias sociales: 3 de 7. Con área autodeclarada y n tan pequeño, el dato no es concluyente.', 'EAFIT encuentra que Ciencias sociales es el área con más aprobados.'], SRCP)
    D.chart('Objetivos y requisitos claros; tiempo de preparación corto', P['lk_E4'],
            ['94 % considera claros los objetivos.', 'Solo 55 % cree que el tiempo para preparar la propuesta fue suficiente.'], SRCP)
    D.chart('El proceso se valora bien, salvo trámites y acompañamiento', P['lk_E5'],
            ['Comunicación de la decisión: 88 % buena o muy buena.', 'Procedimientos administrativos: 53 %. Formalización en EAFIT: la más baja (3,09).'], SRCP)
    D.chart('Los rechazados ven menos claros los criterios y la decisión', P['e_compare'],
            ['Criterios de evaluación: 3,78 frente a 4,49.', 'Comunicación de la decisión: 3,75 frente a 4,39.', 'Dirección consistente, aunque no resiste la corrección por pruebas múltiples.'], SRCP)
    D.chart('Casi nadie recibió retroalimentación detallada', P['bar_E6'],
            ['12 % detallada, 23 % general, 32 % ninguna, 33 % no recuerda.', 'Solo 3 de 45 pudieron opinar sobre la convocatoria.'], SRCP)
    D.chart('Formular la propuesta ayudó a afinar el problema, aun sin financiación', P['lk_E8'],
            ['74 % dice que ayudó a precisar la pregunta de investigación.', 'Los rechazados reportan menos aprendizaje (3,21 frente a 3,92).'], SRCP)
    D.chart('Sin financiación, los equipos se disuelven', P['mu_E9'],
            ['5 de 8 equipos no financiados dejaron de trabajar juntos.', 'Ninguno volvió a presentar la propuesta ni consiguió otra fuente.'], 'Fuente: encuesta Alianza 4U, no financiados (n=8).')

    # 6 -----------------------------------------------------------------
    D.section('6', 'Proyectos financiados', 'Estado, gobernanza, coordinación, relaciones, consolidación y balance')
    D.chart('La mayoría terminó, pero con productos pendientes', P['bar_F1'],
            ['42 % finalizó con productos en desarrollo; 28 % en ejecución; 28 % cerró formalmente.', 'EAFIT solo encuentra cierre verificable sin pendientes en 3 de 23 proyectos.'], SRCF)
    D.two('Gobernanza y relaciones: los bloques mejor valorados', P['lk_F2'], P['lk_F4'],
          ['91 % sabía quién decidía; 86 % vio capacidades complementarias. Ojo: 42 % respondió "Completamente" a todo (ver subtexto).'], SRCF)
    D.two('Coordinación buena; institucionalización débil', P['lk_F3'], P['lk_F5'],
          ['27 % dice que el proyecto dependió de acuerdos personales; 28 % que la colaboración no siguió después.'], SRCF)
    D.two('Más esfuerzo que un proyecto propio, pero con balance positivo', P['bar_F6'], P['bar_F7'],
          ['53 % percibe más esfuerzo de coordinación. 58 % dice que los beneficios superaron las dificultades; 14 % lo contrario.'], SRCF)

    # 7 -----------------------------------------------------------------
    D.section('7', 'Capacidades, productos y uso', 'Lo que se fortaleció, lo que se produjo y quién lo usa')
    D.chart('Capacidades científicas fortalecidas en grado moderado-alto', P['lk_G1'],
            ['Lo más fortalecido: combinar metodologías (71 %).', 'Lo menos: coordinar equipos de varias instituciones (58 %).'], SRCF)
    D.two('Capacidades institucionales y aprendizaje: más débiles en CESA', P['lk_G2'], P['lk_G3'],
          ['Fortalecer el propio grupo: 51 %. Convertir aprendizajes en prácticas para otros: 57 %.'], SRCF)
    D.chart('Casi todos los proyectos prometen artículos; pocos los reportan terminados', P['h1'],
            ['Artículos previstos en 98 %, completados en 38 %.', 'Lo más completado: divulgación (50 %) e informes técnicos (48 %).', 'Patentes y prototipos: marginales.'], SRCF)
    D.two('Los artículos se escriben entre universidades; los productos se califican muy alto', P['mu_H2'], P['lk_H3'],
          ['90 % hace artículos con al menos dos universidades 4U. 98 % califica de calidad alta o muy alta sus productos.'], SRCF)
    D.two('Los resultados circulan sobre todo en la academia', P['mu_H4'], P['mu_H6'],
          ['Publicaciones (74 %) y congresos (67 %). Reuniones con usuarios: 19 %. 19 % de proyectos sin actores externos.'], SRCF)
    D.chart('Fuera de la academia, el uso de resultados es casi nulo', P['h5'],
            ['Entidades públicas: 3 % reporta uso. Empresas: 3 %.', 'Comunidades: 50 % tuvo alguna interacción, 6 % usó resultados.'], SRCF)
    D.two('El conocimiento se usa para seguir investigando y enseñar', P['mu_H7'], P['mu_H8'],
          ['Nuevas investigaciones 74 %, docencia 62 %, políticas 17 %. 26 % no tiene ninguna evidencia de uso.'], SRCF)

    # 8 -----------------------------------------------------------------
    D.section('8', 'Impacto y adicionalidad', 'Contribuciones, madurez de los resultados y qué habría pasado sin la Alianza')
    D.chart('Las contribuciones son el bloque más bajo de los financiados', P['lk_I1'],
            ['Índice 3,50.', 'Cambios en prácticas o decisiones: 32 % alto o decisivo.', 'Responder a una problemática relevante: 64 %.'], SRCF)
    D.two('Los resultados más importantes aún son jóvenes y de alcance interno', P['bar_I2'], P['bar_I3'],
          ['45 % incipiente o no observable; solo 21 % establecido. El alcance típico: varias universidades 4U (29 %).'], SRCF)
    D.two('Alta adicionalidad percibida', P['bar_I5'], P['mu_I6'],
          ['48 %: sin 4U el proyecto no habría existido. Lo atribuido a la Alianza: financiación (93 %) y equipo (79 %).'], SRCF)
    D.two('Continuidad incierta; efectos no previstos positivos', P['bar_I4'], P['bar_I7'],
          ['52 % ve probable que todo siga sin nueva financiación; 29 % lo ve improbable. 57 % reporta efectos no previstos positivos.'], SRCF)
    D.chart('La buena gobernanza va de la mano con mejores resultados', P['corr'],
            ['Consolidación (F5) con capacidades (G1): rho=0,67.', 'Relaciones (F4) con contribuciones (I1): 0,61.', 'Correlación no es causalidad: también refleja respuestas uniformes.'], SRCF)
    D.chart('Lo más significativo: publicaciones, formación y comparaciones regionales', P['txt_I8'],
            ['Casos: hoja de ruta de amoníaco verde, monitoreo de aves con el Humboldt, datos de informalidad en cuatro ciudades, encuesta a 2.200 estudiantes.'], SRCF)

    # 9 -----------------------------------------------------------------
    D.section('9', 'Futuro y barreras', 'Intención de participar, intereses, dificultades y prioridades')
    D.two('Los financiados quieren repetir y liderar', P['j12'], P['j12u'],
          ['72 % de financiados ve probable volver a colaborar; 65 % liderar. Entre los rechazados domina la indecisión.'], SRC)
    D.chart('Interés principal: más proyectos y más publicaciones', P['mu_J3'],
            ['80 % proyectos, 74 % publicaciones, 61 % movilidad.', 'Los no postulantes prefieren la docencia conjunta (66 %).'], SRC)
    D.chart('El tiempo es la barrera, lejos de cualquier otra', P['mu_J4'],
            ['77 % falta de tiempo; 38 % trámites; 38 % financiación; 37 % encontrar socios.', 'Tres personas mencionan la jubilación.'], SRC)
    D.chart('Lo que piden: encontrar socios y unificar trámites', P['mu_J5'],
            ['52 % facilitar socios; 41 % armonizar procedimientos; 32 % difundir mejor.', 'Los rechazados piden retroalimentación (36 %).'], SRC)
    D.chart('En sus palabras: ampliar temas, simplificar trámites y conocerse', P['txt_J6'],
            ['"Contar con un único proceso administrativo entre las 4 universidades."', '"¿Encuentro anual de investigadores de la red?"'], SRC)
    D.two('Diferencias por sexo y experiencia: pequeñas y exploratorias', P['idx_sexo'], P['idx_exp'],
          ['Ningún índice difiere significativamente. Las mujeres financiadas valoran algo peor la gobernanza (F2 4,14 frente a 4,63).'], SRC)
    D.chart('Las cuatro universidades se parecen más de lo que difieren', P['idx_uni'],
            ['Ninguna diferencia de índice entre universidades es significativa.', 'CESA tiene los valores más bajos en aprendizaje (G3) y Uninorte los más altos en varios índices de proyecto.'], SRC)

    # 10 ----------------------------------------------------------------
    D.section('10', 'Comparación con EAFIT, verificación y efecto ajustado', 'Rangos armonizados, representatividad y réplica de las estrategias de EAFIT')
    D.chart('Con los mismos rangos, coincide la universidad; difieren sexo, área y trayectoria', P['harm'],
            ['Universidad: diferencias < 5 pp.', 'Sexo: +11 pp de mujeres (respondieron más).', 'Área y trayectoria: se miden distinto (título frente a autodeclaración; pregrado frente a experiencia investigativa).'], SRCE)
    D.chart('La encuesta cubre al 47 % de los aprobados', P['cov'],
            ['Más cobertura en CESA (57 %) y mujeres (58 %); menos en Uninorte (42 %) y hombres (40 %).', 'Ponderar por universidad y sexo cambia los indicadores en menos de 5 pp.'], SRCE)
    D.chart('Ajustando por perfil: más colaboración, no más productos', P['eff'],
            ['Colaborar con otra universidad 4U y ejecutar proyectos con ella: efecto significativo.', 'Publicaciones conjuntas: +18 a +28 pp, no concluyente.', 'Coincide con EAFIT: no aumenta la cantidad de productos.'], SRCE)
    v = verification_summary()[0]
    D.table('Verificación: los números se sostienen', v, 'Fuente: comparación de la base exportada con las tablas de la plataforma.', size=12,
            note='Las diferencias se deben a 16 perfiles parciales que la plataforma cuenta y no exportó. Con ellos, el perfil cambia como máximo 3,3 pp. Además, 37 cifras de los informes se recalcularon desde los datos crudos y todas coinciden.')

    # 11 ----------------------------------------------------------------
    D.section('11', 'Análisis de subtexto', 'Lo que los datos dicen sin decirlo, leído con el contexto de la investigación en Colombia')
    D.chart('Contexto: la Alianza financia investigación en un país que invierte muy poco y cada vez menos', P['ctx'],
            ['I+D en Colombia: 0,21 % del PIB (2022), frente a 2,71 % en la OCDE.', 'MinCiencias pasó de ~485 mil millones (2023) a ~300 mil millones (2025).',
             'Los COP 5.512 millones de 4U equivalen a ~1,8 % de un año de MinCiencias: poco en el país, mucho para estos equipos.'],
            'Fuentes: CONPES 4145 vía Ámbito Jurídico; El Tiempo; El Espectador; presentación EAFIT.')
    D.chart('El subtexto del "sí a todo": muchas respuestas uniformes en los bloques de autoevaluación', P['straight'],
            ['42 % respondió igual todos los ítems de gobernanza (F2) y relaciones (F4); 50 % en la calidad de sus productos (H3).',
             'Sin ellos, F2 baja de 4,36 a 3,93 y F5 de 4,02 a 3,69.', 'Las condiciones institucionales (C3) casi no tienen respuestas uniformes: ahí sí se piensa la respuesta.'])
    D.chart('Se declara más de lo que se puede mostrar', P['gaps'],
            ['98 % califica alta la calidad de sus productos; 62 % tiene alguna evidencia de uso.', '13 de 41 financiados valoran alto sus productos y a la vez no tienen evidencia o no saben.',
             'La encuesta subestima los artículos (38 %) frente a EAFIT (61 %): el investigador no cuenta "sometido" como terminado.'], SRCE)
    D.two('Uninorte es el centro de la red; CESA, la periferia', P['net'], P['cent'],
          ['Uninorte es nombrada como socia por 63 % de las personas de otras universidades y participa en los 23 proyectos (EAFIT). CESA: 11 %. EAFIT casi no colabora con CESA (5 %).'], SRCE)
    D.chart('Un núcleo pequeño concentra las victorias', P['conc'],
            ['5 investigadores ganaron las 4 convocatorias y suman 14 % de las participaciones; 17 de 96 repiten.',
             'Es el patrón del "efecto Mateo": quien gana una vez tiene más probabilidad de volver a ganar (Bol et al., 2018, PNAS).',
             'Encaja con la queja de "dificultad para encontrar socios": la red funciona, pero entre conocidos.'],
            'Fuentes: presentación EAFIT; Bol, de Vaan y van de Rijt (2018).')
    D.chart('En las propuestas abiertas, la palabra que pesa es "administrativo"', P['lex'],
            ['El lenguaje es de fricción: "desgastante", "la firma de un abogado", "fechas de cierre diferentes".',
             '15 % compara implícitamente a su universidad con las demás ("en la Icesi... no aplica"): la Alianza aún se vive como cuatro sistemas.'], SRC)
    D.table('Pocas líneas de proyecto dominan la narrativa de resultados', ST.flagship_table(), SRCF, colw=[6.2, 2.6, 3.5], size=12,
            note='La economía informal y la IA en el aprendizaje aparecen en varias respuestas: los 45 financiados representan menos de 23 proyectos, y algunos pesan doble en los promedios.')
    D.text('Lectura de subtexto: seis ideas', [
        ('1. Voluntad sin tiempo. ', 'La brecha más grande (42 pp) es entre querer colaborar y poder hacerlo. En Colombia, la docencia sostiene financieramente a las universidades privadas; la investigación compite con la carga lectiva. La Alianza financia proyectos, no tiempo.'),
        ('2. Métrica que moldea la producción. ', 'El modelo de medición de MinCiencias premia artículos indexados; los proyectos se diseñan para artículos (98 %) y casi nunca para patentes, prototipos o uso externo (3 %).'),
        ('3. Autoevaluación generosa. ', 'Los bloques sobre el propio proyecto tienen más respuestas uniformes y puntajes más altos que los bloques sobre la institución. Las cifras de gobernanza e impacto deben leerse como techo.'),
        ('4. Memoria institucional débil. ', '33-40 % no recuerda si recibió retroalimentación u opinó; 26 % de proyectos sin estado verificable según EAFIT. La Alianza deja menos rastro documental del que deja en la experiencia.'),
        ('5. Red con centro y periferia. ', 'Uninorte articula; CESA, la más pequeña y especializada en negocios, queda al margen. Las brechas de CESA en utilidad y comunidad reflejan su posición en la red, no solo su opinión.'),
        ('6. Género: mejor que el país, con matices. ', 'La Alianza aprueba más mujeres (44,8 %) que el promedio nacional de investigadores reconocidos (40,5 %), y ellas responden más. Pero valoran peor la gobernanza y ocupan los roles de apoyo.'),
    ], 'Fuentes: encuesta; presentación EAFIT; MinCiencias; La República; El Colombiano; Romero (2019).', size=13)
    D.chart('El grupo con más potencial: 27 no postulantes con intención de colaborar', P['pot'],
            ['16 de ellos solo habían recibido información.', '70 % hombres; 12 de Uninorte.', 'Barreras: tiempo (78 %), financiación (48 %), socios (44 %).'], SRC)

    # 12 ----------------------------------------------------------------
    D.section('12', 'Conclusiones y recomendaciones')
    D.text('Conclusiones', [
        'La comunidad quiere colaborar; las universidades no le dan el tiempo ni los trámites para hacerlo.',
        'La Alianza aumenta la colaboración entre las cuatro universidades y probablemente la publicación conjunta, pero no la cantidad de productos (encuesta y EAFIT coinciden).',
        'Las convocatorias son claras, pero con poco tiempo, poca retroalimentación y sin canal para mejorarlas.',
        'Los proyectos tienen buena gobernanza interna y débil institucionalización; los resultados son académicos y todavía incipientes.',
        'Sin financiación, los equipos se disuelven; con financiación, un núcleo pequeño gana repetidamente.',
        'Las autoevaluaciones de los proyectos son altas y uniformes: el impacto real probablemente es menor que el declarado.',
    ], SRC, size=15)
    D.table('Recomendaciones', pd.DataFrame([
        ['Descarga académica acordada entre las 4 universidades', '77 % cita falta de tiempo'],
        ['Ventanilla y calendario administrativo comunes', '41 % lo prioriza; "fricción administrativa" en 24 % de textos'],
        ['Directorio y encuentros de emparejamiento', '52 % lo prioriza; red concentrada en Uninorte'],
        ['Retroalimentación detallada y canal de opinión', '12 % la recibió detallada'],
        ['Capital semilla para equipos no financiados', '5 de 8 se disolvieron'],
        ['Fondo de cierre de artículos y continuidad', '55 % de artículos en desarrollo'],
        ['Exigir y financiar vinculación temprana de usuarios', '3 % de uso por entidades públicas y empresas'],
        ['Cupos o puntos para nuevos investigadores y para CESA', '5 personas ganaron las 4 convocatorias'],
        ['Contactar a los 27 postulantes potenciales', '16 solo recibieron información'],
        ['Unir encuesta y base bibliométrica; medir con evidencia', '96 % autorizó vincular sus datos'],
    ], columns=['Recomendación', 'Evidencia']), SRCE, colw=[7.3, 5.0], size=12)
    D.text('Fuentes de contexto', [f'{a}: {b}' for a, b in ST.SOURCES], '', size=10)
    D.save(OUT)
    print('ok', OUT, D.n, 'diapositivas')


if __name__ == '__main__':
    build()
