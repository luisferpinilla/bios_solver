# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


def __remover_underscores(x: str) -> str:

    x = str(x)
    x = x.lower()
    x = x.replace('_', '')
    x = x.replace('-', '')
    x = x.replace(' ', '')

    return x


def __inventario_inicial_puerto(parametros: dict, file: str):
    # $IP_{l}$ : inventario inicial en puerto para la carga $l$.

    inventarios_puerto_df = pd.read_excel(
        file, sheet_name='inventario_puerto', usecols='B:H')

    campos = ['empresa', 'operador', 'imp-motonave', 'ingrediente']

    for campo in campos:
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(
            __remover_underscores)

    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)

    parametros['inventario_inicial_cargas'] = {
        f"IP_{inventarios_puerto_df.iloc[fila]['key']}": inventarios_puerto_df.iloc[fila]['cantidad_kg'] for fila in range(inventarios_puerto_df.shape[0])}


def __llegadas_a_puerto(parametros: dict, conjuntos: dict, file: str):

    # $AR_{l}^{t}$ : Cantidad de material que va a llegar a la carga $l$ durante el día $t$, sabiendo que: $material \in I$ y $carga \in J$.

    cap_descarge_per_dia = 5000000

    inventarios_puerto_df = pd.read_excel(
        file, sheet_name='tto_puerto', usecols='B:H')

    campos = ['empresa', 'operador', 'imp-motonave', 'ingrediente']

    for campo in campos:
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(
            __remover_underscores)

    
    fechas_dict = {conjuntos['fechas'][x]: str(
        x) for x in conjuntos['periodos']}

    inventarios_puerto_df['periodo'] = inventarios_puerto_df['fecha_llegada'].map(
        fechas_dict)
    
    inventarios_puerto_df = inventarios_puerto_df[~inventarios_puerto_df['periodo'].isna()]
    
    # regenerar key
    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)
    
    
    df_dict = {column:list() for column in inventarios_puerto_df.columns}
    
    for i in inventarios_puerto_df.index:
        empresa = inventarios_puerto_df.loc[i]['empresa']
        operador =inventarios_puerto_df.loc[i]['operador']
        ingrediente = inventarios_puerto_df.loc[i]['ingrediente']
        impmotonave = inventarios_puerto_df.loc[i]['imp-motonave']
        cantidad_kg = inventarios_puerto_df.loc[i]['cantidad_kg']
        fecha_llegada = inventarios_puerto_df.loc[i]['fecha_llegada']
        valor_kg = inventarios_puerto_df.loc[i]['valor_kg']
        key = inventarios_puerto_df.loc[i]['key']
        periodo = int(inventarios_puerto_df.loc[i]['periodo'])
        
        while cantidad_kg > 0:
            df_dict['empresa'].append(empresa)
            df_dict['operador'].append(operador)
            df_dict['ingrediente'].append(ingrediente)
            df_dict['imp-motonave'].append(impmotonave)
            cantidad_descarga = min(cap_descarge_per_dia, cantidad_kg)
            df_dict['cantidad_kg'].append(cantidad_descarga)
            cantidad_kg -= cantidad_descarga
            df_dict['fecha_llegada'].append(fecha_llegada)
            df_dict['valor_kg'].append(valor_kg) 
            df_dict['key'].append(key)            
            df_dict['periodo'].append(str(periodo))  
            periodo = periodo+1
            
    df = pd.DataFrame(df_dict)
    
    
    parametros['llegadas_cargas'] = {
        f"AR_{df.iloc[i]['key']}_{df.iloc[i]['periodo']}": df.iloc[i]['cantidad_kg'] for i in range(df.shape[0])}


def __costo_almacenamiento_puerto(parametros: dict, conjuntos: dict, file: str):

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.

    cc_df = pd.read_excel(
        file, sheet_name='costos_almacenamiento_cargas', usecols='B:G')

    campos = ['empresa', 'ingrediente', 'operador-puerto', 'imp-motonave']

    for campo in campos:
        cc_df[campo] = cc_df[campo].apply(__remover_underscores)

    # regenerar key
    cc_df['key'] = cc_df.apply(lambda field: '_'.join(
        [field[x] for x in campos]), axis=1)

    cc_df = cc_df[cc_df['fecha_corte'].isin(
        conjuntos['fechas'])].copy()

    fechas_dict = {conjuntos['fechas'][x]: x for x in range(
        len(conjuntos['fechas']))}

    cc_df['periodo'] = cc_df['fecha_corte'].map(fechas_dict)

    parametros['costos_almacenamiento'] = {
        f"CC_{cc_df.iloc[i]['key']}_{cc_df.iloc[i]['periodo']}": cc_df.iloc[i]['valor_kg'] for i in range(cc_df.shape[0])}


def __costo_operacion_puerto(parametros: dict, conjuntos: dict, file: str):

    df = pd.read_excel(file, sheet_name='costos_operacion_portuaria')

    df['operador'] = df['operador-puerto-ing'].apply(
        lambda x: str(x).split('_')[0])

    df['operador'] = df['operador'].apply(__remover_underscores)

    df['ingrediente'] = df['operador-puerto-ing'].apply(
        lambda x: str(x).split('_')[1])

    df['key'] = df['operador'] + "_" + df['ingrediente']

    xtd_df = df[df['tipo_operacion'] == 'directo']

    xpl_df = df[df['tipo_operacion'] == 'bodega']

    # CD costo operativo para despacho directo
    # CB costo operativo para alacenamiento a bodega

    cd_dict = {f"CD_{xtd_df.iloc[x]['key']}": xtd_df.iloc[x]
               ['valor_kg'] for x in range(xtd_df.shape[0])}

    cb_dict = {f"CB_{xpl_df.iloc[x]['key']}": xpl_df.iloc[x]
               ['valor_kg'] for x in range(xpl_df.shape[0])}

    parametros['costos_operacion_directo'] = cd_dict

    parametros['costos_operacion_bodega'] = cb_dict


def __costos_transporte(parametros: dict, file: str):
    # $CF_{lm}$ : Costo fijo de transporte por camión despachado llevando la carga $l$ hasta la unidad de almacenamiento $m$.
    # $ CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.

    fletes = ['fletes_fijos', 'fletes_variables']

    for flete in fletes:

        parametros[flete] = dict()

        df = pd.read_excel(file, sheet_name=flete)

        df = df.melt(id_vars=['operador-puerto-ing'], value_vars=list(df.columns).remove(
            'operador-puerto-ing'), var_name='planta', value_name='costo')

        df['operador'] = df['operador-puerto-ing'].apply(
            lambda x: str(x).split('_')[0])

        df['ingrediente'] = df['operador-puerto-ing'].apply(
            lambda x: str(x).split('_')[1])

        df['key'] = df['operador'] + "_" + \
            df['planta'] + "_" + df['ingrediente']

        values_dict = {df.iloc[i]['key']: df.iloc[i]['costo']
                       for i in range(df.shape[0])}

        parametros[flete] = values_dict


def __venta_intercompany(parametros: dict, file: str):
    # $CW_{lm}$ : Costo de vender una carga perteneciente a una empresa a otra.

    costo_cambio_empresa_df = pd.read_excel(file, 'venta_entre_empresas')

    costo_cambio_empresa_df = costo_cambio_empresa_df.melt(
        id_vars='origen', value_vars=['contegral', 'finca'], var_name='destino')

    parametros['costo_venta_intercompany'] = {
        f"CW_{costo_cambio_empresa_df.iloc[x]['origen']}_{costo_cambio_empresa_df.iloc[x]['destino']}": costo_cambio_empresa_df.iloc[x]['value'] for x in range(costo_cambio_empresa_df.shape[0])}


def __tiempo_transporte(parametros: dict, conjuntos: dict, file: str):

    # $TT_{jk}$ : tiempo en días para transportar la carga desde el puerto $j$ hacia la planta $k$.

    return
    parametros['tiempo_transporte'] = dict()

    for puerto in conjuntos['puertos']:
        for planta in conjuntos['plantas']:
            lista_ua = [ua for ua in conjuntos
                        ['unidades_almacenamiento'] if planta in ua.split('_')[0]]
            for ua in lista_ua:
                parametros.dict['tiempo_transporte'][f"TT_{puerto}_{ua}"] = 0


def __capacidad_almacenamiento_planta(parametros: dict, conjuntos: dict, file: str):

    # $CA_{m}^{i}$ : Capacidad de almacenamiento de la unidad $m$ en toneladas del ingrediente $i$, tenendo en cuenta que $m \in K$.

    inventario_planta_df = pd.read_excel(
        file, sheet_name='unidades_almacenamiento')

    # Eliminar unidades con materiales que no están en la lista

    inventario_planta_df = inventario_planta_df[inventario_planta_df['ingrediente_actual'].isin(
        conjuntos['ingredientes'])].copy()
    
    # Eliminar nulos del reporte
    
    for ingrediente in conjuntos['ingredientes']:
        inventario_planta_df[ingrediente] = inventario_planta_df[ingrediente].fillna(0.0)
    
    inventario_planta_df['Suma'] = inventario_planta_df[conjuntos['ingredientes']].apply(
        sum, axis=1)

    # Eliminar unidades de almacenamiento que no reportan capacidad para ningun ingrediente
    inventario_planta_df = inventario_planta_df[inventario_planta_df['Suma'] > 0].copy()

    # Eliminar columna de suma recién creada
    inventario_planta_df.drop(columns=['Suma'], inplace=True)


    capacidad_df = inventario_planta_df.melt(id_vars=['empresa', 'planta'],
                                             value_vars=conjuntos['ingredientes'],
                                             var_name='ingrediente',
                                             value_name='capacidad').rename(columns={'key': 'unidad_almacenamiento'})

    capacidad_df = capacidad_df.groupby(['empresa', 'planta', 'ingrediente'])[
        ['capacidad']].sum().reset_index()

    capacidad_df['key'] = capacidad_df['empresa'] + "_" + \
        capacidad_df['planta'] + "_" + capacidad_df['ingrediente']

    capacidad_dict = {f"CI_{capacidad_df.iloc[x]['key']}": capacidad_df.iloc[x]['capacidad'] for x in range(
        capacidad_df.shape[0])}

    parametros['capacidad_almacenamiento_planta'] = capacidad_dict


def __inventario_planta(parametros: dict, conjuntos: dict, file: str):

    # $II_{m}^{i}$ : Inventario inicial del ingrediente $i$ en la unidad $m$, teniendo en cuenta que $m \in K$

    campos = ['empresa', 'planta', 'ingrediente_actual']

    inventario_planta_df = pd.read_excel(
        file, sheet_name='unidades_almacenamiento', usecols='B:F')

    inventario_planta_df = inventario_planta_df[inventario_planta_df['ingrediente_actual'].isin(
        conjuntos['ingredientes'])]

    inventario_planta_df = inventario_planta_df.groupby(
        campos)[['cantidad_actual']].sum().reset_index()

    inventario_planta_df['key'] = inventario_planta_df.apply(
        lambda x: '_'.join([x[c] for c in campos]), axis=1)

    inventario_planta_df.set_index('key', inplace=True, drop=True)

    ingredientes_dict = dict()

    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:
            key = f'{planta}_{ingrediente}'
            if key in inventario_planta_df.index:
                ingredientes_dict[f'II_{key}'] = inventario_planta_df.loc[key]['cantidad_actual']
            else:
                ingredientes_dict[f'II_{key}'] = 0

    parametros['inventario_inicial_ua'] = ingredientes_dict


def __transitos_a_plantas(parametros:dict, conjuntos:dict, file:str):
    
    transitos_df = pd.read_excel(io=file, sheet_name='tto_plantas')
    
    fechas_dict = {conjuntos['fechas'][x]: x for x in range(
        len(conjuntos['fechas']))}
    
    transitos_df['periodo'] = transitos_df['fecha_llegada'].map(fechas_dict)
    
    transitos_df = transitos_df.groupby(['empresa', 'planta', 'ingrediente', 'periodo'])[['cantidad']].sum()
    
    transitos_dict = dict()
    
    for periodo in conjuntos['periodos']:
        for planta in conjuntos['plantas']:
            for ingrediente in conjuntos['ingredientes']:
                
                campos = planta.split('_')
                p_empresa = campos[0]
                p_planta = campos[1]
                
                indextr = (p_empresa, p_planta, ingrediente, periodo)
                
                tt_name = f'TT_{p_empresa}_{p_planta}_{ingrediente}_{periodo}'
                
                if indextr in transitos_df.index:
                    tt_value = transitos_df.loc[indextr]['cantidad']
                else:
                    tt_value = 0.0
                
                transitos_dict[tt_name] = tt_value
                
    parametros['transitos_a_plantas'] = transitos_dict
    


def __consumo_proyectado(parametros: dict, conjuntos: dict, file: str, usecols: str):

    # $DM_{ki}^{t}$: Demanda del ingrediente $i$ en la planta $k$ durante el día $t$.

    demanda_df = pd.read_excel(
        file, sheet_name='consumo_proyectado', usecols=usecols)

    demanda_df.fillna(0.0, inplace=True)

    mean_df = demanda_df.copy()

    mean_df.set_index(['empresa', 'ingrediente', 'planta'],
                      drop=True, inplace=True)


    mean_df['mean'] = mean_df.apply(np.mean, axis=1)

    mean_df = mean_df.reset_index()

    mean_dict = {
        f"{mean_df.loc[r]['planta']}_{mean_df.loc[r]['ingrediente']}": mean_df.loc[r]['mean'] for r in mean_df.index}

    demanda_df = demanda_df.melt(
        id_vars=['empresa', 'ingrediente', 'planta'], var_name='fecha', value_name='consumo')

    demanda_df['fecha'] = pd.to_datetime(
        demanda_df['fecha'], format='%d/%m/%Y')

    fechas_dict = {conjuntos['fechas'][x]: str(
        x) for x in range(len(conjuntos['fechas']))}

    demanda_df['periodo'] = demanda_df['fecha'].map(fechas_dict)

    campos = ['empresa', 'planta', 'ingrediente', 'periodo']

    # regenerar key
    demanda_df['key'] = demanda_df.apply(
        lambda field: '_'.join([str(field[x]) for x in campos]), axis=1)

    demanda_dict = {f"DM_{demanda_df.iloc[i]['key']}": demanda_df.iloc[i]['consumo'] for i in range(
        demanda_df.shape[0])}

    parametros['consumo_proyectado'] = demanda_dict

    parametros['Consumo_promedio'] = mean_dict


def __safety_stock_planta(parametros: dict, conjuntos: dict, file: str):

    param_dict = dict()

    ss_df = pd.read_excel(file, sheet_name='Safety_stock')

    ss_dict = {f"{ss_df.loc[r]['planta']}_{ss_df.loc[r]['ingrediente']}": ss_df.loc[r]
               ['dias_ss'] for r in ss_df.index}

    mean_dict = parametros['Consumo_promedio']

    for planta in conjuntos['plantas']:
        p_empresa = planta.split('_')[0]
        p_planta = planta.split('_')[1]
        for ingrediente in conjuntos['ingredientes']:
            name_ss = f'{p_planta}_{ingrediente}'
            name_consumo = f'{p_planta}_{ingrediente}'
            if name_ss in ss_dict.keys() and name_consumo in mean_dict.keys():
                param_dict[f'SS_{planta}_{ingrediente}'] = ss_dict[name_ss] * \
                    mean_dict[name_consumo]
            else:
                param_dict[f'SS_{planta}_{ingrediente}'] = 0.0

    parametros['safety_stock'] = param_dict


def __costo_asignacion_ingrediantes_ua(parametros: dict, file: str):

    # $CI_{im}^{t}$ : Costo de asignar el ingrediente $i$ a la unidad de almacenamiento $m$ durante el periodo $t$. Si la unidad de almacenamiento no puede contener el ingrediente, este costo será $infinito$.
    pass


def __costo_insatisfaccion_ss(parametros: dict, file: str):
    # $CS_{ik}^{t}$ : Costo de no satisfacer el inventario de seguridad para el ingrediente $i$ en la planta $k$ durante el día $t$.
    # problema.parametros['costo_no_safety_stock'] = {f'CS_{k}':1000000 for k in ss_df.index}
    pass


def __costo_insatisfaccion_demanda(parametros: dict, file: str):
    # $CD_{ik}^{t}$ : Costo de no satisfacer la demanda del ingrediente $i$  en la planta $k$ durante el día $t$.
    # problema.parametros['costo_no_demanda'] = {f'CD_{k}':10000000 for k in ss_df.index}
    pass


def __costo_backorder_planta(parametros: dict, file: str):
    # $CK_{ik}^{t}$ : Costo del backorder del ingrediente $i$  en la planta $k$ durante el día $t$.
    # problema.parametros['costo_backorder'] = {f'CK_{k}':10000 for k in ss_df.index}
    pass



def generar_parametros(parametros: dict, conjuntos: dict, file: str, usecols: str) -> dict:

    __inventario_inicial_puerto(parametros=parametros, file=file)

    __llegadas_a_puerto(parametros=parametros, conjuntos=conjuntos, file=file)

    __costo_almacenamiento_puerto(
        parametros=parametros, conjuntos=conjuntos, file=file)

    __costos_transporte(parametros=parametros, file=file)

    __venta_intercompany(parametros=parametros, file=file)

    __tiempo_transporte(parametros=parametros, conjuntos=conjuntos, file=file)

    __capacidad_almacenamiento_planta(
        parametros=parametros, conjuntos=conjuntos, file=file)
    
    __transitos_a_plantas(parametros=parametros, conjuntos=conjuntos, file=file)

    __inventario_planta(parametros=parametros, conjuntos=conjuntos, file=file)

    __consumo_proyectado(parametros=parametros,
                         conjuntos=conjuntos, file=file, usecols=usecols)

    __safety_stock_planta(parametros=parametros,
                          conjuntos=conjuntos, file=file)

    __costo_asignacion_ingrediantes_ua(parametros=parametros, file=file)

    __costo_insatisfaccion_ss(parametros=parametros, file=file)

    __costo_insatisfaccion_demanda(parametros=parametros, file=file)

    __costo_backorder_planta(parametros=parametros, file=file)

    __costo_operacion_puerto(parametros=parametros,
                             conjuntos=conjuntos, file=file)
