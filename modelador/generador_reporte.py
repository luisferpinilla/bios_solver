# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 15:11:39 2023

@author: LuisFer_BAires
"""

import pandas as pd
import json


def generar_periodos(problema: dict):

    periodos = dict()
    periodos['periodos'] = list()
    periodos['fechas'] = list()

    for k, v in problema['conjuntos']['periodos'].items():
        periodos['periodos'].append(k)
        periodos['fechas'].append(v)

    periodos_df = pd.DataFrame(periodos)

    return periodos_df


def generar_invenario_puerto(problema: dict, variables: dict):

    invenatario_puertos = dict()
    invenatario_puertos['periodo'] = list()
    invenatario_puertos['empresa'] = list()
    invenatario_puertos['puerto'] = list()
    invenatario_puertos['barco'] = list()
    invenatario_puertos['ingrediente'] = list()
    invenatario_puertos['llegadas'] = list()
    invenatario_puertos['inventario_final'] = list()

    for carga in problema['conjuntos']['cargas']:
        for periodo in range(problema['periodos']):

            campos = carga.split('_')
            empresa = campos[0]
            puerto = campos[1]
            barco = campos[2]
            ingrediente = campos[3]

            xip_name = f'XIP_{carga}_{periodo}'
            xip_var = variables['XIP'][xip_name]

            xpl_name = f'XPL_{carga}_{periodo}'
            xpl_var = variables['XPL'][xpl_name]

            invenatario_puertos['periodo'].append(periodo)
            invenatario_puertos['empresa'].append(empresa)
            invenatario_puertos['puerto'].append(puerto)
            invenatario_puertos['barco'].append(barco)
            invenatario_puertos['ingrediente'].append(ingrediente)
            invenatario_puertos['llegadas'].append(xpl_var.varValue)
            invenatario_puertos['inventario_final'].append(xip_var.varValue)

    invenatario_puertos_df = pd.DataFrame(invenatario_puertos)

    return invenatario_puertos_df


def generar_inventario_plantas(problema: dict, variables: dict, verbose=False):

    inventario_plantas = dict()
    inventario_plantas['periodo'] = list()
    inventario_plantas['empresa'] = list()
    inventario_plantas['planta'] = list()
    inventario_plantas['unidad'] = list()
    inventario_plantas['ingrediente'] = list()
    inventario_plantas['llegadas_barco'] = list()
    inventario_plantas['llegadas_almacen'] = list()
    inventario_plantas['demanda'] = list()
    inventario_plantas['inventario_final'] = list()

    for ingrediente in problema['conjuntos']['ingredientes']:
        for unidad in problema['conjuntos']['unidades_almacenamiento']:

            campos = unidad.split('_')
            empresa = campos[0]
            planta = campos[1]
            ua = campos[2]
            periodo = int(campos[3])

            xiu_name = f'XIU_{ingrediente}_{unidad}'
            xiu_var = variables['XIU'][xiu_name]

            xdm_name = f'XDM_{ingrediente}_{unidad}'
            xdm_var = variables['XDM'][xdm_name]

            inventario_plantas['periodo'].append(periodo)
            inventario_plantas['empresa'].append(empresa)
            inventario_plantas['planta'].append(planta)
            inventario_plantas['unidad'].append(ua)
            inventario_plantas['ingrediente'].append(ingrediente)
            inventario_plantas['demanda'].append(xdm_var.varValue)
            inventario_plantas['inventario_final'].append(xiu_var.varValue)

            # totalizar las llegadas desde puerto
            llegadas_barco = 0.0
            Llegadas_almacen = 0.0

            for carga in problema['conjuntos']['cargas']:

                if periodo >= 2:

                    xtr_name = f'XTR_{carga}_{empresa}_{planta}_{ua}_{periodo-2}'
                    xtr_var = variables['XTR'][xtr_name]
                    Llegadas_almacen += xtr_var.varValue

                    xtd_name = f'XTD_{carga}_{empresa}_{planta}_{ua}_{periodo-2}'
                    xtd_var = variables['XTD'][xtd_name]
                    llegadas_barco += xtd_var.varValue

            inventario_plantas['llegadas_barco'].append(llegadas_barco)
            inventario_plantas['llegadas_almacen'].append(Llegadas_almacen)

    inventario_plantas_df = pd.DataFrame(inventario_plantas)

    return inventario_plantas_df


def generar_reporte_transitos(problema: dict, variables: dict):

    transitos = dict()

    transitos['tipo'] = list()
    transitos['empresa_origen'] = list()
    transitos['ingrediente'] = list()
    transitos['puerto'] = list()
    transitos['barco'] = list()
    transitos['empresa_destino'] = list()
    transitos['planta'] = list()
    transitos['unidad'] = list()
    transitos['cantidad'] = list()
    transitos['costo_fijo'] = list()
    transitos['costo_variable'] = list()
    transitos['costo_intercompany'] = list()
    transitos['costo_total'] = list()
    transitos['periodo_despacho'] = list()
    transitos['periodo_llegada'] = list()

    for carga in problema['conjuntos']['cargas']:

        campos = carga.split('_')
        empresa_origen = campos[0]
        puerto = campos[1]
        barco = campos[2]
        ingrediente_origen = campos[3]

        for ua in problema['conjuntos']['unidades_almacenamiento']:

            campos_ua = ua.split('_')
            empresa_destino = campos_ua[0]
            planta = campos_ua[1]
            unidad = campos_ua[2]
            periodo = int(campos_ua[3])

            xtd_name = f'XTD_{carga}_{ua}'
            xtd_var = variables['XTD'][xtd_name]
            xtd_val = xtd_var.varValue

            cf_name = f'CF_{puerto}_{empresa_destino}_{planta}'
            cf_val = problema['parametros']['fletes_fijos'][cf_name]

            ct_name = f'CT_{puerto}_{empresa_destino}_{planta}'
            ct_val = problema['parametros']['fletes_variables'][ct_name]

            ci_name = f'CW_{empresa_origen}_{empresa_destino}'
            ci_value = problema['parametros']['costo_venta_intercompany'][ci_name]

            ct = cf_val + (ct_val + ci_value)*xtd_val

            transitos['tipo'].append('Barco->Planta')
            transitos['empresa_origen'].append(empresa_origen)
            transitos['puerto'].append(puerto)
            transitos['ingrediente'].append(ingrediente_origen)
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

            xtr_name = f'XTR_{carga}_{ua}'
            xtr_var = variables['XTR'][xtr_name]
            xtr_val = xtr_var.varValue

            cf_name = f'CF_{puerto}_{empresa_destino}_{planta}'
            cf_val = problema['parametros']['fletes_fijos'][cf_name]

            ct_name = f'CT_{puerto}_{empresa_destino}_{planta}'
            ct_val = problema['parametros']['fletes_variables'][ct_name]

            ci_name = f'CW_{empresa_origen}_{empresa_destino}'
            ci_value = problema['parametros']['costo_venta_intercompany'][ci_name]

            ct = cf_val + (ct_val + ci_value)*xtr_val

            transitos['tipo'].append('BodegaPuerto->Planta')
            transitos['empresa_origen'].append(empresa_origen)
            transitos['puerto'].append(puerto)
            transitos['ingrediente'].append(ingrediente_origen)
            transitos['barco'].append(barco)
            transitos['empresa_destino'].append(empresa_destino)
            transitos['planta'].append(planta)
            transitos['unidad'].append(unidad)
            transitos['cantidad'].append(xtr_val)
            transitos['costo_fijo'].append(cf_val)
            transitos['costo_variable'].append(ct_val)
            transitos['costo_intercompany'].append(ci_value)
            transitos['costo_total'].append(ct)
            transitos['periodo_despacho'].append(periodo)
            transitos['periodo_llegada'].append(periodo+2)

    transitos_df = pd.DataFrame(transitos)

    transitos_df = transitos_df[transitos_df['cantidad'] > 0]

    return transitos_df


def generar_reporte(problema: dict, variables: dict):

    print('guardando archivos')
    with pd.ExcelWriter('data.xlsx') as writer:

        print('guardar periodos')
        periodos_df = generar_periodos(problema=problema)
        periodos_df.to_excel(writer, sheet_name='periodos', index=False)

        print('guardar transitos')
        transitos_df = generar_reporte_transitos(
            problema=problema, variables=variables)
        transitos_df.to_excel(
            writer, sheet_name='tr_puerto_planta', index=False)

        print('guardar inventario_plantas')
        inventarios_plantas_df = generar_inventario_plantas(
            problema=problema, variables=variables)
        inventarios_plantas_df.to_excel(
            writer, sheet_name='inventario_plantas', index=False)

        print('guardar inventario_puertos')
        inventarios_puertos_df = generar_invenario_puerto(
            problema=problema, variables=variables)
        inventarios_puertos_df.to_excel(
            writer, sheet_name='inventario_puertos', index=False)

        print('listo')


def guardar_data(problema: dict, variables: dict):

    with open('diccionario_datos.json') as file:
        data = json.load(file)

    solucion = dict()

    # Variables
    with pd.ExcelWriter('solución.xlsx') as writer:
        for tipo, var_list in variables.items():

            data_dict = dict()
            data_dict['tipo'] = list()
            data_dict['nombre_variable'] = list()
            data_dict['valor'] = list()

            # print('guardando', tipo)
            for var_name, var_value in var_list.items():

                data_dict['tipo'].append(tipo)
                data_dict['nombre_variable'].append(var_name)
                data_dict['valor'].append(var_value.varValue)

            df = pd.DataFrame(data_dict)

            # df['slices'] = df['nombre_variable'].apply(
            #     lambda x: len(x.split('_')))

            columns = data[tipo]

            cont = 1
            for column in columns:

                # print('  ', 'trabajando con', column)

                df[column] = df['nombre_variable'].apply(
                    lambda x: x.split('_')[cont])
                cont += 1

            df.to_excel(writer, sheet_name=tipo, index=False)

            solucion[tipo] = df

        for tipo, var_list in problema['parametros'].items():

            data_dict = dict()
            data_dict['tipo'] = list()
            data_dict['nombre_variable'] = list()
            data_dict['valor'] = list()

            # print('guardando', tipo)
            for var_name, var_value in var_list.items():

                data_dict['tipo'].append(tipo)
                data_dict['nombre_variable'].append(var_name)
                data_dict['valor'].append(var_value)

            df = pd.DataFrame(data_dict)

            df['slices'] = df['nombre_variable'].apply(
                lambda x: len(x.split('_')))

            columns = data[tipo]

            cont = 1
            for column in columns:

                # print('  ', 'trabajando con', column)

                df[column] = df['nombre_variable'].apply(
                    lambda x: x.split('_')[cont])
                cont += 1

            df.to_excel(writer, sheet_name=tipo, index=False)

            solucion[tipo] = df

    return solucion
