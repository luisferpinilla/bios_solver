from datetime import datetime
import pulp as pu
from modelador.generador_conjuntos import generar_conjuntos
from modelador.generador_parametros import generar_parametros
from modelador.generador_variables import generar_variables
from modelador.generador_restricciones import generar_restricciones
from modelador.generador_fobjetivo import generar_fob
from modelador.generador_reporte import generar_reporte


def generar_problema(file:str):
    
    now = datetime(2023, 7, 7)
        
    problema = dict()
        
    problema['fecha_inicial'] = now
        
    generar_conjuntos(problema=problema, file=file)
        
    generar_parametros(problema=problema, file=file, now=now)
        
    variables = generar_variables(problema)
            
    restricciones = generar_restricciones(problema, variables)    
    
    fobjetivo = generar_fob(problema, variables)
    
    return fobjetivo, restricciones, problema, variables

                                                    
if __name__ == '__main__':
    
    file = './model_3.xlsm'
    # Problema
    problema = pu.LpProblem("Bios", sense=pu.const.LpMinimize)
    
    fobjetivo, restricciones, problema, variables = generar_problema(file=file)
    
    # Agregar función objetivo
    problema += fobjetivo
    
    rest_set = ['Satisfaccion_demanda', 'Capacidad de carga de camiones', 'capacidad de unidades de almacenamiento', 'balance_masa_bif', 'inventario_inicial_puerto', 'balance_puerto', 'balance_ua', 'inventario_inicial_ua', 'asignación de unidades de almacenamiento']
    
    
    # Agregar restricciones
    for name,value in restricciones.items():
        for rest in value:        
            problema += rest
    
    problema.writeLP(filename='model.lp')
    
    problema.solve()       
    
    generar_reporte(problema=problema, variables=variables)
    
    
    

    

