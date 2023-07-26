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
                
            # print(ip_name,"==",ip_val)    
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


def _satisfaccion_demanda_plantas(restricciones:list, variables:list, plantas:list, ingredientes:list, unidades:list, consumo_proyectado:list):
    
    # sum(XDM) = DM * (1 -BCD)
    # sum(XDM) = DM - DM*BCD)
    # sum(XDM) + DM*BCD = DM
    
    
    # XDM_{empresa}_{planta}_{unidad}_{ingrediente}_{periodo}
    # DM_{empresa}_{planta}_{ingrediente}_{periodo}
    
    restricciones['Satisfaccion_demanda'] = list()

    for planta in plantas:    
        for ingrediente in ingredientes:
            for periodo in range(30):
            
                left_expesion = list()
                
                dm_name = f'DM_{planta}_{ingrediente}_{periodo}'
                if dm_name in consumo_proyectado.keys():
                    dm_value = consumo_proyectado[dm_name]
                else:
                    dm_value = 0.0
                
                for ua in unidades:
                    
                    campos = ua.split('_')
                    empresa = campos[0]
                    planta_ua = campos[1]
                    unidad = campos[2]
            
                    if planta == planta_ua:
    
                        xdm_name = f'XDM_{empresa}_{planta}_{unidad}_{ingrediente}_{periodo}'
                        xdm_var = variables[xdm_name]
                        
                        left_expesion.append(xdm_var)
                
                rest = (pu.lpSum(left_expesion)==dm_value, f'satisfacción_demanda_{dm_name}') 
                
                restricciones['Satisfaccion_demanda'].append(rest)            


def _balance_masa_ua(restricciones:list, variables:list, ingredientes:list, cargas:list, unidades:list, inventario_inicial:dict()):
    
    # XIU = XIU_t-1 + TR + XDT_t-2 + XTR_t-2 - XDM
    # XIU - XIU_t-1      - XTD_t-2 - XTR_t-2 + XDM = TR
    
    # XIU_{empresa}_{planta}_{unidad}_{ingrediente}_{periodo}'
    # XDM_{empresa}_{planta}_{unidad}_{ingrediente}_{periodo}
    # 
    
    restricciones['balance_masa_inventario'] = list()
    
    
    
    for periodo in range (30):
        for ingrediente in ingredientes:
            for ua in unidades:            
                
                left_expesion = list()
                right_value = 0.0
                
                campos = ua.split('_')
                empresa = campos[0]
                planta = campos[1]
                unidad = campos[2]
                
                
                # XIU_t-1 o II traer el inventario al final del periodo anterior
                # si no estamos en el periodo inicial
                if periodo > 0:
                    # traer variable de inventario final
                    xiu_ant_name = f'XIU_{empresa}_{planta}_{unidad}_{ingrediente}_{periodo}'
                    xiu_ant_var = variables[xiu_ant_name]
                    left_expesion.append(-1*xiu_ant_var)
                    
                else:
                    # traer el inventario inicial desde los parámetros
                    ii_name = f'II_{empresa}_{planta}_{unidad}_{ingrediente}'
                    if ii_name in inventario_inicial.keys():
                        ii_value = inventario_inicial[ii_name] 
                    else:
                        ii_value = 0.0
                    
                    right_value = right_value + ii_value
                
                # XTD despachos directos desde barco
                # XTR despachos desde bodega puerto
                if periodo >=2:
                    # agregar el despacho directo si lo hay
                    for carga in cargas:
                        xtd_name = f'XTD_{carga}_{ua}_{periodo}'
                        if xtd_name in variables:
                            xtd_var = variables[xtd_name]
                            left_expesion.append(-1*xtd_var)
                            
                        xtr_name = f'XTR_{carga}_{ua}_{periodo}'
                        if xtr_name in variables.keys():
                            xtr_var = variables[xtr_name]
                            left_expesion.append(-1*xtr_var) 
                            
                # XDM: demanda
                xdm_name = f'XDM_{empresa}_{planta}_{unidad}_{ingrediente}_{periodo}'
                xdm_var = variables[xdm_name]
                left_expesion.append(xdm_var)
                
                # armar restriccion
                rest = (pu.lpSum(left_expesion)==right_value, 'balance_masa_{ua}_{ingrediente}_{periodo}')
            
                # agregar la restriccion
                restricciones['balance_masa_inventario'].append(rest)
    
    
def _inventario_inicial_ua(restricciones:list, parametros:list):
    pass    

def _mantenimiento_ss_plantas(restricciones:list, variables:list):
    
    # sum(XDM) > SS * (1 - BSS)
    # sum(XDM) > SS - BSS*SS
    
    pass

def _capacidad_camiones(restricciones:list, variables:list, cargas:list, unidades:list):
    
    # XTR_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}: cantidad a despachar desde almacenamiento en puerto
    # XTD_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}: cantidad a despachar desde barco en puerto 
    # ITR_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}: cantidad de camiones desde almacenamiento
    # ITD_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{periodo}: cantidad de camiones desde barco
    
    restricciones['Capacidad de carga de camiones'] = list()
    
    for carga in cargas:
        for ua in unidades:
            for periodo in range(30):
                
                xtr_name = f'XTR_{carga}_{ua}_{periodo}'                
                itr_name = f'ITR_{carga}_{ua}_{periodo}'
                
                xdt_name = f'XDR_{carga}_{ua}_{periodo}' 
                itd_name = f'IDR_{carga}_{ua}_{periodo}' 

                if xtr_name in variables.keys() and itr_name in variables.keys():
                    
                    xtr_var = variables[xtr_name]
                    itr_var = variables[itr_name]
                    
                    rest = (xtr_var <= 34*itr_var ,f'capacidad de carga de camiones despacho almacenamiento {carga}_{ua}_{periodo}')
                    restricciones['Capacidad de carga de camiones'].append(rest)
            
                if xdt_name in variables.keys() and itd_name in variables.keys():
                    
                    xdt_var = variables[xdt_name]
                    idt_var = variables[itd_name]
                    
                    rest = (xdt_var <= 34*idt_var ,f'capacidad de carga de camiones despacho directo {carga}_{ua}_{periodo}')
                    restricciones['Capacidad de carga de camiones'].append(rest)
            

def _capacidad_unidades_almacenamiento():
    pass



def generar_restricciones(parametros:list, variables:list):
    
    restricciones = dict()
    
    # empresas = parametros['conjuntos']['empresas']
    # periodos = parametros['conjuntos']['periodos']
    plantas = parametros['conjuntos']['plantas']
    consumo_proyectado = parametros['parametros']['consumo_proyectado']
    ingredientes = parametros['conjuntos']['ingredientes']
    inventario_inicial = parametros['parametros']['inventario_inicial_cargas']
    llegadas = parametros['parametros']['llegadas_cargas']
    unidades = parametros['conjuntos']['unidades_almacenamiento']
    cargas = parametros['conjuntos']['cargas']
    

    
    # Satisfaccion de la demanda en las plantas
    _satisfaccion_demanda_plantas(restricciones, variables, plantas, ingredientes, unidades, consumo_proyectado)

    # Mantenimiento del nivel de seguridad de igredientes en plantas
    _mantenimiento_ss_plantas(restricciones, variables)

    # Capacidad de carga de los camiones
    _capacidad_camiones(restricciones, variables, cargas, unidades)
    
    # Capacidad de almacenamiento en unidades de almacenamiento
    _capacidad_unidades_almacenamiento()

    # Balances de masa de inventarios    
    ## Balance de masa en cargas en puerto
    
    ### Balance de masa en bif    
    _balance_masa_bif(restricciones, variables, llegadas, unidades)
    
    ### Inventario inicial puerto
    _inventario_inicial_bodega_puerto(restricciones, variables, cargas, inventario_inicial)
    
    ### Balance de masa en Bodega puerto
    _balance_masa_bodega_puerto(restricciones,variables,cargas, unidades)
   
    ## Balance de masa en plantas   
    ### Balance de masa en unidades de almacenamiento por producto en planta
    _balance_masa_ua(restricciones, variables, ingredientes, cargas, unidades, inventario_inicial)
    
    ## Asignación de uniades de almacenamiento a ingredientes
    
    return restricciones
    


