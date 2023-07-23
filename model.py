import pulp as pu
from datetime import datetime

from modelador.generador_conjuntos import generar_conjuntos
from modelador.generador_parametros import generar_parametros

file = '/Users/luispinilla/Documents/source_code/bios_solver/model_1.xlsm'


def construir_parametros(now: datetime, parametros:dict):

    parametros['fecha_inicial'] = now
    
    generar_conjuntos(parametros, file)
    
    generar_parametros(parametros, file, now)
    
    return parametros


def construir_variables(parametros: dict):

    variables = dict()

    # Variables asociadas al almacenamiento en puerto

    # $XPL_{l}^{t}$ : Cantidad de la carga $l$ que llega al puerto y que será almacenada en el mismo.

    for k,v in parametros['parametros']['llegadas_cargas'].items():
        campos = k.split('_')
        print(campos)
        empresa = campos[1]
        ingrediente = campos[2]
        puerto = campos[3]
        barco = campos[4]
        periodo = int(campos[5])
        var_name = f"XPL_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}"        
        variables[var_name] = pu.LpVariable(name=var_name, lowBound=0.0, cat=pu.LpContinuous)

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$

    for k,v in parametros['parametros']['llegadas_cargas'].items():
        campos = k.split('_')
        print(campos)
        empresa = campos[1]
        ingrediente = campos[2]
        puerto = campos[3]
        barco = campos[4]
        periodo = int(campos[5])
              
        variables[var_name] = pu.LpVariable(name=var_name, lowBound=0.0, cat=pu.LpContinuous)
        
        for ua in parametros['conjuntos']['unidades_almacenamiento']:
            var_name = f"XTD_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}"        
            variables[var_name] = pu.LpVariable(name=var_name, lowBound=0.0, cat=pu.LpContinuous)


    # $XIP_{j}^{t}$ : Cantidad de la carga $l$ en puerto al final del periodo $t$
     
    for periodo in parametros['conjuntos']['periodos']:
        for carga in parametros['conjuntos']['cargas']:
            var_name = f"XIP_{carga}_{periodo}"
            variables[var_name] = pu.LpVariable(name=var_name, lowBound=0.0, cat=pu.LpContinuous)

    # Variables asociadas al transporte entre puertos y plantas

    # $XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$

    # $ITR_{lm}^{t}$ : Cantidad de camiones con carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$



    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$

    # Variables asociadas a la operación en planta

    # $IIU_{im}^{t}$ : Binaria, 1 sí el ingrediente $i$ esta almacenado en la unidad de almacenamiento $m$ al final del periodo $t$; 0 en otro caso

    # $XIU_{m}^{t}$ : Cantidad de ingrediente almacenado en la unidad de almacenameinto $m$ al final del periodo $t$

    # $XDM_{im}^{t}$: Cantidad de producto $i$ a sacar de la unidad de almacenamiento $m$ para satisfacer la demanda e el día $t$.

    # $BSS_{ik}^{t}$ : Binaria, si se cumple que el inventario del ingrediente $i$ en la planta $k$ al final del día $t$ esté sobre el nivel de seguridad $SS_{ik}^{t}$

    # $BCD_{ik}^{t}$ : si estará permitido que la demanda de un ingrediente $i$ no se satisfaga en la planta $k$ al final del día $t$
    
    return variables


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
    
    return None


def construir_restricciones(parametros:dict, variables:dict):
    
    restricciones = list()
    
    empresas = parametros['conjuntos']['empresas']
    periodos = parametros['conjuntos']['periodos']
    ingredientes = parametros['conjuntos']['ingredientes']
    llegadas = parametros['parametros']['llegadas_cargas']
    unidades = parametros['conjuntos']['unidades_almacenamiento']

    # Satisfaccion de la demanda en las plantas

    # Mantenimiento del nivel de seguridad de igredientes en plantas

    # Capacidad de carga de los camiones

    # Capacidad de almacenamiento en unidades de almacenamiento

    # Balances de masa de inventarios

    ## Balance de masa en bif

    for llegada in llegadas:
        campos = llegada.split('_')
        empresa = campos[1]
        ingrediente = campos[2]
        puerto = campos[3]
        barco = campos[4]
        periodo = int(campos[5])
        
        # AR = XPL + XTD
        
        ar_name = f'AR_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}'
        
        if ar_name in parametros['parametros']['llegadas_cargas'].keys():
            
            ar_val = llegadas[ar_name]
            
            xpl_name = f'XPL_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}'
            xpl_var = variables[xpl_name]
            
            left_expesion = list()
            
            left_expesion.append(xpl_var)
            
            for ua in unidades:
                
                xtd_name = f'XTD_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}'
                xtd_var = variables[xtd_name]
                
                left_expesion.append(xtd_var)
                
            restricciones.append((pu.lpSum(left_expesion)==ar_val,f'balance bif_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}'))
        
            

    ## Balance de masa en cargas en puerto
    
    
    
    
    
   
    ## Balance de masa en unidades de almacenamiento por producto en planta

    # Asignación de uniades de almacenamiento a ingredientes

    return restricciones


def resolver():
    pass


def generar_reporte():
    pass


now = datetime(2023, 7, 7)

parametros = dict()

generar_conjuntos(parametros=parametros, file=file)

parametros = construir_parametros(now)

variables = construir_variables(parametros)

restricciones = construir_restricciones(parametros, variables)


# Problema
# problema = pu.LpProblem("Bios", sense=pu.const.LpMinimize)
