import pulp as pu


def _balance_masa_bif(restricciones: dict, variables: dict, cargas: list, llegadas: dict, plantas: list, periodos: list):

    print('generando restricciones de balance de masa en bifurcación')
    # XPL + XTD = AR

    rest_list = list()

    for periodo in periodos:
        for carga in cargas:

            left_expesion = list()

            # XPL + sum(XTD) = AR
            ar_name = f'AR_{carga}_{periodo}'

            if ar_name in llegadas.keys():
                ar_val = llegadas[ar_name]
            else:
                ar_val = 0.0

            xpl_name = f'XPL_{carga}_{periodo}'
            xpl_var = variables['XPL'][xpl_name]

            left_expesion.append(xpl_var)

            for planta in plantas:

                xtd_name = f'XTD_{carga}_{planta}_{periodo}'
                xtd_var = variables['XTD'][xtd_name]

                left_expesion.append(xtd_var)

            rest_list.append((pu.lpSum(left_expesion) == ar_val,
                             f'balance bif_{carga}_{periodo}'))

    restricciones['balance_masa_bif'] = rest_list


def _balance_masa_bodega_puerto(restricciones: list, variables: list, cargas: list, plantas: list, inventario_inicial: dict, periodos=list):

    print('generando restricciones de balance de masa en almacenamiento de puerto')
    # XIP = XIPt-1 + XPL - sum(XTR)
    # XIP + sum(XTR) = XIPt-1 + XPL

    rest_list = list()

    for periodo in periodos:
        for carga in cargas:

            left_expresion = list()
            rigth_expresion = list()

            # XIP
            xip_current_name = f'XIP_{carga}_{periodo}'
            xip_current_var = variables['XIP'][xip_current_name]
            left_expresion.append(xip_current_var)

            # XIPt-1 / inventario inicial
            if periodo > 0:
                xip_anterior_name = f'XIP_{carga}_{periodo-1}'
                xip_anterior_var = variables['XIP'][xip_anterior_name]
                rigth_expresion.append(xip_anterior_var)
            else:
                ii_name = f'IP_{carga}'
                if ii_name in inventario_inicial.keys():
                    ii_value = inventario_inicial[ii_name]
                else:
                    ii_value = 0.0
                rigth_expresion.append(ii_value)

            # XPL
            xpl_name = f'XPL_{carga}_{periodo}'
            xpl_var = variables['XPL'][xpl_name]
            rigth_expresion.append(xpl_var)

            # sum(XTR)
            for planta in plantas:
                xtr_name = f'XTR_{carga}_{planta}_{periodo}'
                xtr_var = variables['XTR'][xtr_name]
                left_expresion.append(xtr_var)

            rest = (pu.lpSum(left_expresion) == pu.lpSum(
                rigth_expresion), f'balance de masa en {carga}_{periodo}')

            rest_list.append(rest)

    restricciones['Balance_masa_bodega_puerto'] = rest_list


def _balance_masa_planta(restricciones: list, variables: list, cargas: list, plantas: list, inventario_inicial: dict, ingredientes: list, periodos: list, consumo: list):

    print('generando restricciones de balance de masa en planta')
    # XIU = XIUt-1 + SUM(XTR) + SUM(XTD) + XBK - DM

    rest_list = list()

    for periodo in periodos:
        for ingrediente in ingredientes:
            for planta in plantas:

                left_expesion = list()
                rigth_expresion = list()

                # XIU
                xiu_name = f'XIU_{planta}_{ingrediente}_{periodo}'
                xiu_var = variables['XIU'][xiu_name]
                left_expesion.append(xiu_var)

                # XIUt-1 / inventario inicial
                if periodo > 0:
                    xiu_ant_name = f'XIU_{planta}_{ingrediente}_{periodo-1}'
                    xiu_ant_var = variables['XIU'][xiu_ant_name]
                    rigth_expresion.append(xiu_ant_var)
                else:
                    ii_name = f'II_{planta}_{ingrediente}'
                    ii_value = inventario_inicial[ii_name]
                    rigth_expresion.append(ii_value)

                # SUM(XTD)
                # SUM(XTR)
                for carga in cargas:

                    # ['empresa', 'operador',  'imp-motonave', 'ingrediente']
                    campos = carga.split('_')
                    c_empresa = campos[0]
                    c_operador = campos[1]
                    c_importacion = campos[2]
                    c_ingrediente = campos[3]

                    if ingrediente == c_ingrediente:

                        xtd_name = f'XTD_{carga}_{planta}_{periodo}'
                        xtd_var = variables['XTD'][xtd_name]
                        rigth_expresion.append(xtd_var)

                        xtr_name = f'XTR_{carga}_{planta}_{periodo}'
                        xtr_var = variables['XTR'][xtr_name]
                        rigth_expresion.append(xtr_var)

                # XBK
                xdm_name = f'XBK_{planta}_{ingrediente}_{periodo}'
                xdm_var = variables['XBK'][xdm_name]
                rigth_expresion.append(xdm_var)

                # DM
                dm_name = f'DM_{planta}_{ingrediente}_{periodo}'
                dm_value = consumo[dm_name]
                rigth_expresion.append(-1*dm_value)

                rest = (pu.lpSum(left_expesion) == pu.lpSum(
                    rigth_expresion), f'Balance masa de {ingrediente} en {planta} durante el periodo {periodo}')

                rest_list.append(rest)

    restricciones['Balance_masa_unidades'] = rest_list


def select_ua_by_period_planta(planta: str, period: int, unidades: list):
    list_to_return = list()

    for ua in unidades:
        campos = ua.split('_')
        ua_empresa = campos[0]
        ua_planta = campos[1]
        ua_codigo = campos[2]
        ua_periodo = int(campos[3])

        if planta == f'{ua_empresa}_{ua_planta}' and period == ua_periodo:
            list_to_return.append(ua)

    return list_to_return


def _mantenimiento_ss_plantas(restricciones: list, variables: list, plantas: list, ingredientes: list, periodos: list, safety_stock: dict):

    print('Generando restricciones de mantnimiento de safety stock en planta')

    # XIU >= SS * (1-BSS)
    # XIU >= SS - SS*BSS
    # XIU + SS*BSS >= SS

    rest_list = list()

    for ingrediente in ingredientes:
        for planta in plantas:
            for periodo in periodos:

                left_expesion = list()

                # XIU
                xiu_name = f'XIU_{planta}_{ingrediente}_{periodo}'
                xiu_var = variables['XIU'][xiu_name]
                left_expesion.append(xiu_var)

                # SS
                ss_name = f'SS_{planta}_{ingrediente}'
                ss_value = safety_stock[ss_name]

                # BSS
                bss_name = f'BSS_{planta}_{ingrediente}_{periodo}'
                bss_var = variables['BSS'][bss_name]
                left_expesion.append(ss_value*bss_var)

                rest = (pu.lpSum(left_expesion) >= ss_value,
                        f'safety_stock {ingrediente} en {planta} en {periodo}')

                rest_list.append(rest)

    restricciones['Safety stock en planta'] = rest_list


def _capacidad_camiones(restricciones: list, variables: list, periodos_en_firme=21):

    print('Restricciones de capacidad de carga de camiones')

    # XTD <= 34*ITD
    # XTR <= 34*ITR

    rest_list = list()

    for xtd_name, xtd_var in variables['XTD'].items():

        itd_name = xtd_name.replace('XTD', 'ITD')
        itd_var = variables['ITD'][itd_name]

        periodo = int(itd_name.split('_')[7])

        if periodo < periodos_en_firme:
            rest_list.append(
                (xtd_var == 34000*itd_var, f'capacidad carga directa {xtd_name}'))

    for xtr_name, xtr_var in variables['XTR'].items():

        itr_name = xtr_name.replace('XTR', 'ITR')
        itr_var = variables['ITR'][itr_name]

        periodo = int(itr_name.split('_')[7])

        if periodo < periodos_en_firme:
            rest_list.append(
                (xtr_var == 34000*itr_var, f'capacidad carga desde almacenamiento en {xtr_name}'))

    restricciones['Capacidad carga de camiones'] = rest_list


def _capacidad_almacenamiento_planta(restricciones: list, variables: dict, coeficientes_capacidad: dict, plantas: list, ingredientes: list, periodos: list):

    rest = list()

    # SUM(XPI)<=1.0

    for planta in plantas:
        for periodo in periodos:

            left_expresion = list()
            for ingrediente in ingredientes:

                xiu_name = f'XIU_{planta}_{ingrediente}_{periodo}'
                xiu_var = variables['XIU'][xiu_name]

                ci_name = f'CI_{planta}_{ingrediente}'

                if ci_name in coeficientes_capacidad:
                    # Traer el inverso de la capacidad de este ingrediente en esta planta
                    ci_value = coeficientes_capacidad[ci_name]
                    if ci_value > 0:
                        # evitar que el valor sea cero y convertirlo
                        ci_facc = 1/(ci_value)
                        left_expresion.append(ci_facc*xiu_var)

                        rest.append(
                            (xiu_var <= ci_value, f'no sobrepaso de capacidad de {ingrediente} en {planta} durante {periodo}'))

            # rest.append((pu.lpSum(left_expresion) <= 1.0,
            #              f'Capacidad usada con {ingrediente} en {planta} durante {periodo}'))

    restricciones['Capacidad plantas'] = rest


def generar_restricciones(restricciones: dict, conjuntos: dict, parametros: dict, variables: dict):

    periodos = conjuntos['periodos']
    plantas = conjuntos['plantas']
    consumo_proyectado = parametros['consumo_proyectado']
    ingredientes = conjuntos['ingredientes']
    inventario_inicial_cargas = parametros['inventario_inicial_cargas']
    llegadas = parametros['llegadas_cargas']
    capacidad_plantas = parametros['capacidad_almacenamiento_planta']
    cargas = conjuntos['cargas']
    inventario_inicial_ua = parametros['inventario_inicial_ua']
    safety_stock = parametros['safety_stock']

    _balance_masa_bif(restricciones=restricciones,
                      variables=variables,
                      cargas=cargas,
                      llegadas=llegadas,
                      plantas=plantas,
                      periodos=periodos)

    _balance_masa_bodega_puerto(restricciones=restricciones,
                                variables=variables,
                                plantas=plantas,
                                cargas=cargas,
                                inventario_inicial=inventario_inicial_cargas,
                                periodos=periodos)

    _capacidad_almacenamiento_planta(restricciones=restricciones,
                                     variables=variables,
                                     coeficientes_capacidad=capacidad_plantas,
                                     plantas=plantas,
                                     ingredientes=ingredientes,
                                     periodos=periodos)

    _mantenimiento_ss_plantas(restricciones=restricciones,
                              variables=variables,
                              ingredientes=ingredientes,
                              periodos=periodos,
                              plantas=plantas,
                              safety_stock=safety_stock)

    _capacidad_camiones(restricciones=restricciones,
                        variables=variables)

    # _asignacion_unidades_almacenamiento(
    #    restricciones=restricciones, variables=variables, unidades=unidades, ingredientes=ingredientes)

    _balance_masa_planta(restricciones=restricciones, variables=variables, cargas=cargas, plantas=plantas,
                         inventario_inicial=inventario_inicial_ua, ingredientes=ingredientes, periodos=periodos, consumo=consumo_proyectado)

    # _satisfaccion_demanda_plantas(restricciones=restricciones, variables=variables, plantas=plantas,
    #                              ingredientes=ingredientes, unidades=unidades, consumo_proyectado=consumo_proyectado, periodos=periodos)
