# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime


def generar_parametros(problema:dict, file:str, now:datetime)->dict:
    
    problema['parametros'] = dict()
    
    # $IP_{l}$ : inventario inicial en puerto para la carga $l$.

    inventarios_puerto_df = pd.read_excel(file, sheet_name='cargas_puerto')
    
    inventarios_puerto_df['status'] = inventarios_puerto_df['fecha_llegada'].apply(lambda x: 'arrival' if x >= now else 'inventory')

    ip_df = inventarios_puerto_df[inventarios_puerto_df['status'] == 'inventory'].groupby(['key'])[['cantidad']].sum().reset_index()
    
    # problema['diccionarios']['ingredientes_puerto'] = {ingrediente: list(inventarios_puerto_df[inventarios_puerto_df['ingrediente'] == ingrediente]['barco'].unique()) for ingrediente in problema['conjuntos']['ingredientes']}

    problema['parametros']['inventario_inicial_cargas'] = {f"IP_{ip_df.iloc[fila]['key']}": ip_df.iloc[fila]['cantidad'] for fila in range(ip_df.shape[0])}

    # $AR_{l}^{t}$ : Cantidad de material que va a llegar a la carga $l$ durante el día $t$, sabiendo que: $material \in I$ y $carga \in J$.

    ar_df = inventarios_puerto_df[inventarios_puerto_df['status'] == 'arrival'].groupby(['key', 'fecha_llegada'])[['cantidad']].sum().reset_index()

    ar_df['periodo'] = ar_df['fecha_llegada'].map(problema['conjuntos']['fechas'])

    problema['parametros']['llegadas_cargas'] = {f"AR_{ar_df.iloc[i]['key']}_{ar_df.iloc[i]['periodo']}": ar_df.iloc[i]['cantidad'] for i in range(ar_df.shape[0])}

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.

    cc_df = pd.read_excel(file, sheet_name='costos_almacenamiento_cargas')

    cc_df = cc_df[cc_df['fecha_llegada'].isin(problema['conjuntos']['fechas'])].copy()

    cc_df['periodo'] = cc_df['fecha_llegada'].map(problema['conjuntos']['fechas'])

    problema['parametros']['costos_almacenamiento'] = {f"CC_{cc_df.iloc[i]['key']}_{cc_df.iloc[i]['periodo']}": cc_df.iloc[i]['Valor_por_tonelada'] for i in range(cc_df.shape[0])}

    # $CF_{lm}$ : Costo fijo de transporte por camión despachado llevando la carga $l$ hasta la unidad de almacenamiento $m$.

    problema['parametros']['fletes_fijos'] = dict()
    fletes_fijos_df = pd.read_excel(file, sheet_name='fletes_fijos')
    fletes_fijos_df.set_index('puerto', drop=True, inplace=True)
    fletes_fijos_df.fillna(0.0, inplace=True)

    for puerto in problema['conjuntos']['puertos']:
        for planta in problema['conjuntos']['plantas']:
            problema['parametros']['fletes_fijos'][f'CF_{puerto}_{planta}'] = fletes_fijos_df.loc[puerto][planta]

    # $ CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.

    problema['parametros']['fletes_variables'] = dict()

    fletes_variables_df = pd.read_excel(file, sheet_name='fletes_variables')
    fletes_variables_df.set_index('puerto', drop=True, inplace=True)

    for puerto in problema['conjuntos']['puertos']:
        for planta in problema['conjuntos']['plantas']:
            problema['parametros']['fletes_variables'][f'CT_{puerto}_{planta}'] = fletes_variables_df.loc[puerto][planta]

    # $CW_{lm}$ : Costo de vender una carga perteneciente a una empresa a otra.

    costo_cambio_empresa_df = pd.read_excel(file, 'venta_entre_empresas')

    costo_cambio_empresa_df = costo_cambio_empresa_df.melt(id_vars='origen', value_vars=['contegral', 'finca'], var_name='destino')

    problema['parametros']['costo_venta_intercompany'] = {f"CW_{costo_cambio_empresa_df.iloc[x]['origen']}_{costo_cambio_empresa_df.iloc[x]['destino']}":costo_cambio_empresa_df.iloc[x]['value'] for x in range(costo_cambio_empresa_df.shape[0])}

    # $TT_{jk}$ : tiempo en días para transportar la carga desde el puerto $j$ hacia la planta $k$.

    problema['parametros']['tiempo_transporte'] = dict()

    for puerto in problema['conjuntos']['puertos']:
        for planta in problema['conjuntos']['plantas']:
            lista_ua = [ua for ua in problema['conjuntos']['unidades_almacenamiento'] if planta in ua.split('_')[0]]
            for ua in lista_ua:
                problema['parametros']['tiempo_transporte'][f"TT_{puerto}_{ua}"] = 2

    # $CA_{m}^{i}$ : Capacidad de almacenamiento de la unidad $m$ en toneladas del ingrediente $i$, tenendo en cuenta que $m \in K$.

    inventario_planta_df = pd.read_excel(file, sheet_name='unidades_almacenamiento', skiprows=1)
            
    capacidad_ua_df = inventario_planta_df.melt(id_vars=['key'], value_vars=problema['conjuntos']['ingredientes'],var_name='ingrediente', value_name='capacidad').rename(columns={'key':'unidad_almacenamiento'})

    problema['parametros']['capacidad_almacenamiento_ua'] = {f"CA_{capacidad_ua_df.iloc[x]['ingrediente']}_{capacidad_ua_df.iloc[x]['unidad_almacenamiento']}":capacidad_ua_df.iloc[x]['capacidad'] for x in range(capacidad_ua_df.shape[0])}

    # $II_{m}^{i}$ : Inventario inicial del ingrediente $i$ en la unidad $m$, teniendo en cuenta que $m \in K$

    problema['parametros']['inventario_inicial_ua'] = {f"II_{inventario_planta_df.iloc[x]['key']}_{inventario_planta_df.iloc[x]['ingrediente_actual']}":inventario_planta_df.iloc[x]['cantidad_actual'] for x in range(inventario_planta_df.shape[0])}

    # $DM_{ki}^{t}$: Demanda del ingrediente $i$ en la planta $k$ durante el día $t$.

    demanda_df = pd.read_excel(file, sheet_name='consumo_proyectado')

    demanda_df = demanda_df.melt(id_vars=['key', 'ingrediente', 'planta'], var_name='fecha', value_name='consumo').copy()

    demanda_df['periodo'] = demanda_df['fecha'].map(problema['conjuntos']['fechas'])

    problema['parametros']['consumo_proyectado'] = {f"DM_{demanda_df.iloc[i]['key']}_{demanda_df.iloc[i]['periodo']}": demanda_df.iloc[i]['consumo'] for i in range(demanda_df.shape[0])}

    

    # $CI_{im}^{t}$ : Costo de asignar el ingrediente $i$ a la unidad de almacenamiento $m$ durante el periodo $t$. Si la unidad de almacenamiento no puede contener el ingrediente, este costo será $infinito$.

    # $SS_{ik}^{t}$ : Inventario de seguridad a tener del ingrediente $i$ en la planta $k$ al final del día $t$.
    ss_df = pd.read_excel(file, sheet_name='consumo_proyectado')
    ss_df.drop(columns=['ingrediente', 'planta'], inplace=True)
    ss_df.set_index(keys='key', drop=True, inplace=True)
    ss_df['SS'] = ss_df.apply(np.mean, axis=1)*10    
    problema['parametros']['safety_stock'] = {f'SS_{k}':ss_df.loc[k]['SS'] for k in ss_df.index}

    # $CS_{ik}^{t}$ : Costo de no satisfacer el inventario de seguridad para el ingrediente $i$ en la planta $k$ durante el día $t$.
    # problema['parametros']['costo_no_safety_stock'] = {f'CS_{k}':1000000 for k in ss_df.index}

    # $CD_{ik}^{t}$ : Costo de no satisfacer la demanda del ingrediente $i$  en la planta $k$ durante el día $t$.
    # problema['parametros']['costo_no_demanda'] = {f'CD_{k}':10000000 for k in ss_df.index}
    
    
    # $CK_{ik}^{t}$ : Costo del backorder del ingrediente $i$  en la planta $k$ durante el día $t$.
    # problema['parametros']['costo_backorder'] = {f'CK_{k}':10000 for k in ss_df.index}
    

    # $TR_{im}^{t}$ : Cantidad en tránsito programada para llegar a la unidad de almacenamiento $m$ durante el día $t$,




