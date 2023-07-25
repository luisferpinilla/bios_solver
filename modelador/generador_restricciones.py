import pulp as pu

def _balance_masa_bif(restricciones: list, variables:list, llegadas: list, unidades:list):

    # AR = XPL + XTD
    
    restricciones['balance_masa_bif'] = list()

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

        restricciones['balance_masa_bif'].append((pu.lpSum(left_expesion) == ar_val, f'balance bif_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}'))

def _inventario_inicial_bodega_puerto(restricciones:list, variables:list, cargas:list, inventario_inicial:list):
    
    # XIP_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}
    
    restricciones['inventario_inicial_puerto'] = list()
    
    for carga in cargas:
       
        campos = carga.split('_')
        empresa = campos[0]
        ingrediente = campos[1]
        puerto = campos[2]
        barco = campos[3]
        
        xip_name = f'XIP_{empresa}_{ingrediente}_{puerto}_{barco}_{0}'
        
        if xip_name in variables:
            xip_var = variables[xip_name]
            ip_name = f'IP_{empresa}_{ingrediente}_{puerto}_{barco}'
            
            if ip_name in inventario_inicial:
                ip_val = inventario_inicial[ip_name]
            else:
                ip_val = 0.0
                
            print(ip_name,"==",ip_val)    
            rest = (xip_var == ip_val,f'inventario_inicial_puerto_{carga}')
            
            restricciones['inventario_inicial_puerto'].append(rest)


def _balance_masa_bodega_puerto(restricciones:list, variables:list, cargas:list, unidades:list):
    
    # XIP_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}
    # XPL_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}
    # XTR_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}
    
    # XIP_t-1 + XPL - sum(XTR) = XIP
    # XIP_t-1 + XPL - sum(XTR) - XIP = 0
    
    # carga: empresa_ingrediente_puerto_barco
    
    restricciones['balance_masa_bodega_puerto'] = list()
    
    for periodo in range(1,30):
        
        for carga in cargas:
            
            left_expesion = []
        
            campos = carga.split('_')
            empresa = campos[0]
            ingrediente = campos[1]
            puerto = campos[2]
            barco = campos[3]
            
            xip_anterior_name = f'XPL_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo-1}'
            if xip_anterior_name in variables.keys():
                xip_anterior_var = variables[xip_anterior_name]
                left_expesion.append(xip_anterior_var)
            
            xip_actual_name = f'XPL_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo-1}'
            if xip_actual_name in variables.keys():
                xip_actual_var = variables[xip_actual_name]
                left_expesion.append(xip_actual_var)
            
            xpl_name = f'XPL_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo-1}'            
            if xpl_name in variables.keys():
                xpl_name_var = variables[xpl_name]
                left_expesion.append(xpl_name_var)

            
            for ua in unidades:
                xtr_name = f'XTR_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}'
                if xtr_name in variables.keys():
                    xtr_var = variables[xtr_name]
                    left_expesion.append(-1*xtr_var)
            
            restricciones['balance_masa_bodega_puerto'].append((pu.lpSum(left_expesion) == 0, f'balance_masa_{carga}_{periodo}'))


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
    
    restricciones = dict()
    
    # empresas = parametros['conjuntos']['empresas']
    # periodos = parametros['conjuntos']['periodos']
    # ingredientes = parametros['conjuntos']['ingredientes']
    inventario_inicial = parametros['parametros']['inventario_inicial_cargas']
    llegadas = parametros['parametros']['llegadas_cargas']
    unidades = parametros['conjuntos']['unidades_almacenamiento']
    cargas = parametros['conjuntos']['cargas']
    
    ## Balance de masa en bif    
    _balance_masa_bif(restricciones, variables, llegadas, unidades)
    
    ## Inventario inicial puerto
    _inventario_inicial_bodega_puerto(restricciones, variables, cargas, inventario_inicial)
    
    ## Balance de masa en Bodega puerto
    _balance_masa_bodega_puerto(restricciones,variables,cargas, unidades)
    
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
    


