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
    # XIU = XIUt-1 + TT + SUM(XTR) + SUM(XTD) + SBK - DM

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
                sbk_name = f'SBK_{planta}_{ingrediente}_{periodo}'
                sbk_var = variables['SBK'][sbk_name]
                rigth_expresion.append(sbk_var)

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

    # XIU + SSS >= SS


    rest_list = list()

    for ingrediente in ingredientes:
        for planta in plantas:
            for periodo in periodos:

                # XIU
                xiu_name = f'XIU_{planta}_{ingrediente}_{periodo}'
                xiu_var = variables['XIU'][xiu_name]

                # SS
                ss_name = f'SS_{planta}_{ingrediente}'
                ss_value = safety_stock[ss_name]

                # SSS
                sss_name = f'SSS_{planta}_{ingrediente}_{periodo}'
                sss_var = variables['SSS'][sss_name]

                rest = (xiu_var + sss_var >= ss_value,
                        f'safety_stock {ingrediente} en {planta} en {periodo}')

                rest_list.append(rest)

    restricciones['Safety stock en planta'] = rest_list


def _inventario_objetivo_plantas(restricciones: list, variables: list, plantas: list, ingredientes: list, periodos: list, dio: dict, consumo_promedio:dict):

    print('rest: superar inventario objetivo en planta')

    # XIU + SIO >= consumoPromedio*dio

    rest_list = list()

    for ingrediente in ingredientes:
        for planta in plantas:
            periodo = periodos[-1]

            # XIU
            xiu_name = f'XIU_{planta}_{ingrediente}_{periodo}'
            xiu_var = variables['XIU'][xiu_name]

            # dio
            dio_name = f'{ingrediente}'
            dio_value = dio[dio_name]

            # Consumo promedio
            con_name = f"{planta.split('_')[1]}_{ingrediente}"
            con_value = consumo_promedio[con_name]

            # Lo que falta para llegar a inventario objetivo
            sio_name = f'SIO_{planta}_{ingrediente}_{periodo}'
            sio_var = variables['SIO'][sio_name]

            rest = (xiu_var + sio_var >= dio_value*con_value,
                    f'inventario objetivo {ingrediente} en {planta} en {periodo}')

            rest_list.append(rest)

    restricciones['Inventario Objetivo en planta'] = rest_list


def _capacidad_almacenamiento_planta(restricciones: list, 
                                     variables: dict, 
                                     capacidad_plantas_ingredientes: dict, 
                                     consumo_promedio:dict,
                                     plantas: list, 
                                     ingredientes: list, 
                                     max_cap_almacenamiento_planta: dict, 
                                     periodos: list):

    print('rest: capacidad de almacenamiento en planta')

    rest = list()

    # xiu - sal <= max(ci - cc,0)

    for planta in plantas:

        capacidad_maxima = max_cap_almacenamiento_planta[f'MX_{planta}']

        for periodo in periodos:

            left_expresion = list()

            for ingrediente in ingredientes:

                xiu_name = f'XIU_{planta}_{ingrediente}_{periodo}'
                xiu_var = variables['XIU'][xiu_name]

                sal_name = f'SAL_{planta}_{ingrediente}_{periodo}'
                sal_var = variables['SAL'][sal_name]

                ci_name = f'CI_{planta}_{ingrediente}'
                ci_value = capacidad_plantas_ingredientes[ci_name]

                cp_name = f'{planta}_{ingrediente}'
                cp_value = consumo_promedio[cp_name]

                rest.append(
                    (xiu_var - sal_var <= max(0.0, ci_value - cp_value), f'no sobrepaso de capacidad de {ingrediente} en {planta} durante {periodo}'))

                if ci_value > 0:
                    # evitar que el valor sea cero y convertirlo
                    ci_facc = capacidad_maxima/(ci_value)
                    left_expresion.append(ci_facc*xiu_var)

            #if len(left_expresion)>0:
                # Esta restriccion esta generando problemas
                # rest.append((pu.lpSum(left_expresion) <= capacidad_maxima + 1000000*bal_var,
                #              f'Capacidad usada total en {planta} durante {periodo}'))

    restricciones['Capacidad almacenamiento plantas'] = rest


def _tiempo_administrativo(restricciones:dict, variables:dict, conjuntos:dict, periodos_restringidos:[0]):

    rest_list = list()

    for carga in conjuntos['cargas']:
        for planta in conjuntos['plantas']:
            for periodo in periodos_restringidos:

                itr_name = f'xtr_{carga}_{planta}_{periodo}'
                itr_var = variables['ITR'][itr_name]
                rest = (itr_var == 0.0, f'No despacho directo de {carga} hacia {planta} en {periodo}')
                rest_list.append(rest)


                itd_name = f'itd_{carga}_{planta}_{periodo}'
                itd_var = variables['ITd'][itd_name]
                rest = (itd_var == 0.0, f'No despacho indirecto de {carga} hacia {planta} en {periodo}')
                rest_list.append(rest)

    restricciones['No despacho'] = rest_list


def generar_restricciones(restricciones: dict, conjuntos: dict, parametros: dict, variables: dict):

    periodos = conjuntos['periodos']
    plantas = conjuntos['plantas']
    consumo_proyectado = parametros['consumo_proyectado']
    consumo_promedio = parametros['Consumo_promedio']
    ingredientes = conjuntos['ingredientes']
    inventario_inicial_cargas = parametros['inventario_inicial_cargas']
    llegadas = parametros['llegadas_cargas']
    transitos = parametros['transitos_a_plantas']
    capacidad_plantas_ingredientes = parametros['capacidad_almacenamiento_planta']
    max_cap_almacenamiento_planta = parametros['capacidad_almacenamiento_maxima']
    cargas = conjuntos['cargas']
    inventario_inicial_ua = parametros['inventario_inicial_ua']
    safety_stock = parametros['safety_stock']
    
    dio = parametros['dio_objetivo']
    # costo_penalizacion_capacidad_planta = parametros['costo_penalizacion_capacidad_maxima']

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
                                     capacidad_plantas_ingredientes=capacidad_plantas_ingredientes,
                                     consumo_promedio=consumo_promedio,
                                     max_cap_almacenamiento_planta=max_cap_almacenamiento_planta,
                                     plantas=plantas,
                                     ingredientes=ingredientes,
                                     periodos=periodos)

    _mantenimiento_ss_plantas(restricciones=restricciones,
                              variables=variables,
                              ingredientes=ingredientes,
                              periodos=periodos,
                              plantas=plantas,
                              safety_stock=safety_stock)

    _inventario_objetivo_plantas(restricciones=restricciones,
                                 variables=variables,
                                 plantas=plantas,
                                 ingredientes=ingredientes,
                                 periodos=periodos,
                                 dio=dio,
                                 consumo_promedio=consumo_promedio)

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
    
    _tiempo_administrativo(restricciones=restricciones,
                           variables=variables,
                           conjuntos=conjuntos,
                           periodos_restringidos=['0'])

 