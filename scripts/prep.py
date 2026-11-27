"""Preparación de datos: carga, limpieza, variables derivadas y catálogo de ítems."""
import warnings
warnings.simplefilter("ignore")
import re
import numpy as np
import pandas as pd
from load import load

df_raw, H = load()

def item_label(c):
    s = H[c]
    return s.split(' - ')[-1].strip() if ' - ' in s else s

# ---------------------------------------------------------------- escalas
L_MEDIDA = {'Nada': 1, 'En pequeña medida': 2, 'En medida moderada': 3, 'En gran medida': 4, 'Completamente': 5}
L_COMP = {'Mucho menores': 1, 'Menores': 2, 'Similares': 3, 'Mayores': 4, 'Mucho mayores': 5}
L_CAMBIO = {'Disminuyó mucho': 1, 'Disminuyó algo': 2, 'No cambió': 3, 'Aumentó algo': 4, 'Aumentó mucho': 5}
L_CALIDAD = {'Muy deficiente': 1, 'Deficiente': 2, 'Aceptable': 3, 'Buena': 4, 'Muy buena': 5}
L_CONTRIB = {'Ninguna': 1, 'Baja': 2, 'Moderada': 3, 'Alta': 4, 'Decisiva': 5}
L_VALOR = {'Muy baja': 1, 'Baja': 2, 'Media': 3, 'Alta': 4, 'Muy alta': 5}
L_PROB = {'Muy improbable.': 1, 'Improbable.': 2, 'Ni probable ni improbable.': 3, 'Probable.': 4, 'Muy probable.': 5}
L_UTIL = {'Nada útil.': 1, 'Poco útil.': 2, 'Moderadamente útil.': 3, 'Muy útil.': 4, 'Completamente útil.': 5}
L_CANT = {'Ninguna': 0, 'Una': 1, 'Dos o tres': 2.5, 'Cuatro o cinco': 4.5, 'Más de cinco': 6,
          'Ninguno.': 0, 'Uno.': 1, 'Dos o tres.': 2.5, 'Cuatro o cinco.': 4.5, 'Más de cinco.': 6}
L_H5 = {'No hubo interacción': 0, 'Recibió información sobre los resultados': 1,
        'Entregó comentarios o participó en discusiones': 2,
        'Participó en el diseño, producción o validación': 3, 'Ha utilizado o incorporado algún resultado': 4}
ORD = {  # orden de presentación de categorías
    'medida': list(L_MEDIDA) + ['No tengo información suficiente', 'No aplica'],
    'comp': list(L_COMP) + ['No tengo información suficiente'],
    'cambio': list(L_CAMBIO) + ['No tengo información suficiente', 'No aplica'],
    'calidad': list(L_CALIDAD) + ['No tengo información suficiente', 'No aplica'],
    'contrib': list(L_CONTRIB) + ['Todavía no es observable', 'No tengo información suficiente', 'No aplica'],
    'valor': list(L_VALOR) + ['Todavía no es posible valorar', 'No aplica'],
    'cant': ['Ninguna', 'Una', 'Dos o tres', 'Cuatro o cinco', 'Más de cinco', 'No recuerda'],
    'h1': ['No estaba previsto', 'Previsto, pero no iniciado', 'En desarrollo', 'Completado', 'No tengo información.'],
    'h5': list(L_H5) + ['No tengo información'],
}
SCALES = {'medida': L_MEDIDA, 'comp': L_COMP, 'cambio': L_CAMBIO, 'calidad': L_CALIDAD,
          'contrib': L_CONTRIB, 'valor': L_VALOR, 'cant': L_CANT, 'h5': L_H5}

# Bloques tipo matriz (Likert): código, título, columnas, escala, población
MATRIX = [
    ('C1', 'Disposición y preparación para la colaboración interuniversitaria', range(46, 52), 'medida', 'todos'),
    ('C2', 'Proyectos interinstitucionales comparados con los de una sola universidad', range(52, 56), 'comp', 'todos'),
    ('C3', 'Condiciones institucionales para investigar con otras instituciones', range(56, 62), 'medida', 'todos'),
    ('C4', 'Cambio en capacidades de colaboración desde enero de 2021', range(62, 69), 'cambio', 'todos'),
    ('D7', 'Número de experiencias interinstitucionales desde 2021', range(99, 104), 'cant', 'todos'),
    ('E4', 'Diseño de la convocatoria de referencia', range(110, 116), 'medida', 'postulantes'),
    ('E5', 'Valoración del proceso de la convocatoria', range(116, 124), 'calidad', 'postulantes'),
    ('E8', 'Aportes del proceso de formulación de la propuesta', range(127, 132), 'contrib', 'postulantes'),
    ('F2', 'Arquitectura y toma de decisiones del proyecto', range(144, 149), 'medida', 'financiados'),
    ('F3', 'Coordinación interinstitucional', range(149, 156), 'medida', 'financiados'),
    ('F4', 'Calidad de las relaciones', range(156, 161), 'medida', 'financiados'),
    ('F5', 'Consolidación institucional', range(161, 165), 'medida', 'financiados'),
    ('G1', 'Capacidades científicas y colaborativas fortalecidas', range(168, 175), 'contrib', 'financiados'),
    ('G2', 'Capacidades institucionales fortalecidas', range(175, 179), 'contrib', 'financiados'),
    ('G3', 'Aprendizaje organizacional', range(179, 183), 'contrib', 'financiados'),
    ('H1', 'Estado de los productos del proyecto', range(184, 193), 'h1', 'financiados'),
    ('H3', 'Valoración de los productos', range(203, 207), 'valor', 'financiados'),
    ('H5', 'Nivel de interacción y uso por tipo de actor', range(217, 223), 'h5', 'financiados'),
    ('I1', 'Contribuciones observadas de Alianza 4U', range(254, 262), 'contrib', 'financiados'),
]
# Bloques de selección múltiple
MULTI = [
    ('D4', 'Medios por los que conoció Alianza 4U', range(73, 81), 'todos'),
    ('D5', 'Instituciones con las que colaboró desde 2021', range(81, 89), 'todos'),
    ('D6', 'Actividades interinstitucionales desde 2021', range(89, 99), 'todos'),
    ('E9', 'Qué ocurrió con la propuesta o el equipo tras el resultado', range(132, 142), 'no_financiados'),
    ('H2', 'Productos desarrollados conjuntamente por ≥2 universidades 4U', range(193, 203), 'financiados'),
    ('H4', 'Mecanismos de movilización de resultados', range(207, 217), 'financiados'),
    ('H6', 'Etapas con participación de actores externos', range(223, 232), 'financiados'),
    ('H7', 'Ámbitos de uso del conocimiento', range(232, 242), 'financiados'),
    ('H8', 'Evidencias verificables de uso', range(242, 252), 'financiados'),
    ('I6', 'Elementos posibles o fortalecidos gracias a Alianza 4U', range(266, 278), 'financiados'),
    ('J3', 'Iniciativas en las que tendría interés', range(284, 295), 'todos'),
    ('J4', 'Principales dificultades para participar', range(295, 310), 'todos'),
    ('J5', 'Aspectos que Alianza 4U debería priorizar', range(310, 321), 'todos'),
]
# Preguntas de respuesta única
SINGLE = [
    ('B4', 32, 'Universidad de vinculación', 'todos'),
    ('B5', 33, 'Facultad o unidad', 'todos'),
    ('B6', 35, 'Tipo de vinculación', 'todos'),
    ('B7', 37, 'Función principal', 'todos'),
    ('B8', 39, 'Rango o categoría académica', 'todos'),
    ('B9', 41, 'Área de conocimiento', 'todos'),
    ('B10', 43, 'Años de experiencia en investigación', 'todos'),
    ('B11', 44, 'Dedicación a investigación', 'todos'),
    ('A2', 27, 'Autorización de integración de datos', 'todos'),
    ('D1', 70, 'Había escuchado de Alianza 4U', 'todos'),
    ('D2', 71, 'Conocimiento de objetivos y convocatorias', 'todos'),
    ('D3', 72, 'Relación previa con Alianza 4U', 'todos'),
    ('D8', 104, 'Proyectos interinstitucionales antes de 2021', 'todos'),
    ('E1', 106, 'Participación en la postulación', 'postulantes'),
    ('E2', 107, 'Resultado de la postulación', 'postulantes'),
    ('E3', 108, 'Rol en la propuesta', 'postulantes'),
    ('E6', 124, 'Retroalimentación recibida', 'postulantes'),
    ('E6b', 125, 'Utilidad de la retroalimentación', 'postulantes'),
    ('E7', 126, 'Oportunidad de opinar sobre la convocatoria', 'postulantes'),
    ('F1', 143, 'Estado del proyecto', 'financiados'),
    ('F6', 165, 'Esfuerzo de coordinación vs. proyecto de una universidad', 'financiados'),
    ('F7', 166, 'Balance costo-beneficio de la colaboración', 'financiados'),
    ('I2', 262, 'Estado del resultado más significativo', 'financiados'),
    ('I3', 263, 'Alcance del resultado más significativo', 'financiados'),
    ('I4', 264, 'Probabilidad de continuidad sin nueva financiación', 'financiados'),
    ('I5', 265, 'Contrafactual: qué habría pasado sin Alianza 4U', 'financiados'),
    ('I7', 278, 'Efectos no previstos', 'financiados'),
    ('J1', 282, 'Probabilidad de participar con otra universidad 4U (2 años)', 'todos'),
    ('J2', 283, 'Probabilidad de liderar una iniciativa interinstitucional', 'todos'),
    ('J7', 322, 'Autoriza contacto para entrevista o grupo focal', 'todos'),
    ('J7b', 323, 'Medio de contacto preferido', 'todos'),
]
SINGLE_ORDER = {
    'B10': ['Menos de 3 años.', 'Entre 3 y 5 años.', 'Entre 6 y 10 años.', 'Entre 11 y 20 años.', 'Más de 20 años.'],
    'B11': ['Ninguna.', 'Entre 1% y 20%.', 'Entre 21% y 40%.', 'Entre 41% y 60%.', 'Entre 61% y 80%.', 'Más de 80%.'],
    'B8': ['Profesor(a) auxiliar.', 'Profesor(a) asistente.', 'Profesor(a) asociado(a).', 'Profesor(a) titular.',
           'Investigador(a) con categoría institucional.', 'Mi institución utiliza una clasificación diferente.',
           'No tengo rango o categoría académica.', 'Otra.¿Cuál?'],
    'D2': ['No los conocía.', 'Los conocía muy poco.', 'Tenía un conocimiento general.', 'Los conocía bastante.',
           'Los conocía en profundidad.', 'No estoy seguro(a).'],
    'D8': ['Ninguno.', 'Uno.', 'Dos o tres.', 'Cuatro o cinco.', 'Más de cinco.', 'No recuerda.'],
    'E6b': list(L_UTIL),
    'F6': ['Mucho menor.', 'Menor.', 'Similar.', 'Mayor.', 'Mucho mayor.', 'No tengo un referente para compararlo.'],
    'F7': ['Los costos y dificultades fueron muy superiores a los beneficios.',
           'Los costos y dificultades fueron algo superiores a los beneficios.',
           'Los beneficios y las dificultades estuvieron equilibrados.',
           'Los beneficios fueron superiores a las dificultades.',
           'Los beneficios fueron muy superiores a las dificultades.', 'Todavía es muy pronto para valorarlo.'],
    'I2': ['Todavía no se observa.', 'Es un resultado incipiente.', 'Está siendo probado o implementado.',
           'Se encuentra establecido.', 'Se ha mantenido durante al menos un año.', 'No tengo información suficiente.'],
    'I4': list(L_PROB) + ['No tengo información suficiente.'],
    'J1': list(L_PROB),
    'J2': list(L_PROB) + ['No estaría dentro de mis funciones.'],
}

# ---------------------------------------------------------------- sexo estimado por nombre
FEM = set('''ALEJANDRA AMALIA ANA ANGELA ANGELICA CAMILA CARMEN CLAUDIA DANIELA DANIELLA DORYS EDNA ELOISA ENA ERIKA
GERTRUDIS HEYDY INGE JANA KAREN KATHERINE LAURA LILIANA LINA LOURDES LUZ MARIA MARÍA MARIANGELA MARISABELLA MARTA
MERY NATHALIE NORIDA OLGA ORIETHA PAOLA PATRICIA SILVANA STEFANY VALERIA VIVIAM YIRYS YULIETH'''.split())
MAS = set('''ADOLFO ALBERTO ALEX ALEXANDER ALFREDO ANDRES ANDRÉS ANIBAL ARTURO CAMILO CARLOS CESAR CHRISTIAN DARÍO DARIO
EDGAR EDISON ENRIQUE GIOVANNI GUILLERMO GUSTAVO HABIB JAHIR JAVIER JOAQUIN JOHAN JORGE JOSÉ JOSE JUAN LUIS MARIO
MAURICIO NELSON NICOLÁS NICOLAS OSCAR RAFAEL RICARDO RODRIGO SEBASTIAN SERGIO VÍCTOR VICTOR'''.split())

def sexo(nombre):
    t = str(nombre).strip().upper().split()
    if not t:
        return 'Sin dato'
    if t[0] in FEM:
        return 'Mujer'
    if t[0] in MAS:
        return 'Hombre'
    return 'Sin dato'

# ---------------------------------------------------------------- base analítica
def clean(v):
    if isinstance(v, str):
        v = v.strip()
        return v if v else np.nan
    return v

df = df_raw.copy()
for c in df.columns:
    if c != 'archivo':
        df[c] = df[c].map(clean)
df = df.sort_values(['archivo', 3]).reset_index(drop=True)
df['ID'] = ['R%03d' % (i + 1) for i in range(len(df))]

UNI_MAP = {'Universidad CESA.': 'CESA', 'Universidad EAFIT.': 'EAFIT', 'Universidad Icesi.': 'ICESI',
           'Universidad del Norte.': 'Uninorte'}
df['Universidad'] = df[32].map(UNI_MAP)
df['Vinculado_4U'] = np.where(df['Universidad'].notna(), 'Sí', 'No')
df['Universidad'] = df['Universidad'].fillna(df['archivo'])  # no vinculados: universidad del enlace de la encuesta
df['Encuesta'] = df['archivo']
df['Sexo (estimado)'] = df[29].map(sexo)

def grupo(v):
    if pd.isna(v):
        return 'No postuló'
    if v == 'Fue financiada por Alianza 4U.':
        return 'Financiado'
    if v == 'No recuerda o no conoce el resultado.':
        return 'Postuló, resultado desconocido'
    return 'Postuló, no financiado'
df['Grupo'] = df[107].map(grupo)
GROUPS = ['Financiado', 'Postuló, no financiado', 'No postuló']
UNIS = ['CESA', 'EAFIT', 'ICESI', 'Uninorte']

EXP_ORD = {k: i + 1 for i, k in enumerate(SINGLE_ORDER['B10'])}
EXP_YRS = {'Menos de 3 años.': 1.5, 'Entre 3 y 5 años.': 4, 'Entre 6 y 10 años.': 8,
           'Entre 11 y 20 años.': 15.5, 'Más de 20 años.': 25}
DED_PCT = {'Ninguna.': 0, 'Entre 1% y 20%.': 10.5, 'Entre 21% y 40%.': 30.5, 'Entre 41% y 60%.': 50.5,
           'Entre 61% y 80%.': 70.5, 'Más de 80%.': 90}
df['Experiencia_ord'] = df[43].map(EXP_ORD)
df['Experiencia_años_aprox'] = df[43].map(EXP_YRS)
df['Experiencia (agrupada)'] = df[43].map({'Entre 3 y 5 años.': '≤10 años', 'Entre 6 y 10 años.': '≤10 años',
                                          'Menos de 3 años.': '≤10 años', 'Entre 11 y 20 años.': '11-20 años',
                                          'Más de 20 años.': '>20 años'})
df['Dedicación_inv_pct_aprox'] = df[44].map(DED_PCT)
RANK_SHORT = {'Profesor(a) auxiliar.': 'Auxiliar', 'Profesor(a) asistente.': 'Asistente',
              'Profesor(a) asociado(a).': 'Asociado', 'Profesor(a) titular.': 'Titular'}
df['Rango (agrupado)'] = df[39].map(RANK_SHORT).fillna('Otro / sin rango')

# numéricas de matrices
NUM = {}
for code, title, cols, sc, pop in MATRIX:
    if sc in SCALES:
        for j, c in enumerate(cols):
            name = f'{code}_{j + 1}'
            NUM[name] = (code, c)
            df[name] = df[c].map(SCALES[sc])
df['D8_num'] = df[104].map(L_CANT)
df['J1_num'] = df[282].map(L_PROB)
df['J2_num'] = df[283].map(L_PROB)
df['I4_num'] = df[264].map(L_PROB)
df['E6b_num'] = df[125].map(L_UTIL)
df['F6_num'] = df[165].map({'Mucho menor.': 1, 'Menor.': 2, 'Similar.': 3, 'Mayor.': 4, 'Mucho mayor.': 5})
df['F7_num'] = df[166].map({k: i + 1 for i, k in enumerate(SINGLE_ORDER['F7'][:5])})
df['D2_num'] = df[71].map({k: i + 1 for i, k in enumerate(SINGLE_ORDER['D2'][:5])})

# Conteos derivados
four_u = {'CESA': 81, 'EAFIT': 82, 'ICESI': 83, 'Uninorte': 84}
df['D5_n_instituciones'] = df[list(range(81, 88))].notna().sum(axis=1)
df['D5_n_socios_4U_otras'] = [sum(pd.notna(r[four_u[u]]) for u in four_u if u != r['Universidad'])
                              for _, r in df.iterrows()]
df['D6_n_actividades'] = df[list(range(89, 97))].notna().sum(axis=1)
df['D7_total_experiencias_aprox'] = df[[f'D7_{i}' for i in range(1, 6)]].sum(axis=1, min_count=1)
df['D7_productos_aprox'] = df['D7_3']
h1 = df[list(range(184, 193))]
df['H1_n_completados'] = (h1 == 'Completado').sum(axis=1)
df['H1_n_en_desarrollo'] = (h1 == 'En desarrollo').sum(axis=1)
df['H1_n_previstos'] = h1.isin(['Previsto, pero no iniciado', 'En desarrollo', 'Completado']).sum(axis=1)
df['H2_n_tipos_conjuntos'] = df[list(range(193, 202))].notna().sum(axis=1)
df['H4_n_mecanismos'] = df[list(range(207, 214))].notna().sum(axis=1)
df['H8_tiene_evidencia'] = df[list(range(242, 249))].notna().any(axis=1)
df['J4_n_barreras'] = df[list(range(295, 308))].notna().sum(axis=1)

# Índices (promedio de ítems válidos, mínimo 50 % de ítems respondidos)
INDEX = {}
for code, title, cols, sc, pop in MATRIX:
    if sc in ('medida', 'comp', 'cambio', 'calidad', 'contrib', 'valor'):
        items = [f'{code}_{j + 1}' for j in range(len(cols))]
        if code == 'F3':
            items = items[:6]  # 'No surgieron conflictos' mide otra cosa
        sub = df[items]
        idx = sub.mean(axis=1)
        idx[sub.notna().sum(axis=1) < len(items) / 2] = np.nan
        df[f'IDX_{code}'] = idx
        INDEX[code] = (title, items)

# Población por bloque
def pop_mask(pop):
    if pop == 'todos':
        return pd.Series(True, index=df.index)
    if pop == 'financiados':
        return df['Grupo'] == 'Financiado'
    if pop == 'postulantes':
        return df['Grupo'] != 'No postuló'
    if pop == 'no_financiados':
        return df['Grupo'].isin(['Postuló, no financiado', 'Postuló, resultado desconocido'])
    raise ValueError(pop)

# Consistencia (respuestas fuera de flujo)
QUALITY = []
nf = df['Grupo'] != 'Financiado'
for code, cols, lab in [('F1-F7', range(143, 167), 'Gobernanza del proyecto financiado'),
                        ('G1-G3', range(168, 183), 'Fortalecimiento de capacidades'),
                        ('H1-H8', range(184, 253), 'Productos y uso del conocimiento'),
                        ('I1-I8', range(254, 281), 'Impacto y adicionalidad')]:
    n = int((df.loc[nf, list(cols)].notna().any(axis=1)).sum())
    QUALITY.append((code, lab, n))

TEXT_COLS = {'H8b': 252, 'I7b': 279, 'I8': 280, 'J6': 321}
