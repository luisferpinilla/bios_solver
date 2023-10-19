def _costos_almacenamiento_puerto(variables: dict, costos_almacenamiento: dict, valor_cif:dict, cargas: list, periodos: int):

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.
    # XIP_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo} : Cantidad de la carga $l$ en puerto al final del periodo $t$

    print('fob: Agregando costos de almacenamiento en puerto')

    fobj = list()
    for carga in cargas:
        for periodo in periodos:

            xip_name = f'XIP_{carga}_{periodo}'
            xip = variables['XIP'][xip_name]

            cc_name = f'CC_{carga}_{periodo}'
            coef_value = costos_almacenamiento[cc_name]

            cif_name = f'VC_{carga}'
            cif_value = valor_cif[cif_name]

            fobj.append(coef_value*cif_value*xip)

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

                itr_name = f'ITR_{carga}_{planta}_{periodo}'
                itr_var = variables['ITR'][itr_name]

                itd_name = f'ITD_{carga}_{planta}_{periodo}'
                itd_var = variables['ITD'][itd_name]

                # Costo variables por transporte entre operdor y planta
                cv_coef_name = f'CV_{operador}_{planta}_{ingrediente}'
                cv_coef_val = costo_transporte_variable[cv_coef_name]+int(periodo)
                fobj.append(34000*cv_coef_val*itr_var)
                fobj.append(34000*cv_coef_val*itd_var)

                # Costo fijos por transporte entre operador y planta
                cf_coef_name = f'CF_{operador}_{planta}_{ingrediente}'
                cf_coef_value = costo_transporte_fijos[cf_coef_name]
                fobj.append(cf_coef_value*itr_var)
                fobj.append(cf_coef_value*itd_var)

                # Costo intercompany y valor de la carga
                ci_iter_name = f"CW_{empresa_origen}_{empresa_destino}"
                ci_iter_val = costo_intercompany[ci_iter_name]
                vc_name = f"VC_{empresa_origen}_{operador}_{importacion}_{ingrediente}"
                vc_value = costo_carga[vc_name]
                fobj.append(34000*vc_value*ci_iter_val*itr_var)
                fobj.append(34000*vc_value*ci_iter_val*itd_var)

    return fobj



def _costo_exceder_capacidad_almacenamiento(conjuntos:dict, variables:dict, BigM:float):
    
    print('fobj: Agregando costo de penalidad por exceder capacidad almacenamiento')
    
    fobj = list()

    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:
            for periodo in conjuntos['periodos']:
                
                sal_name = f'SAL_{planta}_{ingrediente}_{periodo}'
                sal_var = variables['SAL'][sal_name]
            
                fobj.append((2*BigM - int(periodo))*sal_var)
                
    return fobj
    



def _costo_bakorder(conjuntos:dict, variables: dict, bigM:float):

    print('fob: Agregando costos de penalidad por backorder')

    fobj = list()
    
    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:
            for periodo in conjuntos['periodos']:
                
                xbk_name = f'SBK_{planta}_{ingrediente}_{periodo}'
                xbk_var = variables['SBK'][xbk_name]
    
                fobj.append((bigM - int(periodo))*xbk_var)
    

    return fobj


def _costo_safety_stock(conjuntos:dict, variables: dict, bigM:float):

    print('fob: Agregando costos de penalidad por Safety Stock')

    fobj = list()
    
    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:
            for periodo in conjuntos['periodos']:
                
                sss_name = f'SSS_{planta}_{ingrediente}_{periodo}'
                sss_var = variables['SSS'][sss_name]
                
                fobj.append((bigM/2-int(periodo))*sss_var)


    return fobj


def _costo_inventario_objetivo(conjuntos:dict, variables: dict, bigM:float):

    print('fob: Agregando costos de penalidad por Safety Stock')

    fobj = list()
    
    for planta in conjuntos['plantas']:
        for ingrediente in conjuntos['ingredientes']:
            for periodo in conjuntos['periodos']:
                
                btg_name = f'BTG_{planta}_{ingrediente}_{periodo}'
                btg_var = variables['BTG'][btg_name]
                
                fobj.append((bigM/3-periodo*10)*btg_var)


    return fobj


def generar_fob(fob: list, parametros: dict, conjuntos: dict, variables: dict):

    valor_cif_carga = parametros['valor_cif']
    costos_almacenamiento = parametros['costos_almacenamiento']
    costos_despacho_directo = parametros['costos_operacion_directo']
    costo_envio_bodega = parametros['costos_operacion_bodega']
    costo_intercompany = parametros['costo_venta_intercompany']
    costo_transporte_variable = parametros['fletes_variables']
    costo_transporte_fijos = parametros['fletes_fijos']
    periodos = conjuntos['periodos']
    cargas = conjuntos['cargas']
    plantas = conjuntos['plantas']
    # penalizacion_backorder = parametros['penalizacion_backorder']
    # penalizacion_exceder_almacenamiento = parametros['costo_penalizacion_capacidad_maxima']

    bigM = 10000

    # Almacenamiento en puerto por corte de Facturación:
    cap = _costos_almacenamiento_puerto(variables=variables,
                                        costos_almacenamiento=costos_almacenamiento,
                                        valor_cif=valor_cif_carga,
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
                           costo_carga=valor_cif_carga,
                           cargas=cargas,
                           plantas=plantas,
                           periodos=periodos)

    # Costo del backorder
    cbk = _costo_bakorder(conjuntos=conjuntos, 
                          variables=variables, 
                          bigM=bigM)
    
    # Costo de no respetar un inventario de seguridad de un ingrediente en una planta
    css = _costo_safety_stock(conjuntos=conjuntos, variables=variables, bigM=1000000)
    
    ctg = _costo_inventario_objetivo(conjuntos=conjuntos, variables=variables, bigM=1000000)

    # Costo de exceder las capacidades máximas de almacenamiento
    cal = _costo_exceder_capacidad_almacenamiento(conjuntos=conjuntos, 
                                                  variables=variables, 
                                                  BigM=bigM)

    ctotal = cap + cop + ct  + cal + ctg + cbk + css  

    for term in ctotal:
        fob.append(term)
