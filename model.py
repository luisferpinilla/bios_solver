from datetime import datetime

from modelador.generador_conjuntos import generar_conjuntos
from modelador.generador_parametros import generar_parametros
from modelador.generador_variables import generar_variables
from modelador.generador_restricciones import generar_restricciones


file = '/Users/luispinilla/Dropbox/Trabajos/wa/bios_2023/model_1.xlsm'


    
now = datetime(2023, 7, 7)
    
parametros = dict()
    
parametros['fecha_inicial'] = now
    
generar_conjuntos(parametros=parametros, file=file)
    
generar_parametros(parametros=parametros, file=file, now=now)
    
variables = generar_variables(parametros)
        
restricciones = generar_restricciones(parametros, variables)    








# Problema
# problema = pu.LpProblem("Bios", sense=pu.const.LpMinimize)
