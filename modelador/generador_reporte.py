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
    
    return periodos_df


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
    
    return invenatario_puertos_df
    
    
    

def generar_inventario_plantas(parametros:dict, variables:dict, verbose=False):

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
                
                if verbose:
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
    
    return inventario_plantas_df


def generar_reporte_transitos(parametros:dict, variables:dict):
    
    transitos = dict()
    
    transitos['tipo'] = list()
    transitos['empresa_origen'] = list()
    transitos['ingrediente'] = list()
    transitos['barco']=list()
    transitos['empresa_destino']=list()
    transitos['planta']=list()
    transitos['unidad']=list()
    transitos['cantidad']=list()
    transitos['costo_fijo'] = list()
    transitos['costo_variable']=list()
    transitos['costo_intercompany'] = list()
    transitos['costo_total'] = list()
    transitos['periodo_despacho'] = list()
    transitos['periodo_llegada'] = list()
    
    
    for carga in parametros['conjuntos']['cargas']:

        campos = carga.split('_')
        empresa_origen = campos[0]
        ingrediente = campos[1]
        puerto = campos[2]
        barco = campos[3]
        
        for ua in parametros['conjuntos']['unidades_almacenamiento']:
            
            campos_ua = ua.split('_')
            empresa_destino = campos_ua[0]
            planta = campos_ua[1]
            unidad = campos_ua[2]
            
            for periodo in range(parametros['periodos']):
            
                xtd_name = f'XTD_{empresa_origen}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}' 
            
                if xtd_name in variables:
                    xtd_var = variables[xtd_name]
                    xtd_val = xtd_var.varValue
                    
                    cf_name = f'CF_{puerto}_{empresa_destino}_{planta}'
                    cf_val = parametros['parametros']['fletes_fijos'][cf_name]
                
                    ct_name = f'CT_{puerto}_{empresa_destino}_{planta}'
                    ct_val = parametros['parametros']['fletes_variables'][ct_name]
                    
                    ci_name = f'CW_{empresa_origen}_{empresa_destino}'
                    ci_value = parametros['parametros']['costo_venta_intercompany'][ci_name]
                    
                    ct = cf_val + (ct_val + ci_value)*xtd_val
                
                    transitos['tipo'].append('Indirecto')
                    transitos['empresa_origen'].append(empresa_origen)
                    transitos['ingrediente'].append(ingrediente)
                    transitos['barco'].append(barco)
                    transitos['empresa_destino'].append(empresa_destino)
                    transitos['planta'].append(planta)
                    transitos['unidad'].append(unidad)
                    transitos['cantidad'].append(xtd_val)
                    transitos['costo_fijo'].append(cf_val)
                    transitos['costo_variable'].append(ct_val)
                    transitos['costo_intercompany'].append(ci_value)
                    transitos['costo_total'].append(ct)
                    transitos['periodo_despacho'].append(periodo)
                    transitos['periodo_llegada'].append(periodo+2)
        
            
        transitos_df = pd.DataFrame(transitos)
        
        transitos_df.to_parquet('transporte_puerto_planta.parquet')
        
        return transitos_df
            
        
        
        
    


def generar_reporte(parametros:dict, variables:dict):
    
    
    transitos_df = generar_reporte_transitos(parametros=parametros, variables=variables)
    
    with pd.ExcelWriter('data.xlsx') as writer:
        
        print('guardar periodos')
        generar_periodos(parametros=parametros).to_excel(writer, sheet_name='periodos')
        
        print('guardar inventario_plantas')
        generar_inventario_plantas(parametros=parametros, variables=variables).to_excel(writer, sheet_name='inventario_plantas')
        
        print('guardar inventario_puertos')
        generar_invenario_puerto(parametros=parametros, variables=variables).to_excel(writer, sheet_name='inventario_puertos')
        
        print('guardar transitos')
        transitos_df.to_excel(writer, sheet_name='transitos')
        
        print('listo')
    
    
    
