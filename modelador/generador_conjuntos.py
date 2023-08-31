import pandas as pd
from datetime import datetime


def __remover_underscores(x:str)->str:
    
    x = x.lower()
    x = x.replace('_', '')
    x = x.replace('-', '')
    x = x.replace(' ', '')
    
    return x


def _generar_periodos(problema:dict, file:str):
    
    # extraer los periodos de los títulos del archivo
    
    df = pd.read_excel(io=file, sheet_name='consumo_proyectado')
    
    columns = df.columns
    
    columns_to_remove = ['key', 'empresa', 'ingrediente', 'planta']
    
    dates = [datetime.strptime(x, '%d/%m/%Y') for x in columns if not x in columns_to_remove]
    
    dates = sorted(dates)
    
    problema['fecha_inicial'] = dates[0]
    
    problema['conjuntos']['periodos'] = len(dates)
    
    problema['conjuntos']['fechas'] = dates
    
    


def _generar_empresas(problema:dict, file:str):
    
    empresas_df = pd.read_excel(file, sheet_name='empresas')
    
    empresas_df['empresa'] = empresas_df['empresa'].apply(__remover_underscores) 
    
    problema['conjuntos']['empresas'] = empresas_df['empresa'].to_list()


def _generar_ingredientes(problema:dict, file:str):
    
    ingredientes_df = pd.read_excel(file, sheet_name='ingredientes')
    
    ingredientes_df['ingrediente'] = ingredientes_df['ingrediente'].apply(__remover_underscores)
    
    problema['conjuntos']['ingredientes'] = ingredientes_df['ingrediente'].to_list()
 
    
def _generar_operadores(problema:dict, file:str):
    
    puertos_df = pd.read_excel(file, sheet_name='puertos')
    
    puertos_df['operador'] = puertos_df['operador'].apply(__remover_underscores)
    
    
    problema['conjuntos']['puertos'] = puertos_df['operador'].to_list()
    

def _generar_plantas(problema:dict, file:str):

    plantas_df = pd.read_excel(file, sheet_name='plantas')
    
    plantas_df['planta'] = plantas_df['planta'].apply(__remover_underscores)
    
    plantas_df['empresa'] = plantas_df['empresa'].apply(__remover_underscores)
    
    plantas_df['key'] = plantas_df.apply(
        lambda x: x['empresa'] + "_" + x['planta'], axis=1)
    
    problema['conjuntos']['plantas'] = plantas_df['key'].to_list()


def _generar_unidades_almacenamiento(problema:dict, file:str):
    
    unidades_df = pd.read_excel(
        file, sheet_name='unidades_almacenamiento')
    
    # unidades_df['key'] = unidades_df['key'].apply(__remover_underscores)
    
    unidades = unidades_df['key'].to_list()
    
    periodos = problema['conjuntos']['periodos']
    
    unidades = [f'{x}_{t}' for x in unidades for t in range(periodos)]

    problema['conjuntos']['unidades_almacenamiento'] = unidades    
    

def _generar_cargas_en_puerto(problema:list, file=str):
    
    transitos_a_puerto_df = pd.read_excel(file, sheet_name='tto_puerto')
    inventarios_puerto_df = pd.read_excel(file, sheet_name='inventario_puerto')
    
    campos = ['empresa', 'ingrediente', 'operador',  'imp-moto-nave']
    
    for campo in campos:
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(__remover_underscores)
        transitos_a_puerto_df[campo] = transitos_a_puerto_df[campo].apply(__remover_underscores)
    
    transitos_a_puerto_df['key'] = transitos_a_puerto_df.apply(lambda field: '_'.join([field[x] for x in campos]) ,axis=1)
    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(lambda field: '_'.join([field[x] for x in campos]) ,axis=1)
    
    
    cargas_transito = [f'{c}' for c in  list(transitos_a_puerto_df['key'].unique())]
    cargas_inventario = [f'{c}' for c in  list(inventarios_puerto_df['key'].unique())]
    
    
    
    cargas = list(set(cargas_inventario + cargas_transito))
      
    problema['conjuntos']['cargas'] = cargas
    


def generar_conjuntos(problema: dict, file: str) -> dict:

    problema['conjuntos'] = dict()

    # Empresas
    _generar_empresas(problema=problema, file=file)

    # Calendario
    _generar_periodos(problema=problema, file=file)

    # Ingredientes
    _generar_ingredientes(problema=problema, file=file)

    # Puertos
    _generar_operadores(problema=problema, file=file)

    # plantas
    _generar_plantas(problema=problema, file=file)

    # Unidades de almacenamiento
    _generar_unidades_almacenamiento(problema=problema, file=file)

    # Cargas
    _generar_cargas_en_puerto(problema=problema, file=file)
    

