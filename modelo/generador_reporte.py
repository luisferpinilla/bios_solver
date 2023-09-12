# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 15:11:39 2023

@author: LuisFer_BAires
"""

import pandas as pd


def __procesar_listado_variables(variable_dict: dict, campos: list) -> pd.DataFrame:
    """Transforma el listado de variables entregado en un dataframe

    Args:
        variable_dict (dict): Listado de variables
        campos (list): Listado de campos que van en el nombre de la variables

    Returns:
        DataFrame: Dataframe pandas con las variables seleccionadas y el valor obtenido
    """
    dict_var = dict()
    dict_var['name'] = list()
    dict_var['value'] = list()

    for name, var in variable_dict.items():
        dict_var['name'].append(name)
        dict_var['value'].append(var.varValue)

    df = pd.DataFrame(dict_var)

    for i in range(len(campos)):
        campo = campos[i]
        df[campo] = df['name'].apply(lambda x: str(x).split('_')[i])

    df.drop(columns=['name'], inplace=True)

    df['periodo'] = pd.to_numeric(df['periodo'])

    df['value'] = pd.to_numeric(df['value'])

    df = df[campos + ['value']]

    return df


def __procesar_listado_parametros(par_dict: dict, campos: list):

    dict_parameters = dict()
    dict_parameters['name'] = list()
    dict_parameters['value'] = list()

    for name, value in par_dict.items():
        dict_parameters['name'].append(name)
        dict_parameters['value'].append(value)

    df = pd.DataFrame(dict_parameters)

    for i in range(len(campos)):
        campo = campos[i]
        df[campo] = df['name'].apply(lambda x: str(x).split('_')[i])

    df.drop(columns=['name'], inplace=True)

    df['value'] = pd.to_numeric(df['value'])

    df = df[campos + ['value']]

    return df


def __obtener_map_fechas(conjuntos: dict, formato='%b-%d'):

    fechas = {x: conjuntos['fechas'][x].strftime(formato)
              for x in range(len(conjuntos['fechas']))}

    return fechas


def _procesar_variables_transporte(df_dict: dict, variables: dict, conjuntos: dict):

    campos = ['tipo',
              'empresa_origen',
              'operador',
              'importacion',
              'ingrediente',
              'empresa_destino',
              'planta',
              'periodo']

    # Cargar data

    fechas = __obtener_map_fechas(conjuntos=conjuntos)

    xdt_df = __procesar_listado_variables(variables['XTD'], campos)
    xdt_df['fecha despacho'] = xdt_df['periodo'].map(fechas)
    xdt_df.drop(columns=['tipo'], inplace=True)
    xdt_df['value'] = xdt_df['value'].apply(lambda x: round(x, 0))
    xdt_df = xdt_df[xdt_df['value'] > 0]
    xdt_df.rename(columns={'value': 'kilos_despachados'}, inplace=True)

    itd_df = __procesar_listado_variables(variables['ITD'], campos)
    itd_df.drop(columns=['tipo'], inplace=True)
    itd_df.rename(columns={'value': 'camiones_despachados'}, inplace=True)

    xtr_df = __procesar_listado_variables(variables['XTR'], campos)
    xtr_df['fecha despacho'] = xtr_df['periodo'].map(fechas)
    xtr_df.drop(columns=['tipo'], inplace=True)
    xtr_df['value'] = xtr_df['value'].apply(lambda x: round(x, 0))
    xtr_df = xtr_df[xtr_df['value'] > 0]
    xtr_df.rename(columns={'value': 'kilos_despachados'}, inplace=True)

    itr_df = __procesar_listado_variables(variables['ITR'], campos)
    itr_df.drop(columns=['tipo'], inplace=True)
    itr_df.rename(columns={'value': 'camiones_despachados'}, inplace=True)

    campos.remove('tipo')

    xdt_df = xdt_df.pivot_table(index=['empresa_origen',
                                       'operador',
                                       'ingrediente',
                                       'importacion',
                                       'fecha despacho'], columns='planta', values='kilos_despachados',
                                aggfunc=sum)

    xtr_df = xtr_df.pivot_table(index=['empresa_origen', 'operador',
                                       'ingrediente',
                                       'importacion',
                                       'fecha despacho'], columns='planta', values='kilos_despachados', aggfunc=sum)

    df_dict['Despacho directo'] = xdt_df
    df_dict['Despacho desde Bodega'] = xtr_df


def _procesar_variables_alacenamiento_puerto(df_dict: dict, variables: dict, conjuntos: dict):

    campos = ['tipo', 'empresa', 'operador',
              'importacion', 'ingrediente', 'periodo']

    variable_dict = variables['XPL']

    fechas = __obtener_map_fechas(conjuntos=conjuntos)

    xpl_df = __procesar_listado_variables(variable_dict, campos)

    xpl_df['fecha'] = xpl_df['periodo'].map(fechas)

    xpl_df['value'] = xpl_df['value'].apply(lambda x: round(x, 0))

    xpl_df['variable'] = 'Descargue a bodega'

    variable_dict = variables['XIP']

    xip_df = __procesar_listado_variables(variable_dict, campos)

    xip_df['fecha'] = xip_df['periodo'].map(fechas)

    xip_df['value'] = xip_df['value'].apply(lambda x: round(x, 0))

    xip_df['variable'] = 'Inventario al final del día'

    variable_dict = variables['XTR']

    xtr_df = __procesar_listado_variables(variable_dict=variable_dict,
                                          campos=['tipo',
                                                  'empresa_origen',
                                                  'operador',
                                                  'importacion',
                                                  'ingrediente',
                                                  'empresa_destino',
                                                  'planta',
                                                  'periodo'])

    xtr_df.rename(columns={'empresa_origen': 'empresa'}, inplace=True)
    xtr_df.drop(columns=['empresa_destino', 'planta'], inplace=True)
    xtr_df['fecha'] = xtr_df['periodo'].map(fechas)
    xtr_df['variable'] = 'Despachos hacia plantas'

    df = pd.concat([xpl_df, xip_df, xtr_df])

    df = df[df['value'] > 0]

    df['value'] = df['value'].apply(lambda x: round(x, 0))

    df = df.pivot_table(values='value',
                        index=['variable',
                               'empresa',
                               'ingrediente',
                               'operador',
                               'importacion'],
                        columns='fecha', aggfunc=sum)

    df_dict['Inventario en Puerto'] = df


def _procesar_variables_almacenamiento_planta(df_dict: dict, variables: dict, conjuntos: dict, parametros: dict, generar_excel=False):

    # Leer y procesar inventario final
    campos = ['tipo', 'empresa', 'planta', 'ingrediente', 'periodo']

    variable_dict = variables['XIU']

    inventario_df = __procesar_listado_variables(variable_dict, campos)

    fechas = __obtener_map_fechas(conjuntos=conjuntos)

    inventario_df.drop(columns=['tipo'], inplace=True)

    inventario_df['value'] = inventario_df['value'].apply(
        lambda x: round(x, 0))

    inventario_df.rename(columns={'value': 'inventario'}, inplace=True)

    # Leer y procesar backorder
    variable_dict = variables['XBK']

    backorder_df = __procesar_listado_variables(variable_dict, campos)

    backorder_df.drop(columns=['tipo'], inplace=True)

    backorder_df['value'] = backorder_df['value'].apply(lambda x: round(x, 0))

    backorder_df.rename(columns={'value': 'backorder'}, inplace=True)

    # Leer y procesar Cumplimiento SS

    variable_dict = variables['BSS']

    cumple_SS_df = __procesar_listado_variables(variable_dict, campos)

    cumple_SS_df.drop(columns=['tipo'], inplace=True)

    cumple_SS_df['value'] = cumple_SS_df['value'].apply(lambda x: round(x, 0))

    cumple_SS_df.rename(columns={'value': 'alarma safety stock'}, inplace=True)

    # Leer y procesar Despachos directos
    campos = ['tipo',
              'empresa_origen',
              'operador',
              'importacion',
              'ingrediente',
              'empresa_destino',
              'planta',
              'periodo']

    variable_dict = variables['XTD']

    despacho_directo_df = __procesar_listado_variables(variable_dict, campos)

    despacho_directo_df.drop(columns=['tipo'], inplace=True)

    despacho_directo_df['value'] = despacho_directo_df['value'].apply(
        lambda x: round(x, 0))

    despacho_directo_df.rename(columns={'empresa_destino': 'empresa',
                                        'value': 'despacho directo'}, inplace=True)

    despacho_directo_df = despacho_directo_df.groupby(['empresa',
                                                       'planta',
                                                       'ingrediente',
                                                       'periodo'])[['despacho directo']].sum().reset_index()

    # Leer y procesar despachos desde bodega en puerto

    variable_dict = variables['XTR']

    despacho_bodega_df = __procesar_listado_variables(variable_dict, campos)

    despacho_bodega_df.drop(columns=['tipo'], inplace=True)

    despacho_bodega_df['value'] = despacho_bodega_df['value'].apply(
        lambda x: round(x, 0))

    despacho_bodega_df.rename(columns={'empresa_destino': 'empresa',
                                       'value': 'despacho bodega puerto'}, inplace=True)

    despacho_bodega_df = despacho_bodega_df.groupby(['empresa',
                                                     'planta',
                                                     'ingrediente',
                                                     'periodo'])[['despacho bodega puerto']].sum().reset_index()

    # Leer y procesar parametros de demanda
    campos = ['tipo', 'empresa', 'planta', 'ingrediente', 'periodo']

    par_dict = parametros['consumo_proyectado']

    demanda_df = __procesar_listado_parametros(
        par_dict=par_dict, campos=campos)

    demanda_df.drop(columns=['tipo'], inplace=True)

    demanda_df['value'] = demanda_df['value'].apply(lambda x: round(x, 0))

    demanda_df.rename(columns={'value': 'demanda'}, inplace=True)

    demanda_df['periodo'] = demanda_df['periodo'].apply(lambda x: int(x))

    # Leer y procesar parametros de capacidad de almacenamiento
    campos = ['tipo', 'empresa', 'planta', 'ingrediente']

    par_dict = parametros['capacidad_almacenamiento_planta']

    capacidad_df = __procesar_listado_parametros(
        par_dict=par_dict, campos=campos)

    capacidad_df.drop(columns=['tipo'], inplace=True)

    capacidad_df['value'] = capacidad_df['value'].apply(lambda x: round(x, 0))

    capacidad_df.rename(columns={'value': 'capacidad'}, inplace=True)

    # Leer y procesar parametros de safety stock
    par_dict = parametros['safety_stock']

    campos = ['tipo', 'empresa', 'planta', 'ingrediente']

    safety_df = __procesar_listado_parametros(par_dict, campos)

    safety_df.drop(columns=['tipo'], inplace=True)

    safety_df['value'] = safety_df['value'].apply(lambda x: round(x, 0))

    safety_df.rename(columns={'value': 'safety_stock'}, inplace=True)

    # Efectuar las uniones
    df = pd.merge(left=inventario_df, right=backorder_df,
                  left_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  right_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  how='left')

    df = pd.merge(left=df, right=despacho_directo_df,
                  left_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  right_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  how='left')

    df = pd.merge(left=df, right=despacho_bodega_df,
                  left_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  right_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  how='left')

    df = pd.merge(left=df, right=cumple_SS_df,
                  left_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  right_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  how='left')

    df = pd.merge(left=df, right=demanda_df,
                  left_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  right_on=['empresa', 'planta', 'ingrediente', 'periodo'],
                  how='left')

    df = pd.merge(left=df, right=capacidad_df,
                  left_on=['empresa', 'planta', 'ingrediente'],
                  right_on=['empresa', 'planta', 'ingrediente'],
                  how='left')

    df = pd.merge(left=df, right=safety_df,
                  left_on=['empresa', 'planta', 'ingrediente'],
                  right_on=['empresa', 'planta', 'ingrediente'],
                  how='left')

    df['fecha'] = df['periodo'].map(fechas)

    df_dict['Almacenamiento en Planta'] = df[['planta',
                                              'ingrediente',
                                              'fecha',
                                              'despacho directo',
                                              'despacho bodega puerto',
                                              'demanda',
                                              'backorder',
                                              'inventario',
                                              'safety_stock',
                                              'alarma safety stock',
                                              'capacidad']]

    if generar_excel:
        with pd.ExcelWriter('solucion.xlsx') as writer:
            df.to_excel(writer, sheet_name='consolidado')
            backorder_df.to_excel(writer, sheet_name='XBK')
            despacho_bodega_df.to_excel(writer, sheet_name='XTR')
            safety_df.to_excel(writer, sheet_name='safety_stock')
            cumple_SS_df.to_excel(writer, sheet_name='BSS')
            capacidad_df.to_excel(writer, sheet_name='cap almacenamiento')
            demanda_df.to_excel(writer, sheet_name='consumo proyectado')
            despacho_directo_df.to_excel(writer, sheet_name='XTD')
            inventario_df.to_excel(writer, sheet_name='XIU')


def _procesar_variables_safety_stock(df_dict: dict, variables: dict):

    campos = ['tipo', 'ingrediente', 'empresa', 'planta', 'periodo']

    variable_dict = variables['BSS']

    df = __procesar_listado_variables(variable_dict, campos)

    df.rename(columns={'value': 'safety_stock_activado'}, inplace=True)

    df_dict['Safety stock'] = df

    variable_dict = variables['XBK']

    df = __procesar_listado_variables(variable_dict, campos)

    df.rename(columns={'value': 'Backorder'}, inplace=True)

    df_dict['Backorder'] = df


def generar_reporte(variables: dict, parametros: dict, conjuntos: dict):

    df_dict = dict()

    _procesar_variables_transporte(
        df_dict=df_dict, variables=variables, conjuntos=conjuntos)

    _procesar_variables_alacenamiento_puerto(
        df_dict, variables=variables, conjuntos=conjuntos)

    _procesar_variables_almacenamiento_planta(
        df_dict, variables, conjuntos, parametros)

    _procesar_variables_safety_stock(df_dict, variables)

    return df_dict
