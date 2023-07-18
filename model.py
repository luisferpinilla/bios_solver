import pulp as pu
import pandas as pd
from datetime import datetime

file = '/Users/luispinilla/Documents/source_code/bios_solver/model_1.xlsm'


def construir_parametros(now: datetime):

    parametros = dict()

    parametros['fecha_inicial'] = now
    parametros['conjuntos'] = dict()
    parametros['diccionarios'] = dict()

    # Conjuntos

    # Empresas
    empresas_df = pd.read_excel(file, sheet_name='empresas')
    parametros['conjuntos']['empresas'] = empresas_df['empresa'].to_list()

    # Calendario
    periodos_df = pd.read_excel(file, sheet_name='periodos')
    parametros['conjuntos']['periodos'] = {
        periodos_df.loc[i]['Id']: periodos_df.loc[i]['Fecha'] for i in periodos_df.index}
    parametros['conjuntos']['fechas'] = {
        periodos_df.loc[i]['Fecha']: periodos_df.loc[i]['Id'] for i in periodos_df.index}

    # Ingredientes
    ingredientes_df = pd.read_excel(file, sheet_name='ingredientes')
    parametros['conjuntos']['ingredientes'] = ingredientes_df['ingrediente'].to_list()

    # Puertos
    puertos_df = pd.read_excel(file, sheet_name='puertos')
    parametros['conjuntos']['puertos'] = puertos_df['puerto'].to_list()

    # plantas
    plantas_df = pd.read_excel(file, sheet_name='plantas')
    parametros['conjuntos']['plantas'] = plantas_df['planta'].to_list()

    # Unidades de almacenamiento
    unidades_df = pd.read_excel(file, sheet_name='unidades_almacenamiento')
    parametros['conjuntos']['unidades_almacenamiento'] = unidades_df['key'].to_list()

    # diccionarios

    parametros['diccionarios']['empresas_plantas'] = dict()
    parametros['diccionarios']['empresas_plantas']['contegral'] = [
        'bogota', 'cartago', 'envigado', 'neiva']
    parametros['diccionarios']['empresas_plantas']['finca'] = [
        'bmanga', 'buga', 'cienaga', 'itagui', 'mosquera']

    parametros['diccionarios']['plantas_unidades'] = {p: list(
        unidades_df[unidades_df['planta'] == p]['key'].unique()) for p in parametros['conjuntos']['plantas']}

    # $IP_{l}$ : inventario inicial en puerto para la carga $l$.

    inventarios_puerto_df = pd.read_excel(file, sheet_name='cargas_puerto')

    inventarios_puerto_df['status'] = inventarios_puerto_df['fecha_llegada'].apply(
        lambda x: 'arrival' if x > now else 'inventory')

    ip_df = inventarios_puerto_df[inventarios_puerto_df['status'] == 'inventory'].groupby(
        ['ingrediente', 'puerto', 'barco'])[['cantidad']].sum().reset_index()

    parametros['diccionarios']['ingredientes_puerto'] = {ingrediente: list(
        inventarios_puerto_df[inventarios_puerto_df['ingrediente'] == ingrediente]['barco'].unique()) for ingrediente in parametros['conjuntos']['ingredientes']}

    parametros['inventario_inicial_cargas'] = {
        f"IP_{ip_df.iloc[fila]['barco']}": ip_df.iloc[fila]['cantidad'] for fila in range(ip_df.shape[0])}

    # $AR_{l}^{t}$ : Cantidad de material que va a llegar a la carga $l$ durante el día $t$, sabiendo que: $material \in I$ y $carga \in J$.

    ar_df = inventarios_puerto_df[inventarios_puerto_df['status'] == 'arrival'].groupby(
        ['ingrediente', 'puerto', 'barco', 'fecha_llegada'])[['cantidad']].sum().reset_index()

    ar_df['periodo'] = ar_df['fecha_llegada'].map(
        parametros['conjuntos']['fechas'])

    parametros['llegadas_cargas'] = {
        f"AR_{ar_df.iloc[i]['barco']}_{ar_df.iloc[i]['periodo']}": ar_df.iloc[i]['cantidad'] for i in range(ar_df.shape[0])}

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.

    cc_df = pd.read_excel(file, sheet_name='costos_almacenamiento_cargas')

    cc_df = cc_df[cc_df['fecha_llegada'].isin(
        parametros['conjuntos']['fechas'])].copy()

    cc_df['periodo'] = cc_df['fecha_llegada'].map(
        parametros['conjuntos']['fechas'])

    parametros['costos_almacenamiento'] = {
        f"CC_{cc_df.iloc[i]['barco']}_{cc_df.iloc[i]['periodo']}": cc_df.iloc[i]['Valor_por_tonelada'] for i in range(cc_df.shape[0])}

    # $CF_{lm}$ : Costo fijo de transporte por camión despachado llevando la carga $l$ hasta la unidad de almacenamiento $m$.

    parametros['fletes_fijos'] = dict()
    fletes_fijos_df = pd.read_excel(file, sheet_name='fletes_fijos')
    fletes_fijos_df.set_index('puerto', drop=True, inplace=True)
    fletes_fijos_df.fillna(0.0, inplace=True)

    for puerto in parametros['conjuntos']['puertos']:
        for planta in parametros['conjuntos']['plantas']:
            parametros['fletes_fijos'][f'CF_{puerto}_{planta}'] = fletes_fijos_df.loc[puerto][planta]

    # $ CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.

    parametros['fletes_variables'] = dict()

    fletes_variables_df = pd.read_excel(file, sheet_name='fletes_variables')
    fletes_variables_df.set_index('puerto', drop=True, inplace=True)

    for puerto in parametros['conjuntos']['puertos']:
        for planta in parametros['conjuntos']['plantas']:
            parametros['fletes_variables'][f'CT_{puerto}_{planta}'] = fletes_variables_df.loc[puerto][planta]

    # $CW_{lm}$ : Costo de vender una carga perteneciente a una empresa a otra.

    costo_cambio_empresa_df = pd.read_excel(file, 'venta_entre_empresas')

    costo_cambio_empresa_df.melt(id_vars='origen', value_vars=['contegral', 'finca'], var_name='destino')

    # $TT_{jk}$ : tiempo en días para transportar la carga desde el puerto $j$ hacia la planta $k$.

    parametros['tiempo_transporte'] = dict()

    for puerto in parametros['conjuntos']['puertos']:
        for planta in parametros['conjuntos']['plantas']:
            lista_ua = [ua for ua in parametros['conjuntos'] ['unidades_almacenamiento'] if planta in ua.split('_')[0]]
            for ua in lista_ua:
                parametros['tiempo_transporte'][f"TT_{puerto}_{ua}"] = 2

    # $CA_{m}^{i}$ : Capacidad de almacenamiento de la unidad $m$ en toneladas del ingrediente $i$, tenendo en cuenta que $m \in K$.

    # $DM_{ki}^{t}$: Demanda del ingrediente $i$ en la planta $k$ durante el día $t$.

    demanda_df = pd.read_excel(file, sheet_name='consumo_proyectado')

    demanda_df = demanda_df.melt(id_vars=['ingrediente', 'planta'], var_name='fecha', value_name='consumo').copy()

    demanda_df['periodo'] = demanda_df['fecha'].map(
        parametros['conjuntos']['fechas'])

    parametros['consumo_proyectado'] = {f"DM_{demanda_df.iloc[i]['planta']}_{demanda_df.iloc[i]['ingrediente']}_{demanda_df.iloc[i]['periodo']}": demanda_df.iloc[i]['consumo'] for i in range(demanda_df.shape[0])}

    # $CD_{ik}^{t}$ : Costo de no satisfacer la demanda del ingrediente $i$  en la planta $k$ durante el día $t$.

    # $CI_{im}^{t}$ : Costo de asignar el ingrediente $i$ a la unidad de almacenamiento $m$ durante el periodo $t$. Si la unidad de almacenamiento no puede contener el ingrediente, este costo será $infinito$.

    # $SS_{ik}^{t}$ : Inventario de seguridad a tener del ingrediente $i$ en la planta $k$ al final del día $t$.

    # $CS_{ik}^{t}$ : Costo de no satisfacer el inventario de seguridad para el ingrediente $i$ en la planta $k$ durante el día $t$.

    # $TR_{im}^{t}$ : Cantidad en tránsito programada para llegar a la unidad de almacenamiento $m$ durante el día $t$,

    return parametros


def construir_variables(conjuntos: dict):

    variables = dict()

    # Variables asociadas al almacenamiento en puerto

    # $XPL_{l}^{t}$ : Cantidad de la carga $l$ que llega al puerto y que será almacenada en el mismo.

    # $XIP_{j}^{t}$ : Cantidad de la carga $l$ en puerto al final del periodo $t$

    # Variables asociadas al transporte entre puertos y plantas

    # $XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$

    # $ITR_{lm}^{t}$ : Cantidad de camiones con carga $l$ en puerto a despachar hacia la unidad $m$ durante el día $t$

    # $XTD_{lm}^{t}$ : Cantidad de carga $l$ en barco a transportar bajo despacho directo hacia la unidad $m$ durante el día $t$

    # $ITD_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar directamente hacia la unidad $m$ durante el día $t$

    # Variables asociadas a la operación en planta

    # $IIU_{im}^{t}$ : Binaria, 1 sí el ingrediente $i$ esta almacenado en la unidad de almacenamiento $m$ al final del periodo $t$; 0 en otro caso

    # $XIU_{m}^{t}$ : Cantidad de ingrediente almacenado en la unidad de almacenameinto $m$ al final del periodo $t$

    # $XDM_{im}^{t}$: Cantidad de producto $i$ a sacar de la unidad de almacenamiento $m$ para satisfacer la demanda e el día $t$.

    # $BSS_{ik}^{t}$ : Binaria, si se cumple que el inventario del ingrediente $i$ en la planta $k$ al final del día $t$ esté sobre el nivel de seguridad $SS_{ik}^{t}$

    # $BCD_{ik}^{t}$ : si estará permitido que la demanda de un ingrediente $i$ no se satisfaga en la planta $k$ al final del día $t$


def construir_fob():

    fob = list()

    # Costos por almacenamiento

    # Almacenamiento en puerto por corte de Facturación:

    # Costos por transporte

    # Costo variable de transportar cargas desde puertos hacia plantas

    # Costo fijo de transportar un camion desde puerto hacia plantas

    # Costos por Penalización

    # Costo de no respetar un inventario de seguridad de un ingrediente en una planta

    # Costo de no satisfacer una demanda en una planta

    # Costo por permitir guardar un ingrediente en una planta


def construir_restricciones():

    # Satisfaccion de la demanda en las plantas

    # Mantenimiento del nivel de seguridad de igredientes en plantas

    # Capacidad de carga de los camiones

    # Capacidad de almacenamiento en unidades de almacenamiento

    # Balances de masa de inventarios

    # Balance de masa en cargas en puerto

    # Balance de masa en unidades de almacenamiento por producto en planta

    # Asignación de uniades de almacenamiento a ingredientes

    pass


def resolver():
    pass


def generar_reporte():
    pass


now = datetime(2023, 7, 7)

parametros = construir_parametros(now)


# Problema
# problema = pu.LpProblem("Bios", sense=pu.const.LpMinimize)
