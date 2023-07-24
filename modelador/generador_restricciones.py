import pulp as pu

def _balance_masa_bif(restricciones: list, variables:list, llegadas: list, unidades:list):

    for llegada in llegadas:

        campos = llegada.split('_')
        empresa = campos[1]
        ingrediente = campos[2]
        puerto = campos[3]
        barco = campos[4]
        periodo = int(campos[5])

        # AR = XPL + XTD

        ar_name = f'AR_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}'

        ar_val = llegadas[ar_name]

        xpl_name = f'XPL_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}'
        xpl_var = variables[xpl_name]

        left_expesion = list()

        left_expesion.append(xpl_var)

        for ua in unidades:

            xtd_name = f'XTD_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}'
            xtd_var = variables[xtd_name]

            left_expesion.append(xtd_var)

        restricciones.append((pu.lpSum(left_expesion) == ar_val, f'balance bif_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}'))

def _satisfaccion_demanda_plantas(restricciones:list, variables:list):
    
    # sum(XDM) = DM * BCD
    
    pass

def _mantenimiento_ss_plantas(restricciones:list, variables:list):
    
    # sum(XDM) > SS * (1 - BSS)
    # sum(XDM) > SS - BSS*SS
    
    pass

def _capacidad_camiones():
    pass

def _capacidad_unidades_almacenamiento():
    pass



def generar_restricciones(parametros:list, variables:list):
    
    restricciones = list()
    
    empresas = parametros['conjuntos']['empresas']
    periodos = parametros['conjuntos']['periodos']
    ingredientes = parametros['conjuntos']['ingredientes']
    llegadas = parametros['parametros']['llegadas_cargas']
    unidades = parametros['conjuntos']['unidades_almacenamiento']
    
    ## Balance de masa en bif    
    _balance_masa_bif(restricciones, variables, llegadas, unidades)
    
    # Satisfaccion de la demanda en las plantas
    _satisfaccion_demanda_plantas(restricciones, variables)

    # Mantenimiento del nivel de seguridad de igredientes en plantas
    _mantenimiento_ss_plantas(restricciones, variables)

    # Capacidad de carga de los camiones
    _capacidad_camiones()
    
    # Capacidad de almacenamiento en unidades de almacenamiento
    _capacidad_unidades_almacenamiento()

    # Balances de masa de inventarios
    
    ## Balance de masa en cargas en puerto
   
    ## Balance de masa en unidades de almacenamiento por producto en planta

    # Asignación de uniades de almacenamiento a ingredientes
    
    return restricciones
    


