"""Genera el libro de Excel con toda la estadística."""
import numpy as np
import pandas as pd
from analysis import *
from extend import *

OUT = '/projects/sandbox/analisis-cuatro-u/resultados/Estadisticas_Alianza_4U.xlsx'


def build(E1, E2):
    W = pd.ExcelWriter(OUT, engine='xlsxwriter')
    wb = W.book
    f_title = wb.add_format({'bold': True, 'font_size': 14, 'font_color': '#1F3864'})
    f_sub = wb.add_format({'bold': True, 'font_size': 11, 'font_color': '#2E75B6'})
    f_hdr = wb.add_format({'bold': True, 'bg_color': '#1F3864', 'font_color': 'white', 'text_wrap': True,
                           'valign': 'top', 'border': 1})
    f_wrap = wb.add_format({'text_wrap': True, 'valign': 'top'})
    f_note = wb.add_format({'italic': True, 'font_color': '#595959', 'text_wrap': True})
    index_rows = []

    def put(sheet, blocks, desc):
        """blocks: lista de (subtítulo, DataFrame, nota)."""
        ws = wb.add_worksheet(sheet)
        W.sheets[sheet] = ws
        ws.write(0, 0, desc, f_title)
        row = 2
        maxw = {}
        for sub, t, note in blocks:
            ws.write(row, 0, sub, f_sub)
            row += 1
            if note:
                ws.write(row, 0, note, f_note)
                row += 1
            t = t.copy()
            row_h = row
            for j, c in enumerate(t.columns):
                ws.write(row_h, j, str(c), f_hdr)
            t.to_excel(W, sheet_name=sheet, startrow=row_h + 1, index=False, header=False)
            for j, c in enumerate(t.columns):
                w = max([len(str(c))] + [len(str(x)) for x in t[c].head(200)])
                maxw[j] = max(maxw.get(j, 8), min(w + 2, 60))
            row = row_h + len(t) + 3
        for j, w in maxw.items():
            ws.set_column(j, j, w, f_wrap if w >= 60 else None)
        ws.freeze_panes(2, 1)
        index_rows.append((sheet, desc))
        return ws

    # ---------------- 0 Notas
    notes = pd.DataFrame({'Aspecto': [
        'Fuente', 'Unidad de análisis', 'Registros analizados', 'Grupos de comparación', 'Universidad',
        'Sexo', 'Edad', 'Escalas Likert', 'Índices', 'Pruebas estadísticas', 'Selección múltiple',
        'Cantidades (D7, D8)', 'Experiencia y dedicación', 'Flujo de la encuesta', 'Confidencialidad', 'Cautela'],
        'Detalle': [
        'Exportaciones de la plataforma de encuestas: Resultados CESA, EAFIT, ICESI y Uninorte (hoja "Datos sin procesar"). Cuestionario: "Contenido encuesta alianza 4U.pdf".',
        'Persona encuestada (docente, investigador o directivo de la red 4U).',
        f'{len(df)} registros únicos ({(df[1] == "Completed").sum()} completos y {(df[1] == "Started").sum()} parciales). No hay cédulas, correos ni nombres duplicados entre archivos. Todos aceptaron participar (A1).',
        'Financiado = E2 "Fue financiada por Alianza 4U" (n=45). Postuló, no financiado = no financiada, elegible sin financiación o retirada (n=11). No postuló = no respondió la sección E (n=45). Un caso con "No recuerda el resultado" se reporta solo en totales.',
        'Se usa la universidad declarada en B4. Para 5 personas que dicen no estar vinculadas actualmente a 4U se usa la universidad del enlace de la encuesta.',
        'La encuesta NO pregunta sexo. Se estimó a partir del primer nombre (Mujer/Hombre). Es una aproximación y puede no coincidir con la identidad de género de la persona. Solo se reporta de forma agregada.',
        'La encuesta NO pregunta edad ni fecha de nacimiento. Como aproximación de trayectoria se usan los años de experiencia en investigación (B10) y el rango académico (B8).',
        'Codificación 1-5 (1 = valor más bajo, 5 = más alto). "No tengo información suficiente", "No aplica", "Todavía no es observable" se excluyen de medias y porcentajes de la escala, pero se reportan como NS/NA.',
        'IDX_xx = promedio de los ítems válidos del bloque (requiere al menos la mitad de los ítems). En F3 se excluye el ítem "No surgieron diferencias o conflictos". Confiabilidad con alfa de Cronbach.',
        'Diferencias entre grupos: Kruskal-Wallis (3+ grupos) o Mann-Whitney U (2 grupos). Asociación categórica: chi² con V de Cramér y exacta de Fisher en tablas 2x2. Correlaciones de Spearman. Significancia p<0,05; tendencia p<0,10.',
        'Porcentajes calculados sobre las personas que marcaron al menos una opción del bloque. La suma puede superar 100 %.',
        'Para estimar totales se usan puntos medios: Ninguna=0, Una=1, Dos o tres=2,5, Cuatro o cinco=4,5, Más de cinco=6. Son aproximaciones.',
        'Años aprox.: <3=1,5; 3-5=4; 6-10=8; 11-20=15,5; >20=25. Dedicación aprox.: punto medio de cada rango.',
        'Las secciones F, G, H e I se refieren al proyecto financiado y se analizan solo para el grupo Financiado. Algunas personas no financiadas respondieron G o I por fuera del flujo previsto (ver hoja Calidad de datos).',
        'La base anonimizada excluye nombre, cédula, correo, IP y metadatos de navegador. Los textos abiertos se publican sin nombres propios de personas.',
        'Muestra pequeña (12 a 42 por universidad; 11 no financiados). Las diferencias deben leerse como indicativas, no como inferencias poblacionales.']})
    put('0_Notas', [('Notas metodológicas', notes, None)], 'Notas metodológicas y definiciones')

    # ---------------- 1 Resumen KPIs
    fin = df[df['Grupo'] == 'Financiado']
    kpi = [
        ('Registros analizados', len(df)),
        ('Respuestas completas', int((df[1] == 'Completed').sum())),
        ('Financiados (aprobados)', int((df['Grupo'] == 'Financiado').sum())),
        ('Postularon y no fueron financiados', int((df['Grupo'] == 'Postuló, no financiado').sum())),
        ('No postularon', int((df['Grupo'] == 'No postuló').sum())),
        ('Éxito entre postulantes ENCUESTADOS con resultado conocido (%) (no es la tasa del programa)', round(pct(45, 56), 1)),
        ('Cobertura de la encuesta sobre los 96 aprobados (EAFIT) %', 46.9),
        ('Mujeres (estimado) %', round(pct((df['Sexo (estimado)'] == 'Mujer').sum(), len(df)), 1)),
        ('Profesores de planta o tiempo completo %', round(pct((df[35] == 'Profesor(a) de planta o tiempo completo.').sum(), len(df)), 1)),
        ('Con más de 10 años de experiencia en investigación %', round(pct(df[43].isin(['Entre 11 y 20 años.', 'Más de 20 años.']).sum(), df[43].notna().sum()), 1)),
        ('Dedican 40 % o menos a investigación %', round(pct(df[44].isin(['Ninguna.', 'Entre 1% y 20%.', 'Entre 21% y 40%.']).sum(), df[44].notna().sum()), 1)),
        ('Había escuchado de Alianza 4U %', round(pct((df[70] == 'Sí.').sum(), df[70].notna().sum()), 1)),
        ('Sin proyectos interinstitucionales antes de 2021 %', round(pct((df[104] == 'Ninguno.').sum(), df[104].notna().sum()), 1)),
        ('Índice de disposición a colaborar C1 (1-5)', round(df['IDX_C1'].mean(), 2)),
        ('Índice de condiciones institucionales C3 (1-5)', round(df['IDX_C3'].mean(), 2)),
        ('Financiados: balance beneficios > dificultades %', round(pct(fin[166].isin(SINGLE_ORDER['F7'][3:5]).sum(), fin[166].notna().sum()), 1)),
        ('Financiados: "sin 4U el proyecto no se habría realizado" %', round(pct((fin[265] == 'Probablemente el proyecto no se habría realizado.').sum(), fin[265].notna().sum()), 1)),
        ('Financiados: artículos científicos completados %', round(pct((fin[184] == 'Completado').sum(), fin[184].notna().sum()), 1)),
        ('Probable o muy probable participar en 2 años (J1) %', round(pct(df[282].isin(['Probable.', 'Muy probable.']).sum(), df[282].notna().sum()), 1)),
        ('Barrera principal: falta de tiempo o carga académica %', round(pct(df[295].notna().sum(), df[list(range(295, 310))].notna().any(axis=1).sum()), 1)),
        ('Autorizan ser contactados para entrevista %', round(pct((df[322] == 'Sí.').sum(), df[322].notna().sum()), 1)),
    ]
    put('1_Resumen', [('Indicadores clave', pd.DataFrame(kpi, columns=['Indicador', 'Valor']), None)], 'Resumen de indicadores clave')

    # ---------------- 2 Participación
    q = pd.DataFrame(QUALITY, columns=['Secciones', 'Contenido', 'Personas no financiadas que respondieron'])
    put('2_Participacion', [
        ('Respuestas por encuesta (enlace de cada universidad)', participation(),
         'Las cifras "plataforma" provienen de la hoja Estadísticas generales; la base exportada contiene menos registros incompletos.'),
        ('Universidad declarada (B4) según enlace de la encuesta', pd.crosstab(df['Encuesta'], df[32].fillna('Sin dato'), margins=True, margins_name='Total').reset_index(), None),
        ('Respuestas por grupo y universidad', pd.crosstab(df['Universidad'], df['Grupo'], margins=True, margins_name='Total').reset_index(), None),
    ], 'Participación, cobertura y grupos')

    # ---------------- 3 Perfil
    blocks = []
    for code, col, lab, pop in SINGLE[:8]:
        blocks.append((f'{code}. {lab} – por grupo', single_table(code, col, 'Grupo'), None))
        blocks.append((f'{code}. {lab} – por universidad', single_table(code, col, 'Universidad'), None))
        blocks.append((f'{code}. {lab} – por sexo (estimado)', single_table(code, col, 'Sexo'), None))
    blocks.insert(0, ('Sexo (estimado por nombre) – por grupo', single_table('SX', 'Sexo (estimado)', 'Grupo'),
                      'Estimación a partir del primer nombre; la encuesta no pregunta sexo.'))
    blocks.insert(1, ('Sexo (estimado por nombre) – por universidad', single_table('SX', 'Sexo (estimado)', 'Universidad'), None))
    blocks.insert(2, ('Sexo (estimado) – por experiencia', single_table('SX', 'Sexo (estimado)', 'Experiencia'), None))
    oth = []
    for c, lab in [(34, 'B5 Otra facultad'), (36, 'B6 Otra vinculación'), (38, 'B7 Otra función'), (40, 'B8 Otro rango'), (42, 'B9 Otra área')]:
        for v in df[c].dropna():
            oth.append({'Pregunta': lab, 'Respuesta "Otra"': v})
    blocks.append(('Respuestas "Otra ¿cuál?" del perfil', pd.DataFrame(oth), None))
    put('3_Perfil', blocks, 'Perfil sociodemográfico y académico (sección B)')

    # ---------------- 4 Cruces
    cr = []
    for a, b, lab in [('Sexo (estimado)', 'Rango (agrupado)', 'Sexo × rango académico'),
                      ('Sexo (estimado)', 'Experiencia (agrupada)', 'Sexo × experiencia'),
                      ('Sexo (estimado)', 41, 'Sexo × área de conocimiento'),
                      ('Sexo (estimado)', 44, 'Sexo × dedicación a investigación'),
                      ('Sexo (estimado)', 108, 'Sexo × rol en la propuesta (postulantes)'),
                      ('Rango (agrupado)', 'Experiencia (agrupada)', 'Rango × experiencia'),
                      ('Rango (agrupado)', 'Grupo', 'Rango × grupo'),
                      ('Experiencia (agrupada)', 'Grupo', 'Experiencia × grupo'),
                      (41, 'Grupo', 'Área de conocimiento × grupo'),
                      (37, 'Grupo', 'Función principal × grupo'),
                      (44, 'Grupo', 'Dedicación a investigación × grupo'),
                      (104, 'Grupo', 'Proyectos interinstitucionales antes de 2021 × grupo'),
                      (71, 'Grupo', 'Conocimiento de Alianza 4U × grupo'),
                      (41, 'Universidad', 'Área de conocimiento × universidad'),
                      ('Rango (agrupado)', 'Universidad', 'Rango × universidad'),
                      ('Experiencia (agrupada)', 'Universidad', 'Experiencia × universidad')]:
        ct = pd.crosstab(df[a].fillna('Sin dato'), df[b].fillna('Sin dato'), margins=True, margins_name='Total')
        ct.index.name = lab
        cr.append((lab + ' (n)', ct.reset_index(), None))
        cp = (pd.crosstab(df[a].fillna('Sin dato'), df[b].fillna('Sin dato'), normalize='columns') * 100).round(1)
        cp.index.name = lab
        cr.append((lab + ' (% por columna)', cp.reset_index(), None))
    put('4_Cruces', cr, 'Tablas cruzadas del perfil')

    # ---------------- 5 Tasa de éxito y asociación
    put('5_Exito_y_asociacion', [
        ('Tasa de éxito en convocatorias por perfil (postulantes con resultado conocido, n=56)', success_rate(),
         'Tasa de éxito = financiados / (financiados + no financiados). Grupos pequeños: leer con cautela.'),
        ('Asociación entre perfil y grupo de vinculación', assoc_table(), None)], 'Tasa de éxito y factores asociados a la financiación')

    # ---------------- 6 Likert global
    put('6_Likert_global', [('Estadísticos por ítem (todas las preguntas matriz)', matrix_overall(),
                             'Población: todos / postulantes / financiados según la sección.')],
        'Estadísticos descriptivos de cada ítem de escala')
    dist = matrix_dist()
    put('7_Likert_distribucion', [(f'Distribución completa – escala "{k}"', v, None) for k, v in dist.items()],
        'Distribución de frecuencias de todas las categorías por ítem')
    put('8_Likert_por_grupo', [('Ítems comparables entre grupos (secciones C, D7, E)', matrix_by('Grupo'),
                                'Media y % favorable por grupo, con prueba de diferencias.')], 'Comparación por grupo de vinculación')
    put('9_Likert_por_universidad', [('Todos los ítems por universidad', matrix_by('Universidad'), None)], 'Comparación por universidad')
    put('10_Likert_sexo_experiencia', [('Por sexo (estimado)', matrix_by('Sexo'), None),
                                       ('Por experiencia en investigación', matrix_by('Experiencia'), None)],
        'Comparación por sexo y experiencia')

    # ---------------- 11 índices
    put('11_Indices', [('Índices compuestos y confiabilidad', index_table(), None),
                       ('Índices por grupo', index_by('Grupo'), None),
                       ('Índices por universidad', index_by('Universidad'), None),
                       ('Índices por sexo (estimado)', index_by('Sexo'), None),
                       ('Índices por experiencia', index_by('Experiencia'), None),
                       ('Índices por rango académico', index_by('Rango'), None)], 'Índices compuestos por dimensión')

    # ---------------- 12 respuesta única (secciones D-J)
    blocks = []
    for code, col, lab, pop in SINGLE[8:]:
        by = 'Grupo' if pop == 'todos' else 'Universidad'
        blocks.append((f'{code}. {lab} – por {by.lower()}', single_table(code, col, by, pop), f'Población: {pop}'))
        if pop == 'todos':
            blocks.append((f'{code}. {lab} – por universidad', single_table(code, col, 'Universidad', pop), None))
        if pop == 'postulantes':
            post = single_table(code, col, 'Grupo', pop)
            post = post[[c for c in post.columns if not c.startswith('No postuló')]]
            blocks.append((f'{code}. {lab} – por grupo', post, None))
    put('12_Respuesta_unica', blocks, 'Preguntas de respuesta única (secciones A, D a J)')

    # ---------------- 13 selección múltiple
    blocks = []
    for code, title, cols, pop in MULTI:
        if pop == 'todos':
            blocks.append((f'{code}. {title} – por grupo', multi_table(code, title, cols, pop, 'Grupo'), None))
        blocks.append((f'{code}. {title} – por universidad', multi_table(code, title, cols, pop, 'Universidad'), f'Población: {pop}'))
        blocks.append((f'{code}. {title} – por sexo (estimado)', multi_table(code, title, cols, pop, 'Sexo'), None))
    put('13_Seleccion_multiple', blocks, 'Preguntas de selección múltiple')

    # ---------------- 14 producción
    put('14_Produccion', [
        ('Indicadores de colaboración y producción (todos), por grupo', production_table(),
         'Valores aproximados por puntos medios. La prueba compara los tres grupos.'),
        ('Productos de los proyectos financiados (H1, H2, H4) por universidad', production_fin(), None),
        ('H1. Estado de cada tipo de producto (financiados)', matrix_dist()['h1'], None),
        ('H8b. Evidencias citadas (enlaces y referencias)', code_text(252, {})[1][['ID', 'Universidad', 'Grupo', 'Texto (anonimizado)']], None),
    ], 'Producción académica, productos y evidencias')

    # ---------------- 15 correlaciones
    rho, pv = corr_table()
    rf, pf = corr_fin()
    put('15_Correlaciones', [('Spearman rho – todos los encuestados', rho.reset_index().rename(columns={'index': 'Variable'}), None),
                             ('p-valores', pv.reset_index().rename(columns={'index': 'Variable'}), None),
                             ('Spearman rho – solo financiados', rf.reset_index().rename(columns={'index': 'Variable'}), None),
                             ('p-valores (financiados)', pf.reset_index().rename(columns={'index': 'Variable'}), None)],
        'Correlaciones entre trayectoria, percepciones y resultados')
    ws = W.sheets['15_Correlaciones']

    # ---------------- 16 texto abierto
    blocks = []
    for code, col, themes, lab in [('J6', 321, THEMES_J6, 'Cambio propuesto para mejorar la línea de investigación'),
                                   ('I8', 280, THEMES_I8, 'Resultado más significativo del proyecto'),
                                   ('I7b', 279, THEMES_I7, 'Efectos no previstos')]:
        t, qq = code_text(col, themes)
        blocks.append((f'{code}. {lab} – temas', t, 'Codificación temática por palabras clave; una respuesta puede tener varios temas.'))
        blocks.append((f'{code}. {lab} – respuestas', qq, None))
    put('16_Texto_abierto', blocks, 'Análisis de preguntas abiertas')

    # ---------------- 17 calidad
    miss = []
    for code, col, lab, pop in SINGLE:
        m = pop_mask(pop)
        miss.append({'Pregunta': code, 'Contenido': lab, 'Población': pop, 'Población n': int(m.sum()),
                     'Respondieron': int(df.loc[m, col].notna().sum()),
                     '% sin respuesta': round(pct(m.sum() - df.loc[m, col].notna().sum(), m.sum()), 1)})
    put('17_Calidad_datos', [('Respuestas fuera del flujo previsto', q, 'Estas respuestas no se incluyen en los análisis de las secciones F a I.'),
                             ('Completitud por pregunta', pd.DataFrame(miss), None),
                             ('Duración de la encuesta (minutos)', (df[5].astype(float) / 60).describe().round(1).reset_index().rename(columns={'index': 'Estadístico', 5: 'Minutos'}), None),
                             ('Autorización de vinculación de datos (A2)', df[27].value_counts().reset_index(), None)],
        'Calidad y completitud de los datos')

    # ---------------- 19-25 ampliación
    vs, pq = verification_summary()
    vt = pd.read_pickle('/projects/sandbox/work/verify.pkl')
    vt = vt[vt['n base exportada'].notna() & (vt['Diferencia'] != 0)]
    put('18_Verificacion', [
        ('Coincidencia entre base exportada y tablas de la plataforma', vs, 'Celdas = categoría × pregunta × universidad. La plataforma incluye respuestas parciales no exportadas.'),
        ('Diferencia (plataforma − base) por pregunta de respuesta única', pq, None),
        ('Perfil: plataforma (118) frente a base exportada (102)', platform_profile(), None),
        ('Cifras de los informes recalculadas desde los datos crudos', claims(), None),
        ('Detalle de celdas con diferencia', vt, None)], 'Verificación de los datos')
    H = harmonized()
    put('19_Comparacion_EAFIT', [
        ('Encuesta (financiados) frente a la presentación de EAFIT con rangos armonizados', H, 'Ver columna Nota: varias variables no miden lo mismo.'),
        ('Trayectoria EAFIT en rangos originales (% de aprobados)', pd.DataFrame(list(EAFIT['tray_fino'].items()), columns=['Rango (años desde pregrado)', '%']), None),
        ('Resultados de impacto de EAFIT', pd.DataFrame(EAFIT['impacto'], columns=['Resultado', 'Efecto', 'IC 95 %', 'p']), None),
        ('Área (rangos EAFIT) por grupo – encuesta', single_table('AR', 'Área (rangos EAFIT)', 'Grupo'), None),
        ('Trayectoria (rangos EAFIT) por grupo – encuesta', single_table('TR', 'Trayectoria (rangos EAFIT aprox.)', 'Grupo'), None),
        ('Sexo (rangos EAFIT) por grupo – encuesta', single_table('SXE', 'Sexo (rangos EAFIT)', 'Grupo', order=['Mujeres', 'Hombres', 'No informado']), None),
        ('Área (rangos EAFIT) por universidad – encuesta', single_table('AR', 'Área (rangos EAFIT)', 'Universidad'), None)],
        'Comparación con la presentación de la oficina de inteligencia en CTeI de EAFIT')
    wi, wt = weighted_indicators()
    put('20_Representatividad', [('Cobertura sobre los 96 aprobados', coverage(), None),
                                 ('Indicadores de financiados sin ponderar y ponderados (raking por universidad y sexo)', wi, None),
                                 ('Pesos', wt, None)], 'Representatividad y ponderación')
    put('21_Efecto_ajustado', [
        ('Estrategia 1: todos los no financiados como controles', E1, 'ATT por emparejamiento 1:1 con reemplazo, exacto por universidad; IC bootstrap (500). MCO con errores robustos HC1. pp para resultados binarios.'),
        ('Estrategia 2: postulantes rechazados como controles', E2, None),
        ('Balance de covariables – estrategia 1', balance('todos'), 'DME = diferencia de medias estandarizada; |DME|<0,25 se considera aceptable.'),
        ('Balance de covariables – estrategia 2', balance('rechazados'), None)], 'Efecto ajustado de ser financiado')
    put('22_Comparaciones_multiples', [('Todas las pruebas de ítems con corrección de Benjamini-Hochberg', multiple_testing(), None)],
        'Corrección por comparaciones múltiples')
    put('23_Intervalos_confianza', [('Intervalos de confianza al 95 %', ci_table(), 'Wilson para proporciones; bootstrap (2.000) para índices.')],
        'Intervalos de confianza de las cifras principales')
    a_, prof, bar = potential()
    put('24_Postulantes_potenciales', [('Conteos', a_, None), ('Perfil (n=27)', prof, None), ('Barreras y prioridades', bar, None)],
        'No postulantes con intención de colaborar')

    # ---------------- 26 base anonimizada
    base = anonymized_base()
    for c in ['Área (rangos EAFIT)', 'Trayectoria (rangos EAFIT aprox.)', 'Sexo (rangos EAFIT)', 'Estado proyecto (rangos EAFIT)', 'Artículos (rangos EAFIT)']:
        base[c] = df[c].values
    base.to_excel(W, sheet_name='25_Base_anonimizada', index=False)
    ws = W.sheets['25_Base_anonimizada']
    for j, c in enumerate(base.columns):
        ws.write(0, j, str(c), f_hdr)
    ws.set_row(0, 60)
    ws.set_column(0, len(base.columns), 18)
    ws.freeze_panes(1, 1)
    index_rows.append(('25_Base_anonimizada', 'Base de datos unificada y anonimizada (una fila por persona)'))

    # ---------------- índice
    ws = wb.add_worksheet('Indice')
    ws.write(0, 0, 'Estadísticas – Evaluación de la línea de investigación de Alianza 4U', f_title)
    ws.write(1, 0, 'Encuestas CESA, EAFIT, ICESI y Uninorte (sep-nov 2026)', f_note)
    ws.write(3, 0, 'Hoja', f_hdr)
    ws.write(3, 1, 'Contenido', f_hdr)
    for i, (s, d) in enumerate(index_rows):
        ws.write_url(4 + i, 0, f"internal:'{s}'!A1", string=s)
        ws.write(4 + i, 1, d)
    ws.set_column(0, 0, 28)
    ws.set_column(1, 1, 80)
    ws.activate()
    wb.worksheets_objs.insert(0, wb.worksheets_objs.pop())
    W.close()
    print('ok', OUT)


if __name__ == '__main__':
    E1 = pd.read_pickle('/projects/sandbox/work/eff_todos.pkl')
    E2 = pd.read_pickle('/projects/sandbox/work/eff_rechazados.pkl')
    build(E1, E2)
