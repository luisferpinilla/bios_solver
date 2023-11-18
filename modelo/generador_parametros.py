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


def __generar_plantas_empresas(parametros:dict, file: str):
    

    plantas_df = pd.read_excel(file, sheet_name='plantas')

    plantas_df['planta'] = plantas_df['planta'].apply(__remover_underscores)

    plantas_df['empresa'] = plantas_df['empresa'].apply(__remover_underscores)

    empresas_dict = dict()
    
    for i in plantas_df.index:
        par_planta = plantas_df.loc[i]['planta']
        par_empresa = plantas_df.loc[i]['empresa']
        empresas_dict[par_planta] = par_empresa

    parametros['empresas_plantas'] = empresas_dict


def __llegadas_a_puerto(parametros: dict, conjuntos: dict, file: str):

    # $AR_{l}^{t}$ : Cantidad de material que va a llegar a la carga $l$ durante el día $t$, sabiendo que: $material \in I$ y $carga \in J$.

    cap_descarge_per_dia = 5000000

    inventarios_puerto_df = pd.read_excel(
        file, sheet_name='tto_puerto')

    campos = ['empresa', 'operador', 'imp-motonave', 'ingrediente']

    for campo in campos:
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(
            __remover_underscores)

    fechas_dict = {conjuntos['fechas'][x]: str(
        x) for x in conjuntos['periodos']}

    inventarios_puerto_df['periodo'] = inventarios_puerto_df['fecha_llegada'].map(
        fechas_dict)

    inventarios_puerto_df = inventarios_puerto_df[~inventarios_puerto_df['periodo'].isna(
    )]

    # regenerar key

    campos = campos + ['periodo']

    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)

    df_dict = {column: list() for column in inventarios_puerto_df.columns}

    for i in inventarios_puerto_df.index:
        empresa = inventarios_puerto_df.loc[i]['empresa']
        operador = inventarios_puerto_df.loc[i]['operador']
        ingrediente = inventarios_puerto_df.loc[i]['ingrediente']
        impmotonave = inventarios_puerto_df.loc[i]['imp-motonave']
        cantidad_kg = inventarios_puerto_df.loc[i]['cantidad_kg']
        fecha_llegada = inventarios_puerto_df.loc[i]['fecha_llegada']
        valor_kg = inventarios_puerto_df.loc[i]['valor_kg']
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
            key = f'AR_{empresa}_{operador}_{impmotonave}_{ingrediente}_{periodo}'
            df_dict['key'].append(key)
            df_dict['periodo'].append(str(periodo))
            periodo = periodo+1

    df = pd.DataFrame(df_dict)

    df.set_index('key', drop=True, inplace=True)

    ar_dict = dict()

    for periodo in conjuntos['periodos']:
        for carga in conjuntos['cargas']:

            par_name = f'AR_{carga}_{periodo}'

            if par_name in df.index:

                par_value = df.loc[par_name]['cantidad_kg']

            else:

                par_value = 0.0

            ar_dict[par_name] = par_value

    parametros['llegadas_cargas'] = ar_dict


def __generar_costos_cif_cargas(parametros: dict, conjuntos: dict, file=str):
    

    transitos_a_puerto_df = pd.read_excel(file, sheet_name='tto_puerto')
    inventarios_puerto_df = pd.read_excel(file, sheet_name='inventario_puerto')

    campos = ['empresa', 'operador',  'imp-motonave', 'ingrediente']

    for campo in campos:
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(
            __remover_underscores)
        transitos_a_puerto_df[campo] = transitos_a_puerto_df[campo].apply(
            __remover_underscores)

    transitos_a_puerto_df['key'] = transitos_a_puerto_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)
    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)
    
    transitos_a_puerto_df.rename(columns={'valor_kg':'valor_cif'}, inplace=True)
    
    inventarios_puerto_df.rename(columns={'valor_cif_kg':'valor_cif'}, inplace=True)

    df = pd.concat([transitos_a_puerto_df, inventarios_puerto_df])
    
    df.set_index('key', drop=True, inplace=True)
    
    cif_dict = dict()

    for carga in conjuntos['cargas']:
        par_name = f'VC_{carga}'
        if carga in df.index:
            cif_dict[par_name] = df.loc[carga]['valor_cif']
        else:
            print('no har valor para',carga)
            cif_dict[par_name] = 0.0

    parametros['valor_cif'] = cif_dict


def __costo_almacenamiento_puerto(parametros: dict, conjuntos: dict, file: str):

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.

    cc_df = pd.read_excel(
        file, sheet_name='costos_almacenamiento_cargas', usecols='B:G')

    campos = ['empresa', 'operador-puerto', 'imp-motonave', 'ingrediente']
    
    ultima_fecha = conjuntos['fechas'][-1]

    for campo in campos:
        cc_df[campo] = cc_df[campo].apply(__remover_underscores)

    cc_df['fecha_corte'] = cc_df['fecha_corte'].apply(lambda x: x if x <= ultima_fecha else ultima_fecha)

    fechas_dict = {conjuntos['fechas'][x]: x for x in range(len(conjuntos['fechas']))}

    cc_df['periodo'] = cc_df['fecha_corte'].map(fechas_dict)

    # regenerar key
    campos = campos + ['periodo']
    cc_df['key'] = cc_df.apply(lambda field: '_'.join(
        [str(field[x]) for x in campos]), axis=1)

    cc_df['key'] = cc_df['key'].apply(lambda x: f'CC_{x}')

    cc_df.set_index('key', drop=True, inplace=True)

    costos_dict = dict()

    for carga in conjuntos['cargas']:
        for periodo in conjuntos['periodos']:
            par_name = f'CC_{carga}_{periodo}'
            if par_name in cc_df.index:
                par_value = cc_df.loc[par_name]['valor_kg']
            else:
                par_value = 0.0

            costos_dict[par_name] = par_value

    parametros['costos_almacenamiento'] = costos_dict


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


def __costos_transporte(conjuntos: dict, parametros: dict, file: str):
    # $CF_{lm}$ : Costo fijo de transporte por camión despachado llevando la carga $l$ hasta la unidad de almacenamiento $m$.
    # $ CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.

    fletes = {'fletes_fijos': 'CF', 'fletes_variables': 'CV'}

    for flete, codigo in fletes.items():

        values_dict = dict()

        df = pd.read_excel(file, sheet_name=flete)

        df['operador-puerto-ing'] = df['operador-puerto-ing'].apply(
            lambda x: str(x).replace('-', ''))

        df = df.melt(id_vars=['operador-puerto-ing'], value_vars=list(df.columns).remove(
            'operador-puerto-ing'), var_name='planta', value_name='costo')

        df['operador'] = df['operador-puerto-ing'].apply(
            lambda x: str(x).split('_')[0])

        df['ingrediente'] = df['operador-puerto-ing'].apply(
            lambda x: str(x).split('_')[1])

        df['key'] = codigo + "_" + df['operador'] + "_" + \
            df['planta'] + "_" + df['ingrediente']

        df.set_index('key', drop=True, inplace=True)

        big_m = df['costo'].sum()

        for operador in conjuntos['operadores']:
            for planta in conjuntos['plantas']:
                for ingrediente in conjuntos['ingredientes']:
                    par_name = f'{codigo}_{operador}_{planta}_{ingrediente}'
                    if par_name in df.index:
                        par_value = df.loc[par_name]['costo']
                    else:
                        par_value = big_m

                    values_dict[par_name] = par_value

        parametros[flete] = values_dict


def __venta_intercompany(parametros: dict, file: str):
    # $CW_{lm}$ : Costo de vender una carga perteneciente a una empresa a otra.

    costo_cambio_empresa_df = pd.read_excel(file, 'venta_entre_empresas')

    costo_cambio_empresa_df = costo_cambio_empresa_df.melt(
        id_vars='origen', value_vars=['contegral', 'finca'], var_name='destino')

    parametros['costo_venta_intercompany'] = {
        f"CW_{costo_cambio_empresa_df.iloc[x]['origen']}_{costo_cambio_empresa_df.iloc[x]['destino']}": costo_cambio_empresa_df.iloc[x]['value'] for x in range(costo_cambio_empresa_df.shape[0])}


def __capacidad_recepcion_ingredientes(parametros:dict, conjuntos:dict, file:str):
    
    empresas_plantas = parametros['empresas_plantas']
    
    df = pd.read_excel(io=file, sheet_name='Safety_stock')[['planta', 'ingrediente', 'Capacidad_recepcion_kg']]
    
    df['empresa'] = df['planta'].map(empresas_plantas)
    
    df['key'] = df['empresa'] + '_' + df['planta'] + '_' + df['ingrediente']

    df.drop(columns=['empresa' ,'planta', 'ingrediente'], inplace=True)
    
    df.set_index('key', drop=True, inplace=True)
    
    
    capacidad_recepcion_ingredientes_dict = dict()
    
    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:
            
            name = f'{planta}_{ingrediente}'
            
            if name in df.index:
                capacidad_recepcion_ingredientes_dict[name] = df.loc[name]['Capacidad_recepcion_kg']
            else:
                capacidad_recepcion_ingredientes_dict[name] = 0
            
    
    parametros['capacidad_recepcion_ingredientes'] = capacidad_recepcion_ingredientes_dict


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
        inventario_planta_df[ingrediente] = inventario_planta_df[ingrediente].fillna(
            0.0)
    

    inventario_planta_df['Suma'] = inventario_planta_df[conjuntos['ingredientes']].apply(
        sum, axis=1)

    # Eliminar unidades de almacenamiento que no reportan capacidad para ningun ingrediente
    inventario_planta_df = inventario_planta_df[inventario_planta_df['Suma'] > 0].copy(
    )

    # Eliminar columna de suma recién creada
    inventario_planta_df.drop(columns=['Suma'], inplace=True)    

    # Traer la capacidad por ingrediente
    
    #capacidad_df = inventario_planta_df.melt(id_vars=['empresa', 'planta'],
    #                                         value_vars=conjuntos['ingredientes'],
    #                                         var_name='ingrediente',
    #                                         value_name='capacidad').rename(columns={'key': 'unidad_almacenamiento'})
    
    capacidad_df = inventario_planta_df.groupby(['empresa', 'planta', 'ingrediente_actual'])[conjuntos['ingredientes']].sum().reset_index()

    capacidad_df['capacidad'] = capacidad_df.apply(lambda x: x[x['ingrediente_actual']], axis=1)
    
    capacidad_df.drop(columns=conjuntos['ingredientes'], inplace=True)
    
    capacidad_df.rename(columns={'ingrediente_actual':'ingrediente'}, inplace=True)

    capacidad_df['key'] = 'CI_' + capacidad_df['empresa'] + "_" + capacidad_df['planta'] + "_" + capacidad_df['ingrediente']
        
    capacidad_df.set_index('key', drop=True, inplace=True)

    capacidad_dict = dict()
        
    for planta in conjuntos['plantas']:
        
        for ingrediente in conjuntos['ingredientes']:
            par_name = f'CI_{planta}_{ingrediente}'
           
            if par_name in capacidad_df.index:
               
                par_value = capacidad_df.loc[par_name]['capacidad']
               
            else:
               
               par_value = 0.0
               
            capacidad_dict[par_name] = par_value


    parametros['capacidad_almacenamiento_planta'] = capacidad_dict


def __inventario_planta(parametros: dict, conjuntos: dict, file: str):

    # $II_{m}^{i}$ : Inventario inicial del ingrediente $i$ en la unidad $m$, teniendo en cuenta que $m \in K$

    campos = ['empresa', 'planta', 'ingrediente_actual']

    inventario_planta_df = pd.read_excel(
        file, sheet_name='unidades_almacenamiento', usecols='B:F')

    inventario_planta_df['empresa'] = inventario_planta_df['planta'].map(parametros['empresas_plantas'])

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


def __transitos_a_plantas(parametros: dict, conjuntos: dict, file: str):

    transitos_df = pd.read_excel(io=file, sheet_name='tto_plantas')

    fechas_dict = {conjuntos['fechas'][x]: x for x in range(
        len(conjuntos['fechas']))}

    transitos_df['periodo'] = transitos_df['fecha_llegada'].map(fechas_dict)

    transitos_df = transitos_df.groupby(
        ['empresa', 'planta', 'ingrediente', 'periodo'])[['cantidad']].sum()

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
    
    mean_df['key'] = mean_df['planta'] + "_" + mean_df['ingrediente']

    mean_df.set_index('key', drop=True, inplace=True)

    # mean_dict = {
    #    f"{mean_df.loc[r]['planta']}_{mean_df.loc[r]['ingrediente']}": mean_df.loc[r]['mean'] for r in mean_df.index}

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

    demanda_df['key'] = demanda_df['key'].apply(lambda x: f'DM_{x}')

    demanda_df.set_index('key', drop=True, inplace=True)

    mean_dict = dict()

    demanda_dict = dict()

    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:
            
            par_name = f"{planta.split('_')[1]}_{ingrediente}"
            
            if par_name in mean_df.index:
                par_value = mean_df.loc[par_name]['mean']
            else:
                par_value = 0.0
            
            mean_dict[par_name] = par_value            
            
            for periodo in conjuntos['periodos']:

                par_name = f'DM_{planta}_{ingrediente}_{periodo}'

                if par_name in demanda_df.index:
                    par_value = demanda_df.loc[par_name]['consumo']
                else:
                    par_value = 0.0

                demanda_dict[par_name] = par_value

    parametros['consumo_proyectado'] = demanda_dict

    parametros['Consumo_promedio'] = mean_dict


def __safety_stock_planta(parametros: dict, conjuntos: dict, file: str):

    param_dict = dict()

    ss_df = pd.read_excel(file, sheet_name='Safety_stock')
    
    ss_df['dias_ss'] = ss_df['dias_ss'].fillna(0.0) 

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
    

def __calcular_dio_general(parametros:dict, file:str)->dict:
    
    dio_dict = dict()
    
    df = pd.read_excel(file, sheet_name='DIO')[['ingrediente', 'DIO_General']]
    
    df.set_index('ingrediente', drop=True, inplace=True)

    for ingrediente in df.index:
        dio_dict[ingrediente] = df.loc[ingrediente]['DIO_General']

    
    parametros['dio_objetivo']= dio_dict    


def __fechas_iniciales_cargas(parametros:dict, conjuntos:dict):
    
    initial_dates_inventory_dict = dict()
    
    for carga in conjuntos['cargas']:
        
        # Verificar si la tiene inventario desde el momento 0
        par_name = f'IP_{carga}'
        
        if par_name in parametros['inventario_inicial_cargas'].keys():
            
            initial_dates_inventory_dict[carga] = 100
            
        else:
            
            # determinar desde qué periodo se debe crear las variables de almacenamiento y despacho
            
            for periodo in conjuntos['periodos']:
                
                par_name = f'AR_{carga}_{periodo}'
                
                par_value = parametros['llegadas_cargas'][par_name]
                
                if par_value > 0:
                    
                    initial_dates_inventory_dict[carga] = periodo
                    
                    break
                
                
                
    parametros['periodos_atencion_cargas'] = initial_dates_inventory_dict
    
def __max_cantidad_camiones_a_despachar(parametros:dict, conjuntos:dict):
    
    cap_almacenamiento_planta = parametros['capacidad_almacenamiento_planta']
    Consumo_promedio_planta = parametros['Consumo_promedio']
    safety_stock = parametros['safety_stock']
    recepcion = parametros['capacidad_recepcion_ingredientes']
    
    max_dict = dict()
    
    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:
            
            # Obtener capacidad máxima de almacenamiento
            cap_name = f'CI_{planta}_{ingrediente}'
            cap_value = cap_almacenamiento_planta[cap_name]
            
            # Obtener el consumo promedio
            con_name = f'{planta.split("_")[1]}_{ingrediente}'
            con_value = Consumo_promedio_planta[con_name]
            
            # Obtener el safety stock
            ss_name = f'SS_{planta}_{ingrediente}'
            ss_value = safety_stock[ss_name]
            
            # Obtener la capacidad de recepcion de ingredientes
            rec_name = f'{planta}_{ingrediente}'
            rec_val = recepcion[rec_name]
            
            if con_value > 0.0:
                
                # Capacidad almacenamiento + un camión - consumo_medio
                cap_rec_camiones = int(rec_val/34000)
                cap_calc_camiones = int((cap_value - con_value + 34000)/34000)
                cap_max_camiones = min(cap_rec_camiones, cap_calc_camiones)
                
                max_dict[f'{planta}_{ingrediente}'] = cap_max_camiones
            else:
                max_dict[f'{planta}_{ingrediente}'] = 0
                
    parametros['capacidad_recepcion_max_camiones'] = max_dict
            
            
            
    
    
    

def generar_parametros(parametros: dict, conjuntos: dict, file: str, usecols: str) -> dict:

    
    __generar_plantas_empresas(parametros=parametros, file=file)

    __inventario_inicial_puerto(parametros=parametros, file=file)

    __llegadas_a_puerto(parametros=parametros, conjuntos=conjuntos, file=file)

    __generar_costos_cif_cargas(parametros=parametros, conjuntos=conjuntos, file=file)

    __costo_almacenamiento_puerto(
        parametros=parametros, conjuntos=conjuntos, file=file)

    __costos_transporte(conjuntos=conjuntos, parametros=parametros, file=file)

    __venta_intercompany(parametros=parametros, file=file)

    __tiempo_transporte(parametros=parametros, conjuntos=conjuntos, file=file)

    __capacidad_recepcion_ingredientes(parametros=parametros, conjuntos=conjuntos, file=file)

    __capacidad_almacenamiento_planta(parametros=parametros, conjuntos=conjuntos, file=file)

    __transitos_a_plantas(parametros=parametros,
                          conjuntos=conjuntos, file=file)

    __inventario_planta(parametros=parametros, conjuntos=conjuntos, file=file)

    __consumo_proyectado(parametros=parametros,
                         conjuntos=conjuntos, file=file, usecols=usecols)

    __safety_stock_planta(parametros=parametros,
                          conjuntos=conjuntos, file=file)

    __costo_operacion_puerto(parametros=parametros,
                             conjuntos=conjuntos, file=file)
    
    __calcular_dio_general(parametros=parametros, file=file)
    
    
    __fechas_iniciales_cargas(parametros=parametros, conjuntos=conjuntos)
    
    __max_cantidad_camiones_a_despachar(parametros=parametros, conjuntos=conjuntos)
