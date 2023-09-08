# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 15:11:39 2023

@author: LuisFer_BAires
"""

import pandas as pd


def __procesar_listado_variables(variable_dict: dict, campos: list):

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

    fechas = {x: conjuntos['fechas'][x]
              for x in range(len(conjuntos['fechas']))}

    xdt_df = __procesar_listado_variables(variables['XTD'], campos)
    xdt_df['fecha'] = xdt_df['periodo'].map(fechas)
    xdt_df.drop(columns=['tipo'], inplace=True)
    xdt_df.rename(columns={'value': 'kilos_despachados'}, inplace=True)

    itd_df = __procesar_listado_variables(variables['ITD'], campos)
    itd_df.drop(columns=['tipo'], inplace=True)
    itd_df.rename(columns={'value': 'camiones_despachados'}, inplace=True)

    xtr_df = __procesar_listado_variables(variables['XTR'], campos)
    xtr_df['fecha'] = xtr_df['periodo'].map(fechas)
    xtr_df.drop(columns=['tipo'], inplace=True)
    xtr_df.rename(columns={'value': 'kilos_despachados'}, inplace=True)

    itr_df = __procesar_listado_variables(variables['ITR'], campos)
    itr_df.drop(columns=['tipo'], inplace=True)
    itr_df.rename(columns={'value': 'camiones_despachados'}, inplace=True)

    campos.remove('tipo')

    # dt_df = pd.merge(left=xdt_df, right=itd_df,
    #                 left_on=campos,
    #                 right_on=campos,
    #                 how='inner')

    xdt_df['Variable'] = 'Despacho Directo'

    xdt_df = xdt_df[xdt_df['kilos_despachados'] > 0]

    xdt_df = xdt_df.pivot_table(index=['Variable',
                                       'empresa_origen',
                                       'ingrediente',
                                       'importacion',
                                       'fecha'], columns='planta', values='kilos_despachados',
                                aggfunc=sum)

    # tr_df = pd.merge(left=xtr_df, right=itr_df,
    #                 left_on=campos,
    #                 right_on=campos,
    #                 how='inner')

    xtr_df['Variable'] = "Despacho bodega"

    xtr_df = xtr_df[xtr_df['kilos_despachados'] > 0]

    xtr_df = xtr_df.pivot_table(index=['Variable',
                                       'empresa_origen',
                                       'ingrediente',
                                       'importacion',
                                       'fecha'], columns='planta', values='kilos_despachados', aggfunc=sum)

    df_dict['Despacho directo'] = xdt_df
    df_dict['Despacho desde Bodega'] = xtr_df


def _procesar_variables_alacenamiento_puerto(df_dict: dict, variables: dict):

    campos = ['tipo', 'empresa', 'ingrediente',
              'operador', 'importacion', 'periodo']

    variable_dict = variables['XPL']

    df = __procesar_listado_variables(variable_dict, campos)

    df_dict['Almacenamiento en Puerto'] = df

    variable_dict = variables['XIP']

    df = __procesar_listado_variables(variable_dict, campos)

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

    _procesar_variables_alacenamiento_puerto(df_dict, variables)

    _procesar_variables_almacenamiento_planta(df_dict, variables)

    # _procesar_variables_demanda(df_dict, variables)

    _procesar_variables_safety_stock(df_dict, variables)

    return df_dict
