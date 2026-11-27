"""Informe técnico detallado (Word)."""
from facts import *
from docx_utils import Doc
import charts
import charts_ext
from report_ext import add_sections
from extend import harmonized, coverage

OUT = '/projects/sandbox/analisis-cuatro-u/resultados/Informe_detallado_Alianza_4U.docx'
FIN, NF, NP = 'Financiado', 'Postuló, no financiado', 'No postuló'


def compact_items(code, extra=None):
    m = matrix_overall()
    t = m[m['Bloque'] == code]
    sc = [x for x in MATRIX if x[0] == code][0][3]
    if sc in ('cant',):
        cols = ['Ítem', 'Enunciado', 'n válido (escala)', 'Media aprox. (n.º)', '% con al menos una', '% con 4 o más', 'Total estimado (n.º)']
    elif sc == 'h1':
        cols = ['Ítem', 'Enunciado', 'Respuestas', '% completado', '% en desarrollo', '% previsto (cualquier estado)']
    elif sc == 'h5':
        cols = ['Ítem', 'Enunciado', 'n válido (escala)', 'Nivel medio (0-4)', '% con alguna interacción', '% con participación activa (≥3)', '% uso efectivo (4)']
    else:
        cols = ['Ítem', 'Enunciado', 'n válido (escala)', 'NS/NA/NR', 'Media (1-5)', 'Desv. est.', '% favorable (4-5)', '% desfavorable (1-2)']
    t = t[cols].rename(columns={'n válido (escala)': 'n'})
    t['Enunciado'] = t['Enunciado'].str.rstrip('.')
    return t


def by_group_items(code):
    t = matrix_by('Grupo')
    t = t[t['Bloque'] == code]
    keep = ['Ítem'] + [c for c in t.columns if c.endswith('media')] + ['p-valor']
    t = t[keep].copy()
    t.columns = [c.replace(' media', '') for c in t.columns]
    return t.dropna(axis=1, how='all')


def by_uni_items(code):
    t = matrix_by('Universidad')
    t = t[t['Bloque'] == code]
    keep = ['Ítem'] + [c for c in t.columns if c.endswith('media')] + ['p-valor']
    t = t[keep].copy()
    t.columns = [c.replace(' media', '') for c in t.columns]
    return t


def multi_short(code, by=None):
    m = [x for x in MULTI if x[0] == code][0]
    t = multi_table(*m, by=by)
    cols = ['Opción', 'Total n', 'Total %'] + ([f'{g} %' for g in (G3 if by == 'Grupo' else UNIS)] if by else [])
    t = t[cols]
    t = t[(t['Total n'] > 0)]
    t.columns = [c.replace(' %', ' %') for c in t.columns]
    return t


def single_short(code, col, pop, by=None):
    t = single_table(code, col, by, pop)
    if by == 'Grupo':
        cols = ['Categoría', 'Total n', 'Total %'] + [f'{g} %' for g in G3]
    elif by == 'Universidad':
        cols = ['Categoría', 'Total n', 'Total %'] + [f'{u} %' for u in UNIS]
    else:
        cols = ['Categoría', 'Total n', 'Total %']
    return t[cols]


def build(E1, E2):
    P = charts.build_all()
    P.update(charts_ext.build(E1, E2))
    D = Doc()
    fin = sub('financiados')
    n_tot = len(df)
    D.cover('Evaluación de la línea de investigación de Alianza 4U',
            'Informe técnico detallado de resultados de la encuesta a docentes e investigadores',
            ['Universidad CESA · Universidad EAFIT · Universidad Icesi · Universidad del Norte',
             f'Base analizada: {n_tot} personas · Trabajo de campo: 22 de septiembre a 14 de noviembre de 2026',
             'Noviembre de 2026'])
    D.toc()

    # ================================================================ 1
    D.h('1. Resumen de hallazgos', 1)
    D.p(f'La encuesta reunió {n_tot} respuestas utilizables de docentes, investigadores y directivos de las cuatro universidades de Alianza 4U. '
        f'De ellas, 45 corresponden a personas cuya propuesta fue financiada por la Alianza, 11 a personas que se postularon y no obtuvieron financiación '
        f'y 45 a personas que no se postularon. Un caso adicional se postuló pero no recuerda el resultado. '
        f'Entre los postulantes que respondieron y conocen su resultado, el 80,4 % fue financiado (45 de 56). Esta cifra no es la tasa de aprobación del programa: '
        f'la encuesta cubre al 47 % de los 96 aprobados que registra la oficina de inteligencia en CTeI de EAFIT y solo a 11 rechazados. '
        f'Todas las cifras se recalcularon desde los datos crudos y se contrastaron con las tablas de la plataforma y con la presentación de EAFIT (secciones 15 a 18).')
    D.bullets([
        ('Perfil. ', f'La muestra es paritaria según el sexo estimado por nombre (51 mujeres y 51 hombres). El 80 % es profesor de planta, el 75 % tiene más de 10 años de experiencia investigativa '
                     f'y el 75 % dedica 40 % o menos de su tiempo a investigar. Predominan Economía y negocios (25 %) e Ingeniería y tecnología (24 %).'),
        ('Disposición alta, condiciones institucionales débiles. ', f'El índice de disposición a colaborar (C1) es 4,41 sobre 5, mientras que el de condiciones institucionales (C3) es 3,36. '
                     f'Solo el {fav("C3_3")} dice que su carga de trabajo permite participar en proyectos interinstitucionales y el {fav("C3_5")} que los procedimientos administrativos lo facilitan.'),
        ('Los financiados colaboran más. ', 'Los financiados trabajaron con más tipos de instituciones (3,5 frente a 1,9 de quienes no se postularon), con más universidades 4U distintas a la propia (1,9 frente a 0,5) '
                     'y acumularon más experiencias interinstitucionales desde 2021 (12,3 frente a 6,2). Al emparejar por perfil, como hace EAFIT, se mantiene el efecto en colaboración con otras universidades 4U y en proyectos ejecutados con ellas; '
                     'el efecto en publicaciones conjuntas es positivo (+18 a +28 pp) pero no concluyente, y no hay efecto en la cantidad de productos. Esto coincide con las conclusiones de EAFIT.'),
        ('Representatividad. ', 'Los financiados encuestados reproducen la distribución por universidad de los aprobados, pero tienen más mujeres (56 % frente a 44,8 %) porque las mujeres respondieron más. Ponderar por universidad y sexo cambia los indicadores en menos de 5 puntos.'),
        ('Convocatorias bien valoradas, con puntos débiles. ', f'Los objetivos (94 % favorable) y requisitos (89 %) se consideran claros; el tiempo para preparar la propuesta (55 %) y la claridad de los procedimientos administrativos (53 %) son lo menos valorado. '
                     f'Solo el 12 % recibió retroalimentación detallada y el 7 % tuvo oportunidad de opinar sobre la convocatoria.'),
        ('Proyectos financiados con buena gobernanza. ', 'Los índices de toma de decisiones (4,36), relaciones (4,35) y coordinación (4,12) son altos. El 58 % valora que los beneficios superaron las dificultades, aunque el 53 % reporta un esfuerzo de coordinación mayor que en un proyecto de una sola universidad.'),
        ('Producción. ', f'En los proyectos financiados, los artículos científicos estaban previstos en el 98 % de los casos, pero solo el 38 % los reporta completados (55 % en desarrollo). '
                     f'Los productos completados más frecuentes son los de divulgación (50 %) e informes técnicos (48 %). El 90 % desarrolla artículos con al menos dos universidades 4U. Las patentes y prototipos son marginales.'),
        ('Adicionalidad. ', 'El 48 % de los financiados cree que sin Alianza 4U el proyecto no se habría realizado y el 26 % que habría tenido menor alcance. La financiación (93 %) y la conformación del equipo interinstitucional (79 %) son lo que más se atribuye a la Alianza.'),
        ('Impacto todavía incipiente. ', 'El índice de contribuciones (I1) es 3,50. Los cambios en prácticas o decisiones (32 % favorable) y el fortalecimiento de organizaciones externas (33 %) son los efectos más débiles. Solo el 21 % de los resultados más significativos está establecido o se ha sostenido al menos un año.'),
        ('Futuro y barreras. ', 'El 64 % considera probable volver a colaborar con otra universidad 4U en dos años (72 % de los financiados). La falta de tiempo o carga académica es la barrera dominante (77 %). Las prioridades pedidas son facilitar la identificación de socios (52 %) y armonizar procedimientos administrativos (41 %).'),
    ])

    # ================================================================ 2
    D.h('2. Objetivo, fuentes y método', 1)
    D.h('2.1 Objetivo', 2)
    D.p('Describir con el mayor detalle posible el perfil de las personas encuestadas, sus experiencias de colaboración y su relación con Alianza 4U. '
        'El informe compara a quienes fueron financiados, quienes se postularon sin éxito y quienes no se postularon, y analiza el funcionamiento, los productos y los efectos de los proyectos financiados.')
    D.h('2.2 Fuentes', 2)
    D.bullets(['Cuatro exportaciones de la plataforma de encuestas (Resultados CESA, EAFIT, ICESI y Uninorte), cada una con 325 variables por persona.',
               'Cuestionario "Encuesta para la evaluación de resultados de la línea de investigación de Alianza 4U" (secciones A a J, 75 preguntas).',
               'El archivo "Entrega 2 - Proyecto de Aula Final" del repositorio trata sobre material particulado PM2.5 en Medellín. No tiene relación con la encuesta y no se usó en el análisis.'])
    D.h('2.3 Definición de grupos', 2)
    D.table(pd.DataFrame([
        ['Financiado', 'E2 = "Fue financiada por Alianza 4U"', 45],
        ['Postuló, no financiado', 'E2 = no financiada (9), elegible sin financiación (1) o retirada (1)', 11],
        ['No postuló', 'No respondió la sección E (relación con 4U solo informativa, eventos, evaluación, etc.)', 45],
        ['Postuló, resultado desconocido', 'E2 = "No recuerda o no conoce el resultado". Se incluye solo en totales', 1]],
        columns=['Grupo', 'Criterio', 'n']), 'Grupos de comparación', widths=[4, 10.5, 1.5])
    D.h('2.4 Tratamiento de los datos', 2)
    D.bullets([
        ('Unicidad. ', 'No hay cédulas, correos ni nombres repetidos entre las cuatro bases. Se analizan 102 registros (97 completos y 5 parciales con información útil).'),
        ('Universidad. ', 'Se usa la universidad declarada en B4. Cinco personas dicen no estar vinculadas actualmente a 4U; para ellas se usa la universidad del enlace por el que respondieron. Doce personas respondieron por el enlace de otra universidad (por ejemplo, 6 de Uninorte y 2 de ICESI por el de EAFIT); se clasifican por B4.'),
        ('Sexo. ', 'El cuestionario no pregunta sexo. Se estimó a partir del primer nombre (todas las personas fueron clasificables). Es una aproximación que puede no coincidir con la identidad de género y se reporta solo de forma agregada.'),
        ('Edad. ', 'El cuestionario no pregunta edad ni fecha de nacimiento, por lo que no es posible reportarla. Como aproximación de la etapa de carrera se usan los años de experiencia en investigación (B10) y el rango académico (B8).'),
        ('Publicaciones y productos. ', 'No hay un conteo exacto de publicaciones. Se usan D7 (número aproximado de propuestas, proyectos y productos con otra universidad desde 2021), D8 (proyectos interinstitucionales antes de 2021), H1-H2 (estado y coautoría de productos del proyecto financiado) y las evidencias citadas en H8b.'),
        ('Escalas. ', 'Las escalas de cinco puntos se codifican de 1 (más bajo) a 5 (más alto). "No tengo información", "No aplica" y "Todavía no es observable" se excluyen de medias y porcentajes. "% favorable" = respuestas 4 y 5.'),
        ('Índices. ', 'Para cada bloque se calcula el promedio de los ítems válidos (mínimo la mitad respondidos). Todos tienen alfa de Cronbach entre 0,75 y 0,95, lo que indica consistencia interna aceptable a excelente.'),
        ('Pruebas. ', 'Kruskal-Wallis o Mann-Whitney para diferencias entre grupos; chi² con V de Cramér y prueba exacta de Fisher para asociaciones; Spearman para correlaciones. Significancia: p<0,05; tendencia: p<0,10.'),
        ('Flujo de la encuesta. ', 'Las secciones F a I se refieren al proyecto financiado y se analizan solo para los 45 financiados. Algunas personas no financiadas respondieron G (11) o I (11) por fuera del flujo previsto; esas respuestas se excluyeron.'),
        ('Comparaciones múltiples. ', 'Con más de cien pruebas, algunas salen significativas por azar. Tras la corrección de Benjamini-Hochberg solo se mantienen dos diferencias (sección 15.3); las demás diferencias de ítems citadas con p<0,05 son exploratorias.'),
        ('Rangos armonizados. ', 'Para comparar con la presentación de EAFIT, el sexo, el área de conocimiento, la trayectoria, el estado del proyecto y el estado de los artículos se reagruparon en los rangos de esa presentación (sección 16).'),
        ('Confidencialidad. ', 'Los informes y la base anonimizada no contienen nombres, cédulas, correos ni direcciones IP. En las citas textuales se omitieron nombres propios.'),
    ])
    D.h('2.5 Limitaciones', 2)
    D.p('La muestra es pequeña y no probabilística: 12 personas en CESA, 23 en EAFIT, 25 en ICESI y 42 en Uninorte, y solo 11 postulantes no financiados. '
        'No se conoce el universo total invitado, pero según EAFIT hubo 96 aprobados, así que la encuesta cubre al 47 % de ellos. Las diferencias deben leerse como indicativas. '
        'Además, la información es autorreportada y retrospectiva, y quienes tuvieron una experiencia más intensa con la Alianza pueden haber tenido más motivación para responder.')

    # ================================================================ 3
    D.pagebreak()
    D.h('3. Participación en la encuesta', 1)
    pt = participation()[['Encuesta (enlace)', 'Respuestas totales (plataforma)', 'Terminadas (plataforma)', 'Tasa de finalización % (plataforma)',
                          'Registros en base exportada', 'Completos en base', 'Mediana duración (min)']]
    pt.columns = ['Enlace', 'Respuestas plataforma', 'Terminadas', '% finalización', 'Registros exportados', 'Completos', 'Mediana min']
    D.table(pt, 'Respuestas por enlace de encuesta', font=8)
    D.p('La plataforma registró 146 inicios y 101 respuestas terminadas (69,2 % de finalización). ICESI tuvo la menor tasa de finalización (55,1 %) y la mayor duración mediana (36 minutos), '
        'lo que sugiere que el cuestionario resultó largo para una parte de su población. La duración mediana global fue de 24 minutos (mínimo 2,4 y máximo 136,5). '
        'Todas las personas aceptaron participar (A1) y el 96 % autorizó vincular sus respuestas con registros administrativos y bibliométricos (A2). '
        'Las tablas de la plataforma incluyen 16 perfiles parciales que no están en la base exportada; su ausencia no cambia las distribuciones (sección 15.1).')
    D.img(P['grupos_uni'], 15, 'Encuestados por universidad (B4) y grupo de vinculación')
    D.table(pd.crosstab(df['Universidad'], df['Grupo'], margins=True, margins_name='Total').reset_index(), 'Encuestados por universidad y grupo', font=8)
    D.p('Uninorte aporta el 41 % de la muestra y el 42 % de los financiados (19 de 45). En las cuatro universidades, financiados y no postulantes tienen un peso casi idéntico, lo que permite comparaciones equilibradas dentro de cada una.')

    # ================================================================ 4
    D.pagebreak()
    D.h('4. Perfil de las personas encuestadas', 1)
    D.h('4.1 Sexo (estimado)', 2)
    D.p('Según el primer nombre, la muestra está compuesta por 51 mujeres y 51 hombres (50 % cada uno), con la misma proporción en las cuatro universidades. '
        'Por grupo, las mujeres son el 56 % de los financiados (25 de 45) y el 73 % de los postulantes no financiados (8 de 11), mientras que los hombres son el 60 % de quienes no se postularon (27 de 45). '
        'La presentación de EAFIT registra 44,8 % de mujeres entre los 96 aprobados; la diferencia con el 56 % de la encuesta se debe a que las mujeres aprobadas respondieron más (58 % frente a 40 % de los hombres). '
        'La asociación entre sexo y grupo es marginal (chi², p=0,099). Entre postulantes, la tasa de éxito fue de 75,8 % para mujeres y 87,0 % para hombres; la diferencia no es significativa (prueba exacta de Fisher, p=0,50).')
    D.img(P['sexo'], 15, 'Sexo estimado por grupo')
    D.p('Hay diferencias de composición por sexo según el área y la función: los hombres predominan en Ingeniería y tecnología (18 de 24) y Ciencias naturales (5 de 6); las mujeres en Economía y negocios (17 de 26) y Humanidades (10 de 14). '
        'Doce de las 19 personas en dirección o gestión académica son mujeres. En el rango académico la distribución es casi idéntica (titulares: 10 y 10; asociados: 12 mujeres y 10 hombres). '
        'En los proyectos, mujeres y hombres ocupan por igual el rol de investigador principal (10 y 10), y las cinco personas que se declaran "integrante del equipo" son mujeres.')
    sx = pd.crosstab(df['Rango (agrupado)'], df['Sexo (estimado)'], margins=True, margins_name='Total').reset_index()
    D.table(sx, 'Rango académico por sexo estimado (n)', font=8)
    sx2 = pd.crosstab(df[41].str.rstrip('.'), df['Sexo (estimado)'], margins=True, margins_name='Total').reset_index().rename(columns={41: 'Área de conocimiento'})
    D.table(sx2, 'Área de conocimiento por sexo estimado (n)', font=8)

    D.h('4.2 Edad y etapa de carrera', 2)
    D.p('La encuesta no recoge edad. Los años de experiencia investigativa y el rango sirven como aproximación de la etapa de carrera. '
        'El 44 % tiene entre 11 y 20 años de experiencia y el 31 % más de 20; nadie reporta menos de 3 años. El promedio aproximado es de 16,4 años. '
        'No hay diferencias significativas de experiencia entre grupos (p=0,36), aunque los no financiados tienen mayor proporción de personas con más de 20 años (45 %).')
    D.img(P['exp'], 15, 'Experiencia en investigación por grupo')
    D.table(single_short('B10', 43, 'todos', 'Grupo'), 'Años de experiencia en investigación (B10) por grupo', font=8)
    D.p('En los rangos de la presentación de EAFIT (<10, 10-19 y 20 o más años), los financiados encuestados se distribuyen en 29 %, 44 % y 27 %, frente a 4 %, 44 % y 47 % de los aprobados según EAFIT. '
        'La diferencia se explica porque EAFIT mide años desde el pregrado y la encuesta años de experiencia en investigación.')
    D.table(single_short('TR', 'Trayectoria (rangos EAFIT aprox.)', 'todos', 'Grupo'), 'Trayectoria en rangos EAFIT por grupo', font=8)

    D.h('4.3 Vinculación, función y rango', 2)
    D.p('El 80 % es profesor de planta o tiempo completo, el 8 % de cátedra y el 7 % directivo. El 62 % combina docencia e investigación, el 19 % se dedica a dirección o gestión académica y solo el 4 % principalmente a investigar. '
        'Por rango, el 43 % es asistente, el 22 % asociado, el 20 % titular y el 4 % auxiliar. Entre los financiados, el 51 % es asistente; entre los no financiados, el 45 % es asociado. '
        'Los asociados tienen la menor tasa de éxito (61,5 %, 8 de 13), frente a 85,2 % de asistentes y 91,7 % de titulares (asociados frente al resto: Fisher p=0,10, no significativo).')
    D.img(P['rango'], 15, 'Rango académico por grupo')
    D.table(single_short('B6', 35, 'todos', 'Grupo'), 'Tipo de vinculación (B6) por grupo', font=8)
    D.table(single_short('B7', 37, 'todos', 'Grupo'), 'Función principal (B7) por grupo', font=8)
    D.table(single_short('B8', 39, 'todos', 'Grupo'), 'Rango académico (B8) por grupo', font=8)

    D.h('4.4 Área de conocimiento y unidad académica', 2)
    D.p('Las áreas más representadas son Economía, administración y negocios (26 personas), Ingeniería y tecnología (24), Ciencias sociales (16) y Humanidades (14). '
        'En las respuestas "Otra", aparecen Computación, Física, Matemática, Diseño, Sostenibilidad e Idiomas. Varias personas indican el Instituto de Idiomas de Uninorte como unidad. '
        'Entre los postulantes encuestados, Ciencias sociales tuvo menor proporción de financiación (3 de 7) que el resto (Fisher p=0,022). Este dato no es concluyente: son 7 personas que se clasificaron ellas mismas en el área, '
        'y según la presentación de EAFIT, que clasifica por el título más alto, Ciencias sociales es el área con más aprobados (30,2 %).')
    D.table(single_short('AR', 'Área (rangos EAFIT)', 'todos', 'Grupo'), 'Área de conocimiento en rangos EAFIT por grupo', font=8)
    D.img(P['area'], 14, 'Área principal de conocimiento')
    D.table(single_short('B9', 41, 'todos', 'Universidad'), 'Área de conocimiento (B9) por universidad', font=8)

    D.h('4.5 Dedicación a la investigación', 2)
    D.p('El 35 % dedica entre 1 % y 20 % de su tiempo a investigar y el 38 % entre 21 % y 40 %. Solo el 6 % dedica más del 60 %. La dedicación promedio aproximada es del 29 % y es similar en los tres grupos (31 % financiados, 27 % no financiados y no postulantes; p=0,62). '
        'La dedicación sí se asocia con la intensidad de colaboración: a mayor dedicación, más instituciones socias (rho=0,33), más tipos de actividad (rho=0,31) y más experiencias interinstitucionales (rho=0,31), todas con p<0,01.')
    D.img(P['ded'], 15, 'Dedicación a investigación por grupo')

    # ================================================================ 5
    D.pagebreak()
    D.h('5. Colaboración interinstitucional en general (sección C)', 1)
    D.h('5.1 Disposición y preparación (C1)', 2)
    D.p('La disposición a colaborar es muy alta. El 95 % confía en la calidad del trabajo de investigadores de otras universidades, el 94 % considera útil la colaboración para problemas complejos y el 93 % se siente preparado para participar en un equipo interinstitucional. '
        'Los puntos relativamente más bajos son sentirse parte de una comunidad académica que trasciende la propia universidad (75 %) y sentirse preparado para coordinar un equipo interinstitucional (79 %). '
        'Los financiados se sienten más preparados para participar (media 4,73 frente a 4,36 de no postulantes, p=0,02) y para coordinar (4,42 frente a 3,91 de no financiados; tendencia, p=0,07).')
    D.img(P['lk_C1'], 16, 'C1. Disposición y preparación para la colaboración (todos)')
    D.table(compact_items('C1'), 'C1. Estadísticos por ítem', font=7.5)
    D.p('Por universidad, CESA tiene la media más baja en utilidad percibida de la colaboración (4,00 frente a 4,89 de EAFIT; p=0,005) y en sentido de comunidad más allá de la propia universidad (3,83 frente a 4,52 de EAFIT; p=0,047).')

    D.h('5.2 Valor percibido de los proyectos interinstitucionales (C2)', 2)
    D.p('Comparados con proyectos de una sola universidad, los interinstitucionales se consideran mayores o mucho mayores en alcance y visibilidad (91 %) y en capacidad para integrar conocimientos y recursos (85 %). '
        'La calidad científica obtiene la valoración más moderada: 64 % la considera mayor, el 34 % similar, y 11 personas dicen no tener información suficiente. No hay diferencias significativas entre grupos ni universidades.')
    D.img(P['lk_C2'], 16, 'C2. Proyectos interinstitucionales frente a proyectos de una sola universidad')
    D.table(compact_items('C2'), 'C2. Estadísticos por ítem', font=7.5)

    D.h('5.3 Condiciones institucionales (C3)', 2)
    D.p('Es el bloque peor valorado de toda la encuesta (índice 3,36; solo el 26 % de las personas tiene un índice de 4 o más). Las dos condiciones más débiles son la carga de trabajo (26 % favorable, 34 % desfavorable) '
        'y los procedimientos administrativos (33 % favorable, 34 % desfavorable). El reconocimiento o los incentivos por participar también son bajos (46 % favorable, 24 % desfavorable). '
        'La percepción es igual en los tres grupos (p=0,90) y en las cuatro universidades (p=0,69): ser financiado no cambia la percepción sobre las condiciones institucionales.')
    D.img(P['lk_C3'], 16, 'C3. Condiciones institucionales para investigar con otras instituciones')
    D.table(compact_items('C3'), 'C3. Estadísticos por ítem', font=7.5)
    D.p('Las personas con más socios institucionales (D5) valoran peor las condiciones (rho=-0,25; p=0,01). Esto sugiere que quienes más colaboran son quienes más perciben las dificultades administrativas y de tiempo.')

    D.h('5.4 Cambio en capacidades desde 2021 (C4)', 2)
    D.p('El 81 % dice haber aumentado su capacidad para producir conocimiento de manera colaborativa y el 78 % para identificar socios. La capacidad que menos creció es gestionar proyectos con requisitos administrativos distintos (64 %). '
        'Los financiados reportan un aumento algo mayor (índice 4,17 frente a 3,92 de no postulantes), pero la diferencia no es significativa (p=0,29). '
        'Las personas con más de 20 años de experiencia reportan menos cambio (3,78 frente a 4,17 de quienes tienen 10 años o menos; rho=-0,21, p=0,04), lo cual es esperable porque ya tenían esas capacidades.')
    D.img(P['lk_C4'], 16, 'C4. Cambio en capacidades de colaboración desde enero de 2021')
    D.table(compact_items('C4'), 'C4. Estadísticos por ítem', font=7.5)
    D.img(P['idx_grupos'], 16, 'Índices de las secciones C y E por grupo de vinculación')
    D.table(index_by('Grupo')[['Índice', 'Dimensión', 'Financiado media', 'Postuló, no financiado media', 'No postuló media', 'p-valor']].rename(
        columns={'Financiado media': 'Financiado', 'Postuló, no financiado media': 'No financiado', 'No postuló media': 'No postuló'}), 'Índices por grupo', font=8)

    # ================================================================ 6
    D.pagebreak()
    D.h('6. Trayectoria de colaboración y relación con Alianza 4U (sección D)', 1)
    D.h('6.1 Conocimiento de la Alianza (D1, D2, D4)', 2)
    D.p('El 95 % había oído hablar de Alianza 4U antes de la encuesta; las cinco personas que no la conocían pertenecen al grupo de no postulantes. '
        'El conocimiento de los objetivos y convocatorias es mucho mayor entre los financiados: el 64 % los conocía bastante o en profundidad, frente al 21 % de los no postulantes (chi² p<0,001; V=0,44 en financiado frente a resto). '
        'La comunicación institucional es el principal canal de conocimiento (83 %), seguida de colegas de la propia universidad (42 %) y las convocatorias (36 %). '
        'Entre los no postulantes, los eventos y talleres (49 %) y la web o redes sociales (27 %) tienen más peso que entre los financiados.')
    D.img(P['d2'], 15, 'D2. Conocimiento de objetivos y convocatorias de Alianza 4U por grupo')
    D.img(P['mu_D4'], 15, 'D4. Medios por los que conoció Alianza 4U')
    D.h('6.2 Relación previa con la Alianza (D3)', 2)
    D.table(single_short('D3', 72, 'todos', 'Grupo'), 'D3. Relación previa con Alianza 4U', font=7.5)
    D.p('Entre los no postulantes, el 39 % recibió información pero no participó, el 31 % solo había oído hablar de la Alianza, el 15 % actuó como evaluador, asesor o gestor y el 13 % participó en eventos o redes. Hay por tanto un grupo de personas informadas que no se ha convertido en postulante.')

    D.h('6.3 Colaboraciones desde 2021 (D5, D6)', 2)
    D.p('Uninorte es la institución con la que más personas declaran haber colaborado (61 %), seguida de ICESI (47 %), EAFIT (44 %) y universidades internacionales (43 %). CESA aparece en el 20 % de los casos. '
        'Ningún financiado declara ausencia de colaboración interinstitucional, frente al 18 % de los no postulantes. '
        'Los financiados colaboraron en promedio con 1,9 universidades 4U distintas a la propia, frente a 0,5 de los no financiados y no postulantes (p<0,001).')
    D.img(P['mu_D5'], 16, 'D5. Instituciones con las que ha colaborado desde 2021, por grupo')
    D.img(P['mu_D6'], 16, 'D6. Actividades interinstitucionales desde 2021, por grupo')
    D.p('En actividades, las mayores brechas entre financiados y no postulantes están en la ejecución de proyectos (93 % frente a 25 %), la formulación de propuestas (93 % frente a 41 %) y las publicaciones conjuntas (84 % frente a 48 %). '
        'El desarrollo tecnológico o la innovación es poco frecuente en todos los grupos (14 % en total).')

    D.h('6.4 Producción interinstitucional y experiencia previa (D7, D8)', 2)
    D.p('Con puntos medios de los rangos, las 100 personas que respondieron D7 suman aproximadamente 210 propuestas, 140 proyectos ejecutados y 212 productos académicos o aplicados con otra universidad desde 2021, además de 186 iniciativas con actores externos y 206 relaciones de colaboración activas. '
        'Estas cifras son estimaciones y pueden contar más de una vez un mismo producto cuando lo reportan varios coautores.')
    D.img(P['d7'], 16, 'D7. Número aproximado de experiencias interinstitucionales desde 2021 por grupo')
    D.table(compact_items('D7'), 'D7. Experiencias desde 2021 (todos)', font=7.5)
    pr = production_table()
    pr = pr[['Indicador', 'Total media', 'Financiado media', 'Postuló, no financiado media', 'No postuló media', 'p-valor']]
    pr.columns = ['Indicador', 'Total', 'Financiado', 'No financiado', 'No postuló', 'p-valor']
    D.table(pr, 'Indicadores de colaboración y producción por grupo (medias aproximadas)', font=7.5, fmt={'p-valor': '{:.4f}'})
    D.p('Antes de 2021, el 42 % no había participado en ningún proyecto interinstitucional, proporción similar entre financiados (40 %) y no postulantes (50 %). '
        'La experiencia previa no difiere significativamente entre grupos (p=0,33), lo que indica que la Alianza financió tanto a investigadores con trayectoria de colaboración como a quienes no la tenían: '
        '18 de los 20 postulantes sin experiencia previa fueron financiados (90 %). La experiencia previa sí se asocia con más colaboración posterior a 2021 (rho=0,39; p<0,001).')
    D.img(P['d8'], 15, 'D8. Proyectos interinstitucionales antes de 2021 por grupo')

    # ================================================================ 7
    D.pagebreak()
    D.h('7. Experiencia con las convocatorias (sección E)', 1)
    D.h('7.1 Participación, resultado y rol', 2)
    D.p('De las 57 personas que respondieron la sección E, el 79 % participó directamente en la preparación de la propuesta y el 18 % parcialmente. El 35 % fue investigador principal y el 56 % coinvestigador. '
        'Los investigadores principales tuvieron una tasa de éxito de 89,5 % (17 de 19), los coinvestigadores de 78,1 % y los integrantes de equipo de 60 %. '
        'Quienes participaron directamente tuvieron más éxito (84 %) que quienes participaron solo parcialmente (60 %).')
    D.img(P['exito'], 15, 'Tasa de éxito por perfil del postulante')
    sr = success_rate()
    D.table(sr, 'Tasa de éxito por perfil (postulantes con resultado conocido)', font=7.5)
    D.note('La tasa de éxito se calcula solo con los postulantes que respondieron la encuesta (56). No es la tasa de aprobación del programa; el intervalo de confianza al 95 % va de 68 % a 89 %.')
    D.p('Por universidad, la tasa de éxito es similar en EAFIT (84,6 %), ICESI (84,6 %) y Uninorte (82,6 %), y menor en CESA (57,1 %, 4 de 7). '
        'Con tan pocos casos en CESA, la diferencia no es estadísticamente significativa (Fisher p=0,13).')

    D.h('7.2 Diseño de la convocatoria (E4) y proceso (E5)', 2)
    D.p('Los objetivos (94 % favorable) y los requisitos (89 %) se consideran claros, al igual que los criterios de evaluación (88 %) y la comunicación de la decisión (88 %). '
        'Los aspectos más débiles son el tiempo para preparar la propuesta (55 %), la claridad de los procedimientos administrativos (53 %) y el acompañamiento durante la formulación (68 %). '
        'La formalización y puesta en marcha tiene un 11 % de valoraciones deficientes, y es especialmente baja en EAFIT (media 3,09 frente a 4,20 en ICESI; p=0,014).')
    D.img(P['lk_E4'], 16, 'E4. Diseño de la convocatoria de referencia (postulantes)')
    D.table(compact_items('E4'), 'E4. Estadísticos por ítem', font=7.5)
    D.img(P['lk_E5'], 16, 'E5. Valoración del proceso (postulantes)')
    D.table(compact_items('E5'), 'E5. Estadísticos por ítem', font=7.5)
    D.p('Los no financiados valoran peor la convocatoria. Las diferencias son significativas en la claridad de los requisitos (4,66 frente a 4,00; p=0,02), la comprensión y transparencia de los criterios de evaluación (4,49 frente a 3,78; p=0,01), '
        'el favorecimiento de equipos complementarios (4,35 frente a 3,70; p=0,02) y la claridad de la comunicación de la decisión (4,39 frente a 3,75; p=0,04). '
        'Ninguna de estas diferencias se mantiene tras corregir por comparaciones múltiples, porque los no financiados son solo 11; la dirección es consistente en todos los ítems.')
    D.img(P['e_compare'], 15, 'Valoración de la convocatoria: financiados frente a no financiados')

    D.h('7.3 Retroalimentación y participación en la mejora (E6, E7)', 2)
    D.p('Solo el 12 % recibió retroalimentación suficientemente detallada; el 23 % la recibió muy general, el 32 % no la recibió y el 33 % no recuerda. '
        'Entre quienes valoraron su utilidad, el 34 % la considera muy o completamente útil y el 28 % poco o nada útil. Solo 3 de 45 personas (7 %) tuvieron oportunidad de opinar sobre el diseño de la convocatoria. '
        'Entre los no financiados, el 36 % pide mejorar la retroalimentación a las propuestas (J5), frente al 5 % de los financiados.')
    D.img(P['bar_E6'], 13, 'E6. Retroalimentación recibida (postulantes)')

    D.h('7.4 Aportes del proceso de formulación (E8) y qué ocurrió después (E9)', 2)
    D.p('Independientemente del resultado, el proceso de formulación ayudó sobre todo a precisar el problema de investigación (74 % alta o decisiva) y a integrar disciplinas (72 %). '
        'Generar una idea reutilizable en otras convocatorias es lo menos frecuente (52 %). Los no financiados reportan aportes menores, en especial para precisar el problema (3,20 frente a 4,06; p=0,004) e identificar socios (3,10 frente a 3,97; p=0,048).')
    D.table(compact_items('E8'), 'E8. Aportes del proceso de formulación (postulantes)', font=7.5)
    D.p('De las 8 personas no financiadas que respondieron E9, 5 indican que el equipo dejó de trabajar conjuntamente, 2 que la idea se incorporó a otro proyecto y 1 que se buscaron otras fuentes. '
        'Ninguna reporta haber obtenido financiación de otra fuente ni haber vuelto a presentar la propuesta. La red creada para postular tiende a disolverse cuando no hay financiación.')
    D.img(P['mu_E9'], 14, 'E9. Qué ocurrió con la propuesta o el equipo (no financiados)')

    # ================================================================ 8
    D.pagebreak()
    D.h('8. Gobernanza y funcionamiento de los proyectos financiados (sección F)', 1)
    D.p('Esta sección se basa en los 43 financiados que la respondieron.')
    D.h('8.1 Estado de los proyectos (F1)', 2)
    D.p('El 42 % de los proyectos terminó actividades pero tiene productos en desarrollo, el 28 % está en ejecución y el 28 % finalizó y cerró formalmente. Una persona no conoce el estado de su proyecto.')
    D.img(P['bar_F1'], 13, 'F1. Estado del proyecto (financiados)')
    D.h('8.2 Toma de decisiones, coordinación, relaciones y consolidación (F2-F5)', 2)
    D.p('La gobernanza de los proyectos es bien valorada. Se sabía quién tomaba las decisiones (91 % favorable), las funciones se distribuyeron adecuadamente entre instituciones (88 %) y las capacidades fueron complementarias (86 %). '
        'Los aspectos menos sólidos son la institucionalización: el 27 % dice que el proyecto dependió en buena medida de acuerdos personales (F5.1) y el 28 % que la colaboración no continuó después de la financiación (F5.4). '
        'El 23 % reporta que sí surgieron diferencias o conflictos, pero el 79 % considera que se gestionaron oportunamente.')
    for c in ['F2', 'F3', 'F4', 'F5']:
        D.img(P[f'lk_{c}'], 16, f'{c}. {[m[1] for m in MATRIX if m[0] == c][0]}')
        D.table(compact_items(c), f'{c}. Estadísticos por ítem', font=7.5)
    D.p('Por sexo estimado, los hombres valoran mejor la existencia de reglas explícitas (4,67 frente a 4,04; p=0,045), la construcción de confianza (4,74 frente a 4,09; p=0,026) y la continuidad de la colaboración tras la financiación (4,47 frente a 3,41; p=0,027). '
        'Estas diferencias se basan en unos 20 casos por grupo y conviene explorarlas en las entrevistas.')
    D.h('8.3 Esfuerzo de coordinación y balance (F6, F7)', 2)
    D.p('El 53 % considera que el esfuerzo administrativo y de coordinación fue mayor o mucho mayor que en un proyecto de una sola universidad y el 35 % lo considera similar. '
        'Aun así, el 58 % valora que los beneficios superaron las dificultades, el 23 % que estuvieron equilibrados y el 14 % que los costos fueron superiores. '
        'El esfuerzo mayor no se asocia con un peor balance (sin correlación significativa entre F6 y F7). El balance sí se asocia con la calidad de la toma de decisiones (rho=0,42) y de la coordinación (rho=0,37).')
    D.img(P['bar_F6'], 13, 'F6. Esfuerzo de coordinación frente a un proyecto de una sola universidad')
    D.img(P['bar_F7'], 14, 'F7. Balance de la experiencia')

    # ================================================================ 9
    D.pagebreak()
    D.h('9. Fortalecimiento de capacidades (sección G)', 1)
    D.p('El fortalecimiento de capacidades por participar en el proyecto es moderado-alto: índice 3,81 en capacidades científicas y colaborativas, 3,75 en capacidades institucionales y 3,68 en aprendizaje organizacional. '
        'La capacidad más fortalecida es aplicar o combinar metodologías diferentes (71 % alta o decisiva), seguida de fortalecer los mecanismos institucionales de apoyo a la investigación (73 %) e integrar capacidades entre universidades (71 %). '
        'Las más débiles son fortalecer el propio grupo de investigación (51 %), coordinar equipos de varias instituciones (58 %) y convertir aprendizajes en prácticas utilizables por otros (57 %).')
    for c in ['G1', 'G2', 'G3']:
        D.img(P[f'lk_{c}'], 16, f'{c}. {[m[1] for m in MATRIX if m[0] == c][0]} (financiados)')
        D.table(compact_items(c), f'{c}. Estadísticos por ítem', font=7.5)
    D.p('CESA tiene los valores más bajos en este bloque (aprendizaje organizacional 2,83; producción de conocimiento 2,75), con solo 4 financiados. '
        'Las capacidades fortalecidas se asocian fuertemente con la consolidación institucional del proyecto (F5 con G1: rho=0,67) y con la calidad de las relaciones (F4 con G1: rho=0,55).')

    # ================================================================ 10
    D.pagebreak()
    D.h('10. Productos, movilización y uso del conocimiento (sección H)', 1)
    D.h('10.1 Estado de los productos (H1)', 2)
    D.p('Sobre 42 proyectos financiados con información, los artículos científicos son el producto casi universal (previstos en el 98 %), pero la mayoría está en desarrollo (55 %) y solo el 38 % está completado. '
        'Los productos completados con más frecuencia son los de divulgación o apropiación social (50 %) y los informes técnicos o recomendaciones (48 %), seguidos de artículos (38 %) y bases de datos o software (33 %). '
        'Los prototipos (7 %) y la propiedad intelectual (5 %) son marginales. Cada proyecto completó en promedio 2,6 tipos de producto y tiene 1,6 en desarrollo.')
    D.img(P['h1'], 16, 'H1. Estado de los productos de los proyectos financiados')
    D.table(compact_items('H1'), 'H1. Estado por tipo de producto', font=7.5)
    pf = production_fin()
    pf = pf[['Indicador'] + [c for c in pf.columns if c.endswith('media')]]
    pf.columns = [c.replace(' media', '') for c in pf.columns]
    D.table(pf, 'Producción por proyecto financiado, según universidad (promedio de tipos de producto)', font=8)
    D.h('10.2 Productos conjuntos y valoración (H2, H3)', 2)
    D.p('El 90 % desarrolla artículos científicos con personas de al menos dos universidades 4U; el 40 % productos de divulgación y el 38 % productos de formación o tesis. Ningún proyecto reporta productos conjuntos de propiedad intelectual. '
        'Los propios investigadores valoran muy bien sus productos: 100 % califica como alta o muy alta su pertinencia para el proyecto y 98 % su calidad científica. El potencial de aplicación en otros contextos es lo menos valorado (85 %).')
    D.img(P['mu_H2'], 15, 'H2. Productos desarrollados conjuntamente por al menos dos universidades 4U')
    D.table(compact_items('H3'), 'H3. Valoración de los productos', font=7.5)
    D.h('10.3 Movilización y actores externos (H4, H5, H6)', 2)
    D.p('Los resultados se movilizan sobre todo por canales académicos: publicaciones (74 %) y congresos (67 %). Les siguen medios y redes sociales (38 %). Los mecanismos orientados a usuarios son poco frecuentes: reuniones con usuarios potenciales (19 %) y demostraciones o pilotos (7 %). '
        'El 12 % aún no ha realizado actividades de movilización.')
    D.img(P['mu_H4'], 15, 'H4. Mecanismos de movilización de resultados')
    D.p('La interacción con actores no académicos es limitada. Con investigadores y comunidades académicas, el 98 % tuvo alguna interacción y el 63 % una participación activa. '
        'Con entidades públicas solo el 24 % tuvo alguna interacción y el 3 % reporta uso de resultados; con empresas, 31 % y 3 %. Las comunidades y organizaciones sociales tienen una interacción algo mayor (50 % y 39 %). '
        'El 19 % de los proyectos no tuvo participación de actores externos en ninguna etapa; cuando participan, lo hacen sobre todo en la comunicación de resultados (48 %).')
    D.img(P['h5'], 16, 'H5. Nivel de interacción por tipo de actor')
    D.table(compact_items('H5'), 'H5. Interacción y uso por tipo de actor (0 = sin interacción, 4 = uso del resultado)', font=7.5)
    D.img(P['mu_H6'], 15, 'H6. Etapas con participación de actores externos')
    D.h('10.4 Uso del conocimiento y evidencias (H7, H8)', 2)
    D.p('El conocimiento se usa sobre todo para nuevas investigaciones (74 %) y docencia (62 %). El uso en políticas, programas o regulaciones (17 %) y en cambios de procedimientos (17 %) es poco frecuente. '
        'En cuanto a evidencias verificables, la más común es la citación en una publicación (36 %), seguida de registros de formación o apropiación (24 %). El 26 % dice que no existe evidencia disponible y el 12 % no sabe. '
        'En H8b se citan 23 referencias, entre ellas artículos con DOI en revistas como Construction and Building Materials, Global and Planetary Change, iScience, Sustainable Production and Consumption y Language and Intercultural Communication; '
        'un capítulo en el Reporte de Biodiversidad del Instituto Humboldt (citado por dos personas), boletines "Datos en Breve" de POLIS-ICESI, un policy brief, una tesis doctoral y un trabajo de grado.')
    D.img(P['mu_H7'], 15, 'H7. Ámbitos de uso del conocimiento')
    D.img(P['mu_H8'], 15, 'H8. Evidencias verificables de uso')

    # ================================================================ 11
    D.pagebreak()
    D.h('11. Impacto, generación de valor y adicionalidad (sección I)', 1)
    D.h('11.1 Contribuciones observadas (I1)', 2)
    D.p('El índice de contribuciones es 3,50, el más bajo de los bloques de los proyectos financiados. Las contribuciones más reconocidas son responder a una problemática relevante (64 % alta o decisiva), fortalecer el ecosistema de CTI (63 %) y consolidar redes (60 %). '
        'Las más débiles son los cambios en prácticas, procesos o decisiones (32 %; 29 % ninguna o baja) y el fortalecimiento de organizaciones o comunidades (33 %). '
        'Entre 2 y 9 personas por ítem consideran que la contribución todavía no es observable o no tienen información.')
    D.img(P['lk_I1'], 16, 'I1. Contribuciones observadas de Alianza 4U')
    D.table(compact_items('I1'), 'I1. Estadísticos por ítem', font=7.5)
    D.h('11.2 Madurez, alcance y sostenibilidad del resultado principal (I2-I4)', 2)
    D.p('El resultado más significativo es todavía incipiente o no observable en el 45 % de los casos; el 21 % está en prueba o implementación y solo el 21 % está establecido o se ha mantenido al menos un año. '
        'El alcance más frecuente es el de varias universidades de la Alianza (29 %) o los propios integrantes del proyecto (21 %). El 17 % alcanza un nivel nacional o internacional. '
        'El 52 % considera probable o muy probable que las relaciones, productos o cambios continúen sin nueva financiación de la Alianza, mientras que el 29 % lo ve improbable.')
    D.img(P['bar_I2'], 13, 'I2. Estado actual del resultado más significativo')
    D.img(P['bar_I3'], 13, 'I3. Mayor nivel de alcance del resultado')
    D.img(P['bar_I4'], 13, 'I4. Probabilidad de continuidad sin nueva financiación')
    D.h('11.3 Adicionalidad (I5, I6)', 2)
    D.p('El 48 % cree que sin Alianza 4U el proyecto probablemente no se habría realizado, el 26 % que se habría hecho con menor alcance o con menos instituciones y el 17 % que se habría hecho más tarde. '
        'Solo una persona cree que habría ocurrido igual. Esto indica una adicionalidad alta según la percepción de los participantes. '
        'La financiación (93 %), la conformación del equipo interinstitucional (79 %) y la integración de disciplinas (71 %) son los elementos que más se atribuyen a la Alianza. '
        'La continuidad de la red (17 %) y la consecución de financiación posterior (12 %) son los menos atribuidos.')
    D.img(P['bar_I5'], 14, 'I5. Qué habría ocurrido sin Alianza 4U')
    D.img(P['mu_I6'], 15, 'I6. Elementos posibles o fortalecidos gracias a Alianza 4U')
    D.h('11.4 Efectos no previstos (I7)', 2)
    D.p('El 57 % reporta efectos no previstos principalmente positivos y una persona efectos tanto positivos como negativos. Los efectos descritos incluyen nuevos proyectos con aliados gubernamentales, conexión con investigadores y aliados internacionales, '
        'el desarrollo de una plataforma para vendedores ambulantes, un sistema RAG desarrollado con Eduteka, una estación de investigación y una página web con el estudio comparado de cuatro universidades. '
        'Entre los efectos negativos se menciona la imposibilidad de dar continuidad cuando terminan el proyecto y la vinculación de los estudiantes.')
    D.img(P['bar_I7'], 13, 'I7. Efectos no previstos')
    D.h('11.5 Factores asociados a mejores resultados', 2)
    D.p('En los financiados, los índices de gobernanza (F2-F5) se correlacionan de forma positiva y significativa con todos los indicadores de resultado. La consolidación institucional (F5) es el factor más asociado con las capacidades fortalecidas (G1 rho=0,67; G3 rho=0,66) '
        'y la calidad de las relaciones (F4) con las contribuciones observadas (I1 rho=0,61). La coordinación (F3) se asocia con la intención de volver a colaborar (J1 rho=0,40). '
        'Los proyectos con reglas claras, buena coordinación y procedimientos institucionales logran más capacidades, mejor valoración de productos y mayor probabilidad de continuidad.')
    rf, pfv = corr_fin()
    sel = ['IDX F2 Decisiones', 'IDX F3 Coordinación', 'IDX F4 Relaciones', 'IDX F5 Consolidación']
    tgt = ['IDX G1 Cap. científicas', 'IDX G2 Cap. institucionales', 'IDX G3 Aprendizaje', 'IDX H3 Valor productos', 'IDX I1 Contribuciones', 'F7 Balance', 'I4 Continuidad', 'J1 Prob. participar']
    ct = rf.loc[sel, tgt].astype(object).copy()
    for i in sel:
        for j in tgt:
            pv = pfv.loc[i, j]
            ct.loc[i, j] = f"{rf.loc[i, j]:.2f}{'*' if pv < 0.05 else ''}".replace('.', ',')
    ct = ct.reset_index().rename(columns={'index': 'Gobernanza'})
    D.table(ct, 'Correlación de Spearman entre gobernanza y resultados (financiados; * p<0,05)', font=7.5)

    # ================================================================ 12
    D.pagebreak()
    D.h('12. Participación futura y barreras (sección J)', 1)
    D.h('12.1 Intención de participar y liderar (J1, J2)', 2)
    D.p('El 64 % considera probable o muy probable participar en una iniciativa con otra universidad 4U en los próximos dos años y el 53 % liderar una iniciativa interinstitucional. '
        'Los financiados tienen la mayor intención "muy probable" de participar (37 % frente a 11 % de los no postulantes y 9 % de los no financiados) y de liderar (23 % frente a 2 % y 0 %). '
        'La asociación es significativa (J1 p=0,003 y J2 p<0,001 en financiado frente a resto). Entre los no financiados predomina la indecisión: el 36 % no sabe si participará y el 45 % no sabe si liderará.')
    D.img(P['j12'], 15, 'Intención de participar y liderar por grupo')
    D.table(single_short('J1', 282, 'todos', 'Grupo'), 'J1. Probabilidad de participar con otra universidad 4U', font=7.5)
    D.table(single_short('J2', 283, 'todos', 'Grupo'), 'J2. Probabilidad de liderar una iniciativa', font=7.5)
    D.h('12.2 Iniciativas de interés (J3)', 2)
    D.p('Los intereses principales son proyectos de investigación (80 %) y publicaciones conjuntas (74 %), seguidos de movilidad (61 %), formación y docencia conjunta (56 %) y presentación conjunta a convocatorias externas (54 %). '
        'Solo una persona dice no tener interés en participar. Los no postulantes muestran más interés en la formación y docencia conjunta (66 %).')
    D.img(P['mu_J3'], 16, 'J3. Iniciativas en las que tendría interés, por grupo')
    D.h('12.3 Barreras (J4)', 2)
    D.p('La falta de tiempo o carga académica es la barrera dominante (77 %), muy por encima de los procesos administrativos complejos (38 %), la falta de financiación (38 %) y la dificultad para identificar socios (37 %). '
        'Los financiados mencionan más las diferencias de procedimientos entre universidades (30 % frente a 14 % de no postulantes), mientras que los no financiados mencionan más la falta de financiación (55 %). '
        'Tres personas mencionan la jubilación como límite.')
    D.img(P['mu_J4'], 16, 'J4. Principales dificultades para participar, por grupo')
    D.h('12.4 Prioridades para la Alianza (J5)', 2)
    D.p('Las prioridades más pedidas son facilitar la identificación de socios (52 %), armonizar procedimientos administrativos (41 %) y mejorar la difusión de oportunidades (32 %). '
        'Las prioridades cambian según la experiencia: los financiados piden armonizar procedimientos (54 %) y ajustar montos y duración (33 %); los no postulantes, mejorar la difusión (49 %); los no financiados, mejorar la retroalimentación (36 %) y facilitar la continuidad de redes (36 %).')
    D.img(P['mu_J5'], 16, 'J5. Aspectos que Alianza 4U debería priorizar, por grupo')
    D.h('12.5 Disposición a continuar en la evaluación (J7)', 2)
    D.p('El 77 % autoriza ser contactado para entrevistas o grupos focales (84 % de los financiados y 64 % de los no financiados). El 76 % prefiere el correo electrónico.')

    # ================================================================ 13
    D.pagebreak()
    D.h('13. Comparaciones transversales', 1)
    D.h('13.1 Por universidad', 2)
    D.p('Las cuatro universidades tienen perfiles parecidos en la mayoría de índices; ninguna diferencia de índice entre universidades es significativa al 5 %. Las diferencias de ítem más notables son: '
        'CESA valora menos la utilidad de la colaboración (C1.1) y el sentido de comunidad (C1.4); EAFIT valora menos la formalización del proyecto (E5.8); ICESI percibe menos respuesta a problemáticas relevantes (I1.8: 3,27 frente a 4,50 de CESA y 4,07 de Uninorte; p=0,04). '
        'Uninorte tiene los valores más altos en la mayoría de índices de los proyectos financiados (F2, F3, F4, G3, H3).')
    D.note('Ninguna de las diferencias de ítem por universidad, sexo o experiencia se mantiene tras la corrección de Benjamini-Hochberg (sección 15.3).')
    D.img(P['idx_uni'], 15, 'Índices por universidad')
    t = index_by('Universidad')
    t = t[['Índice', 'Dimensión'] + [f'{u} media' for u in UNIS] + ['p-valor']]
    t.columns = [c.replace(' media', '') for c in t.columns]
    D.table(t, 'Índices por universidad', font=7.5, fmt={'p-valor': '{:.3f}'})
    D.h('13.2 Por sexo (estimado)', 2)
    t = index_by('Sexo')
    t = t[['Índice', 'Dimensión', 'Mujer media', 'Hombre media', 'p-valor']]
    t.columns = ['Índice', 'Dimensión', 'Mujeres', 'Hombres', 'p-valor']
    D.p('Ningún índice difiere significativamente por sexo. Las mujeres valoran algo peor las condiciones institucionales (3,27 frente a 3,45) y, en los proyectos financiados, la gobernanza (F2 4,14 frente a 4,63). '
        'En cambio, las mujeres financiadas reportan mayor interacción con entidades públicas y comunidades (tendencias, p<0,10).')
    D.table(t, 'Índices por sexo estimado', font=7.5, fmt={'p-valor': '{:.3f}'})
    D.h('13.3 Por experiencia y rango', 2)
    t = index_by('Experiencia')
    t = t[['Índice', 'Dimensión'] + [f'{e} media' for e in EXPS] + ['p-valor']]
    t.columns = [c.replace(' media', '') for c in t.columns]
    D.p('No hay diferencias significativas de índices por experiencia. Las personas con más de 20 años reportan menos productos con otras universidades desde 2021 (1,3 frente a 2,4-2,5; p=0,02) y menos aumento de capacidades (C4). '
        'Las personas con 10 años o menos de experiencia tuvieron la mayor tasa de éxito (93 %, 13 de 14).')
    D.table(t, 'Índices por experiencia en investigación', font=7.5, fmt={'p-valor': '{:.3f}'})
    D.h('13.4 Correlaciones generales', 2)
    D.p('En el conjunto de la muestra, la intensidad de colaboración (instituciones socias, actividades y experiencias) forma un bloque muy correlacionado (rho entre 0,59 y 0,71) y se asocia con ser financiado (rho 0,32-0,45). '
        'La disposición (C1) y el valor percibido (C2) se asocian con la intención de volver a colaborar (J1 rho=0,33 y 0,32). El conocimiento de la Alianza es la variable de perfil más asociada a ser financiado (rho=0,43).')

    # ================================================================ 14
    D.pagebreak()
    D.h('14. Lo que dicen las personas (preguntas abiertas)', 1)
    D.h('14.1 Un cambio para mejorar la línea de investigación (J6)', 2)
    D.p('Respondieron 54 personas. Los temas más frecuentes son ampliar los temas, áreas e interdisciplinariedad (26 %), simplificar y unificar los procesos administrativos (24 %) e identificar socios y conocer los perfiles de investigadores de las otras universidades (22 %). '
        'Les siguen el tiempo y la carga académica (17 %) y más recursos o autonomía presupuestal (13 %).')
    D.img(P['txt_J6'], 15, 'J6. Temas del cambio propuesto')
    D.p('Algunas propuestas textuales (anonimizadas):', italic=True)
    D.bullets(['"Contar con un único proceso administrativo entre las 4 universidades."',
               '"No dejar morir la incipiente formación de equipos de investigadores. [...] ¿Encuentro anual de investigadores de la red?"',
               '"Establecer calendario anual de formulación y presentación de convocatorias."',
               '"Que los resultados exigidos como productos de investigación no sea de dos artículos científicos sino de uno solo."',
               '"Fomentar la comunicación [...] que los investigadores conozcan en qué temas investigan los investigadores de las otras universidades de 4U [...] (una plataforma)."',
               '"Crear una ventana de oportunidad para proyectos que no se inscriban a las líneas priorizadas por la alianza."',
               '"Dar descarga académica para investigar."',
               '"En la segunda ocasión no logre incorporarme a un proyecto [...] porque las fechas de cierre de EAFIT eran diferentes a las de las otras tres universidades."'])
    D.h('14.2 El resultado más significativo (I8)', 2)
    D.p('Respondieron 42 financiados. Los resultados más mencionados son publicaciones científicas (36 %), formación de estudiantes e investigadores (26 %), colaboración y redes (24 %), la posibilidad de comparar regiones, ciudades o universidades (21 %) y desarrollos tecnológicos o herramientas (21 %). '
        'Varias respuestas describen incidencia en políticas públicas, como una hoja de ruta para el amoníaco verde en Colombia, caracterizaciones de poblaciones vulnerables usadas por instancias locales y recomendaciones sobre el tránsito de la educación media a la superior.')
    D.img(P['txt_I8'], 15, 'I8. Temas del resultado más significativo')
    D.bullets(['"El establecimiento del primer programa de monitoreo de aves de bosques seco tropical en América Latina a largo plazo con la vinculación de más de 10 estudiantes, participación de dos universidades internacionales [...]"',
               '"Dos publicaciones científicas que en conjunto a la fecha suman mas de 100 citaciones."',
               '"Haber aplicado una encuesta a 2.200 estudiantes de las universidades EAFIT, ICESI y UNINORTE sobre sus percepciones de la democracia [...]"',
               '"Construcción de página web con datos comparados de informalidad de cuatro ciudades: Cali, Medellín, Barranquilla y Cartagena."',
               '"La publicación de un artículo científico de alto impacto [...] la vinculación de una investigadora postdoctoral y la financiación externa adicional de un centro de investigación internacional."'])

    # ================================================================ 15
    add_sections(D, P, E1, E2)
    D.pagebreak()
    D.h('20. Conclusiones y recomendaciones', 1)
    D.h('20.1 Conclusiones', 2)
    D.bullets([
        'La Alianza llega a una comunidad con alta disposición a colaborar, pero con condiciones institucionales que limitan esa colaboración, en particular la carga de trabajo y los procedimientos administrativos.',
        'Quienes fueron financiados muestran más colaboración con las otras universidades 4U, más actividades conjuntas y mayor intención de volver a colaborar y liderar. Los participantes atribuyen buena parte de esto a la Alianza (alta adicionalidad percibida), aunque el diseño transversal no permite separar el efecto de la Alianza del perfil previo.',
        'La Alianza no financió solo a quienes ya tenían experiencia: 18 de los 20 postulantes sin proyectos interinstitucionales previos fueron financiados.',
        'Las convocatorias son claras en objetivos y requisitos, pero el tiempo de preparación, los procedimientos administrativos, la retroalimentación y la participación de los investigadores en el diseño de las convocatorias son puntos débiles.',
        'La gobernanza interna de los proyectos es buena y se asocia con mejores resultados. La institucionalización es el punto débil: más de una cuarta parte de los proyectos dependió de acuerdos personales y no continuó tras la financiación.',
        'La producción es principalmente académica y todavía en curso: la mayoría de artículos está en desarrollo. La interacción con entidades públicas y empresas es escasa y los cambios en prácticas o decisiones son el efecto menos observado.',
        'Los equipos no financiados tienden a disolverse.',
        'La encuesta y la presentación de EAFIT llegan a conclusiones compatibles: la Alianza aumenta la colaboración y probablemente la publicación conjunta, pero no la cantidad de productos.',
        'Las cifras de la encuesta son consistentes con las tablas de la plataforma y robustas a la ponderación por universidad y sexo. Casi todas las diferencias por universidad, sexo y experiencia son exploratorias.',
        'Hay 27 personas que no se han postulado y tienen intención de colaborar: el grupo con más potencial para nuevas convocatorias.',
    ])
    D.h('20.2 Recomendaciones derivadas de los datos', 2)
    D.bullets([
        ('Descarga académica. ', 'Acordar entre las cuatro universidades horas de descarga o reconocimiento en el plan de trabajo por participar en proyectos 4U (barrera del 77 %; C3.3 con 26 % favorable).'),
        ('Ventanilla administrativa común. ', 'Unificar calendarios de cierre, formatos y trámites contractuales entre universidades (J5 41 %; J6 24 %; C3.5 con 33 % favorable).'),
        ('Directorio y encuentros de investigadores. ', 'Crear un directorio de perfiles y líneas, y encuentros periódicos de "emparejamiento" (J5 52 %; J6 22 %).'),
        ('Mejor retroalimentación. ', 'Entregar retroalimentación detallada a todas las propuestas no financiadas y ofrecer un canal para opinar sobre las convocatorias (solo 12 % recibió retroalimentación detallada y 7 % pudo opinar).'),
        ('Apoyo a equipos no financiados. ', 'Ofrecer capital semilla, acompañamiento para re-postular o conexión con otras fuentes, para que la red formada no se pierda (5 de 8 equipos dejaron de trabajar juntos).'),
        ('Fondos de continuidad y cierre de productos. ', 'Financiar la culminación de artículos y la continuidad de redes después del proyecto (55 % de artículos en desarrollo; 28 % sin continuidad de la colaboración).'),
        ('Vinculación con usuarios. ', 'Incluir en los términos de referencia la participación temprana de entidades públicas, empresas y comunidades, y recursos para pilotos y transferencia (H5: 3 % de uso por entidades públicas y empresas).'),
        ('Ampliar temas. ', 'Evaluar una modalidad abierta o de creación para temas fuera de las líneas priorizadas y para las artes (J6: 26 % pide ampliar temas y áreas).'),
        ('Captar postulantes potenciales. ', 'Contactar a los 27 no postulantes con intención de colaborar, en su mayoría hombres y de Uninorte, con información directa y apoyo para encontrar socios.'),
        ('Integrar las dos fuentes. ', 'Usar la autorización de vinculación de datos (96 %) para unir la encuesta con la base de EAFIT y analizar si las percepciones (gobernanza, barreras) explican las diferencias de producción del event study.'),
    ])

    # ================================================================ Anexos
    D.pagebreak()
    D.h('Anexo A. Distribución completa de preguntas de respuesta única', 1)
    for code, col, lab, pop in SINGLE:
        if code in ('J7b',):
            continue
        by = 'Grupo' if pop == 'todos' else None
        D.table(single_short(code, col, pop, by), f'{code}. {lab} (población: {pop})', font=7)
    D.pagebreak()
    D.h('Anexo B. Selección múltiple por universidad', 1)
    for code, title, cols, pop in MULTI:
        D.table(multi_short(code, 'Universidad'), f'{code}. {title} (población: {pop})', font=7)
    D.pagebreak()
    D.h('Anexo C. Ítems de escala por universidad', 1)
    for code, title, cols, sc, pop in MATRIX:
        if sc == 'h1':
            continue
        D.table(by_uni_items(code), f'{code}. {title} – media por universidad', font=7, fmt={'p-valor': '{:.3f}'})
    D.h('Anexo D. Confiabilidad de los índices', 1)
    it = index_table()[['Índice', 'Dimensión', 'Población', 'N.º ítems', 'n', 'Media', 'Desv. est.', 'Mediana', '% índice ≥4', 'Alfa de Cronbach']]
    D.table(it, 'Índices compuestos y alfa de Cronbach', font=7, fmt={'Alfa de Cronbach': '{:.3f}', 'Media': '{:.2f}', 'Desv. est.': '{:.2f}', 'Mediana': '{:.2f}'})
    D.save(OUT)
    print('ok', OUT, 'figuras', D.fig_n, 'tablas', D.tab_n)


if __name__ == '__main__':
    E1 = pd.read_pickle('/projects/sandbox/work/eff_todos.pkl')
    E2 = pd.read_pickle('/projects/sandbox/work/eff_rechazados.pkl')
    build(E1, E2)
