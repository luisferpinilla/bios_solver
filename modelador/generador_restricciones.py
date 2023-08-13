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


def _balance_masa_bodega_puerto(restricciones: list, variables: list, cargas: list, unidades: list, inventario_inicial: dict, periodos=30):
    pass


def _satisfaccion_demanda_plantas(restricciones: list, variables: list, plantas: list, ingredientes: list, unidades: list, consumo_proyectado: list, periodos=30):
    pass


def _balance_masa_ua(restricciones: list, variables: list, ingredientes: list, cargas: list, unidades: list, inventario_inicial: dict(), periodos=30):

    pass


def _mantenimiento_ss_plantas(restricciones: list, variables: list, unidades: list, ingredientes: list, periodos=30):

    rest_list = list()

    


    restricciones['Safety stock en planta'] = rest_list    



def _capacidad_camiones(restricciones: list, variables: list, cargas: list, unidades: list, periodos=30):

    # XTD <= 34*ITD
    # XTR <= 34*ITR   

    for carga in cargas:
        
        campos = carga.split('_')
        carga_empresa = campos[1]
        carga_ingrediente = campos[2]
        carga_puerto = campos[3]
        carga_motonave = campos[4]
        
        for unidad in unidades:
            campos = unidad.split('_')
            unidad_
            
        
        


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
        


def _asignacion_unidades_almacenamiento(restricciones: list, variables: list, unidades: list, ingredientes: list, periodos=30):

    pass


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

    _balance_masa_bif(restricciones=restricciones, variables=variables,
                      cargas=cargas, llegadas=llegadas, unidades=unidades, periodos=periodos)
    
    _capacidad_unidades_almacenamiento(restricciones=restricciones, variables=variables, unidades=unidades, ingredientes=ingredientes, capacidad_unidades=capacidad_unidades)

    return restricciones
