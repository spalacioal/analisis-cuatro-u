"""Utilidades para construir documentos Word con python-docx."""
import pandas as pd
import numpy as np
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x2E, 0x75, 0xB6)


class Doc:
    def __init__(self):
        self.d = Document()
        st = self.d.styles['Normal']
        st.font.name = 'Calibri'
        st.font.size = Pt(10.5)
        st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.line_spacing = 1.12
        for lvl, size in [(1, 16), (2, 13), (3, 11.5)]:
            h = self.d.styles[f'Heading {lvl}']
            h.font.name = 'Calibri'
            h.font.size = Pt(size)
            h.font.color.rgb = NAVY if lvl < 3 else BLUE
            h.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
        sec = self.d.sections[0]
        sec.left_margin = sec.right_margin = Cm(2.2)
        sec.top_margin = sec.bottom_margin = Cm(2)
        self.fig_n = 0
        self.tab_n = 0
        self._footer()

    def _footer(self):
        p = self.d.sections[0].footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        for t, txt in [('begin', None), (None, 'PAGE'), ('end', None)]:
            if t:
                e = OxmlElement('w:fldChar')
                e.set(qn('w:fldCharType'), t)
                run._r.append(e)
            else:
                e = OxmlElement('w:instrText')
                e.set(qn('xml:space'), 'preserve')
                e.text = txt
                run._r.append(e)
        run.font.size = Pt(8)

    def cover(self, title, subtitle, lines):
        for _ in range(6):
            self.d.add_paragraph()
        p = self.d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title)
        r.bold = True
        r.font.size = Pt(24)
        r.font.color.rgb = NAVY
        p = self.d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(subtitle)
        r.font.size = Pt(14)
        r.font.color.rgb = BLUE
        for _ in range(4):
            self.d.add_paragraph()
        for l in lines:
            p = self.d.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run(l).font.size = Pt(11)
        self.d.add_page_break()

    def toc(self):
        self.h('Contenido', 1)
        p = self.d.add_paragraph()
        run = p.add_run()
        for t, txt in [('begin', None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ('separate', None)]:
            if t:
                e = OxmlElement('w:fldChar')
                e.set(qn('w:fldCharType'), t)
                run._r.append(e)
            else:
                e = OxmlElement('w:instrText')
                e.set(qn('xml:space'), 'preserve')
                e.text = txt
                run._r.append(e)
        r2 = p.add_run('Haga clic derecho aquí y elija "Actualizar campo" para ver la tabla de contenido con números de página.')
        r2.italic = True
        e = OxmlElement('w:fldChar')
        e.set(qn('w:fldCharType'), 'end')
        r2._r.append(e)
        self.d.add_page_break()

    def h(self, text, lvl=1):
        return self.d.add_heading(text, lvl)

    def p(self, text, bold_prefix=None, italic=False, size=None):
        para = self.d.add_paragraph()
        if bold_prefix:
            para.add_run(bold_prefix).bold = True
        r = para.add_run(text)
        r.italic = italic
        if size:
            r.font.size = Pt(size)
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        return para

    def bullets(self, items, style='List Bullet'):
        for it in items:
            para = self.d.add_paragraph(style=style)
            if isinstance(it, tuple):
                para.add_run(it[0]).bold = True
                para.add_run(it[1])
            else:
                para.add_run(it)

    def note(self, text):
        para = self.d.add_paragraph()
        r = para.add_run(text)
        r.italic = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0x59, 0x59, 0x59)

    def img(self, path, width=16, caption=None):
        self.d.add_picture(path, width=Cm(width))
        self.d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption:
            self.fig_n += 1
            c = self.d.add_paragraph()
            c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = c.add_run(f'Figura {self.fig_n}. {caption}')
            r.italic = True
            r.font.size = Pt(8.5)

    def table(self, df, caption=None, widths=None, font=8, fmt=None, header_bg='1F3864'):
        df = df.copy()
        if caption:
            self.tab_n += 1
            c = self.d.add_paragraph()
            r = c.add_run(f'Tabla {self.tab_n}. {caption}')
            r.bold = True
            r.font.size = Pt(9)
            c.paragraph_format.keep_with_next = True
        t = self.d.add_table(rows=1, cols=len(df.columns))
        t.style = 'Table Grid'
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for j, col in enumerate(df.columns):
            cell = t.rows[0].cells[j]
            cell.text = ''
            run = cell.paragraphs[0].add_run(str(col))
            run.bold = True
            run.font.size = Pt(font)
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            sh = OxmlElement('w:shd')
            sh.set(qn('w:val'), 'clear')
            sh.set(qn('w:fill'), header_bg)
            cell._tc.get_or_add_tcPr().append(sh)
        for i, row in enumerate(df.itertuples(index=False)):
            cells = t.add_row().cells
            for j, v in enumerate(row):
                if isinstance(v, float):
                    if np.isnan(v):
                        s = '–'
                    elif float(v).is_integer() and abs(v) >= 1 and not (fmt and fmt.get(df.columns[j])):
                        s = f'{int(v)}'
                    else:
                        s = (fmt or {}).get(df.columns[j], '{:.1f}').format(v)
                    s = s.replace('.', ',')
                else:
                    s = str(v)
                cells[j].text = ''
                run = cells[j].paragraphs[0].add_run(s)
                run.font.size = Pt(font)
                if i % 2 == 1:
                    sh = OxmlElement('w:shd')
                    sh.set(qn('w:val'), 'clear')
                    sh.set(qn('w:fill'), 'EAF0F8')
                    cells[j]._tc.get_or_add_tcPr().append(sh)
        if widths:
            for row in t.rows:
                for j, wd in enumerate(widths):
                    row.cells[j].width = Cm(wd)
        self.d.add_paragraph()
        return t

    def kpis(self, items, cols=3):
        rows = (len(items) + cols - 1) // cols
        t = self.d.add_table(rows=rows, cols=cols)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for k, (val, lab) in enumerate(items):
            cell = t.rows[k // cols].cells[k % cols]
            cell.text = ''
            pr = cell.paragraphs[0]
            pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = pr.add_run(str(val))
            r.bold = True
            r.font.size = Pt(18)
            r.font.color.rgb = NAVY
            p2 = cell.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r2 = p2.add_run(lab)
            r2.font.size = Pt(8.5)
            sh = OxmlElement('w:shd')
            sh.set(qn('w:val'), 'clear')
            sh.set(qn('w:fill'), 'EAF0F8')
            cell._tc.get_or_add_tcPr().append(sh)
        self.d.add_paragraph()

    def pagebreak(self):
        self.d.add_page_break()

    def save(self, path):
        self.d.save(path)
