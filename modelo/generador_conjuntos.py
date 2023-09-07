import pandas as pd
from datetime import datetime


def __remover_underscores(x: str) -> str:

    x = x.lower()
    x = x.replace('_', '')
    x = x.replace('-', '')
    x = x.replace(' ', '')

    return x


def _generar_periodos(problema: dict, file: str, usecols='B:AH'):

    # extraer los periodos de los títulos del archivo

    df = pd.read_excel(
        io=file, sheet_name='consumo_proyectado', usecols=usecols)

    columns = df.columns

    columns_to_remove = ['key', 'empresa', 'ingrediente', 'planta']

    dates = [datetime.strptime(x, '%d/%m/%Y')
             for x in columns if not x in columns_to_remove]

    dates = sorted(dates)

    return [x for x in range(len(dates))], dates


def _generar_empresas(file: str):

    empresas_df = pd.read_excel(file, sheet_name='empresas')

    empresas_df['empresa'] = empresas_df['empresa'].apply(
        __remover_underscores)

    return empresas_df['empresa'].to_list()


def _generar_ingredientes(file: str):

    ingredientes_df = pd.read_excel(file, sheet_name='ingredientes')

    ingredientes_df['ingrediente'] = ingredientes_df['ingrediente'].apply(
        __remover_underscores)

    return ingredientes_df['ingrediente'].to_list()


def _generar_operadores(file: str):

    puertos_df = pd.read_excel(file, sheet_name='puertos')

    campos = ['operador-puerto', 'puerto']

    for campo in campos:
        puertos_df[campo] = puertos_df[campo].apply(__remover_underscores)

    puertos_df['key'] = puertos_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)

    return puertos_df['key'].to_list()


def _generar_plantas(file: str):

    plantas_df = pd.read_excel(file, sheet_name='plantas')

    plantas_df['planta'] = plantas_df['planta'].apply(__remover_underscores)

    plantas_df['empresa'] = plantas_df['empresa'].apply(__remover_underscores)

    plantas_df['key'] = plantas_df.apply(
        lambda x: x['empresa'] + "_" + x['planta'], axis=1)

    return plantas_df['key'].to_list()


def _generar_unidades_almacenamiento(file: str):

    unidades_df = pd.read_excel(
        file, sheet_name='unidades_almacenamiento')

    unidades = unidades_df['key'].to_list()

    return unidades


def _generar_cargas_en_puerto(file=str):

    transitos_a_puerto_df = pd.read_excel(file, sheet_name='tto_puerto')
    inventarios_puerto_df = pd.read_excel(file, sheet_name='inventario_puerto')

    campos = ['empresa', 'operador',  'imp-motonave', 'ingrediente',]

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


def generar_conjuntos(problema: dict, file: str, usecols: str) -> dict:

    # Empresas
    problema['empresas'] = _generar_empresas(file=file)

    # Calendario
    periodos, fechas = _generar_periodos(
        problema=problema, file=file, usecols=usecols)
    problema['periodos'] = periodos
    problema['fechas'] = fechas

    # Ingredientes
    problema['ingredientes'] = _generar_ingredientes(file=file)

    # Puertos
    problema['puertos'] = _generar_operadores(file=file)

    # plantas
    problema['plantas'] = _generar_plantas(file=file)

    # Unidades de almacenamiento
    problema['unidades_almacenamiento'] = _generar_unidades_almacenamiento(
        file=file)

    # Cargas
    problema['cargas'] = _generar_cargas_en_puerto(file=file)
