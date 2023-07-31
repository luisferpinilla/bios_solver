# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 15:11:39 2023

@author: LuisFer_BAires
"""

import pandas as pd

def generar_periodos(parametros:dict):
    
    periodos = dict()
    periodos['periodos'] = list()
    periodos['fechas'] =  list()
    
    for k,v in parametros['conjuntos']['periodos'].items():
        periodos['periodos'].append(k)
        periodos['fechas'].append(v)
        
    periodos_df = pd.DataFrame(periodos)
    
    periodos_df.to_parquet('periodos.parquet')


def generar_invenario_puerto(parametros:dict, variables:dict):
    
    invenatario_puertos = dict()
    invenatario_puertos['periodo'] = list()
    invenatario_puertos['empresa'] =  list()
    invenatario_puertos['puerto'] = list()
    invenatario_puertos['barco'] =  list()
    invenatario_puertos['ingrediente'] =  list()
    invenatario_puertos['inventario_final'] = list()
    
    
    for carga in parametros['conjuntos']['cargas']:
        for periodo in range(parametros['periodos']):
                
            campos = carga.split('_')
            empresa = campos[0]
            ingrediente = campos[1]
            puerto = campos[2]
            barco = campos[3]
            
            xip_name = f'XIP_{carga}_{periodo}'
            xip_var = variables[xip_name]
            
            invenatario_puertos['periodo'].append(periodo)
            invenatario_puertos['empresa'].append(empresa)
            invenatario_puertos['puerto'].append(puerto)
            invenatario_puertos['barco'].append(barco)
            invenatario_puertos['ingrediente'].append(ingrediente)
            invenatario_puertos['inventario_final'].append(xip_var.varValue)
            
    invenatario_puertos_df = pd.DataFrame(invenatario_puertos)
    
    invenatario_puertos_df.to_parquet('invenatarios_puerto.parquet')
    
    
    

def generar_inventario_plantas(parametros:dict, variables:dict):

    inventario_plantas = dict()
    inventario_plantas['periodo'] = list()
    inventario_plantas['empresa'] =  list()
    inventario_plantas['planta'] =  list()
    inventario_plantas['unidad'] =  list()
    inventario_plantas['ingrediente'] =  list()
    inventario_plantas['demanda']=list()
    inventario_plantas['inventario_final'] = list()
    
    
    for ingrediente in parametros['conjuntos']['ingredientes']:
        for unidad in parametros['conjuntos']['unidades_almacenamiento']:
            for periodo in range(parametros['periodos']):
                
                print(unidad,ingrediente,periodo)
                
                campos = unidad.split('_')
                empresa = campos[0]
                planta = campos[1]
                ua = campos[2]
                
                xiu_name = f'XIU_{unidad}_{ingrediente}_{periodo}'                
                xiu_var = variables[xiu_name]
                
                xdm_name = f'XDM_{unidad}_{ingrediente}_{periodo}'  
                xdm_var = variables[xdm_name]
                
                inventario_plantas['periodo'].append(periodo)
                inventario_plantas['empresa'].append(empresa)
                inventario_plantas['planta'].append(planta)
                inventario_plantas['unidad'].append(ua)
                inventario_plantas['ingrediente'].append(ingrediente)
                inventario_plantas['demanda'].append(xdm_var.varValue)
                inventario_plantas['inventario_final'].append(xiu_var.varValue)
                
    inventario_plantas_df = pd.DataFrame(inventario_plantas)
    
    inventario_plantas_df.to_parquet('inventarios_planta.parquet')    


def generar_reporte(parametros:dict, variables:dict):
    
    generar_periodos(parametros=parametros)
    
    generar_inventario_plantas(parametros=parametros, variables=variables)
    
    generar_invenario_puerto(parametros=parametros, variables=variables)
    

    
    
    
