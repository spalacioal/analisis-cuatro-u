"""Secciones nuevas del informe detallado: verificación, comparación con EAFIT, representatividad,
efecto ajustado, robustez estadística y postulantes potenciales."""
from extend import *


def f1(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')


def add_sections(D, P, E1, E2):
    # ---------------------------------------------------------------- 15 verificación
    D.pagebreak()
    D.h('15. Verificación de los datos', 1)
    vs, pq = verification_summary()
    tot, coin = int(vs['Celdas comparadas'].sum()), int(vs['Coinciden'].sum())
    neg = int(vs['Base > plataforma'].sum())
    D.p('Hice tres verificaciones independientes de las cifras de este informe.')
    D.h('15.1 Contra las tablas resumen de la plataforma', 2)
    th = lambda x: f'{x:,}'.replace(',', '.')
    D.p(f'Cada archivo de resultados trae, además de los datos crudos, tablas de frecuencias calculadas por la propia plataforma. Comparé {th(tot)} celdas (categoría por pregunta y universidad) '
        f'con los conteos que obtengo de los datos crudos. Coinciden {th(coin)} ({f1(100 * coin / tot)} %). En ninguna celda la base exportada tiene más respuestas que la plataforma ({neg} casos). '
        'Todas las diferencias van en la misma dirección: la plataforma cuenta más personas.')
    D.table(vs, 'Coincidencia entre la base exportada y las tablas de la plataforma', font=8)
    D.p('La causa es que las tablas de la plataforma incluyen respuestas parciales que no quedaron en la hoja "Datos sin procesar". '
        'En el perfil (sección B) hay 16 personas más en la plataforma (2 en CESA, 2 en EAFIT, 9 en ICESI y 3 en Uninorte), es decir 118 perfiles frente a 102. '
        'De esas 16, dos se declaran financiadas (una de ICESI y una de Uninorte), una no financiada y una no recuerda el resultado; casi ninguna llegó a las secciones F a J. '
        'Para descartar que su ausencia sesgue los resultados, comparé las distribuciones de perfil con los 118 de la plataforma: ninguna categoría difiere en más de 3,3 puntos porcentuales.')
    pp = platform_profile()
    D.table(pp[pp['Pregunta'].isin(['B4', 'B9', 'B10', 'E2'])], 'Perfil con la base exportada (102) frente a las tablas de la plataforma (118)', font=7)
    D.h('15.2 Recálculo de las cifras citadas', 2)
    cl = claims()
    D.p(f'Recalculé {len(cl)} cifras citadas en los informes directamente desde los datos crudos, sin pasar por el código de preparación. Todas coinciden. '
        'Una de ellas (el 7 % que pudo opinar sobre la convocatoria) solo coincide cuando se restringe a los postulantes; la pregunta E7 también la respondieron 19 personas que no se postularon.')
    D.table(cl, 'Cifras del informe recalculadas desde los datos crudos', font=7)
    D.h('15.3 Comparaciones múltiples', 2)
    mt = multiple_testing()
    sig = mt[mt['p-valor'] < 0.05]
    surv = sig[sig['Significativo tras corrección (q<0,05)'] == 'Sí']
    D.p(f'En el informe se probaron {len(mt)} diferencias de ítems entre grupos, universidades, sexos y niveles de experiencia. Con tantas pruebas, algunas salen con p<0,05 por azar. '
        f'Apliqué la corrección de Benjamini-Hochberg: de las {len(sig)} diferencias con p<0,05, solo {len(surv)} se mantienen: '
        + ', '.join(f"{r['Ítem']} ({r['Enunciado'].rstrip('.').lower()})" for _, r in surv.iterrows()) +
        ', ambas entre grupos de vinculación. Las demás diferencias por universidad, sexo y experiencia citadas en las secciones 5 a 13 deben leerse como exploratorias.')
    D.table(sig[['Dimensión', 'Ítem', 'Enunciado', 'p-valor', 'q (Benjamini-Hochberg)', 'Significativo tras corrección (q<0,05)']].rename(
        columns={'Significativo tras corrección (q<0,05)': 'Se mantiene'}), 'Diferencias con p<0,05 antes y después de la corrección', font=7, fmt={'p-valor': '{:.4f}', 'q (Benjamini-Hochberg)': '{:.4f}'})
    D.h('15.4 Intervalos de confianza', 2)
    ci = ci_table()
    D.p('Con muestras de este tamaño, los porcentajes tienen márgenes de error amplios: unos ±9 puntos para preguntas a toda la muestra y ±14 puntos para preguntas solo a financiados. '
        'Por ejemplo, el 80,4 % de éxito entre postulantes encuestados tiene un intervalo de 68 % a 89 %, y el 48 % que cree que sin la Alianza el proyecto no habría existido, de 33 % a 62 %.')
    D.table(ci, 'Intervalos de confianza al 95 % (Wilson para proporciones; bootstrap para índices)', font=7.5)

    # ---------------------------------------------------------------- 16 comparación EAFIT
    D.pagebreak()
    D.h('16. Comparación con la presentación de la oficina de inteligencia en CTeI de EAFIT', 1)
    D.p('La presentación "Informe de resultados Alianza 4U" (septiembre de 2026) analiza los registros del programa: 23 proyectos, COP 5.512 millones, 96 investigadores aprobados (110 autores, 141 participaciones), '
        'su trayectoria en CvLAC y su producción en bases bibliográficas. Este informe analiza la encuesta. Para comparar, reagrupé las variables de la encuesta en los rangos que usa EAFIT cuando ambos miden algo parecido.')
    H = harmonized()
    D.img(P['harm'], 16, 'Encuesta (financiados) frente a presentación de EAFIT, con rangos armonizados')
    D.table(H[['Tema', 'Categoría', 'EAFIT %', 'EAFIT n', 'Encuesta %', 'Encuesta n', 'Diferencia (pp)']], 'Comparación con rangos armonizados', font=7)
    D.h('16.1 Qué coincide y qué no', 2)
    D.bullets([
        ('Universidad: coincide. ', 'La distribución de los financiados encuestados reproduce la de los aprobados con diferencias de menos de 5 puntos (Uninorte 42 % frente a 47 %).'),
        ('Sexo: difiere 11 puntos. ', 'Los financiados encuestados son 56 % mujeres frente a 44,8 % entre los aprobados. No es un error de estimación del sexo: las mujeres aprobadas respondieron más (25 de 43, 58 %) que los hombres (20 de 50, 40 %).'),
        ('Área: difiere por la forma de clasificar. ', 'EAFIT asigna el área según el programa del título más alto; la encuesta, según lo que la persona eligió. Ciencias sociales pasa de 30,2 % en EAFIT a 6,7 % en la encuesta, y Economía de 16,0 % a 28,9 %. '
                    'Si se suma Humanidades a Ciencias sociales, la encuesta llega a 22 %. Las dos fuentes no son comparables en esta variable.'),
        ('Trayectoria: miden cosas distintas. ', 'EAFIT mide años desde el pregrado (47 % con 20 o más); la encuesta, años de experiencia en investigación (27 % con más de 20). Es esperable que la experiencia investigativa sea menor que el tiempo desde el pregrado.'),
        ('Estado de los proyectos y artículos: unidad distinta. ', 'EAFIT cuenta proyectos y artículos con evidencia documental; la encuesta cuenta personas. '
                    'EAFIT registra 61 % de artículos finalizados o sometidos; en la encuesta, el 39 % de las personas con artículos previstos los reporta completados. Probablemente muchos encuestados marcaron "En desarrollo" artículos ya sometidos. '
                    'En el estado del proyecto, EAFIT tiene 26 % sin cierre o estado verificable y la encuesta 2 %: los investigadores dicen conocer el estado, pero la evidencia documental no siempre existe.'),
        ('Tipo de colaboración y número de universidades: no comparables. ', 'La encuesta no identifica el proyecto, así que solo puede aproximar estas variables con lo que la persona hizo desde 2021. Las cifras se muestran en la tabla, pero no deben usarse para contrastar.'),
    ])
    D.h('16.2 Lo que la encuesta no puede medir y EAFIT sí', 2)
    D.p('Montos financiados, nivel educativo (83 % con doctorado), clasificación en MinCiencias (81 % clasificados), producción bibliográfica previa (mediana de 11 artículos antes de postular), '
        'cuartiles (10 de 13 publicaciones en Q1), citas (120) y FWCI (1,08 promedio), y los 17 investigadores que ganaron más de una convocatoria. '
        'La encuesta tampoco pregunta edad; EAFIT tampoco la reporta y advierte que la etapa académica no equivale a edad.')
    D.h('16.3 Lo que la encuesta agrega', 2)
    D.p('La encuesta aporta la percepción sobre las convocatorias, la gobernanza de los proyectos, las capacidades fortalecidas, la interacción con actores externos, la adicionalidad percibida, las barreras y las prioridades, '
        'además de la visión de quienes no se postularon (45 personas), que no aparecen en los registros del programa.')

    # ---------------------------------------------------------------- 17 representatividad
    D.pagebreak()
    D.h('17. Representatividad y ponderación', 1)
    C = coverage()
    D.p('Con los 96 aprobados que reporta EAFIT como referencia, la encuesta cubre al 46,9 % (45 personas). La cobertura es mayor en CESA (57 %) y entre mujeres (58 %), y menor en Uninorte (42 %) y entre hombres (40 %).')
    D.img(P['cov'], 14, 'Cobertura de la encuesta sobre los aprobados')
    D.table(C, 'Cobertura por universidad y sexo', font=8)
    wi, wt = weighted_indicators()
    D.p('Para medir cuánto afecta esta diferencia, calculé pesos por raking (ajuste iterativo a los márgenes de universidad y sexo de los 96 aprobados) y recalculé los indicadores de los financiados. '
        f'Los resultados casi no cambian: la mayor diferencia en porcentajes es de {f1(wi["Diferencia"].iloc[:8].abs().max())} puntos (probabilidad de continuidad sin nueva financiación) y en índices de {f1(wi["Diferencia"].iloc[8:].abs().max(), 2)}. '
        'El sesgo por la mayor respuesta de las mujeres no altera las conclusiones.')
    D.table(wi, 'Indicadores de financiados sin ponderar y ponderados', font=7.5)
    D.table(wt, 'Pesos por universidad y sexo', font=7.5, fmt={'Peso': '{:.3f}'})
    D.p('La cobertura de los rechazados es desconocida: EAFIT usa 23 rechazados únicos como controles para las cohortes 2021-2022, pero no informa el total de rechazados. La encuesta tiene 11. '
        'Por eso el 80,4 % de éxito de este informe no es la tasa de aprobación del programa.')

    # ---------------------------------------------------------------- 18 efecto ajustado
    D.pagebreak()
    D.h('18. Efecto ajustado de ser financiado', 1)
    D.p('Las diferencias brutas entre financiados y no financiados pueden deberse al perfil de las personas y no a la Alianza. Para acercarme al enfoque de EAFIT, repliqué sus dos estrategias con los datos de la encuesta:')
    D.bullets([
        ('Estrategia 1, todos los no financiados como controles ', '(análoga a los controles sintéticos de EAFIT): 45 financiados frente a hasta 55 personas que no se postularon o no fueron financiadas.'),
        ('Estrategia 2, solo los rechazados como controles ', '(análoga a la segunda estrategia de EAFIT): 45 financiados frente a 11 postulantes no financiados.'),
    ])
    D.p('Como EAFIT, estimo un puntaje de propensión y emparejo cada financiado con un control, con reemplazo y con emparejamiento exacto por universidad. '
        'Las covariables son las disponibles antes de la Alianza: sexo, años de experiencia, dedicación a la investigación, rango, área (rangos EAFIT) y proyectos interinstitucionales antes de 2021 (equivalente a la producción previa de EAFIT). '
        'Los intervalos de confianza salen de 500 réplicas bootstrap. Como contraste, también estimo una regresión lineal con las mismas covariables y errores robustos.')
    D.img(P['eff'], 16, 'Efecto ajustado de ser financiado en resultados binarios, por estrategia')
    cols = ['Resultado', 'Financiados n', 'Controles n', 'Diferencia bruta', 'ATT emparejamiento', 'IC95% inf', 'IC95% sup', 'p (bootstrap)', 'MCO coef.', 'MCO p']
    D.table(E1[cols], 'Estrategia 1: todos los no financiados como controles (pp o unidades)', font=7, fmt={'p (bootstrap)': '{:.3f}', 'MCO p': '{:.3f}'})
    D.table(E2[cols], 'Estrategia 2: rechazados como controles (pp o unidades)', font=7, fmt={'p (bootstrap)': '{:.3f}', 'MCO p': '{:.3f}'})
    g = lambda E, k, c='ATT emparejamiento': E.loc[E['Resultado'].str.startswith(k), c].iloc[0]
    D.h('18.1 Resultados', 2)
    D.bullets([
        ('Colaboración con otra universidad 4U: efecto grande y significativo en las dos estrategias. ',
         f'+{f1(g(E1, "Colaboró"))} pp con todos los controles y +{f1(g(E2, "Colaboró"))} pp con rechazados. Este resultado es en parte mecánico: un proyecto 4U implica colaborar con otra universidad 4U.'),
        ('Proyectos ejecutados con otra universidad: significativo en ambas. ', f'+{f1(g(E1, "Al menos un proyecto"))} pp y +{f1(g(E2, "Al menos un proyecto"))} pp. Mismo matiz que el anterior.'),
        ('Publicaciones o productos conjuntos: positivo, pero no concluyente. ',
         f'+{f1(g(E1, "Publicaciones"))} pp (IC {f1(g(E1, "Publicaciones", "IC95% inf"))} a {f1(g(E1, "Publicaciones", "IC95% sup"))}) con todos los controles y +{f1(g(E2, "Publicaciones"))} pp con rechazados. '
         f'La regresión con todos los controles sí es significativa (+{f1(g(E1, "Publicaciones", "MCO coef."))} pp; p={f1(g(E1, "Publicaciones", "MCO p"), 3)}). '
         'El orden de magnitud (+18 a +28 pp) coincide con el efecto de EAFIT sobre la probabilidad de publicar (+18 a +36 pp).'),
        ('Cantidad de productos: sin efecto. ', f'{f1(g(E1, "N.º de productos"), 2)} productos con todos los controles y {f1(g(E2, "N.º de productos"), 2)} con rechazados, ambos no significativos. '
         'Coincide con la conclusión de EAFIT de que el programa no aumenta la cantidad de productos.'),
        ('Iniciativas con actores externos, capacidades e intención futura: sin efecto ajustado significativo. ',
         'Las diferencias brutas de J1 y J2 (+14 a +29 pp) se reducen o pierden significancia al ajustar por perfil, en parte porque los rechazados son solo 11.'),
    ])
    D.table(pd.DataFrame(EAFIT['impacto'], columns=['Resultado EAFIT (event study)', 'Efecto', 'IC 95 %', 'p']),
            'Resultados de impacto reportados por EAFIT, para comparación', font=7.5, fmt={'p': '{:.3f}'})
    D.h('18.2 Calidad del emparejamiento y límites', 2)
    b1 = balance('todos')
    D.p(f'El emparejamiento iguala la universidad (diferencia estandarizada 0) y reduce la diferencia en experiencia y rango asociado. '
        f'Quedan desbalances moderados (diferencia estandarizada mayor que 0,25) en {", ".join(b1.loc[b1["DME después"].abs() > 0.25, "Covariable"])}; la regresión los ajusta además del emparejamiento. '
        'A diferencia de EAFIT, la encuesta no tiene medidas repetidas antes y después, así que estas estimaciones comparan niveles, no cambios. Son menos sólidas que el event study y deben leerse como confirmación de dirección, no de magnitud.')
    D.table(b1, 'Balance de covariables antes y después del emparejamiento (estrategia 1; DME = diferencia de medias estandarizada)', font=7, fmt={c: '{:.3f}' for c in b1.columns[1:]})

    # ---------------------------------------------------------------- 19 postulantes potenciales
    D.pagebreak()
    D.h('19. Postulantes potenciales', 1)
    a, prof, bar = potential()
    D.p('De las 45 personas que no se postularon, 27 consideran probable o muy probable colaborar con otra universidad 4U en los próximos dos años, y 21 de ellas tienen una disposición alta a colaborar (índice C1 de 4 o más). '
        '16 de esas 27 solo habían recibido información o escuchado de la Alianza, sin participar. Es el grupo con más potencial para nuevas convocatorias.')
    D.p('Su perfil difiere del de los financiados: el 70 % son hombres (frente a 44 % entre financiados), y Uninorte aporta 12 de las 27. '
        'Sus barreras principales son la falta de tiempo (78 %), la falta de financiación (48 %) y la dificultad para identificar socios (44 %).')
    D.img(P['pot'], 12, 'No postulantes con intención de colaborar, por universidad')
    D.table(prof, 'Perfil de los postulantes potenciales (n=27)', font=7.5)
    D.table(bar, 'Barreras y prioridades de los postulantes potenciales', font=7.5)
