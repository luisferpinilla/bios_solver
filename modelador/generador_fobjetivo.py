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




def generar_fob(parametros:dict, variables:dict):

    costos_almacenamiento = parametros['parametros']['costos_almacenamiento']
    periodos = parametros['periodos']
    cargas = parametros['conjuntos']['cargas']


    fob = list()

    # Costos por almacenamiento

    ## Almacenamiento en puerto por corte de Facturación:
    fob.append(_costos_almacenamiento_puerto(variables, costos_almacenamiento, cargas, periodos))

    # Costos por transporte

    ## Costo variable de transportar cargas desde puertos hacia plantas

    ## Costo fijo de transportar un camion desde puerto hacia plantas

    # Costos por Penalización

    ## Costo de no respetar un inventario de seguridad de un ingrediente en una planta

    ## Costo de no satisfacer una demanda en una planta

    ## Costo por permitir guardar un ingrediente en una unidad de almacenamiento en una planta
    
    return pu.lpSum(fob)