#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 15:54:50 2023

@author: luispinilla
"""

# unidades de almacenamiento en la planta

from modelo_planta.lector_parametros import get_ingredientes, get_plantas, get_unidades, get_consumo


if __name__ == '__main__':
    
    file = '0_model_23oct-rev.xlsm'
    
    # conjuntos
    ingredientes = get_ingredientes(file=file)
    
    # leer parametros de plantas
    plantas_list, empresas_list, plantas_empresas_dict = get_plantas(file=file)
    
    unidades, capacidad_dict, unidades_plantas, unidades_ingredientes, inventario_actual_unidades = get_unidades(file=file, ingredientes=ingredientes)

    fechas, periodos, consumo_dict = get_consumo(file=file, plantas_list=plantas_list, ingredientes=ingredientes)

    