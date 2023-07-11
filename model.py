import pulp as pu
import pandas as pd


def construir_conjuntos():
    
    conjuntos = dict()    
    
    # Empresas
    empresas_df = pd.read_excel('model_1.xlsm',sheet_name='empresas')  
    conjuntos['empresas'] = empresas_df['empresa'].to_list()
    
    # Calendario
    periodos_df = pd.read_excel('model_1.xlsm',sheet_name='periodos')
    conjuntos['periodos'] = {periodos_df.loc[i]['Id']:periodos_df.loc[i]['Fecha'] for i in periodos_df.index}        
    conjuntos['fechas'] = {periodos_df.loc[i]['Fecha']:periodos_df.loc[i]['Id'] for i in periodos_df.index}
    
    
    # Ingredientes    
    ingredientes_df = pd.read_excel('model_1.xlsm',sheet_name='ingredientes')
    conjuntos['ingredientes'] = ingredientes_df['ingrediente'].to_list()
    
    # Puertos
    puertos_df = pd.read_excel('model_1.xlsm',sheet_name='puertos')
    conjuntos['puertos'] = puertos_df['puerto'].to_list()

    # plantas
    plantas_df = pd.read_excel('model_1.xlsm',sheet_name='plantas')  
    conjuntos['plantas'] = plantas_df['planta'].to_list()
    
    
    # Unidades de almacenamiento
    unidades_df = pd.read_excel('model_1.xlsm',sheet_name='unidades_almacenamiento')
    conjuntos['unidades_almacenamiento'] = unidades_df['key'].to_list()
    
    return conjuntos


    
def construir_parametros(conjuntos:dict):
    
    parametros = dict()
    
    # $IP_{l}$ : inventario inicial en puerto para la carga $l$.

    # $AR_{l}^{t}$ : Cantidad de material que va a llegar a la carga $l$ durante el día $t$, sabiendo que: $material \in I$ y $carga \in J$.

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.
    
    
    # $CF_{lm}$ : Costo fijo de transporte por camión despachado llevando la carga $l$ hasta la unidad de almacenamiento $m$.
    
    parametros['fletes_fijos'] = dict()
    fletes_fijos_df = pd.read_excel('model_1.xlsm',sheet_name='fletes_fijos') 
    fletes_fijos_df.set_index('puerto', drop=True, inplace=True)
   
    
    for puerto in conjuntos['puertos']:
        for planta in conjuntos['plantas']:             
             parametros['fletes_fijos'][f'CF_{puerto}_{planta}'] = fletes_fijos_df.loc[puerto][planta]

    # $ CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.
    
    parametros['fletes_variables'] = dict()
    
    fletes_variables_df = pd.read_excel('model_1.xlsm',sheet_name='fletes_variables') 
    fletes_variables_df.set_index('puerto', drop=True, inplace=True)
    
    
    for puerto in conjuntos['puertos']:
        for planta in conjuntos['plantas']:             
             parametros['fletes_variables'][f'CT_{puerto}_{planta}'] = fletes_variables_df.loc[puerto][planta]

    # $CW_{lm}$ : Costo de vender una carga perteneciente a una empresa a otra.

    # $TT_{jk}$ : tiempo en días para transportar la carga desde el puerto $j$ hacia la planta $k$.         

    # $CA_{m}^{i}$ : Capacidad de almacenamiento de la unidad $m$ en toneladas del ingrediente $i$, tenendo en cuenta que $m \in K$.

    # $DM_{ki}^{t}$: Demanda del ingrediente $i$ en la planta $k$ durante el día $t$.

    # $CD_{ik}^{t}$ : Costo de no satisfacer la demanda del ingrediente $i$  en la planta $k$ durante el día $t$.

    # $CI_{im}^{t}$ : Costo de asignar el ingrediente $i$ a la unidad de almacenamiento $m$ durante el periodo $t$. Si la unidad de almacenamiento no puede contener el ingrediente, este costo será $infinito$.

    # $SS_{ik}^{t}$ : Inventario de seguridad a tener del ingrediente $i$ en la planta $k$ al final del día $t$.

    # $CS_{ik}^{t}$ : Costo de no satisfacer el inventario de seguridad para el ingrediente $i$ en la planta $k$ durante el día $t$.

    # $TR_{im}^{t}$ : Cantidad en tránsito programada para llegar a la unidad de almacenamiento $m$ durante el día $t$,
    
       
    return parametros
    

def construir_variables(conjuntos:dict):
    
    variables = dict()
    
    # $XPL_{l}^{t}$ : Cantidad de la carga $l$ que llega al puerto y que será almacenada en el mismo. 

    # $XIP_{j}^{t}$ : Cantidad de la carga $l$ en puerto al final del periodo $t$

    #### Variables asociadas al transporte entre puertos y plantas

    # $XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$

    # $ITR_{lm}^{t}$ : Cantidad de camiones con carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$

    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$

    #### Variables asociadas a la operación en planta

    # $IIU_{im}^{t}$ : Binaria, 1 sí el ingrediente $i$ esta almacenado en la unidad de almacenamiento $m$ al final del periodo $t$; 0 en otro caso

    # $XIU_{m}^{t}$ : Cantidad de ingrediente almacenado en la unidad de almacenameinto $m$ al final del periodo $t$

    # $XDM_{im}^{t}$: Cantidad de producto $i$ a sacar de la unidad de almacenamiento $m$ para satisfacer la demanda e el día $t$.

    # $BSS_{ik}^{t}$ : Binaria, si se cumple que el inventario del ingrediente $i$ en la planta $k$ al final del día $t$ esté sobre el nivel de seguridad $SS_{ik}^{t}$

    # $BCD_{ik}^{t}$ : si estará permitido que la demanda de un ingrediente $i$ no se satisfaga en la planta $k$ al final del día $t$
    
    
    
    

def construir_fob():
    
    fob = list()
    
    

def construir_restricciones():
    pass

def resolver():
    pass




conjuntos = construir_conjuntos()
parametros = construir_parametros(conjuntos) 


# Problema
problema = pu.LpProblem("Bios", sense=pu.const.LpMinimize)
