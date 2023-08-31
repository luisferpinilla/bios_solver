# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime

def __remover_underscores(x:str)->str:
    
    x = x.lower()
    x = x.replace('_', '')
    x = x.replace('-', '')
    x = x.replace(' ', '')
    
    return x


def __inventario_inicial_puerto(problema:dict, file:str):
    # $IP_{l}$ : inventario inicial en puerto para la carga $l$.

    inventarios_puerto_df = pd.read_excel(file, sheet_name='inventario_puerto')
    
    campos = ['empresa', 'operador', 'imp-moto-nave','ingrediente']
    
    for campo in campos: 
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(__remover_underscores)
    
    
    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(lambda field: '_'.join([field[x] for x in campos]) ,axis=1)

    problema['parametros']['inventario_inicial_cargas'] = {f"IP_{inventarios_puerto_df.iloc[fila]['key']}": inventarios_puerto_df.iloc[fila]['cantidad'] for fila in range(inventarios_puerto_df.shape[0])}

    
def __llegadas_a_puerto(problema:dict, file:str):

    # $AR_{l}^{t}$ : Cantidad de material que va a llegar a la carga $l$ durante el día $t$, sabiendo que: $material \in I$ y $carga \in J$.

    inventarios_puerto_df = pd.read_excel(file, sheet_name='tto_puerto')
    
    campos = ['empresa', 'operador', 'imp-moto-nave', 'ingrediente']
    
    for campo in campos: 
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(__remover_underscores)

    # regenerar key
    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(lambda field: '_'.join([field[x] for x in campos]) ,axis=1)    

    fechas_dict = {problema['conjuntos']['fechas'][x]:x for x in range(len(problema['conjuntos']['fechas']))}

    inventarios_puerto_df['periodo'] = inventarios_puerto_df['fecha_llegada'].map(fechas_dict)
    
    # Extraer los que caen fuera del horizonte de planeación
    inventarios_puerto_df = inventarios_puerto_df[~inventarios_puerto_df['periodo'].isna()]
    
    problema['parametros']['llegadas_cargas'] = {f"AR_{inventarios_puerto_df.iloc[i]['key']}_{inventarios_puerto_df.iloc[i]['periodo']}": inventarios_puerto_df.iloc[i]['cantidad'] for i in range(inventarios_puerto_df.shape[0])}


def __costo_almacenamiento_puerto(problema:dict, file:str):
    
    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.

    cc_df = pd.read_excel(file, sheet_name='costos_almacenamiento_cargas')
    
    campos = ['empresa', 'ingrediente', 'operador', 'imp-moto-nave']
    
    for campo in campos: 
        cc_df[campo] = cc_df[campo].apply(__remover_underscores)

    # regenerar key
    cc_df['key'] = cc_df.apply(lambda field: '_'.join([field[x] for x in campos]) ,axis=1)    

    cc_df = cc_df[cc_df['fecha_corte'].isin(problema['conjuntos']['fechas'])].copy()
    
    fechas_dict = {problema['conjuntos']['fechas'][x]:x for x in range(len(problema['conjuntos']['fechas']))}

    cc_df['periodo'] = cc_df['fecha_corte'].map(fechas_dict)

    problema['parametros']['costos_almacenamiento'] = {f"CC_{cc_df.iloc[i]['key']}_{cc_df.iloc[i]['periodo']}": cc_df.iloc[i]['valor_kg'] for i in range(cc_df.shape[0])}


def __costos_transporte(problema:dict, file:str):
    # $CF_{lm}$ : Costo fijo de transporte por camión despachado llevando la carga $l$ hasta la unidad de almacenamiento $m$.
    # $ CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.

    problema['parametros']['fletes_fijos'] = dict()
    
    fletes_fijos_df = pd.read_excel(file, sheet_name='fletes_fijos')
    fletes_fijos_df.set_index('operador-ing', drop=True, inplace=True)
    fletes_fijos_df.fillna(0.0, inplace=True)

    problema['parametros']['fletes_variables'] = dict()

    fletes_variables_df = pd.read_excel(file, sheet_name='fletes_variables')
    fletes_variables_df.set_index('operador-ing', drop=True, inplace=True)    
    fletes_variables_df.fillna(0.0, inplace=True)
    
    

    for puerto in problema['conjuntos']['puertos']:
        for planta in problema['conjuntos']['plantas']:
            for ingrediente in problema['conjuntos']['ingredientes']:
                
                if f'{puerto}_{ingrediente}' in fletes_fijos_df.index:                
                    problema['parametros']['fletes_fijos'][f'CF_{puerto}_{planta}'] = fletes_fijos_df.loc[f'{puerto}_{ingrediente}'][planta]
                else:
                    #print(f'{puerto}_{ingrediente}')
                    problema['parametros']['fletes_fijos'][f'CF_{puerto}_{planta}'] = 0.0

                if f'{puerto}_{ingrediente}' in fletes_variables_df.index:                    
                
                    problema['parametros']['fletes_variables'][f'CT_{puerto}_{planta}'] = fletes_variables_df.loc[f'{puerto}_{ingrediente}'][planta]
                else:
                    #print(f'{puerto}_{ingrediente}')
                    problema['parametros']['fletes_variables'][f'CT_{puerto}_{planta}'] = 0.0
                    
   
def __venta_intercompany(problema:dict, file:str):
    # $CW_{lm}$ : Costo de vender una carga perteneciente a una empresa a otra.

    costo_cambio_empresa_df = pd.read_excel(file, 'venta_entre_empresas')

    costo_cambio_empresa_df = costo_cambio_empresa_df.melt(id_vars='origen', value_vars=['contegral', 'finca'], var_name='destino')

    problema['parametros']['costo_venta_intercompany'] = {f"CW_{costo_cambio_empresa_df.iloc[x]['origen']}_{costo_cambio_empresa_df.iloc[x]['destino']}":costo_cambio_empresa_df.iloc[x]['value'] for x in range(costo_cambio_empresa_df.shape[0])}
    

def __tiempo_transporte(problema:dict, file:str):
    
    # $TT_{jk}$ : tiempo en días para transportar la carga desde el puerto $j$ hacia la planta $k$.

    problema['parametros']['tiempo_transporte'] = dict()

    for puerto in problema['conjuntos']['puertos']:
        for planta in problema['conjuntos']['plantas']:
            lista_ua = [ua for ua in problema['conjuntos']['unidades_almacenamiento'] if planta in ua.split('_')[0]]
            for ua in lista_ua:
                problema['parametros']['tiempo_transporte'][f"TT_{puerto}_{ua}"] = 2
    

def __capacidad_almacenamiento_planta(problema:dict, file:str):
    
    # $CA_{m}^{i}$ : Capacidad de almacenamiento de la unidad $m$ en toneladas del ingrediente $i$, tenendo en cuenta que $m \in K$.

    inventario_planta_df = pd.read_excel(file, sheet_name='unidades_almacenamiento')
            
    capacidad_ua_df = inventario_planta_df.melt(id_vars=['key'], value_vars=problema['conjuntos']['ingredientes'],var_name='ingrediente', value_name='capacidad').rename(columns={'key':'unidad_almacenamiento'})

    problema['parametros']['capacidad_almacenamiento_ua'] = {f"CA_{capacidad_ua_df.iloc[x]['ingrediente']}_{capacidad_ua_df.iloc[x]['unidad_almacenamiento']}":capacidad_ua_df.iloc[x]['capacidad'] for x in range(capacidad_ua_df.shape[0])}



def __inventario_planta(problema:dict, file:str):
    
    # $II_{m}^{i}$ : Inventario inicial del ingrediente $i$ en la unidad $m$, teniendo en cuenta que $m \in K$

    inventario_planta_df = pd.read_excel(file, sheet_name='unidades_almacenamiento')

    problema['parametros']['inventario_inicial_ua'] = {f"II_{inventario_planta_df.iloc[x]['key']}_{inventario_planta_df.iloc[x]['ingrediente_actual']}":inventario_planta_df.iloc[x]['cantidad_actual'] for x in range(inventario_planta_df.shape[0])}

   
def __consumo_proyectado(problema:dict, file:str):
    
    # $DM_{ki}^{t}$: Demanda del ingrediente $i$ en la planta $k$ durante el día $t$.

    demanda_df = pd.read_excel(file, sheet_name='consumo_proyectado')
    
    demanda_df.fillna(0.0, inplace=True)

    demanda_df = demanda_df.melt(id_vars=['empresa', 'ingrediente', 'planta'], var_name='fecha', value_name='consumo')

    fechas_dict = {problema['conjuntos']['fechas'][x]:x for x in range(len(problema['conjuntos']['fechas']))}

    demanda_df['periodo'] = demanda_df['fecha'].map(fechas_dict)
    
    campos = ['empresa', 'planta', 'ingrediente']
    
    for campo in campos: 
        demanda_df[campo] = demanda_df[campo].apply(__remover_underscores)

    campos += ['periodo']

    # regenerar key
    demanda_df['key'] = demanda_df.apply(lambda field: '_'.join([str(field[x]) for x in campos]) ,axis=1) 


    problema['parametros']['consumo_proyectado'] = {f"DM_{demanda_df.iloc[i]['key']}_{demanda_df.iloc[i]['periodo']}": demanda_df.iloc[i]['consumo'] for i in range(demanda_df.shape[0])}


def __safety_stock_planta(problema:dict, file:str):
    
    # $SS_{ik}^{t}$ : Inventario de seguridad a tener del ingrediente $i$ en la planta $k$ al final del día $t$.
    ss_df = pd.read_excel(file, sheet_name='consumo_proyectado')
    
    campos = ['empresa', 'planta', 'ingrediente']

    for campo in campos: 
        ss_df[campo] = ss_df[campo].apply(__remover_underscores)    
    
    # regenerar key
    ss_df['key'] = ss_df.apply(lambda field: '_'.join([str(field[x]) for x in campos]) ,axis=1) 

    ss_df.drop(columns=campos, inplace=True)
    
    ss_df.set_index(keys='key', drop=True, inplace=True)
    
    ss_df['SS'] = ss_df.apply(np.mean, axis=1)*10
    
    problema['parametros']['safety_stock'] = {f'SS_{k}':ss_df.loc[k]['SS'] for k in ss_df.index}

   
def __costo_asignacion_ingrediantes_ua(problema:dict, file:str):
    
    # $CI_{im}^{t}$ : Costo de asignar el ingrediente $i$ a la unidad de almacenamiento $m$ durante el periodo $t$. Si la unidad de almacenamiento no puede contener el ingrediente, este costo será $infinito$.
    pass
          

def __costo_insatisfaccion_ss(problema:dict, file:str):
    # $CS_{ik}^{t}$ : Costo de no satisfacer el inventario de seguridad para el ingrediente $i$ en la planta $k$ durante el día $t$.
    # problema['parametros']['costo_no_safety_stock'] = {f'CS_{k}':1000000 for k in ss_df.index}
    pass


def __costo_insatisfaccion_demanda(problema:dict, file:str):
    # $CD_{ik}^{t}$ : Costo de no satisfacer la demanda del ingrediente $i$  en la planta $k$ durante el día $t$.
    # problema['parametros']['costo_no_demanda'] = {f'CD_{k}':10000000 for k in ss_df.index}
    pass


def __costo_backorder_planta(problema:dict, file:str):
    # $CK_{ik}^{t}$ : Costo del backorder del ingrediente $i$  en la planta $k$ durante el día $t$.
    # problema['parametros']['costo_backorder'] = {f'CK_{k}':10000 for k in ss_df.index}
    pass


def __transitos_programados_hacia_planta(problema:dict, file:str):
    # $TR_{im}^{t}$ : Cantidad en tránsito programada para llegar a la unidad de almacenamiento $m$ durante el día $t$,
    pass


def generar_parametros(problema:dict, file:str)->dict:
    
    problema['parametros'] = dict()
    
    __inventario_inicial_puerto(problema=problema, file=file)
    
    __llegadas_a_puerto(problema=problema, file=file)
    
    __costo_almacenamiento_puerto(problema=problema, file=file)
    
    __costos_transporte(problema=problema, file=file)
    
    __venta_intercompany(problema=problema, file=file)
    
    __tiempo_transporte(problema=problema, file=file)
        
    __capacidad_almacenamiento_planta(problema=problema, file=file)
    
    __inventario_planta(problema=problema, file=file)
    
    __consumo_proyectado(problema=problema, file=file)
    
    __safety_stock_planta(problema=problema, file=file)

    __costo_asignacion_ingrediantes_ua(problema=problema, file=file)
    
    __costo_insatisfaccion_ss(problema=problema, file=file)
    
    __costo_insatisfaccion_demanda(problema=problema, file=file)
    
    __costo_backorder_planta(problema=problema, file=file)

    __transitos_programados_hacia_planta(problema=problema, file=file)

    
    
    

    



