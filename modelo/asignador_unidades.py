import pandas as pd
from problema import Problema

conjuntos = dict()

parametros = dict()


def _generar_conjuntos(file: str, planta: str):
    # colocar unidades de almacenamiento
    df = pd.read_excel(file, sheet_name='unidades_almacenamientos')
    # tener en cuenta solo la planta en el enfoque
    df = df[df['planta'] == planta]
    conjuntos['unidades_almacenamiento'] = list(
        df['unidad_almacenamiento'].unique())


def _generar_parametros(file: str, planta: str, parametros:dict):

    # Cantidaes de inventario

    inventario_inicial_dict = dict()
    capacidad_ua_dict = dict()

    inventario_df = pd.read_excel(file, sheet_name='unidades_almacenamiento')
    inventario_df = inventario_df[inventario_df['planta'] == planta].copy()
    inventario_df.set_index('unidad_almacenamiento', drop=True, inplace=True)

    for ua in conjuntos['unidades_almacenamiento']:
        for ingrediente in conjuntos['ingredientes']:

            inv_par_name = f'II_{ua}_{ingrediente}'
            
            if inventario_df.loc[ua]['ingrediente_actual'] == ingrediente:
                inv_par_value = inventario_df.loc[ua]['cantidad_actual']
            else:
                inv_par_value = 0.0
            inventario_inicial_dict[inv_par_name] = inv_par_value

            # Capacidades por UA
            cap_par_name = f'CP_{ua}_{ingrediente}'
            cap_par_value = inventario_df.loc[ua][ingrediente]
            capacidad_ua_dict[cap_par_name] = cap_par_value


    parametros['inventario_inicial'] = inventario_inicial_dict

    parametros['capacidad_unidades'] = capacidad_ua_dict

    # Demanda a consumir

    
    # Llegadas de material
    pass


def _generar_variables(problema: Problema, planta: str):
    # asignación de unidades de almacenamiento
    # inventario al final del periodo
    # cantidad de ingrediente a consumir desde la unidad de almacenamiento
    pass


def _generar_objetivo(problema: Problema, planta: str):
    # Minimizar uso de unidades de almacenamiento
    pass


def _generar_restricciones(problma: Problema, planta: str):
    # Solo se puede llenar una unidad de almacenamiento con una materia prima
    # No se debe exceder la capacidad de ninguna materia prima
    # Se debe garantizar que la demanda sea satisfecha totalmente
    # Se debe recibir todos los arrivos
    # Prohibir el uso de una unidad de almacenamiento por dos periodos
    pass


def _generar_reporte(problema: Problema):

    # Mostrar tabla pivote de cómo quedan asignadas las unidades de almacenamiento en el futuro

    pass


def main(problema: Problema, planta: str):

    file = problema.file

    conjuntos['periodos'] = problema.conjuntos['periodos']
    conjuntos['ingredientes'] = problema.conjuntos['ingredientes']

    _generar_conjuntos(file=file, planta=planta, para)

    _generar_parametros(problema=problema, planta=planta)

    _generar_objetivo(problema=problema, planta=planta)

    _generar_restricciones(problma=problema, planta=planta)

    _generar_reporte(problema=problema, planta=planta)
