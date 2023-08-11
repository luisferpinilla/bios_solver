import pulp as pu


def _despacho_directo(variables: dict, cargas: list, unidades: list):

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$
    variables['XTD'] = list()

    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$
    variables['ITD'] = list()

    for carga in cargas:
        for unidad in unidades:
            xtd_name = f'XTD_{carga}_{unidad}'
            xtd_var = pu.LpVariable(
                name=xtd_name, lowBound=0.0, cat=pu.LpContinuous)

            itd_name = f'ITD_{carga}_{unidad}'
            itd_var = pu.LpVariable(
                name=itd_name, lowBound=0.0, cat=pu.LpInteger)

            variables['XTD'].append(xtd_var)
            variables['ITD'].append(itd_var)


def _decargue_barco_a_puerto(variables: dict, cargas: list, periodos: list):
    # $XPL_{l}^{t}$ : Cantidad de la carga $l$ que llega al puerto y que será almacenada en el mismo.
    variables['XPL'] = list()
    for carga in cargas:
        for periodo in periodos:
            xpl_name = f'XPL_{carga}_{periodo}'
            xpl_var = pu.LpVariable(
                name=xpl_name, lowBound=0.0, cat=pu.LpContinuous)
            variables['XPL'].append(xpl_var)


def _despacho_desde_puerto(variables: dict, cargas: list, unidades: list):

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$
    variables['XTR'] = list()

    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$
    variables['ITR'] = list()

    for carga in cargas:
        for unidad in unidades:
            xtd_name = f'XTR_{carga}_{unidad}'
            xtd_var = pu.LpVariable(
                name=xtd_name, lowBound=0.0, cat=pu.LpContinuous)

            itd_name = f'ITR_{carga}_{unidad}'
            itd_var = pu.LpVariable(
                name=itd_name, lowBound=0.0, cat=pu.LpInteger)

            variables['XTR'].append(xtd_var)
            variables['ITR'].append(itd_var)


def generar_variables(problema: dict) -> dict:

    variables = dict()

    periodos = problema['conjuntos']['periodos']
    ingredientes = problema['conjuntos']['ingredientes']
    plantas = problema['conjuntos']['plantas']
    unidades = problema['conjuntos']['unidades_almacenamiento']
    cargas = problema['conjuntos']['cargas']

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$
    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$
    _despacho_directo(variables=variables, cargas=cargas, unidades=unidades)

    # $XPL_{l}^{t}$ : Cantidad de la carga $l$ que llega al puerto y que será almacenada en el mismo.
    _decargue_barco_a_puerto(
        variables=variables, cargas=cargas, periodos=periodos)
    # $XIP_{j}^{t}$ : Cantidad de la carga $l$ en puerto al final del periodo $t$
    variables['XIP'] = dict()

    # XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$
    # $ITR_{lm}^{t}$ : Cantidad de camiones con carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$
    _despacho_desde_puerto(variables=variables,
                           cargas=cargas, unidades=unidades)

    # $IIU_{im}^{t}$ : Binaria, 1 sí el ingrediente $i$ esta almacenado en la unidad de almacenamiento $m$ al final del periodo $t$; 0 en otro caso
    variables['IIU'] = dict()

    # $XIU_{mi}^{t}$ : Cantidad de ingrediente $i$ almacenado en la unidad de almacenameinto $m$ al final del periodo $t$
    variables['XIU'] = dict()

    # $XDM_{im}^{t}$: Cantidad de producto $i$ a sacar de la unidad de almacenamiento $m$ para satisfacer la demanda e el día $t$.
    variables['XDM'] = dict()

    # $BSS_{ik}^{t}$ : Binaria, si se cumple que el inventario del ingrediente $i$ en la planta $k$ al final del día $t$ esté sobre el nivel de seguridad $SS_{ik}^{t}$
    variables['BSS'] = dict()

    # $BCD_{ik}^{t}$ : si estará permitido que la demanda de un ingrediente $i$ no se satisfaga en la planta $k$ al final del día $t$
    variables['BCD'] = dict()

    return variables
