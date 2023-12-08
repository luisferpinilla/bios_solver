#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 14:59:08 2023

@author: luispinilla
"""

import pandas as pd


def sin_capacidad_para_consumo(x) -> bool:
    return x['consumo_medio_kg'] > 0 and x['capacidad_kg'] == 0


def ss_menor_capacidad(x) -> bool:
    return x['capacidad_dias'] < x['ss_dias']


def recepcion_menor_cap_camion(x) -> bool:
    if x['consumo_medio_kg'] > 0:
        return x['capacidad_recepcion_kg'] < 34000
    else:
        return False


def capacidad_menor_ss_mas_un_camion(x) -> bool:

    if x['consumo_medio_kg'] > 0:
        return x['capacidad_kg'] - x['ss_kg'] < 34000
    else:
        return False


def validaciones_completas(x, validaciones: list) -> bool:

    for validacion in validaciones:
        if x[validacion]:
            return False

    return True


def visor_parametros(conjuntos: dict, parametros: dict) -> pd.DataFrame:

    df_dict = dict()

    df_dict['planta'] = list()
    df_dict['ingrediente'] = list()
    df_dict['consumo_medio_kg'] = list()
    df_dict['ss_kg'] = list()
    df_dict['ss_dias'] = list()
    df_dict['inventario_kg'] = list()
    df_dict['inventario_dias'] = list()
    df_dict['capacidad_kg'] = list()
    df_dict['capacidad_dias'] = list()
    df_dict['capacidad_safetyStock_kg'] = list()
    df_dict['capacidad_safetyStock_dias'] = list()
    # df_dict['capacidad_recepcion_kg'] = list()
    # df_dict['capacidad_recepcion_dias'] = list()

    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:

            consumo_medio = parametros['Consumo_promedio'][
                f'{planta.split("_")[1]}_{ingrediente}']
            inventario_inicial = parametros['inventario_inicial_ua'][
                f'II_{planta}_{ingrediente}']
            ss_kg = parametros['safety_stock'][f'SS_{planta}_{ingrediente}']
            ss_camiones = int(ss_kg/34000)
            capacidad = parametros['capacidad_almacenamiento_planta'][
                f'CI_{planta}_{ingrediente}']
            # recepcion_kg = parametros['capacidad_recepcion_ingredientes'][
            #    f'{planta}_{ingrediente}']
            # recepcion_camiones = int(recepcion_kg/34000)
            capacidad_sin_usar = capacidad - inventario_inicial

            if consumo_medio > 0.0:
                inventario_inicial_dio = inventario_inicial/consumo_medio
                capacidad_dio = capacidad/consumo_medio
                ss_dias = ss_kg/consumo_medio
                # recepcion_camiones_dias = recepcion_kg/consumo_medio
                capacidad_sin_usar_dias = capacidad_sin_usar/consumo_medio

            else:
                inventario_inicial_dio = 1000
                capacidad_dio = 1000
                ss_dias = 0
                recepcion_camiones_dias = 1000
                capacidad_sin_usar_dias = 1000

            df_dict['planta'].append(planta)
            df_dict['ingrediente'].append(ingrediente)
            df_dict['consumo_medio_kg'].append(consumo_medio)
            df_dict['ss_kg'].append(ss_kg)
            df_dict['ss_dias'].append(ss_dias)
            df_dict['inventario_kg'].append(inventario_inicial)
            df_dict['inventario_dias'].append(inventario_inicial_dio)
            df_dict['capacidad_kg'].append(capacidad)
            df_dict['capacidad_dias'].append(capacidad_dio)
            df_dict['capacidad_safetyStock_kg'].append(ss_kg)
            df_dict['capacidad_safetyStock_dias'].append(ss_dias)
            # df_dict['capacidad_recepcion_kg'].append(recepcion_kg)
            # df_dict['capacidad_recepcion_dias'].append(recepcion_camiones_dias)

    df = pd.DataFrame(df_dict)

    df.set_index(['planta', 'ingrediente'], inplace=True, drop=True)

    df['Val0'] = df.apply(sin_capacidad_para_consumo, axis=1)
    df['Val1'] = df.apply(ss_menor_capacidad, axis=1)
    # df['Val2'] = df.apply(recepcion_menor_cap_camion, axis=1)
    df['Val3'] = df.apply(capacidad_menor_ss_mas_un_camion, axis=1)

    # Obtener nombres de columnas resultado de validaciones
    validacion_columns = [x for x in df.columns if x.startswith('Val')]

    # Determinar si las validaciones se cumplen
    df['Val'] = df.apply(
        lambda x: validaciones_completas(x, validacion_columns), axis=1)
    # Remover todas las filas que cumplen con las validaciones
    df = df[df['Val'] == False]

    for column in df.columns:

        if column.endswith('kg'):
            df[column] = df[column].apply(lambda x: round(number=x, ndigits=0))

        if column.endswith('dias'):
            df[column] = df[column].apply(lambda x: int(x))

    return df
