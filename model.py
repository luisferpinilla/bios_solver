from datetime import datetime
import pulp as pu
from modelador.generador_conjuntos import generar_conjuntos
from modelador.generador_parametros import generar_parametros
from modelador.generador_variables import generar_variables
from modelador.generador_restricciones import generar_restricciones
from modelador.generador_fobjetivo import generar_fob





def generar_problema(file:str):
    
    now = datetime(2023, 7, 7)
        
    parametros = dict()
        
    parametros['fecha_inicial'] = now
        
    generar_conjuntos(parametros=parametros, file=file)
        
    generar_parametros(parametros=parametros, file=file, now=now)
        
    variables = generar_variables(parametros)
            
    restricciones = generar_restricciones(parametros, variables)    
    
    fobjetivo = generar_fob(parametros, variables)
    
    return fobjetivo, restricciones


if __name__ == '__main__':
    
    file = '/Users/luispinilla/Dropbox/Trabajos/wa/bios_2023/model_1.xlsm'

    # Problema
    problema = pu.LpProblem("Bios", sense=pu.const.LpMinimize)
    
    fobjetivo, restricciones = generar_problema(file=file)
    
    # Agregar función objetivo
    problema += fobjetivo
    
    rest_set = ['Satisfaccion_demanda', 'Capacidad de carga de camiones', 'capacidad de unidades de almacenamiento', 'balance_masa_bif', 'inventario_inicial_puerto', 'balance_masa_bodega_puerto', 'balance_masa_inventario', 'inventario_inicial_ua', 'asignación de unidades de almacenamiento']
    
    
    # Agregar restricciones
    for name,value in restricciones.items():
        for rest in value:        
            problema += rest
    
    
    problema.solve()
    
    problema.writeLP(filename='model.lp')
    
    
    

    

