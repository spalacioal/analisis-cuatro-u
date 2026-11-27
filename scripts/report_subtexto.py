"""Informe Word: análisis cuantitativo-cualitativo de subtexto."""
from docx_utils import Doc
import subtext as ST
import charts_ext
from extend import *

OUT = '/projects/sandbox/analisis-cuatro-u/resultados/Analisis_subtexto_Alianza_4U.docx'


def build():
    P = ST.charts()
    sl = ST.straightlining()
    gp, extra = ST.gaps()
    m, cent = ST.partner_matrix()
    D = Doc()
    D.cover('Alianza 4U: análisis de subtexto', 'Lo que los datos dicen sin decirlo, leído con el contexto de la investigación en Colombia',
            ['Encuesta a 102 docentes e investigadores · presentación de la oficina de inteligencia en CTeI de EAFIT · fuentes públicas', 'Noviembre de 2026'])

    D.h('1. Qué es este análisis', 1)
    D.p('Los informes anteriores describen lo que respondieron las personas. Este documento busca lo que está debajo: patrones en la forma de responder, '
        'contradicciones entre preguntas, silencios, el lenguaje de las respuestas abiertas y la posición de cada universidad en la red. '
        'Cada lectura se apoya en una cifra de la encuesta o de la presentación de EAFIT, y se interpreta con información pública sobre el sistema de ciencia colombiano. '
        'Son interpretaciones razonadas, no hechos comprobados: sirven para formular preguntas para las entrevistas y grupos focales que autorizaron 75 personas.')

    D.h('2. El contexto en el que opera la Alianza', 1)
    D.p('La Alianza 4U reúne a cuatro universidades privadas de cuatro regiones: CESA en Bogotá, EAFIT en Medellín, Icesi en Cali y la Universidad del Norte en Barranquilla. '
        'Se creó para complementarse en docencia, investigación y extensión, y declara valores compartidos como la defensa de la democracia y de las libertades individuales y de empresa. '
        'En 2024 firmó un memorando con la Universidad de Purdue.')
    D.img(P['ctx'], 15, 'Inversión en I+D y presupuesto de MinCiencias')
    D.table(ST.context_table(), 'Indicadores de contexto y su lectura frente a la Alianza', font=8, widths=[5.5, 3.5, 7])
    D.p('Colombia invirtió el 0,21 % del PIB en I+D en 2022, frente a 2,71 % en la OCDE, y el presupuesto de MinCiencias cayó de unos 485 mil millones de pesos en 2023 a unos 300 mil millones en 2025. '
        'En ese contexto, los COP 5.512 millones que la Alianza asignó en cuatro convocatorias son una suma pequeña para el país pero significativa para estos equipos, '
        'y explican la alta adicionalidad percibida: el 48 % de los financiados cree que sin la Alianza el proyecto no habría existido. '
        'Con la financiación pública en retroceso, las alianzas entre universidades privadas pasan de complemento a fuente principal para parte de sus investigadores.')
    D.p('El sistema colombiano reconoce a grupos e investigadores mediante el modelo de medición de MinCiencias (categorías Junior, Asociado, Senior; grupos A1 a C), que valora sobre todo productos de nuevo conocimiento como artículos indexados. '
        'Ese modelo es el telón de fondo de varios hallazgos: el 98 % de los proyectos prevé artículos, el 90 % los escribe con coautores de otra universidad 4U, y solo el 5 % genera propiedad intelectual. '
        'La literatura colombiana sobre trabajo académico describe además un aumento de la carga de los profesores y una presión creciente por productividad, lo que coincide con la barrera principal de la encuesta.')

    D.h('3. Subtexto 1: voluntad sin tiempo', 1)
    D.p(f'El promedio de respuestas favorables en disposición a colaborar (C1) es {ST.c_fav_avg("C1"):.0f} %; en condiciones institucionales (C3), {ST.c_fav_avg("C3"):.0f} %. '
        'Es la brecha más grande de la encuesta. Además, el 93 % se siente preparado para participar en un equipo interinstitucional, pero solo el 64 % cree probable hacerlo en los próximos dos años.')
    D.img(P['gaps'], 16, 'Brechas entre lo que se declara y lo que se evidencia')
    D.p('El subtexto es que la colaboración no falla por falta de voluntad ni de confianza, sino porque compite con la docencia. '
        'En las universidades privadas colombianas la matrícula financia la operación, y la investigación ocupa una fracción de la jornada: el 73 % de los encuestados dedica 40 % o menos a investigar. '
        'La Alianza financia proyectos, pero no compra tiempo de los profesores. Varias respuestas abiertas lo dicen directamente: "dar descarga académica para investigar", "que estos proyectos equilibren cargas académicas". '
        'Que tres personas mencionen la jubilación como límite sugiere además que una parte del núcleo investigador está cerca del retiro, coherente con el 47 % de aprobados con 20 o más años de trayectoria según EAFIT.')

    D.h('4. Subtexto 2: la autoevaluación generosa', 1)
    D.p('Una forma de leer la calidad de las respuestas es contar cuántas personas eligieron exactamente la misma opción en todos los ítems de un bloque. '
        'Cuando el bloque trata sobre el propio proyecto, esa proporción se dispara: 42 % en gobernanza (F2), 42 % en relaciones (F4), 42 % en aprendizaje (G3) y 50 % en la valoración de los productos (H3), casi siempre con la opción más alta. '
        'Cuando el bloque trata sobre la institución (C3), baja a 10 %.')
    D.img(P['straight'], 15, 'Respuestas uniformes por bloque')
    D.table(sl[['Bloque', 'Tema', 'Personas', 'Misma respuesta en todos los ítems', '%', 'Respuesta más repetida', 'Índice (todos)', 'Índice (sin respuestas uniformes)']],
            'Respuestas uniformes y su efecto en los índices', font=7.5)
    D.p('Sin las respuestas uniformes, el índice de gobernanza baja de 4,36 a 3,93 y el de consolidación de 4,02 a 3,69. '
        f'Además, {extra[list(extra)[0]]} financiados califican alto sus productos y al mismo tiempo dicen no tener evidencia de uso o no saberlo. '
        'Esto no significa que las respuestas sean falsas. Es el patrón conocido de deseabilidad social y de efecto halo: quien evalúa su propio proyecto, financiado por una red a la que pertenece y en una encuesta identificada con nombre y cédula, tiende a calificar alto todo el bloque. '
        'Las cifras de gobernanza, productos e impacto deben leerse como un techo. Las de condiciones institucionales, en cambio, son probablemente la lectura más honesta de la encuesta.')
    D.p('Un dato en sentido contrario: los investigadores reportan menos artículos terminados (38 %) que la evidencia documental de EAFIT (61 % finalizados o sometidos). '
        'Para un investigador, un artículo sometido no está "completado" hasta que se publica. La generosidad se concentra en la valoración, no en los conteos.')

    D.h('5. Subtexto 3: los silencios', 1)
    D.p('Las respuestas "no recuerdo", "no sé" o "no aplica" dicen dónde la Alianza deja poco rastro.')
    D.img(P['ns'], 15, 'Proporción de "no sé / no recuerdo / no aplica" por bloque')
    D.p('El 40 % no recuerda si tuvo oportunidad de opinar sobre la convocatoria y el 33 % no recuerda si recibió retroalimentación. '
        'Una retroalimentación útil se recuerda; que no se recuerde es en sí un resultado. '
        'Los bloques con más silencios son la interacción con actores externos (H5, 16 %), el proceso de la convocatoria (E5, 16 %) y las contribuciones (I1, 11 %): '
        'los investigadores conocen bien lo que pasa dentro de su proyecto y poco lo que pasa fuera de él. '
        'EAFIT encuentra un patrón paralelo en los registros: 6 de 23 proyectos sin cierre o estado verificable. La Alianza se vive más de lo que se documenta.')

    D.h('6. Subtexto 4: una red con centro y periferia', 1)
    D.img(P['net'], 12, 'Con quién declara colaborar cada universidad')
    D.img(P['cent'], 12, 'Centralidad de cada universidad')
    D.p(f'Uninorte es mencionada como socia por el {cent.iloc[3, 1]:.0f} % de las personas de las otras tres universidades; EAFIT por el {cent.iloc[1, 1]:.0f} %, ICESI por el {cent.iloc[2, 1]:.0f} % y CESA por el {cent.iloc[0, 1]:.0f} %. '
        'Según EAFIT, Uninorte participa en los 23 proyectos y reúne el 47 % de los aprobados. Solo el 5 % de los encuestados de EAFIT dice haber colaborado con CESA.')
    D.p('El subtexto es que la Alianza funciona como una red con un nodo central. Uninorte tiene la mayor base de investigadores y es la única universidad del Caribe en la red, lo que la hace un socio "necesario" para proyectos comparativos entre regiones, '
        'uno de los resultados más valorados (21 % de los resultados significativos son comparaciones entre ciudades o universidades). '
        'CESA, centrada en administración y con la planta más pequeña, queda en la periferia. Sus valores más bajos en utilidad de la colaboración (4,00 frente a 4,89 en EAFIT) y en sentido de comunidad (3,83) '
        'probablemente reflejan esa posición, no un rechazo a la colaboración. Su menor tasa de éxito entre encuestados (4 de 7) apunta en la misma dirección.')

    D.h('7. Subtexto 5: concentración y efecto Mateo', 1)
    D.img(P['conc'], 13, 'Concentración de participaciones (datos de EAFIT)')
    D.table(ST.concentration(), 'Indicadores de concentración', font=8)
    D.p('Cinco investigadores ganaron las cuatro convocatorias y comparten los mismos proyectos (8, 9 y 13, según EAFIT); suman el 14 % de las participaciones. '
        'Diecisiete de 96 aprobados repiten. En la literatura se llama "efecto Mateo": quien ya fue financiado tiene más probabilidad de volver a serlo, en parte por mérito y en parte porque el primer éxito da visibilidad, socios y experiencia en postular. '
        'La encuesta muestra las dos caras: los financiados tienen más socios, conocen mejor la Alianza (64 % frente a 21 %) y tienen más intención de liderar; '
        'los no financiados se dispersan (5 de 8 equipos se disolvieron) y piden "facilitar la identificación de socios" (55 %). '
        'La red funciona, pero sobre todo entre quienes ya se conocen. Al mismo tiempo, la Alianza sí abrió espacio a nuevos investigadores: 18 de 20 postulantes encuestados sin experiencia interinstitucional previa fueron financiados.')

    D.h('8. Subtexto 6: el lenguaje de las respuestas abiertas', 1)
    D.img(P['lex'], 14, 'Campos semánticos en las propuestas de cambio (J6)')
    D.table(ST.lexicon_table(), 'Campos semánticos en J6 (una respuesta puede tener varios)', font=8)
    D.p('El campo semántico dominante es la fricción administrativa, con palabras como "desgastante", "lentos", "la firma de un abogado" o "fechas de cierre diferentes". '
        'Una respuesta de ICESI dice que en su universidad los procesos son ágiles pero "en las otras universidades pueden ser muy lentos"; otra de EAFIT cuenta que no pudo unirse a un proyecto porque las fechas de cierre de EAFIT eran distintas. '
        'El 15 % de las propuestas compara implícitamente su universidad con las demás. El subtexto es que la Alianza todavía se vive como cuatro sistemas administrativos yuxtapuestos, no como una red con reglas propias.')
    D.p('El segundo campo es la pertenencia: pedir conocer los perfiles de los otros investigadores, un encuentro anual, una plataforma. Uno de cada cuatro encuestados no se siente parte de una comunidad que trasciende su universidad (C1.4). '
        'El tercero es la autonomía temática: ampliar las líneas, abrir una ventana para proyectos fuera de las prioridades, más espacio para las artes. '
        'Detrás aparece una tensión entre la Alianza como política institucional, con temas definidos por las universidades, y la investigación como iniciativa de los profesores.')
    D.table(ST.flagship_table(), 'Líneas de proyecto reconocibles en los textos de los financiados', font=8)
    D.p('Las respuestas abiertas también muestran que unas pocas líneas de proyecto dominan la narrativa: la economía informal en cuatro ciudades y la IA aplicada al aprendizaje aparecen en 4 o 5 respuestas cada una. '
        'Como los 45 financiados encuestados representan menos de 23 proyectos, algunos proyectos pesan varias veces en los promedios. Es otra razón para leer los índices de proyecto con cautela.')

    D.h('9. Subtexto 7: género', 1)
    D.img(P['gender'], 13, 'Participación de mujeres en el país, el programa y la encuesta')
    D.p('La Alianza aprueba una proporción de mujeres (44,8 %) mayor que la de investigadoras reconocidas por MinCiencias (40,5 % en 2024), y en Colombia las mujeres lideran menos del 30 % de los grupos. '
        'Entre los investigadores principales financiados que respondieron, 9 de 17 son mujeres. '
        'Pero hay matices: las mujeres respondieron más la encuesta (58 % frente a 40 % de los hombres aprobados), ocupan 12 de 19 cargos de gestión académica, las 5 posiciones de "integrante del equipo" y valoran peor la gobernanza (4,14 frente a 4,63) y la continuidad de la colaboración (3,41 frente a 4,47). '
        'Uno de los proyectos financiados encontró justamente un "parámetro interinstitucional de exclusión de mujeres" en las universidades de la red. '
        'La lectura es que la Alianza tiene una paridad de entrada superior al país, pero la experiencia dentro de los proyectos no es igual para hombres y mujeres. Las diferencias no resisten la corrección estadística y deberían explorarse en los grupos focales.')

    D.h('10. Subtexto 8: quién respondió y quién no', 1)
    D.p('La encuesta cubre al 47 % de los aprobados, con más respuesta de CESA (57 %) y de mujeres (58 %), y menos de Uninorte (42 %) y de hombres (40 %). '
        'Responder una encuesta de 24 minutos identificada con nombre y cédula exige interés: es probable que respondieran más quienes tuvieron una experiencia intensa con la Alianza, buena o mala. '
        'Los 45 no postulantes que respondieron tampoco son "la comunidad que no participa": el 89 % conocía la Alianza y 26 de ellos recibieron información, asistieron a eventos o actuaron como evaluadores. '
        'Los profesores que nunca se enteraron de la Alianza probablemente no están en la base.')
    D.table(ST.duration_profile(), 'Duración de la encuesta y calidad de las respuestas', font=8)
    D.p('Quienes tardaron entre 20 y 40 minutos escribieron propuestas más largas (22 palabras en promedio frente a 9 de quienes tardaron menos de 10). '
        'Quienes respondieron rápido valoran peor las condiciones institucionales (3,08), un indicio de que la crítica a las condiciones no depende de la reflexión pausada: es la respuesta inmediata.')

    D.h('11. Preguntas para las entrevistas y grupos focales', 1)
    D.bullets([
        '¿Qué haría falta, en horas concretas de descarga, para que un profesor pueda liderar un proyecto 4U?',
        '¿Por qué tantos proyectos califican todo como "completamente" bien? ¿Qué no funcionó y no se dijo?',
        '¿Qué pasó con los equipos no financiados y qué habría permitido que siguieran?',
        '¿Cómo vive CESA su lugar en la red? ¿Qué la haría un socio más buscado?',
        '¿Las mujeres viven distinto la toma de decisiones en los proyectos? ¿Por qué ocupan más los roles de apoyo?',
        '¿Qué trámite concreto de cada universidad es el que más frena a las demás?',
        '¿Qué evidencia de uso existe y no se ha documentado?',
    ])

    D.h('Fuentes', 1)
    for a, b in ST.SOURCES:
        D.p(f'{a}. {b}', size=9)
    D.note('Las cifras de contexto provienen de fuentes públicas citadas; el texto fue parafraseado. Las interpretaciones son del autor del análisis.')
    D.save(OUT)
    print('ok', OUT, D.fig_n, D.tab_n)


if __name__ == '__main__':
    build()
