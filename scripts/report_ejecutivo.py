"""Informe ejecutivo (Word)."""
from facts import *
from docx_utils import Doc
import charts

OUT = '/projects/sandbox/analisis-cuatro-u/resultados/Informe_ejecutivo_Alianza_4U.docx'


def build():
    P = charts.build_all()
    D = Doc()
    D.cover('Alianza 4U: resultados de la línea de investigación',
            'Informe ejecutivo de la encuesta a docentes e investigadores',
            ['CESA · EAFIT · Icesi · Universidad del Norte', '102 personas encuestadas · septiembre a noviembre de 2026', 'Noviembre de 2026'])

    D.h('1. Cifras clave', 1)
    D.kpis([('102', 'personas encuestadas en las 4 universidades'),
            ('45 / 11 / 45', 'financiados / postularon sin éxito / no postularon'),
            ('80 %', 'tasa de éxito de las postulaciones (45 de 56)'),
            ('50 % / 50 %', 'mujeres / hombres (estimado por nombre)'),
            ('75 %', 'con más de 10 años de experiencia investigativa'),
            ('75 %', 'dedica 40 % o menos de su tiempo a investigar'),
            ('4,41 / 5', 'disposición a colaborar entre universidades'),
            ('3,36 / 5', 'condiciones institucionales para hacerlo'),
            ('48 %', 'de financiados: sin 4U el proyecto no habría existido'),
            ('38 %', 'de proyectos con artículos ya completados (55 % en desarrollo)'),
            ('77 %', 'señala la falta de tiempo como principal barrera'),
            ('64 %', 'probablemente colaborará con otra universidad 4U en 2 años')])
    D.note('La encuesta no pregunta edad ni sexo. El sexo se estimó a partir del primer nombre; la edad no puede reportarse y se usa la experiencia investigativa como aproximación.')

    D.h('2. Quiénes respondieron', 1)
    D.p('Respondieron 12 personas de CESA, 23 de EAFIT, 25 de ICESI y 42 de Uninorte. El 80 % es profesor de planta y el 62 % combina docencia e investigación. '
        'Por rango, predominan los asistentes (43 %), seguidos de asociados (22 %) y titulares (20 %). Las áreas más representadas son Economía y negocios (25 %) e Ingeniería y tecnología (24 %). '
        'La muestra es paritaria por sexo estimado y la proporción se mantiene en las cuatro universidades. Los hombres predominan en Ingeniería (18 de 24) y las mujeres en Economía y negocios (17 de 26) y Humanidades (10 de 14).')
    D.img(P['grupos_uni'], 14, 'Encuestados por universidad y grupo')
    prof = pd.DataFrame([
        ['Mujeres (estimado)', '56 %', '73 %', '40 %'],
        ['Más de 20 años de experiencia', '27 %', '45 %', '33 %'],
        ['Profesor(a) asistente', '51 %', '36 %', '38 %'],
        ['Dedicación a investigación (promedio aprox.)', '31 %', '27 %', '27 %'],
        ['Sin proyectos interinstitucionales antes de 2021', '40 %', '18 %', '50 %'],
        ['Conocía bastante o a fondo la Alianza', '64 %', '36 %', '21 %'],
    ], columns=['Indicador', 'Financiados (45)', 'No financiados (11)', 'No postularon (45)'])
    D.table(prof, 'Perfil por grupo', font=8.5)

    D.h('3. Hallazgos principales', 1)
    D.h('3.1 Mucha disposición, pocas condiciones', 2)
    D.p('Entre el 93 % y el 95 % confía en la calidad del trabajo de otras universidades, considera útil colaborar y se siente preparado para participar en equipos interinstitucionales. '
        'Pero solo el 26 % dice que su carga de trabajo le permite participar y el 33 % que los procedimientos administrativos facilitan el trabajo con otras instituciones. '
        'Esta percepción es igual en financiados y no financiados y en las cuatro universidades: es un problema estructural, no de un grupo.')
    D.img(P['lk_C3'], 15, 'Condiciones institucionales para investigar con otras instituciones')

    D.h('3.2 Los financiados colaboran más', 2)
    D.table(pd.DataFrame([
        ['Universidades 4U distintas a la propia con las que colaboró', '1,9', '0,5', '0,5', '<0,001'],
        ['Tipos de instituciones socias desde 2021', '3,5', '2,4', '1,9', '<0,001'],
        ['Experiencias interinstitucionales desde 2021 (aprox.)', '12,3', '10,0', '6,2', '0,001'],
        ['Proyectos ejecutados con otra universidad (aprox.)', '2,0', '1,1', '0,8', '<0,001'],
        ['Probable o muy probable volver a colaborar (J1)', '72 %', '45 %', '61 %', '0,003*'],
        ['Probable o muy probable liderar (J2)', '65 %', '36 %', '45 %', '<0,001*'],
    ], columns=['Indicador', 'Financiados', 'No financiados', 'No postularon', 'p-valor']),
        'Colaboración e intención futura por grupo (* financiados frente al resto)', font=8.5)
    D.p('La diferencia es coherente con un efecto de la Alianza, que los propios financiados confirman (ver 3.5). Sin embargo, la encuesta es transversal y los financiados ya conocían mejor la Alianza, por lo que parte de la diferencia puede deberse al perfil previo. '
        'La experiencia previa en proyectos interinstitucionales no difiere entre grupos, y 18 de los 20 postulantes sin esa experiencia fueron financiados.')

    D.h('3.3 Convocatorias: claras, pero con poco tiempo y poca retroalimentación', 2)
    D.p('Los objetivos (94 % favorable), los requisitos (89 %) y los criterios de evaluación (88 %) se consideran claros. Lo menos valorado es el tiempo para preparar la propuesta (55 %) y la claridad de los procedimientos administrativos (53 %). '
        'Solo el 12 % recibió retroalimentación detallada y solo 3 de 45 personas pudieron opinar sobre la convocatoria. Los no financiados valoran peor los criterios de evaluación (3,78 frente a 4,49) y la comunicación de la decisión (3,75 frente a 4,39). '
        'De 8 equipos no financiados que informaron qué pasó, 5 dejaron de trabajar juntos.')
    D.p('Ciencias sociales tuvo una tasa de éxito de 43 % (3 de 7), frente a 86 % en las demás áreas. Es la única diferencia de éxito significativa (p=0,02). CESA tuvo 57 % (4 de 7), sin diferencia significativa.')
    D.img(P['exito'], 14, 'Tasa de éxito por perfil del postulante')

    D.h('3.4 Proyectos financiados: buena gobernanza, institucionalización débil', 2)
    D.p('El 91 % sabía quién tomaba las decisiones y el 86 % considera que las capacidades de las instituciones fueron complementarias. El 53 % reporta más esfuerzo de coordinación que en un proyecto de una sola universidad, pero el 58 % considera que los beneficios superaron las dificultades. '
        'El punto débil es la institucionalización: el 27 % dice que el proyecto dependió de acuerdos personales y el 28 % que la colaboración no siguió tras la financiación. '
        'Los proyectos con mejor gobernanza reportan más capacidades fortalecidas, mejores productos y mayor probabilidad de continuidad (correlaciones de 0,33 a 0,67).')

    D.h('3.5 Productos y adicionalidad', 2)
    D.p('Los artículos científicos estaban previstos en casi todos los proyectos (98 %), pero solo el 38 % los reporta completados. Los productos completados más comunes son de divulgación (50 %) e informes técnicos (48 %). '
        'El 90 % produce artículos con coautores de al menos dos universidades 4U. Los prototipos (7 %) y la propiedad intelectual (5 %) son marginales.')
    D.img(P['h1'], 15, 'Estado de los productos de los proyectos financiados')
    D.p('El 48 % de los financiados cree que sin la Alianza el proyecto no se habría realizado, el 26 % que habría tenido menor alcance y el 17 % que se habría hecho más tarde. '
        'Lo que más se atribuye a la Alianza es la financiación (93 %), la conformación del equipo (79 %) y la integración de disciplinas (71 %).')

    D.h('3.6 Impacto fuera de la academia: todavía bajo', 2)
    D.p('El conocimiento se usa sobre todo para nuevas investigaciones (74 %) y docencia (62 %). Solo el 3 % reporta uso de resultados por entidades públicas o empresas. '
        'Los cambios en prácticas o decisiones son la contribución menos observada (32 % alta o decisiva) y el 45 % de los resultados principales aún es incipiente o no observable. '
        'Hay casos destacados de incidencia: una hoja de ruta nacional para el amoníaco verde, un programa de monitoreo de aves de bosque seco con el Instituto Humboldt y datos comparados de informalidad en cuatro ciudades.')
    D.img(P['h5'], 15, 'Interacción con actores por tipo')

    D.h('3.7 Barreras y prioridades', 2)
    D.p('La falta de tiempo o carga académica (77 %) es la barrera más citada, seguida de procesos administrativos complejos (38 %), falta de financiación (38 %) y dificultad para identificar socios (37 %). '
        'Las prioridades pedidas son facilitar la identificación de socios (52 %), armonizar procedimientos administrativos (41 %) y mejorar la difusión (32 %). '
        'En las respuestas abiertas, las propuestas más frecuentes son ampliar temas y áreas (26 %), unificar procesos administrativos (24 %) y conocer los perfiles de investigadores de las otras universidades (22 %).')
    D.img(P['mu_J4'], 15, 'Principales barreras para participar, por grupo')

    D.h('4. Recomendaciones', 1)
    D.table(pd.DataFrame([
        ['1', 'Descarga académica acordada entre las 4 universidades para proyectos 4U', '77 % cita falta de tiempo; 26 % dice que su carga lo permite'],
        ['2', 'Ventanilla y calendario administrativo comunes', '41 % lo prioriza; 33 % ve facilidades administrativas'],
        ['3', 'Directorio de investigadores y encuentros de emparejamiento', '52 % lo prioriza; 22 % lo propone en texto abierto'],
        ['4', 'Retroalimentación detallada a toda propuesta y canal para opinar', '12 % recibió retroalimentación detallada; 7 % pudo opinar'],
        ['5', 'Apoyo a equipos no financiados (semilla o re-postulación)', '5 de 8 equipos no financiados se disolvieron'],
        ['6', 'Fondo de cierre de productos y continuidad de redes', '55 % de artículos en desarrollo; 28 % sin continuidad'],
        ['7', 'Exigir y financiar la vinculación temprana de usuarios externos', '3 % de uso por entidades públicas y empresas'],
        ['8', 'Modalidad abierta para áreas menos representadas', 'Éxito de Ciencias sociales: 43 %; 26 % pide ampliar temas'],
        ['9', 'Medir producción real con datos bibliométricos', '96 % autorizó la vinculación de sus datos'],
    ], columns=['#', 'Recomendación', 'Evidencia']), 'Recomendaciones y evidencia que las sustenta', font=8.5, widths=[0.8, 8, 7.5])
    D.h('5. Nota metodológica', 1)
    D.p('Base: 102 registros únicos (97 completos) de las exportaciones de CESA, EAFIT, ICESI y Uninorte. Grupos definidos por la pregunta E2. Escalas codificadas de 1 a 5; se excluyen "No sabe" y "No aplica". '
        'Pruebas no paramétricas (Kruskal-Wallis, Mann-Whitney, Fisher, Spearman). La muestra es pequeña y no probabilística, por lo que las diferencias son indicativas. '
        'El detalle completo está en el Informe técnico detallado y en el libro de Excel de estadísticas.', size=9)
    D.save(OUT)
    print('ok', OUT, D.fig_n, D.tab_n)


if __name__ == '__main__':
    build()
