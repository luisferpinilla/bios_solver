import pulp as pu


def _despacho_directo(variables: dict, cargas: list, unidades: list):

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$
    variables['XTD'] = dict()

    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$
    variables['ITD'] = dict()

    for carga in cargas:
        for unidad in unidades:
            xtd_name = f'XTD_{carga}_{unidad}'
            xtd_var = pu.LpVariable(
                name=xtd_name, lowBound=0.0, cat=pu.LpContinuous)
            variables['XTD'][xtd_name] = xtd_var

            itd_name = f'ITD_{carga}_{unidad}'
            itd_var = pu.LpVariable(
                name=itd_name, lowBound=0.0, cat=pu.LpInteger)
            variables['ITD'][itd_name] = itd_var


def _decargue_barco_a_puerto(variables: dict, cargas: list, periodos: list):
    # $XPL_{l}^{t}$ : Cantidad de la carga $l$ que llega al puerto y que será almacenada en el mismo.
    variables['XPL'] = dict()
    for carga in cargas:
        for periodo in periodos:
            xpl_name = f'XPL_{carga}_{periodo}'
            xpl_var = pu.LpVariable(
                name=xpl_name, lowBound=0.0, cat=pu.LpContinuous)
            variables['XPL'][xpl_name] = xpl_var


def _despacho_desde_puerto(variables: dict, cargas: list, unidades: list):

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$
    variables['XTR'] = dict()

    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$
    variables['ITR'] = dict()

    for carga in cargas:
        for unidad in unidades:
            xtd_name = f'XTR_{carga}_{unidad}'
            xtd_var = pu.LpVariable(
                name=xtd_name, lowBound=0.0, cat=pu.LpContinuous)
            variables['XTR'][xtd_name] = xtd_var

            itd_name = f'ITR_{carga}_{unidad}'
            itd_var = pu.LpVariable(
                name=itd_name, lowBound=0.0, cat=pu.LpInteger)
            variables['ITR'][itd_name] = itd_var


def _almacenamiento_puerto(variables:list, cargas:list, periodos:list):
    # $XIP_{j}^{t}$ : Cantidad de la carga $l$ en puerto al final del periodo $t$
    variables['XIP'] = dict()
    for carga in cargas:
        for periodo in periodos:
            xip_name = f'XIP_{carga}_{periodo}'
            xip_var = pu.LpVariable(name=xip_name, lowBound=0.0, cat=pu.LpContinuous)
            variables['XIP'][xip_name] = xip_var
  



def _almacenamiento_planta(variables: list, unidades: list, ingredientes: list):

    variables['BIU'] = dict()
    variables['XIU'] = dict()
    variables['XDM'] = dict()
    variables['XBS'] = dict()
    variables['BCD'] = dict()

    for unidad in unidades:
        for ingrediente in ingredientes:
            # $IIU_{im}^{t}$ : Binaria, 1 sí el ingrediente $i$ esta almacenado en la unidad de almacenamiento $m$ al final del periodo $t$; 0 en otro caso
            biu_name = f'IIU_{ingrediente}_{unidad}'
            biu_var = pu.LpVariable(name=biu_name, cat=pu.LpBinary)
            variables['BIU'][biu_name] = biu_var

            # $XIU_{mi}^{t}$ : Cantidad de ingrediente $i$ almacenado en la unidad de almacenameinto $m$ al final del periodo $t$
            xiu_name = f'XIU_{ingrediente}_{unidad}'
            xiu_var = pu.LpVariable(
                name=xiu_name, lowBound=0.0, cat=pu.LpContinuous)
            variables['XIU'][xiu_name] = xiu_var

            # $XDM_{im}^{t}$: Cantidad de producto $i$ a sacar de la unidad de almacenamiento $m$ para satisfacer la demanda e el día $t$.
            xdm_name = f'XDM_{ingrediente}_{unidad}'
            xdm_var = pu.LpVariable(
                name=xdm_name, lowBound=0.0, cat=pu.LpContinuous)
            variables['XDM'][xdm_name] = xdm_var

            # $BSS_{ik}^{t}$ : Binaria, si se cumple que el inventario del ingrediente $i$ en la planta $k$ al final del día $t$ esté sobre el nivel de seguridad $SS_{ik}^{t}$
            xbs_name = f'XBS_{ingrediente}_{unidad}'
            xbs_var = pu.LpVariable(name=xbs_name, cat=pu.LpBinary)
            variables['XBS'][xbs_name] = xbs_var

            # $BCD_{ik}^{t}$ : si estará permitido que la demanda de un ingrediente $i$ no se satisfaga en la planta $k$ al final del día $t$
            bcd_name = f'BCD_{ingrediente}_{unidad}'
            bcd_var = pu.LpVariable(name=bcd_name, cat=pu.LpBinary)
            variables['BCD'][bcd_name] = bcd_var


def generar_variables(problema: dict) -> dict:

    variables = dict()

    periodos = problema['conjuntos']['periodos']
    ingredientes = problema['conjuntos']['ingredientes']
    unidades = problema['conjuntos']['unidades_almacenamiento']
    cargas = problema['conjuntos']['cargas']

    _despacho_directo(variables=variables, cargas=cargas, unidades=unidades)

    _decargue_barco_a_puerto(
        variables=variables, cargas=cargas, periodos=periodos)

    _despacho_desde_puerto(variables=variables,
                           cargas=cargas, unidades=unidades)

    _almacenamiento_planta(variables=variables,
                           unidades=unidades, ingredientes=ingredientes)
    
    _almacenamiento_puerto(variables=variables, cargas=cargas, periodos=periodos)

    return variables
