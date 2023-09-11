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
    xdt_df['fecha'] = xdt_df['periodo'].map(fechas)
    xdt_df.drop(columns=['tipo'], inplace=True)
    xdt_df['value'] = xdt_df['value'].apply(lambda x: round(x, 0))
    xdt_df = xdt_df[xdt_df['value'] > 0]
    xdt_df.rename(columns={'value': 'kilos_despachados'}, inplace=True)

    itd_df = __procesar_listado_variables(variables['ITD'], campos)
    itd_df.drop(columns=['tipo'], inplace=True)
    itd_df.rename(columns={'value': 'camiones_despachados'}, inplace=True)

    xtr_df = __procesar_listado_variables(variables['XTR'], campos)
    xtr_df['fecha'] = xtr_df['periodo'].map(fechas)
    xtr_df.drop(columns=['tipo'], inplace=True)
    xtr_df['value'] = xtr_df['value'].apply(lambda x: round(x, 0))
    xtr_df = xtr_df[xtr_df['value'] > 0]
    xtr_df.rename(columns={'value': 'kilos_despachados'}, inplace=True)

    itr_df = __procesar_listado_variables(variables['ITR'], campos)
    itr_df.drop(columns=['tipo'], inplace=True)
    itr_df.rename(columns={'value': 'camiones_despachados'}, inplace=True)

    campos.remove('tipo')

    xdt_df = xdt_df[xdt_df['kilos_despachados'] > 0]

    xdt_df = xdt_df.pivot_table(index=['empresa_origen',
                                       'ingrediente',
                                       'importacion',
                                       'fecha'], columns='planta', values='kilos_despachados',
                                aggfunc=sum)

    xtr_df = xtr_df[xtr_df['kilos_despachados'] > 0]

    xtr_df = xtr_df.pivot_table(index=['empresa_origen',
                                       'ingrediente',
                                       'importacion',
                                       'fecha'], columns='planta', values='kilos_despachados', aggfunc=sum)

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


def _procesar_variables_almacenamiento_planta(df_dict: dict, variables: dict):

    campos = ['tipo', 'empresa', 'planta', 'ingrediente', 'periodo']

    variable_dict = variables['XIU']

    df = __procesar_listado_variables(variable_dict, campos)

    df_dict['Almacenamiento en Planta'] = df


@DeprecationWarning
def _procesar_variables_demanda(df_dict: dict, variables: dict):

    campos = ['tipo', 'ingrediente', 'empresa', 'planta', 'unidad', 'periodo']

    variable_dict = variables['XDM']

    df = __procesar_listado_variables(variable_dict, campos)

    df.rename(columns={'value': 'kilos_consumidos'}, inplace=True)

    df_dict['Ingrediente a consumir'] = df


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

    _procesar_variables_almacenamiento_planta(df_dict, variables)

    # _procesar_variables_demanda(df_dict, variables)

    _procesar_variables_safety_stock(df_dict, variables)

    return df_dict
