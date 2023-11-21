import pandas as pd
from datetime import datetime


def __remover_underscores(x: str) -> str:

    x = str(x)
    x = x.lower()
    x = x.replace('_', '')
    x = x.replace('-', '')
    x = x.replace(' ', '')

    return x


def _generar_periodos(problema: dict, file: str):

    # extraer los periodos de los títulos del archivo

    print('sets: periodos')

    df = pd.read_excel(
        io=file, sheet_name='consumo_proyectado')

    columns = df.columns

    columns_to_remove = ['key', 'empresa', 'ingrediente', 'planta']

    dates = [datetime.strptime(x, '%d/%m/%Y')
             for x in columns if not x in columns_to_remove]

    dates = sorted(dates)

    return [x for x in range(len(dates))], dates


def _generar_empresas(file: str):

    print('sets: empresas')

    empresas_df = pd.read_excel(file, sheet_name='empresas')

    empresas_df['empresa'] = empresas_df['empresa'].apply(
        __remover_underscores)

    return empresas_df['empresa'].to_list()


def _generar_ingredientes(file: str):

    print('sets: ingredientes')

    ingredientes_df = pd.read_excel(file, sheet_name='ingredientes')

    ingredientes_df['nombre'] = ingredientes_df['nombre'].apply(
        __remover_underscores)

    return ingredientes_df['nombre'].to_list()


def _generar_operadores(file: str):

    print('sets: operadores logísticos')

    puertos_df = pd.read_excel(file, sheet_name='operadores')

    puertos_df['operador'] = puertos_df['operador'].apply(
        __remover_underscores)

    return list(puertos_df['operador'].unique())


def _generar_plantas(file: str):

    print('sets: plantas')

    plantas_df = pd.read_excel(file, sheet_name='plantas')

    plantas_df['planta'] = plantas_df['planta'].apply(__remover_underscores)

    plantas_df['empresa'] = plantas_df['empresa'].apply(__remover_underscores)

    plantas_df['key'] = plantas_df.apply(
        lambda x: x['empresa'] + "_" + x['planta'], axis=1)

    return plantas_df['key'].to_list()


def _generar_cargas_en_puerto(file=str):

    print('sets: cargas')

    transitos_a_puerto_df = pd.read_excel(file, sheet_name='tto_puerto')
    inventarios_puerto_df = pd.read_excel(file, sheet_name='inventario_puerto')

    campos = ['empresa', 'operador',  'imp-motonave', 'ingrediente']

    for campo in campos:
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(
            __remover_underscores)
        transitos_a_puerto_df[campo] = transitos_a_puerto_df[campo].apply(
            __remover_underscores)

    transitos_a_puerto_df['key'] = transitos_a_puerto_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)
    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)

    cargas_transito = [f'{c}' for c in list(
        transitos_a_puerto_df['key'].unique())]
    cargas_inventario = [f'{c}' for c in list(
        inventarios_puerto_df['key'].unique())]

    cargas = list(set(cargas_inventario + cargas_transito))

    return cargas


def generar_conjuntos(problema: dict, file: str) -> dict:

    # Empresas
    problema['empresas'] = _generar_empresas(file=file)

    # Calendario
    periodos, fechas = _generar_periodos(problema=problema, file=file)
    problema['periodos'] = periodos
    problema['fechas'] = fechas

    # Ingredientes
    problema['ingredientes'] = _generar_ingredientes(file=file)

    # Puertos
    problema['operadores'] = _generar_operadores(file=file)

    # plantas
    problema['plantas'] = _generar_plantas(file=file)

    # Cargas
    problema['cargas'] = _generar_cargas_en_puerto(file=file)
