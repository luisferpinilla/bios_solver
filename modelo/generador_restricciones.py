import pulp as pu


def _balance_masa_bif(restricciones: dict, variables: dict, cargas: list, llegadas: dict, plantas: list, periodos: list):

    print('generando restricciones de balance de masa en bifurcación')
    # AR = XPL + XTD

    rest_list = list()

    for periodo in periodos:
        for carga in cargas:

            # AR = XPL + sum(XTD)
            ar_name = f'AR_{carga}_{periodo}'

            if ar_name in llegadas.keys():
                ar_val = llegadas[ar_name]
            else:
                ar_val = 0.0

            xpl_name = f'XPL_{carga}_{periodo}'
            xpl_var = variables['XPL'][xpl_name]

            left_expesion = list()

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
    # XIU + DM = XIUt-1 + SUM(XTR) + SUM(XTD) + XBK

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

                # DM
                dm_name = f'DM_{planta}_{ingrediente}_{periodo}'
                dm_value = consumo[dm_name]
                left_expesion.append(dm_value)

                # XIUt-1 / inventario inicial
                if periodo > 0:
                    xiu_ant_name = f'XIU_{planta}_{ingrediente}_{periodo-1}'
                    xiu_ant_var = variables['XIU'][xiu_ant_name]
                    rigth_expresion.append(xiu_ant_var)
                else:
                    ii_name = f'II_{planta}_{ingrediente}'
                    if ii_name in inventario_inicial.keys():
                        ii_value = inventario_inicial[ii_name]
                    else:
                        ii_value = 0.0
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

                rest = (pu.lpSum(left_expesion) == pu.lpSum(
                    rigth_expresion), f'Balance masa de {ingrediente} en {planta} durante el periodo {periodo}')

                rest_list.append(rest)

    restricciones['Balance_masa_unidades'] = rest_list

    pass


@DeprecationWarning
def _satisfaccion_demanda_plantas(restricciones: list, variables: list, plantas: list, ingredientes: list, consumo_proyectado: list, periodos=list):

    print('generando restricciones de demanda en planta')

    # (1) SUM(XDM) + XBK == DM

    rest_list = list()

    for periodo in periodos:
        for ingrediente in ingredientes:
            for planta in plantas:

                campos = planta.split('_')
                c_empresa = campos[0]
                c_planta = campos[1]

                left_expesion = list()

                # DM
                dm_name = f'DM_{planta}_{ingrediente}_{periodo}'
                if dm_name in consumo_proyectado.keys():
                    dm_value = consumo_proyectado[dm_name]
                else:
                    dm_value = 0.0

                # $XBK_{ik}^{t}$: Cantidad de backorder del ingrediente $i$ en planta $k$ luego de no cumplir la demanda  del día $t$.
                xbk_name = f'XBK_{planta}_{ingrediente}_{periodo}'
                xbk_var = variables['XBK'][xbk_name]

                # $BCD_{ik}^{t}$ : Binaria, si estará permitido que la demanda de un ingrediente $i$ no se satisfaga en la planta $k$ al final del día $t$
                # bdc_name = f'BCD_{ingrediente}_{planta}_{periodo}'
                # bdc_var = variables['BCD'][bdc_name]

                # SUM(XDM)
                for unidad in unidades:

                    campos = unidad.split('_')
                    u_empresa = campos[0]
                    u_planta = campos[1]
                    U_codigo = campos[2]
                    u_periodo = int(campos[3])

                    if c_empresa == u_empresa and c_planta == u_planta and u_periodo == periodo:
                        xdm_name = f'XDM_{ingrediente}_{unidad}'
                        xdm_var = variables['XDM'][xdm_name]
                        left_expesion.append(xdm_var)

                left_expesion.append(xbk_var)

                rest = (pu.lpSum(left_expesion) == dm_value,
                        f'Minimizar backorder en {planta} de {ingrediente} en {periodo}')

                rest_list.append(rest)

    restricciones['minimizar backorder'] = rest_list


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


def _capacidad_camiones(restricciones: list, variables: list, cargas: list, unidades: list, periodos=30):

    print('Restricciones de capacidad de carga de camiones')

    # XTD <= 34*ITD
    # XTR <= 34*ITR

    rest_list = list()

    for xtd_name, xtd_var in variables['XTD'].items():

        itd_name = xtd_name.replace('XTD', 'ITD')
        itd_var = variables['ITD'][itd_name]

        rest_list.append(
            (xtd_var <= 34000*itd_var, f'capacidad carga directa {xtd_name}'))

    for xtr_name, xtr_var in variables['XTR'].items():

        itr_name = xtr_name.replace('XTR', 'ITR')
        itr_var = variables['ITR'][itr_name]

        rest_list.append(
            (xtr_var <= 34000*itr_var, f'capacidad carga desde almacenamiento en {xtr_name}'))

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
                        ci_value = 1/(ci_value*0.8)
                        left_expresion.append(ci_value*xiu_var)

                        rest.append((pu.lpSum(left_expresion) <= 1.0,
                                     f'Capacidad usada con {ingrediente} en {planta} durante {periodo}'))

    restricciones['Capacidad plantas'] = rest


@DeprecationWarning
def _capacidad_almacenamiento_unidad_almacenamiento(restricciones: list, variables: dict, plantas: list, ingredientes: list, capacidad_unidades: dict, periodos=30):

    # Se requiere usar la siguiente restriccion de capacidad máxima:

    # Parametro CapacidadTotal = suma de todas las capacidades
    # Variables de decisión con restricciones X <= FraccionIngrediente * CapacidadTotal
    # Suma de X sobre ingrediente <= 1 Para toda planta

    print('Generando restriccion de no sobrepaso de capacidad de unidades de almacenamiento')
    rest_list = list()

    for periodo in periodos:
        for ingrediente in ingredientes:
            for planta in plantas:

                xiu_name = f'XIU_{planta}_{ingrediente}_{periodo}'
                xiu_var = variables['XIU'][xiu_name]

                biu_name = f'BIU_{planta}_{ingrediente}_{periodo}'
                biu_var = variables['BIU'][biu_name]

                cap_name = f'CA_{ingrediente}_{planta}_{ingrediente}_{periodo}'

                if cap_name in capacidad_unidades.keys():
                    cap_val = capacidad_unidades[cap_name]
                else:
                    cap_val = 0.0

                rest_list.append((xiu_var <= cap_val*biu_var,
                                  f'capacidad de almacenamiento para {ingrediente} en {planta} durante {periodo}'))

    restricciones['Capacidad_almacenamiento_UA'] = rest_list


@DeprecationWarning
def _asignacion_unidades_almacenamiento(restricciones: list, variables: list, unidades: list, ingredientes: list):

    print('Generando restricciones sobre asignaciòn de unidades de almacenamiento')
    # no se puede asignar más de un ingrediente a una unidad

    # SUM(BIU, ingrediente,planta, periodo) <= 1

    rest_list = list()

    for unidad in unidades:

        left_expesion = list()

        for ingrediente in ingredientes:

            biu_name = f'BIU_{ingrediente}_{unidad}'

            biu_var = variables['BIU'][biu_name]

            left_expesion.append(biu_var)

        rest = (pu.lpSum(left_expesion) <= 1,
                f'asignacion unica sobre unidad {unidad}')

        rest_list.append(rest)

    restricciones['Asignacion unica de ingredientes a unidades'] = rest_list


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

    # _capacidad_camiones(restricciones=restricciones,
    #                    variables=variables, cargas=cargas, unidades=unidades)

    # _asignacion_unidades_almacenamiento(
    #    restricciones=restricciones, variables=variables, unidades=unidades, ingredientes=ingredientes)

    _balance_masa_planta(restricciones=restricciones, variables=variables, cargas=cargas, plantas=plantas,
                         inventario_inicial=inventario_inicial_ua, ingredientes=ingredientes, periodos=periodos, consumo=consumo_proyectado)

    # _satisfaccion_demanda_plantas(restricciones=restricciones, variables=variables, plantas=plantas,
    #                              ingredientes=ingredientes, unidades=unidades, consumo_proyectado=consumo_proyectado, periodos=periodos)
