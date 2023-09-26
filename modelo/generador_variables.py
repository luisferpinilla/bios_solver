import pulp as pu


def _despacho_directo(variables: dict, periodos: list,  cargas: list, plantas: list, max_trucks=50):

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la planta $k$ durante el día $t$
    variables['XTD'] = dict()

    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la panta $k$ durante el día $t$
    variables['ITD'] = dict()

    for periodo in periodos:
        for carga in cargas:
            for planta in plantas:
                xtd_name = f'XTD_{carga}_{planta}_{periodo}'
                xtd_var = pu.LpVariable(
                    name=xtd_name, lowBound=0.0, upBound=34000*max_trucks, cat=pu.LpContinuous)
                variables['XTD'][xtd_name] = xtd_var

                itd_name = f'ITD_{carga}_{planta}_{periodo}'
                itd_var = pu.LpVariable(
                    name=itd_name, lowBound=0, upBound=max_trucks, cat=pu.LpInteger)
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


def _despacho_desde_puerto(variables: dict, cargas: list, plantas: list, periodos: list, max_trucks=50):

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$
    variables['XTR'] = dict()

    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$
    variables['ITR'] = dict()

    for periodo in periodos:
        for carga in cargas:
            for planta in plantas:
                xtd_name = f'XTR_{carga}_{planta}_{periodo}'
                xtd_var = pu.LpVariable(
                    name=xtd_name, lowBound=0.0, upBound=34000*max_trucks, cat=pu.LpContinuous)
                variables['XTR'][xtd_name] = xtd_var

                itd_name = f'ITR_{carga}_{planta}_{periodo}'
                itd_var = pu.LpVariable(
                    name=itd_name, lowBound=0, upBound=max_trucks, cat=pu.LpInteger)
                variables['ITR'][itd_name] = itd_var


def _almacenamiento_puerto(variables: list, cargas: list, periodos: list):
    # $XIP_{j}^{t}$ : Cantidad de la carga $l$ en puerto al final del periodo $t$
    variables['XIP'] = dict()
    for carga in cargas:
        for periodo in periodos:
            xip_name = f'XIP_{carga}_{periodo}'
            xip_var = pu.LpVariable(
                name=xip_name, lowBound=0.0, cat=pu.LpContinuous)
            variables['XIP'][xip_name] = xip_var


def _almacenamiento_planta(variables: list, plantas: list, ingredientes: list, periodos: list):

    variables['XIU'] = dict()
    variables['BSS'] = dict()
    variables['XBK'] = dict()

    for planta in plantas:
        for ingrediente in ingredientes:
            for periodo in periodos:

                # $XIU_{mi}^{t}$ : proporción de ingrediente $i$ almacenado en la planta $k$ al final del periodo $t$
                xiu_name = f'XIU_{planta}_{ingrediente}_{periodo}'
                xiu_var = pu.LpVariable(
                    name=xiu_name, lowBound=0.0, cat=pu.LpContinuous)
                variables['XIU'][xiu_name] = xiu_var

                # $BSS_{ik}^{t}$ : Binaria, si se cumple que el inventario del ingrediente $i$ en la planta $k$ al final del día $t$ esté sobre el nivel de seguridad $SS_{ik}^{t}$
                xbs_name = f'BSS_{planta}_{ingrediente}_{periodo}'
                xbs_var = pu.LpVariable(name=xbs_name, cat=pu.LpBinary)
                variables['BSS'][xbs_name] = xbs_var

                xbk_name = f'XBK_{planta}_{ingrediente}_{periodo}'
                xbk_var = pu.LpVariable(
                    name=xbk_name, lowBound=0.0, cat=pu.LpContinuous)
                variables['XBK'][xbk_name] = xbk_var


def generar_variables(conjuntos: dict, variables: dict) -> dict:

    periodos = conjuntos['periodos']
    ingredientes = conjuntos['ingredientes']
    plantas = conjuntos['plantas']
    cargas = conjuntos['cargas']

    _despacho_directo(variables=variables, cargas=cargas,
                      plantas=plantas, periodos=periodos)

    _decargue_barco_a_puerto(
        variables=variables, cargas=cargas, periodos=periodos)

    _despacho_desde_puerto(variables=variables,
                           cargas=cargas, periodos=periodos, plantas=plantas)

    _almacenamiento_planta(variables=variables, plantas=plantas,
                           periodos=periodos, ingredientes=ingredientes)

    _almacenamiento_puerto(variables=variables,
                           cargas=cargas, periodos=periodos)
