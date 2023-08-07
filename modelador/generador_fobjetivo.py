import pulp as pu


def _costos_almacenamiento_puerto(variables:dict, costos_almacenamiento:dict, cargas:list, periodos:int):
    
    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.
    # XIP_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo} : Cantidad de la carga $l$ en puerto al final del periodo $t$
    
    fobj = list()
    for periodo in range(periodos):
        for carga in cargas:
            var_name = f'XIP_{carga}_{periodo}'
            var = variables['XIP'][var_name]
            
            coef_name = f'CC_{carga}_{periodo}'
            if coef_name in costos_almacenamiento.keys():
                
                coef_value = costos_almacenamiento[coef_name]
            
                fobj.append(coef_value*var)
    
    return fobj


def _costo_variable_transporte(variables:dict, costos_transporte:dict, cargas:list, unidades:list, periodos:int):
    # $CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.
    # $XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$
    
    fobj = list()
    for periodo in range(periodos):
        for carga in cargas:
            for unidad in unidades:
                
                campos = carga.split('_')
                empresa_origen = campos[0]
                ingrediente = campos[1]
                puerto = campos[2]
                barco = campos[3]
                
                campos = unidad.split('_')
                empresa_destino = campos[0]
                planta = campos[1]
                unidad_detino = campos[2]
            
                var_name = f'XTR_{carga}_{unidad}_{ingrediente}_{periodo}'
                var = variables['XTR'][var_name]
                coef_name = f'CT_{puerto}_{empresa_destino}_{planta}'
                
                if coef_name in costos_transporte.keys():
                    coef_value = costos_transporte[coef_name]                
                    fobj.append(coef_value*var)
    
    return fobj    
    
    


def generar_fob(parametros:dict, variables:dict):

    costos_almacenamiento = parametros['parametros']['costos_almacenamiento']
    costos_transporte = parametros['parametros']['fletes_variables']
    periodos = parametros['periodos']
    cargas = parametros['conjuntos']['cargas']
    unidades = parametros['conjuntos']['unidades_almacenamiento']


    fob = list()

    # Costos por almacenamiento

    ## Almacenamiento en puerto por corte de Facturación:
    fob.append(_costos_almacenamiento_puerto(variables, costos_almacenamiento, cargas, periodos))

    # Costos por transporte

    ## Costo variable de transportar cargas desde puertos hacia plantas
    fob.append(_costo_variable_transporte(variables, costos_transporte, cargas, unidades, periodos))

    ## Costo fijo de transportar un camion desde puerto hacia plantas

    # Costos por Penalización

    ## Costo de no respetar un inventario de seguridad de un ingrediente en una planta

    ## Costo de no satisfacer una demanda en una planta

    ## Costo por permitir guardar un ingrediente en una unidad de almacenamiento en una planta
    
    return pu.lpSum(fob)