import pulp as pu


def _costos_almacenamiento_puerto(variables: dict, costos_almacenamiento: dict, cargas: list, periodos: int):

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.
    # XIP_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo} : Cantidad de la carga $l$ en puerto al final del periodo $t$

    fobj = list()
    for carga in cargas:
        for periodo in range(periodos):
            var_name = f'XIP_{carga}_{periodo}'
            var = variables['XIP'][var_name]

            coef_name = f'CC_{carga}_{periodo}'
            if coef_name in costos_almacenamiento.keys():

                coef_value = costos_almacenamiento[coef_name]

                fobj.append(coef_value*var)

    return fobj


def _costo_transporte(variables: dict, costos_transporte_variables: dict, costos_transporte_fijos: dict, costos_intercompany: dict, cargas: list, unidades: list):
    # $CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.
    # $XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$

    fobj = list()

    for carga in cargas:
        empresa_origen = carga.split('_')[0]
        puerto = carga.split('_')[2]
        for unidad in unidades:
            empresa_destino = f"{unidad.split('_')[0]}_{unidad.split('_')[1]}"

            xtr_name = f'XTR_{carga}_{unidad}'
            xtr_var = variables['XTR'][xtr_name]

            xtd_name = f'XTD_{carga}_{unidad}'
            xtd_var = variables['XTD'][xtd_name]

            ct_coef_name = f'CT_{puerto}_{empresa_destino}'
            cw_iter_name = f"CW_{empresa_origen}_{empresa_destino.split('_')[0]}"

            if ct_coef_name in costos_transporte_variables.keys():

                ct_coef_value = costos_transporte_variables[ct_coef_name]
                ct_coef_value += costos_intercompany[cw_iter_name]

                fobj.append(ct_coef_value*xtr_var)
                fobj.append(ct_coef_value*xtd_var)

            itr_name = f'ITR_{carga}_{unidad}'
            itr_var = variables['ITR'][itr_name]

            itd_name = f'ITD_{carga}_{unidad}'
            itd_var = variables['ITD'][itd_name]

            cf_coef_name = f'CF_{puerto}_{empresa_destino}'

            if cf_coef_name in costos_transporte_fijos.keys():
                cf_coef_value = costos_transporte_fijos[cf_coef_name]
                fobj.append(cf_coef_value*itr_var)
                fobj.append(cf_coef_value*itd_var)

    return fobj


def _costo_safety_stock(variables: dict):

    fobj = list()
    costo_bss = 1000000
    for name, var in variables['BSS'].items():
        # fobj.append(costo_bss)
        fobj.append(costo_bss*var)

    return fobj


@DeprecationWarning
def _costo_no_satisfaccion_demanda(variables: dict):

    fobj = list()
    costo_ddm = 100000000
    for name, var in variables['BCD'].items():
        # fobj.append(costo_ddm)
        fobj.append(costo_ddm*var)

    return fobj


def _costo_bakorder(variables: dict):

    fobj = list()

    for name, var in variables['XBK'].items():
        fobj.append(1000000000*var)

    return fobj


def _costo_asignacion_ingrediente_unidad_almacenamiento(variables: dict):

    fobj = list()

    for name, var in variables['BIU'].items():
        fobj.append(1000*var)

    return fobj


def generar_fob(problema: dict, variables: dict):

    costos_almacenamiento = problema['parametros']['costos_almacenamiento']
    costos_intercompany = problema['parametros']['costo_venta_intercompany']
    costos_transporte_variable = problema['parametros']['fletes_variables']
    costos_transporte_fijos = problema['parametros']['fletes_fijos']
    periodos = problema['conjuntos']['periodos']
    cargas = problema['conjuntos']['cargas']
    unidades = problema['conjuntos']['unidades_almacenamiento']

    fob = list()

    # Almacenamiento en puerto por corte de Facturación:
    fob.append(_costos_almacenamiento_puerto(
        variables, costos_almacenamiento, cargas, periodos))

    # Costos por transporte
    fob.append(_costo_transporte(
        variables, costos_transporte_variable, costos_transporte_fijos, costos_intercompany, cargas, unidades))

    # Costo de no respetar un inventario de seguridad de un ingrediente en una planta
    fob.append(_costo_safety_stock(variables))

    # Costo de no satisfacer una demanda en una planta
    # fob.append(_costo_no_satisfaccion_demanda(variables))

    # Costo del backorder
    fob.append(_costo_bakorder(variables))

    # Costo por permitir guardar un ingrediente en una unidad de almacenamiento en una planta
    fob.append(_costo_asignacion_ingrediente_unidad_almacenamiento(variables))

    return pu.lpSum(fob)
