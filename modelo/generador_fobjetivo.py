def _costos_almacenamiento_puerto(variables: dict, costos_almacenamiento: dict, cargas: list, periodos: int):

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.
    # XIP_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo} : Cantidad de la carga $l$ en puerto al final del periodo $t$

    print('fob: Agregando costos de almacenamiento en puerto')

    fobj = list()
    for carga in cargas:
        for periodo in periodos:

            var_name = f'XIP_{carga}_{periodo}'
            var = variables['XIP'][var_name]

            coef_name = f'CC_{carga}_{periodo}'

            coef_value = costos_almacenamiento[coef_name]

            fobj.append(coef_value*var)

    return fobj


def _costo_operacion_portuaria(variables: dict, costos_despacho_directo: dict, costo_envio_bodega: dict):

    # XTD * CD
    # XPL * CB

    print('fob: Agregando costos de operacion portuaria')

    fobj = list()

    'CB_{operador}_{ingrediente}'
    'XPL_{empresa}_{operador}_{importacion}_{ingrediente}_{periodo}'

    for name, var in variables['XPL'].items():

        operador = name.split('_')[2]
        ingrediente = name.split('_')[4]

        cb_name = f'CB_{operador}_{ingrediente}'
        cb_value = costo_envio_bodega[cb_name]

        fobj.append(cb_value*var)

    for name, var in variables['ITD'].items():

        operador = name.split('_')[2]
        ingrediente = name.split('_')[4]

        cd_name = f'CD_{operador}_{ingrediente}'
        cd_value = 34000*costos_despacho_directo[cd_name]

        fobj.append(cd_value*var)

    return fobj


def _costo_transporte(variables: dict, costo_transporte_variable: dict, costo_transporte_fijos: dict, costo_intercompany: dict, costo_carga: dict, cargas: list, plantas: list, periodos: list):
    # $CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.
    # $XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$

    print('fob: Agregando costo de transporte e intercomany')

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

                empresa_destino = planta.split('_')[0]

                # xtr_name = f'XTR_{carga}_{planta}_{periodo}'
                # xtr_var = variables['XTR'][xtr_name]

                # xtd_name = f'XTD_{carga}_{planta}_{periodo}'
                # xtd_var = variables['XTD'][xtd_name]

                itr_name = f'ITR_{carga}_{planta}_{periodo}'
                itr_var = variables['ITR'][itr_name]

                itd_name = f'ITD_{carga}_{planta}_{periodo}'
                itd_var = variables['ITD'][itd_name]

                # Totalizar costos intercompany por kilo y variables
                # Costo variables por transporte entre operdor y planta
                cv_coef_name = f'CV_{operador}_{planta}_{ingrediente}'
                # Costo intercompany
                ci_iter_name = f"CW_{empresa_origen}_{empresa_destino}"
                # Valor de la carga
                cc_name = f"VC_{empresa_origen}_{operador}_{importacion}_{ingrediente}"
                cc_value = costo_carga[cc_name]

                ct_coef_value = costo_transporte_variable[cv_coef_name] + cc_value*(
                    1 + costo_intercompany[ci_iter_name])

                ct_coef_value += ct_coef_value*(periodo/10)

                fobj.append(34000*ct_coef_value*itr_var)
                fobj.append(34000*ct_coef_value*itd_var)

                cf_coef_name = f'CF_{operador}_{planta}_{ingrediente}'

                cf_coef_value = costo_transporte_fijos[cf_coef_name]
                fobj.append(cf_coef_value*itr_var)
                fobj.append(cf_coef_value*itd_var)

    return fobj


def _costo_safety_stock(variables: dict):

    print('fob: Agregando costos de penalidad por Safety Stock')

    fobj = list()
    costo_bss = 1000
    for name, var in variables['BSS'].items():
        periodo = int(name.split('_')[4])
        fobj.append((costo_bss-periodo*10)*var)
        # fobj.append(costo_bss*var)

    return fobj


def _costo_bakorder(variables: dict):

    print('fob: Agregando costos de penalidad por backorder')

    fobj = list()
    costo_xbk = 10000
    for name, var in variables['XBK'].items():
        periodo = int(name.split('_')[4])
        fobj.append((costo_xbk - periodo*10)*var)
        # fobj.append(costo_xbk*var)

    return fobj


def generar_fob(fob: list, parametros: dict, conjuntos: dict, variables: dict):

    costo_carga = parametros['valor_cif']
    costos_almacenamiento = parametros['costos_almacenamiento']
    costos_despacho_directo = parametros['costos_operacion_directo']
    costo_envio_bodega = parametros['costos_operacion_bodega']
    costo_intercompany = parametros['costo_venta_intercompany']
    costo_transporte_variable = parametros['fletes_variables']
    costo_transporte_fijos = parametros['fletes_fijos']
    periodos = conjuntos['periodos']
    cargas = conjuntos['cargas']
    plantas = conjuntos['plantas']

    # Almacenamiento en puerto por corte de Facturación:
    cap = _costos_almacenamiento_puerto(variables=variables,
                                        costos_almacenamiento=costos_almacenamiento,
                                        cargas=cargas,
                                        periodos=periodos)

    # Costo de operacion portuaria
    cop = _costo_operacion_portuaria(variables=variables,
                                     costos_despacho_directo=costos_despacho_directo,
                                     costo_envio_bodega=costo_envio_bodega)

    # Costos por transporte
    ct = _costo_transporte(variables=variables,
                           costo_transporte_variable=costo_transporte_variable,
                           costo_transporte_fijos=costo_transporte_fijos,
                           costo_intercompany=costo_intercompany,
                           costo_carga=costo_carga,
                           cargas=cargas,
                           plantas=plantas,
                           periodos=periodos)

    # Costo de no respetar un inventario de seguridad de un ingrediente en una planta
    css = _costo_safety_stock(variables)

    # Costo del backorder
    cbk = _costo_bakorder(variables)

    ctotal = cap + cop + ct + css + cbk

    for term in ctotal:
        fob.append(term)
