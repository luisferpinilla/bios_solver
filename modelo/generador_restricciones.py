import pulp as pu


def _balance_masa_bif(restricciones: dict, variables: dict, cargas: list, llegadas: dict, plantas: list, periodos: list):

    print('rest: balance de masa en bifurcación')
    # XPL + XTD = AR (obsolete)
    # XPL +34000*ITD = AR

    rest_list = list()

    for periodo in periodos:
        for carga in cargas:

            left_expesion = list()

            # XPL + sum(XTD) = AR
            ar_name = f'AR_{carga}_{periodo}'
            ar_val = llegadas[ar_name]

            xpl_name = f'XPL_{carga}_{periodo}'
            xpl_var = variables['XPL'][xpl_name]

            left_expesion.append(xpl_var)

            for planta in plantas:

                itd_name = f'ITD_{carga}_{planta}_{periodo}'
                itd_var = variables['ITD'][itd_name]

                left_expesion.append(34000*itd_var)

            rest_list.append((pu.lpSum(left_expesion) == ar_val,
                             f'balance bif_{carga}_{periodo}'))

    restricciones['balance_masa_bif'] = rest_list


def _balance_masa_bodega_puerto(restricciones: list, variables: list, cargas: list, plantas: list, inventario_inicial: dict, periodos=list):

    print('rest: balance de masa en almacenamiento de puerto')
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
                itr_name = f'ITR_{carga}_{planta}_{periodo}'
                itr_var = variables['ITR'][itr_name]
                left_expresion.append(34000*itr_var)

            rest = (pu.lpSum(left_expresion) == pu.lpSum(
                rigth_expresion), f'balance de masa en {carga}_{periodo}')

            rest_list.append(rest)

    restricciones['Balance_masa_bodega_puerto'] = rest_list


def _balance_masa_planta(restricciones: list, variables: list, cargas: list, plantas: list, inventario_inicial: dict, transitos_a_planta: dict, ingredientes: list, periodos: list, consumo: list):

    print('rest: balance de masa en planta')
    # XIU = XIUt-1 + TT + SUM(XTR) + SUM(XTD) + XBK - DM

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

                # TT: transitos a plantas
                tt_name = f'TT_{planta}_{ingrediente}_{periodo}'
                tt_value = transitos_a_planta[tt_name]
                rigth_expresion.append(tt_value)

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

                        xad_name = f'XAD_{carga}_{planta}_{periodo}'
                        xad_var = variables['XAD'][xad_name]
                        rigth_expresion.append(xad_var)

                        xar_name = f'XAR_{carga}_{planta}_{periodo}'
                        xar_var = variables['XAR'][xar_name]
                        rigth_expresion.append(xar_var)

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


def _tiempo_transitos(restricciones: list, variables: list, cargas: list, plantas: list, periodos: list):
    # Cargas => ['empresa', 'operador',  'imp-motonave', 'ingrediente']
    # Plantas => x['empresa', 'planta']
    # variables de despacho directo

    print('rest: sobre tiempo de tránsitos')

    rest_list = list()

    for name_var_despacho, var_despacho in variables['ITD'].items():
        campos = name_var_despacho.split('_')
        empresa_origen = campos[1]
        operador = campos[2]
        importacion = campos[3]
        ingrediente = campos[4]
        empresa_destino = campos[5]
        planta = campos[6]
        periodo = int(campos[7])

        if not periodo in periodos[-2:]:
            name_recibo_2 = f'XAD_{empresa_origen}_{operador}_{importacion}_{ingrediente}_{empresa_destino}_{planta}_{periodo+2}'
            var_recibo_2 = variables['XAD'][name_recibo_2]
            rest = (34000*var_despacho == var_recibo_2,
                    f'Transitos directos {name_var_despacho} y {name_recibo_2}')
            rest_list.append(rest)

        if periodo in periodos[-2:]:
            rest_list.append(
                (var_despacho == 0, f'No fuga puerto por {var_despacho} directo'))

        if periodo < 2:

            name_recibo = f'XAD_{empresa_origen}_{operador}_{importacion}_{ingrediente}_{empresa_destino}_{planta}_{periodo}'
            var_recibo = variables['XAD'][name_recibo]
            rest_list.append(
                (var_recibo == 0.0, f'No fuga planta por {var_recibo} directo'))

        restricciones['Tiempo Transporte Directo'] = rest_list

    rest_list = list()

    for name_var_despacho, var_despacho in variables['ITR'].items():
        campos = name_var_despacho.split('_')
        empresa_origen = campos[1]
        operador = campos[2]
        importacion = campos[3]
        ingrediente = campos[4]
        empresa_destino = campos[5]
        planta = campos[6]
        periodo = int(campos[7])

        if not periodo in periodos[-2:]:
            name_recibo_2 = f'XAR_{empresa_origen}_{operador}_{importacion}_{ingrediente}_{empresa_destino}_{planta}_{periodo+2}'
            var_recibo_2 = variables['XAR'][name_recibo_2]
            rest = (34000*var_despacho == var_recibo_2,
                    f'Transitos bodega {name_var_despacho} y {name_recibo_2}')
            rest_list.append(rest)

        if periodo in periodos[-2:]:
            rest_list.append(
                (var_despacho == 0, f'No fuga puerto por {var_despacho} bodega'))

        if periodo < 2:

            name_recibo = f'XAR_{empresa_origen}_{operador}_{importacion}_{ingrediente}_{empresa_destino}_{planta}_{periodo}'
            var_recibo = variables['XAR'][name_recibo]
            rest_list.append(
                (var_recibo == 0.0, f'No fuga planta por {var_recibo} bodega'))

        restricciones['Tiempo Transporte Desde Bodega'] = rest_list


def _mantenimiento_ss_plantas(restricciones: list, variables: list, plantas: list, ingredientes: list, periodos: list, safety_stock: dict):

    print('rest: mantnimiento de safety stock en planta')

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


def _capacidad_camiones(restricciones: list, variables: list, periodos_en_firme=45, gap=0.0):

    print('rest: capacidad de carga de camiones')

    # XTD <= 34*ITD
    # XTR <= 34*ITR

    rest_list = list()

    for xtd_name, xtd_var in variables['XTD'].items():

        itd_name = xtd_name.replace('XTD', 'ITD')
        itd_var = variables['ITD'][itd_name]

        rest_list.append(
            (xtd_var == 34000*itd_var, f'capacidad carga directa {xtd_name}'))

    for xtr_name, xtr_var in variables['XTR'].items():

        itr_name = xtr_name.replace('XTR', 'ITR')
        itr_var = variables['ITR'][itr_name]

        rest_list.append((xtr_var == 34000*itr_var,
                         f'capacidad carga desde almacenamiento en {xtr_name}'))

    restricciones['Capacidad carga de camiones'] = rest_list


def _capacidad_almacenamiento_planta(restricciones: list, variables: dict, coeficientes_capacidad: dict, plantas: list, ingredientes: list, max_cap: dict, periodos: list):

    print('rest: capacidad de almacenamiento en planta')

    rest = list()

    # SUM(XPI)<=1.0

    for planta in plantas:

        capacidad_maxima = max_cap[f'MX_{planta}']

        for periodo in periodos:

            left_expresion = list()

            for ingrediente in ingredientes:

                xiu_name = f'XIU_{planta}_{ingrediente}_{periodo}'
                xiu_var = variables['XIU'][xiu_name]

                ci_name = f'CI_{planta}_{ingrediente}'
                ci_value = coeficientes_capacidad[ci_name]

                rest.append(
                    (xiu_var <= ci_value, f'no sobrepaso de capacidad de {ingrediente} en {planta} durante {periodo}'))

                if ci_value > 0:
                    # evitar que el valor sea cero y convertirlo
                    ci_facc = capacidad_maxima/(ci_value)
                    left_expresion.append(ci_facc*xiu_var)

            # Esta restriccion esta generando problemas
            # rest.append((pu.lpSum(left_expresion) <= capacidad_maxima,
            #            f'Capacidad usada con {ingrediente} en {planta} durante {periodo}'))

    restricciones['Capacidad plantas'] = rest


def generar_restricciones(restricciones: dict, conjuntos: dict, parametros: dict, variables: dict, use_rest_cap_planta=True):

    periodos = conjuntos['periodos']
    plantas = conjuntos['plantas']
    consumo_proyectado = parametros['consumo_proyectado']
    ingredientes = conjuntos['ingredientes']
    inventario_inicial_cargas = parametros['inventario_inicial_cargas']
    llegadas = parametros['llegadas_cargas']
    transitos = parametros['transitos_a_plantas']
    capacidad_plantas = parametros['capacidad_almacenamiento_planta']
    cargas = conjuntos['cargas']
    inventario_inicial_ua = parametros['inventario_inicial_ua']
    safety_stock = parametros['safety_stock']
    max_cap = parametros['capacidad_almacenamiento_maxima']

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

    if use_rest_cap_planta:
        _capacidad_almacenamiento_planta(restricciones=restricciones,
                                         variables=variables,
                                         coeficientes_capacidad=capacidad_plantas,
                                         max_cap=max_cap,
                                         plantas=plantas,
                                         ingredientes=ingredientes,
                                         periodos=periodos)

    _mantenimiento_ss_plantas(restricciones=restricciones,
                              variables=variables,
                              ingredientes=ingredientes,
                              periodos=periodos,
                              plantas=plantas,
                              safety_stock=safety_stock)

    #_capacidad_camiones(restricciones=restricciones,
    #                    variables=variables)

    # _asignacion_unidades_almacenamiento(
    #    restricciones=restricciones, variables=variables, unidades=unidades, ingredientes=ingredientes)

    _tiempo_transitos(restricciones=restricciones,
                      variables=variables,
                      cargas=cargas,
                      plantas=plantas,
                      periodos=periodos)

    _balance_masa_planta(restricciones=restricciones,
                         variables=variables,
                         cargas=cargas,
                         plantas=plantas,
                         inventario_inicial=inventario_inicial_ua,
                         transitos_a_planta=transitos,
                         ingredientes=ingredientes,
                         periodos=periodos,
                         consumo=consumo_proyectado)

    # _satisfaccion_demanda_plantas(restricciones=restricciones, variables=variables, plantas=plantas,
    #                              ingredientes=ingredientes, unidades=unidades, consumo_proyectado=consumo_proyectado, periodos=periodos)
