def _costos_almacenamiento_puerto(variables: dict, costos_almacenamiento: dict, cargas: list, periodos: int):

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.
    # XIP_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo} : Cantidad de la carga $l$ en puerto al final del periodo $t$

    fobj = list()
    for carga in cargas:
        for periodo in periodos:
            var_name = f'XIP_{carga}_{periodo}'
            var = variables['XIP'][var_name]

            coef_name = f'CC_{carga}_{periodo}'
            if coef_name in costos_almacenamiento.keys():

                coef_value = costos_almacenamiento[coef_name]

                fobj.append(coef_value*var)

    return fobj


def _costo_operacion_portuaria(variables: dict, costos_despacho_directo: dict, costo_envio_bodega: dict):

    # XTD * CD
    # XPL * CB

    fobj = list()

    'CB_{operador}_{ingrediente}'
    'XPL_{empresa}_{operador}_{importacion}_{ingrediente}_{periodo}'

    for name, var in variables['XPL'].items():

        operador = name.split('_')[2]
        ingrediente = name.split('_')[4]

        cb_name = f'CB_{operador}_{ingrediente}'
        cb_value = costo_envio_bodega[cb_name]

        fobj.append(cb_value*var)

    for name, var in variables['XTD'].items():

        operador = name.split('_')[2]
        ingrediente = name.split('_')[4]

        cd_name = f'CD_{operador}_{ingrediente}'
        cd_value = costos_despacho_directo[cd_name]

        fobj.append(cd_value*var)

    return fobj


def _costo_transporte(variables: dict, costos_transporte_variables: dict, costos_transporte_fijos: dict, costos_intercompany: dict, cargas: list, plantas: list, periodos: list):
    # $CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.
    # $XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$

    fobj = list()

    for periodo in periodos:
        for carga in cargas:
            campos = carga.split('_')
            empresa_origen = campos[0]
            operador = campos[1]
            importacion = campos[2]
            ingrediente = campos[3]

            puerto = carga.split('_')[2]
            for planta in plantas:

                xtr_name = f'XTR_{carga}_{planta}_{periodo}'
                xtr_var = variables['XTR'][xtr_name]

                xtd_name = f'XTD_{carga}_{planta}_{periodo}'
                xtd_var = variables['XTD'][xtd_name]

                ct_coef_name = f'CT_{operador}_{puerto}_{planta}_{ingrediente}'
                cw_iter_name = f"CW_{operador}_{puerto}_{planta}_{ingrediente}"

                if ct_coef_name in costos_transporte_variables.keys():

                    ct_coef_value = costos_transporte_variables[ct_coef_name]
                    ct_coef_value += costos_intercompany[cw_iter_name]

                    fobj.append(ct_coef_value*xtr_var)
                    fobj.append(ct_coef_value*xtd_var)

                # itr_name = f'ITR_{carga}_{planta}_{periodo}'
                # itr_var = variables['ITR'][itr_name]

                # itd_name = f'ITD_{carga}_{planta}_{periodo}'
                # itd_var = variables['ITD'][itd_name]

                # cf_coef_name = f'CF_{operador}_{puerto}_{planta}_{ingrediente}'

                # if cf_coef_name in costos_transporte_fijos.keys():
                #    cf_coef_value = costos_transporte_fijos[cf_coef_name]
                #    fobj.append(cf_coef_value*itr_var)
                #    fobj.append(cf_coef_value*itd_var)

    return fobj


def _costo_safety_stock(variables: dict):

    fobj = list()
    costo_bss = 1000
    for name, var in variables['BSS'].items():
        periodo = int(name.split('_')[4])
        fobj.append((costo_bss-periodo*10)*var)
        # fobj.append(costo_bss*var)

    return fobj


def _costo_bakorder(variables: dict):

    fobj = list()
    costo_xbk = 10000
    for name, var in variables['XBK'].items():
        periodo = int(name.split('_')[4])
        fobj.append((costo_xbk - periodo*10)*var)
        # fobj.append(costo_xbk*var)

    return fobj


def _costo_asignacion_ingrediente_unidad_almacenamiento(variables: dict):

    fobj = list()

    for name, var in variables['BIU'].items():
        fobj.append(1000*var)

    return fobj


def generar_fob(fob: list, parametros: dict, conjuntos: dict, variables: dict):

    costos_almacenamiento = parametros['costos_almacenamiento']
    costos_despacho_directo = parametros['costos_operacion_directo']
    costo_envio_bodega = parametros['costos_operacion_bodega']
    costos_intercompany = parametros['costo_venta_intercompany']
    costos_transporte_variable = parametros['fletes_variables']
    costos_transporte_fijos = parametros['fletes_fijos']
    periodos = conjuntos['periodos']
    cargas = conjuntos['cargas']
    plantas = conjuntos['plantas']

    # Almacenamiento en puerto por corte de Facturación:
    fob.append(_costos_almacenamiento_puerto(
        variables, costos_almacenamiento, cargas, periodos))

    # Costo de operacion portuaria
    fob.append(_costo_operacion_portuaria(variables=variables,
                                          costos_despacho_directo=costos_despacho_directo,
                                          costo_envio_bodega=costo_envio_bodega))

    # Costos por transporte
    fob.append(_costo_transporte(variables=variables,
                                 costos_transporte_variables=costos_transporte_variable,
                                 costos_transporte_fijos=costos_transporte_fijos,
                                 costos_intercompany=costos_intercompany,
                                 cargas=cargas,
                                 plantas=plantas,
                                 periodos=periodos))

    # Costo de no respetar un inventario de seguridad de un ingrediente en una planta
    fob.append(_costo_safety_stock(variables))

    # Costo de no satisfacer una demanda en una planta
    # fob.append(_costo_no_satisfaccion_demanda(variables))

    # Costo del backorder
    fob.append(_costo_bakorder(variables))

    # Costo por permitir guardar un ingrediente en una unidad de almacenamiento en una planta
    # fob.append(_costo_asignacion_ingrediente_unidad_almacenamiento(variables))
