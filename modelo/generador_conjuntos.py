import pandas as pd
from datetime import datetime
from modelo.problema import Problema


def __remover_underscores(x: str) -> str:

    x = x.lower()
    x = x.replace('_', '')
    x = x.replace('-', '')
    x = x.replace(' ', '')

    return x


def _generar_periodos(problema: Problema, file: str, usecols='B:AH'):

    # extraer los periodos de los títulos del archivo

    df = pd.read_excel(
        io=file, sheet_name='consumo_proyectado', usecols=usecols)

    columns = df.columns

    columns_to_remove = ['key', 'empresa', 'ingrediente', 'planta']

    dates = [datetime.strptime(x, '%d/%m/%Y')
             for x in columns if not x in columns_to_remove]

    dates = sorted(dates)

    problema['fecha_inicial'] = dates[0]

    problema.conjuntos['periodos'] = len(dates)

    problema.conjuntos['fechas'] = dates


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

    campos = ['empresa', 'ingrediente', 'operador',  'imp-motonave']

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


def generar_conjuntos(problema: Problema) -> dict:

    file = problema.file

    usecols = problema.usecols

    problema.conjuntos = dict()

    # Empresas
    problema.conjuntos['empresas'] = _generar_empresas(
        problema=problema, file=file)

    # Calendario
    problema.conjuntos['periodos'] = _generar_periodos(
        problema=problema, file=file, usecols=usecols)

    # Ingredientes
    problema.conjuntos['ingredientes'] = _generar_ingredientes(
        problema=problema, file=file)

    # Puertos
    problema.conjuntos['puertos'] = _generar_operadores(
        problema=problema, file=file)

    # plantas
    problema.conjuntos['plantas'] = _generar_plantas(
        problema=problema, file=file)

    # Unidades de almacenamiento
    problema.conjuntos['unidades_almacenamiento'] = _generar_unidades_almacenamiento(
        problema=problema, file=file)

    # Cargas
    problema.conjuntos['cargas'] = _generar_cargas_en_puerto(
        problema=problema, file=file)
