#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 15:56:03 2023

@author: luispinilla
"""

import pandas as pd
import numpy as np
from datetime import datetime


def get_ingredientes(file:str):
    
    df = pd.read_excel(file, sheet_name='ingredientes')
    
    ingredientes_list = list(df['ingrediente'].unique())
    
    return ingredientes_list


def get_plantas(file:str):
    
    df = pd.read_excel(io=file, sheet_name='plantas')
    
    plantas_list = list(df['planta'].unique())
    
    empresas_list = list(df['empresa'].unique())
    
    plantas_empresas_dict = dict()
    
    for i in range(df.shape[0]):
        plantas_empresas_dict[df.iloc[i]['planta']] = df.iloc[i]['empresa'] 
     
    return plantas_list, empresas_list, plantas_empresas_dict


def get_unidades(file:str, ingredientes:list):  
    
    df = pd.read_excel(io=file, sheet_name='unidades_almacenamiento')
    
    df = df[['planta', 'unidad_almacenamiento', 'ingrediente_actual',
           'cantidad_actual'] + ingredientes]

    # llenar capacidades nulas con ceros
    for ingrediente in ingredientes:
        df[ingrediente] = df[ingrediente].fillna(0)
    
    # asgurar los tipos de datos correctos
    for column in df.columns: 
        if column in ['planta', 'unidad_almacenamiento', 'ingrediente_actual']:
            df[column] = df[column].astype(str)
        else:
            df[column] = df[column].astype(float)

    # Asignar ingredientes en 0            
    df1 = df[df['ingrediente_actual'].isin(ingredientes)].copy()
    df2 = df[~df['ingrediente_actual'].isin(ingredientes)].copy()
    df2['ingrediente_actual'] = df2[ingredientes].apply(lambda x: ingredientes[np.argmax(x)], axis=1)
    df = pd.concat([df1, df2]).copy()
    
    

    # organizar verticalmente    
    capacidad_df = df.melt(id_vars=['planta', 'unidad_almacenamiento'],
                 value_vars = ingredientes,
                 var_name = 'ingrediente',
                 value_name = 'kg')
    
    capacidad_df['unidad'] = capacidad_df['planta'] + '_' + capacidad_df['unidad_almacenamiento'] + "_" + capacidad_df['ingrediente']

    capacidad_df.set_index('unidad', drop=True, inplace=True)    

    unidades = list(capacidad_df.index)  
    
    capacidad_dict = {i:capacidad_df.loc[i]['kg'] for i in capacidad_df.index}
    
    unidades_plantas = {i:capacidad_df.loc[i]['planta'] for i in capacidad_df.index}

    unidades_ingredientes = {i:capacidad_df.loc[i]['ingrediente'] for i in capacidad_df.index}
    
    df['unidad'] = df['planta'] + '_' + df['unidad_almacenamiento'] + "_" + df['ingrediente_actual']
    
    df.set_index('unidad', drop=True, inplace=True)

    inventario_actual_unidades = dict()

    for ingrediente in ingredientes:
        for unidad in unidades:
            name = f'{unidad}_{ingrediente}'
            if name in df.index:
                inventario_actual_unidades[name] = df.loc[name]['inventario_actual']
            else:
                inventario_actual_unidades[name] = 0.0
            
            
            
    
    return unidades, capacidad_dict, unidades_plantas, unidades_ingredientes, inventario_actual_unidades


def get_consumo(file:str, plantas_list:list, ingredientes:list):
    
    consumo_df = pd.read_excel(io=file, sheet_name='consumo_proyectado')

    for column in ['empresa', 'key']:
        if column in consumo_df.columns:
            consumo_df.drop(columns=column, inplace=True)
            
    fechas = [x for x in consumo_df.drop(columns=['ingrediente', 'planta', 'Average', 'Key2'])]
    
    periodos = [str(i) for i in range(len(fechas))]
    
    map_periodos = {fechas[i]:periodos[i] for i in range(len(fechas))}

    

    consumo_df = pd.melt(frame=consumo_df, id_vars=['ingrediente', 'planta'],
                         value_vars=fechas, 
                         var_name='fecha', 
                         value_name='kg')
    
    consumo_df['periodo'] = consumo_df['fecha'].map(map_periodos)
    
    consumo_df['key'] = consumo_df['planta'] + '_' + consumo_df['ingrediente'] + '_' + consumo_df['periodo']
            
    consumo_df.set_index('key', drop=True, inplace=True)    

    consumo_dict =  dict()
    
    consumo_medio_dict = dict()

    for planta in plantas_list:
        for ingrediente in ingredientes:
            
            for periodo in periodos:
                name = f'{planta}_{ingrediente}_{periodo}'
                if name in consumo_df.index:
                    consumo_dict[name] = consumo_df.loc[name]['kg']
                else:
                    consumo_dict[name] = 0.0

    return fechas, periodos, consumo_dict