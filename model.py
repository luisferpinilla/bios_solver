import pulp as pu
from datetime import datetime

from modelador.generador_conjuntos import generar_conjuntos
from modelador.generador_parametros import generar_parametros
from modelador.generador_restricciones import generar_restricciones
from modelador.generador_variables import generar_variables

file = '/Users/luispinilla/Documents/source_code/bios_solver/model_1.xlsm'


def construir_parametros(now: datetime, parametros:dict):

    parametros['fecha_inicial'] = now
    
    generar_conjuntos(parametros, file)
    
    generar_parametros(parametros, file, now)
    
    return parametros


def construir_variables(parametros: dict):
    
    return generar_variables(parametros)



def construir_fob():

    fob = list()

    # Costos por almacenamiento

    # Almacenamiento en puerto por corte de Facturación:

    # Costos por transporte

    # Costo variable de transportar cargas desde puertos hacia plantas

    # Costo fijo de transportar un camion desde puerto hacia plantas

    # Costos por Penalización

    # Costo de no respetar un inventario de seguridad de un ingrediente en una planta

    # Costo de no satisfacer una demanda en una planta

    # Costo por permitir guardar un ingrediente en una planta
    
    return fob


def resolver():
    pass


def generar_reporte():
    pass


now = datetime(2023, 7, 7)

parametros = dict()

generar_conjuntos(parametros=parametros, file=file)

parametros = construir_parametros(now=now, parametros=parametros)

variables = construir_variables(parametros)

restricciones = generar_restricciones(parametros, variables)


# Problema
# problema = pu.LpProblem("Bios", sense=pu.const.LpMinimize)
