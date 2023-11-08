#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 14:59:08 2023

@author: luispinilla
"""

import pandas as pd

def visor_parametros(conjuntos:dict, parametros:dict)->pd.DataFrame:
    
    df_dict = dict()
    
    df_dict['planta'] = list()
    df_dict['ingrediente'] = list()
    df_dict['consumo_diario_medio'] = list()
    df_dict['ss_kg'] = list()
    df_dict['ss_dias'] = list()
    df_dict['inventario_kg'] = list()
    df_dict['inventario_dias'] = list()
    df_dict['capacidad_kg'] = list()
    df_dict['capacidad_dias'] = list()
    df_dict['capacidad_sin_usar_kg'] = list()
    df_dict['capacidad_sin_usar_dias'] = list()
    df_dict['Capacidad-SafetyStock_kg'] = list()
    df_dict['Capacidad-SafetyStock_camiones'] = list()
    df_dict['Capacidad-SafetyStock_dias'] = list()
    df_dict['Capacidad_recepcion_kg'] = list()
    df_dict['Capacidad_recepcion_camiones'] = list()
    df_dict['Capacidad_recepcion_dias'] = list()
      
    
    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:
            
            consumo_medio = parametros['Consumo_promedio'][f'{planta.split("_")[1]}_{ingrediente}']
            inventario_inicial = parametros['inventario_inicial_ua'][f'II_{planta}_{ingrediente}']
            ss_kg = parametros['safety_stock'][f'SS_{planta}_{ingrediente}']
            ss_camiones = int(ss_kg/34000)
            capacidad = parametros['capacidad_almacenamiento_planta'][f'CI_{planta}_{ingrediente}']
            capacidad_camiones = int(capacidad/34000)
            recepcion_kg = parametros['capacidad_recepcion_ingredientes'][f'{planta}_{ingrediente}']
            recepcion_camiones = int(recepcion_kg/34000)
            capacidad_sin_usar = capacidad - inventario_inicial
            
            
            if consumo_medio >0:
                inventario_inicial_dio = inventario_inicial/consumo_medio
                capacidad_dio = capacidad/consumo_medio
                ss_dias = ss_kg/consumo_medio
                recepcion_camiones_dias = recepcion_kg/consumo_medio
                capacidad_sin_usar_dias = capacidad_sin_usar/consumo_medio
                
            else:
                inventario_inicial_dio = 1000
                capacidad_dio = 1000
                ss_dias = 1000
                recepcion_camiones_dias = 1000
                capacidad_sin_usar_dias = 1000
                
            
            df_dict['planta'].append(planta)
            df_dict['ingrediente'].append(ingrediente)
            df_dict['consumo_diario_medio'].append(consumo_medio)
            df_dict['ss_kg'].append(ss_kg)
            df_dict['ss_dias'].append(ss_dias)
            df_dict['inventario_kg'].append(inventario_inicial)
            df_dict['inventario_dias'].append(inventario_inicial_dio)
            df_dict['capacidad_kg'].append(capacidad)
            df_dict['capacidad_dias'].append(capacidad_dio)
            df_dict['capacidad_sin_usar_kg'].append(capacidad_sin_usar)
            df_dict['capacidad_sin_usar_dias'].append(capacidad_sin_usar_dias)
            df_dict['Capacidad-SafetyStock_kg'].append(ss_kg)
            df_dict['Capacidad-SafetyStock_camiones'].append(ss_camiones)
            df_dict['Capacidad-SafetyStock_dias'].append(ss_dias)
            df_dict['Capacidad_recepcion_kg'].append(recepcion_kg)
            df_dict['Capacidad_recepcion_camiones'].append(recepcion_camiones)
            df_dict['Capacidad_recepcion_dias'].append(recepcion_camiones_dias)
    
     
    return pd.DataFrame(df_dict)
    
    