import pandas as pd


def generar_conjuntos(problema: dict, file: str) -> dict:

    problema['conjuntos'] = dict()

    # Empresas
    empresas_df = pd.read_excel(file, sheet_name='empresas')
    problema['conjuntos']['empresas'] = empresas_df['empresa'].to_list()

    # Calendario
    periodos_df = pd.read_excel(file, sheet_name='periodos')
    problema['conjuntos']['periodos'] = {
        periodos_df.loc[i]['Id']: periodos_df.loc[i]['Fecha'] for i in periodos_df.index}
    problema['conjuntos']['fechas'] = {
        periodos_df.loc[i]['Fecha']: periodos_df.loc[i]['Id'] for i in periodos_df.index}
    problema['periodos'] = len(problema['conjuntos']['periodos'])

    # Ingredientes
    ingredientes_df = pd.read_excel(file, sheet_name='ingredientes')
    problema['conjuntos']['ingredientes'] = ingredientes_df['ingrediente'].to_list()

    # Puertos
    puertos_df = pd.read_excel(file, sheet_name='puertos')
    problema['conjuntos']['puertos'] = puertos_df['puerto'].to_list()

    # plantas
    plantas_df = pd.read_excel(file, sheet_name='plantas')
    plantas_df['key'] = plantas_df.apply(
        lambda x: x['empresa'] + "_" + x['planta'], axis=1)
    problema['conjuntos']['plantas'] = plantas_df['key'].to_list()

    # Unidades de almacenamiento
    unidades_df = pd.read_excel(
        file, sheet_name='unidades_almacenamiento', skiprows=1)
    unidades = unidades_df['key'].to_list()
    unidades = [
        f'{u}_{t}' for u in unidades for t in problema['conjuntos']['periodos']]
    problema['conjuntos']['unidades_almacenamiento'] = unidades

    # Cargas
    inventarios_puerto_df = pd.read_excel(file, sheet_name='cargas_puerto')
    problema['conjuntos']['cargas'] = [f'{c}_{i}' for c in  list(inventarios_puerto_df['key'].unique()) for i in problema['conjuntos']['ingredientes']]
