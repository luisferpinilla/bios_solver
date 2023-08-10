import pulp as pu

def generar_variables(problema:dict)->dict:
    
    variables = dict()    
    
    periodos = problema['periodos']
    ingredientes = problema['conjuntos']['ingredientes']
    plantas = problema['conjuntos']['plantas']
    unidades = problema['conjuntos']['unidades_almacenamiento']  
    cargas = problema['conjuntos']['cargas']

    # Variables asociadas al almacenamiento en puerto

    ## $XPL_{l}^{t}$ : Cantidad de la carga $l$ que llega al puerto y que será almacenada en el mismo.
    variables['XPL'] = dict()
    ## $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$
    variables['XTD'] = dict()
    
    for k in cargas:
        for periodo in range(periodos):
            campos = k.split('_')
            empresa = campos[0]
            ingrediente = campos[1]
            puerto = campos[2]
            barco = campos[3]
            
            xpl_name = f"XPL_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}"        
            variables['XPL'][xpl_name] = pu.LpVariable(name=xpl_name, lowBound=0.0, cat=pu.LpContinuous)
            
            for ua in unidades:
                xtd_name = f"XTD_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{ingrediente}_{periodo}"        
                variables['XTD'][xtd_name] = pu.LpVariable(name=xtd_name, lowBound=0.0, cat=pu.LpContinuous)

    ## $XIP_{j}^{t}$ : Cantidad de la carga $l$ en puerto al final del periodo $t$
    variables['XIP'] = dict()
    for carga in cargas:
        for periodo in range(periodos):
            campos = carga.split('_')
            empresa = campos[0]
            ingrediente = campos[1]
            puerto = campos[2]
            barco = campos[3]
            var_name = f"XIP_{empresa}_{ingrediente}_{puerto}_{barco}_{periodo}"        
            variables['XIP'][var_name] = pu.LpVariable(name=var_name, lowBound=0.0, cat=pu.LpContinuous)
        
    # Variables asociadas al transporte entre puertos y plantas
    variables['XTR'] = dict()
    variables['ITR'] = dict()
    variables['ITD'] = dict()
    for k in cargas:
        for periodo in range(periodos):
            campos = k.split('_')
            empresa = campos[0]
            ingrediente = campos[1]
            puerto = campos[2]
            barco = campos[3]
                
            for ua in unidades:
                
                ## $XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$
                xtr_name = f"XTR_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{ingrediente}_{periodo}"        
                variables['XTR'][xtr_name] = pu.LpVariable(name=xtr_name, lowBound=0.0, cat=pu.LpContinuous)
    
                ## $ITR_{lm}^{t}$ : Cantidad de camiones con carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$
                itr_name = f"ITR_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{ingrediente}_{periodo}"        
                variables['ITR'][itr_name] = pu.LpVariable(name=itr_name, lowBound=0.0, cat=pu.LpInteger)
                
                ## $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$
                itd_name = f"ITD_{empresa}_{ingrediente}_{puerto}_{barco}_{ua}_{ingrediente}_{periodo}"        
                variables['ITD'][itd_name] = pu.LpVariable(name=itd_name, lowBound=0.0, cat=pu.LpInteger)


    # Variables asociadas a la operación en planta
    variables['IIU'] = dict()
    variables['XIU'] = dict()
    variables['XDM'] = dict()
    variables['BSS'] = dict()
    variables['BCD'] = dict()
    for ua in unidades:        
        campos = ua.split('_')        
        empresa = campos[0]
        planta = campos[1]
        unidad = campos[2]        
        for ingrediente in ingredientes:
            for periodo in range(periodos):
                ## $IIU_{im}^{t}$ : Binaria, 1 sí el ingrediente $i$ esta almacenado en la unidad de almacenamiento $m$ al final del periodo $t$; 0 en otro caso
                iiu_name = f'IIU_{empresa}_{planta}_{unidad}_{ingrediente}_{periodo}'
                variables['IIU'][iiu_name] = pu.LpVariable(name=iiu_name, cat=pu.LpBinary)
                ## $XIU_{m}^{t}$ : Cantidad de ingrediente almacenado en la unidad de almacenameinto $m$ al final del periodo $t$
                xiu_name = f'XIU_{empresa}_{planta}_{unidad}_{ingrediente}_{periodo}'
                variables['XIU'][xiu_name] = pu.LpVariable(name=xiu_name, lowBound=0.0, cat=pu.LpContinuous)    
                ## $XDM_{im}^{t}$: Cantidad de producto $i$ a sacar de la unidad de almacenamiento $m$ para satisfacer la demanda e el día $t$.
                xdm_name = f'XDM_{empresa}_{planta}_{unidad}_{ingrediente}_{periodo}'
                variables['XDM'][xdm_name] = pu.LpVariable(name=xdm_name, lowBound=0.0, cat=pu.LpContinuous)    

    
    
    for planta in plantas:
        for ingrediente in ingredientes:
            for periodo in range(periodos):    
                ## $BSS_{ik}^{t}$ : Binaria, si se cumple que el inventario del ingrediente $i$ en la planta $k$ al final del día $t$ esté sobre el nivel de seguridad $SS_{ik}^{t}$
                bss_name = f'BSS_{planta}_{ingrediente}_{periodo}'
                variables['BSS'][bss_name] = pu.LpVariable(name=bss_name, cat=pu.LpBinary)
                ## $BCD_{ik}^{t}$ : si estará permitido que la demanda de un ingrediente $i$ no se satisfaga en la planta $k$ al final del día $t$
                bcd_name = f'BCD_{planta}_{ingrediente}_{periodo}'
                variables['BCD'][bcd_name] = pu.LpVariable(name=bcd_name, cat=pu.LpBinary)
                


    return variables

