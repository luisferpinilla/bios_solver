import pulp as pu


def _balance_masa_bif(restricciones: dict, variables: dict, cargas: list, llegadas: dict, unidades: list, periodos: list):

    print('trabajando')
    # AR = XPL + XTD

    rest_list = list()

    for carga in cargas:

        for periodo in periodos:

            # AR = XPL + sum(XTD)
            ar_name = f'AR_{carga}_{periodo}'

            if ar_name in llegadas.keys():
                ar_val = llegadas[ar_name]
            else:
                ar_val = 0.0

            xpl_name = f'XPL_{carga}_{periodo}'
            xpl_var = variables['XPL'][xpl_name]

            left_expesion = list()

            left_expesion.append(xpl_var)

            for ua in unidades:

                ua_periodo = int(ua.split('_')[3])

                if periodo == ua_periodo:

                    xtd_name = f'XTD_{carga}_{ua}'
                    xtd_var = variables['XTD'][xtd_name]

                    left_expesion.append(xtd_var)

            rest_list.append((pu.lpSum(left_expesion) == ar_val,
                             f'balance bif_{carga}_{periodo}'))

    restricciones['balance_masa_bif'] = rest_list


def _balance_masa_bodega_puerto(restricciones: list, variables: list, cargas: list, unidades: list, inventario_inicial: dict, periodos=list):
    # XIP = XIPt-1 + XPL - sum(XTR)
    # XIP + sum(XTR) = XIPt-1 + XPL
    
    rest_list = list()
    
    for periodo in periodos:
        for carga in cargas:
            
            campos = carga.split('_')
            c_empresa = campos[0]
            c_puerto = campos[1]
            c_motonave = campos[2]
            c_ingrediente = campos[3]
            
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
                ii_value = inventario_inicial[ii_name]
                rigth_expresion.append(ii_value)
            
            # XPL
            xpl_name = f'XPL_{carga}_{periodo}'
            xpl_var = variables['XPL'][xpl_name]            
            rigth_expresion.append(xpl_var)
            
            
            # sum(XTR)
            for unidad in unidades:
                campos = unidad.split('_')
                u_empresa = campos[0]
                u_planta = campos[1]
                u_codigo = campos[2]
                u_periodo = int(campos[3])
                
                
                if periodo == u_periodo:
                    xtr_name = f'XTR_{carga}_{unidad}'
                    xtr_var = variables['XTR'][xtr_name]
                    left_expresion.append(xtr_var)
                
            rest = (pu.lpSum(left_expresion)==pu.lpSum(rigth_expresion), f'balance de masa en {carga}_{periodo}')          
        
            rest_list.append(rest)
    
    restricciones['Balance_masa_bodega_puerto'] = rest_list
    
    
def _balance_masa_ua(restricciones: list, variables: list, cargas: list, unidades: list, inventario_inicial:dict, ingredientes:list, periodos=list):
    
    # XIU = XIUt-1 + SUM(XTR) + SUM(XTD) - XDM
    # XIU + XDM = XIUt-1 + SUM(XTR) + SUM(XTD)
    
    rest_list = list()
    
    for periodo in periodos:
        for ingrediente in ingredientes:
            for unidad in unidades:
                campos = unidad.split('_')
                u_empresa = campos[0]
                u_planta = campos[1]
                u_codigo = campos[2]
                u_periodo = int(campos[3])
                
                if periodo == u_periodo:
                
                    left_expesion = list()
                    rigth_expresion = list()
                    
                    # XIU
                    xiu_name = f'XIU_{ingrediente}_{unidad}'
                    xiu_var = variables['XIU'][xiu_name]
                    left_expesion.append(xiu_var)
                    
                    # XDM
                    xdm_name = f'XDM_{ingrediente}_{unidad}'
                    xdm_var = variables['XDM'][xdm_name]
                    left_expesion.append(xdm_var)
                    
                    # XIUt-1 / inventario inicial
                    if periodo > 0:
                        xiu_ant_name = f'XIU_{ingrediente}_{u_empresa}_{u_planta}_{u_codigo}_{periodo-1}'
                        xiu_ant_var = variables['XIU'][xiu_ant_name]
                        rigth_expresion.append(xiu_ant_var)           
                    else:
                        ii_name = f'II_{u_empresa}_{u_planta}_{u_codigo}_{ingrediente}'
                        ii_value = inventario_inicial[ii_name]
                        rigth_expresion.append(ii_value)
                        
                    
                    for carga in cargas:
                        campos = carga.split('_')
                        c_empresa = campos[0]
                        c_puerto = campos[1]
                        c_motonave = campos[2]
                        c_ingrediente = campos[3]
                        
                        # SUM(XTD) 
                        # SUM(XTR)
                        if c_ingrediente == ingrediente:
                            xtd_name = f'XTD_{carga}_{unidad}'
                            xtd_var = variables['XTD'][xtd_name]
                            rigth_expresion.append(xtd_var)
                            
                            xtr_name = f'XTR_{carga}_{unidad}'
                            xtr_var = variables['XTR'][xtr_name]
                            rigth_expresion.append(xtr_var)
                    
                        
                    
                    
                    
                    
                    rest = (pu.lpSum(left_expesion)==pu.lpSum(rigth_expresion), f'Balance masa de {ingrediente} en {unidad}')
                
                    rest_list.append(rest)

    
    
    
    restricciones['Balance_masa_unidades'] = rest_list
    
    pass


def _satisfaccion_demanda_plantas(restricciones: list, variables: list, plantas: list, ingredientes: list, unidades: list, consumo_proyectado: list, periodos=30):
    pass


def select_ua_by_period_planta(planta:str, period:int, unidades:list):
    list_to_return = list()
    
    for ua in unidades:
        campos = ua.split('_')
        ua_empresa = campos[0]
        ua_planta = campos[1]
        ua_codigo = campos[2]
        ua_periodo = int(campos[3])
        
        if planta == f'{ua_empresa}_{ua_planta}' and period== ua_periodo:
            list_to_return.append(ua)
            
    return list_to_return    


def _mantenimiento_ss_plantas(restricciones: list, variables: list, unidades: list, ingredientes: list, periodos:list, plantas:list, safety_stock:dict):

    # sum(XIU, carga) >= (1-BIU)*SS
    # sum(XIU, carga) >= SS - SS*BIU
    # sum(XIU, carga) + SS*BIU >= SS

    rest_list = list()
    
    
    for ingrediente in ingredientes:
        for planta in plantas:
            for periodo in periodos:                
                
                left_expesion = list()
                
                ua_list = select_ua_by_period_planta(planta=planta, period=periodo, unidades=unidades)
                
                # sum(XIU, carga)
                for ua in ua_list:
                    xiu_name = f'XIU_{ingrediente}_{ua}'
                    xiu_var = variables['XIU'][xiu_name]
                    left_expesion.append(xiu_var)
                    
                # BSS
                bss_name= f'BSS_{ingrediente}_{planta}_{periodo}'
                bss_var = variables['BSS'][bss_name]
                left_expesion.append(bss_var)
                
                ss_name = f'SS_{planta}_{ingrediente}'
                ss_value = safety_stock[ss_name]
                
                rest = (pu.lpSum(left_expesion)>=ss_value, f'safety_stock {ingrediente} en {planta} en {periodo}')
                    
                rest_list.append(rest)   

    restricciones['Safety stock en planta'] = rest_list    


def _capacidad_camiones(restricciones: list, variables: list, cargas: list, unidades: list, periodos=30):

    # XTD <= 34*ITD
    # XTR <= 34*ITR   
    
    rest_list = list()

    for xtd_name, xtd_var in variables['XTD'].items():
        
        itd_name = xtd_name.replace('XTD', 'ITD')
        itd_var = variables['ITD'][itd_name]
        
        rest_list.append((xtd_var <= 34*itd_var, f'capacidad carga directa {xtd_name}'))
        
    for xtr_name, xtr_var in variables['XTR'].items():
        
        itr_name = xtr_name.replace('XTR', 'ITR')
        itr_var = variables['ITR'][itr_name]
        
        rest_list.append((xtr_var <= 34*itr_var, f'capacidad carga desde almacenamiento en {xtr_name}'))
            
            
    restricciones['Capacidad carga de camiones'] = rest_list
        

def _capacidad_unidades_almacenamiento(restricciones: list, variables: list, unidades: list, ingredientes: list, capacidad_unidades: dict, periodos=30):
    
    rest_list = list()
    
    for ingrediente in ingredientes:
        for unidad in unidades:
            campos = unidad.split('_')
            unidad_empresa = campos[0]
            unidad_planta = campos[1]
            unidad_codigo = campos[2]
            unidad_periodo = campos[3]            
            
            xiu_name = f'XIU_{ingrediente}_{unidad}'
            xiu_var = variables['XIU'][xiu_name]
            
            biu_name = f'BIU_{ingrediente}_{unidad}'
            biu_var = variables['BIU'][biu_name]
            

            cap_name = f'CA_{ingrediente}_{unidad_empresa}_{unidad_planta}_{unidad_codigo}'
            
            if cap_name in capacidad_unidades.keys():
                cap_val = capacidad_unidades[cap_name]
            else:
                cap_val = 0.0
            
            rest_list.append((xiu_var <= cap_val*biu_var, f'capacidad de almacenamiento para {ingrediente} en {unidad}'))
            
            
    restricciones['Capacidad_almacenamiento_UA'] = rest_list


def _asignacion_unidades_almacenamiento(restricciones: list, variables: list, unidades: list, ingredientes: list):
    # no se puede asignar más de un ingrediente a una unidad
    
    # SUM(BIU, ingrediente,planta, periodo) <= 1
    
    rest_list = list()
    
    for unidad in unidades:
        
        left_expesion = list()
        
        for ingrediente in ingredientes:
            
            biu_name = f'BIU_{ingrediente}_{unidad}'
        
            biu_var = variables['BIU'][biu_name]
            
            left_expesion.append(biu_var)
            
        rest = (pu.lpSum(left_expesion)<=1, f'asignación única sobre unidad {unidad}')
        
        rest_list.append(rest)

    restricciones['Asignación unica de ingredientes a unidades'] = rest_list


def generar_restricciones(problema: list, variables: list):

    restricciones = dict()

    # empresas = problema['conjuntos']['empresas']
    periodos = list(problema['conjuntos']['periodos'].keys())
    plantas = problema['conjuntos']['plantas']
    consumo_proyectado = problema['parametros']['consumo_proyectado']
    ingredientes = problema['conjuntos']['ingredientes']
    inventario_inicial = problema['parametros']['inventario_inicial_cargas']
    llegadas = problema['parametros']['llegadas_cargas']
    unidades = problema['conjuntos']['unidades_almacenamiento']
    cargas = problema['conjuntos']['cargas']
    capacidad_unidades = problema['parametros']['capacidad_almacenamiento_ua']
    inventario_inicial_ua = problema['parametros']['inventario_inicial_ua']
    safety_stock = problema['parametros']['safety_stock']

    _balance_masa_bif(restricciones=restricciones, variables=variables,
                      cargas=cargas, llegadas=llegadas, unidades=unidades, periodos=periodos)
    
    _capacidad_unidades_almacenamiento(restricciones=restricciones, variables=variables, unidades=unidades, ingredientes=ingredientes, capacidad_unidades=capacidad_unidades)


    _mantenimiento_ss_plantas(restricciones=restricciones, variables=variables, unidades=unidades, ingredientes=ingredientes, periodos=periodos, plantas=plantas, safety_stock=safety_stock)

    _capacidad_camiones(restricciones=restricciones, variables=variables, cargas=cargas, unidades=unidades)
    
    _asignacion_unidades_almacenamiento(restricciones=restricciones, variables=variables, unidades=unidades, ingredientes=ingredientes)

    _balance_masa_bodega_puerto(restricciones=restricciones, variables=variables, cargas=cargas, unidades=unidades, inventario_inicial=inventario_inicial, periodos=periodos)

    _balance_masa_ua(restricciones=restricciones, variables=variables, cargas=cargas, unidades=unidades, inventario_inicial=inventario_inicial_ua, ingredientes=ingredientes, periodos=periodos)

    return restricciones
