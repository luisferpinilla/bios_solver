# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


def __remover_underscores(x: str) -> str:

    x = x.lower()
    x = x.replace('_', '')
    x = x.replace('-', '')
    x = x.replace(' ', '')

    return x


def __inventario_inicial_puerto(parametros: dict, file: str):
    # $IP_{l}$ : inventario inicial en puerto para la carga $l$.

    inventarios_puerto_df = pd.read_excel(
        file, sheet_name='inventario_puerto', usecols='B:H')

    campos = ['empresa', 'operador', 'imp-motonave', 'ingrediente']

    for campo in campos:
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(
            __remover_underscores)

    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)

    parametros['inventario_inicial_cargas'] = {
        f"IP_{inventarios_puerto_df.iloc[fila]['key']}": inventarios_puerto_df.iloc[fila]['cantidad_kg'] for fila in range(inventarios_puerto_df.shape[0])}


def __llegadas_a_puerto(parametros: dict, conjuntos: dict, file: str):

    # $AR_{l}^{t}$ : Cantidad de material que va a llegar a la carga $l$ durante el día $t$, sabiendo que: $material \in I$ y $carga \in J$.

    inventarios_puerto_df = pd.read_excel(
        file, sheet_name='tto_puerto', usecols='B:H')

    campos = ['empresa', 'operador', 'imp-motonave', 'ingrediente']

    for campo in campos:
        inventarios_puerto_df[campo] = inventarios_puerto_df[campo].apply(
            __remover_underscores)

    # regenerar key
    inventarios_puerto_df['key'] = inventarios_puerto_df.apply(
        lambda field: '_'.join([field[x] for x in campos]), axis=1)

    fechas_dict = {conjuntos['fechas'][x]: str(
        x) for x in conjuntos['periodos']}

    inventarios_puerto_df['periodo'] = inventarios_puerto_df['fecha_llegada'].map(
        fechas_dict)

    # Extraer los que caen fuera del horizonte de planeación
    inventarios_puerto_df = inventarios_puerto_df[~inventarios_puerto_df['periodo'].isna(
    )]

    parametros['llegadas_cargas'] = {
        f"AR_{inventarios_puerto_df.iloc[i]['key']}_{inventarios_puerto_df.iloc[i]['periodo']}": inventarios_puerto_df.iloc[i]['cantidad_kg'] for i in range(inventarios_puerto_df.shape[0])}


def __costo_almacenamiento_puerto(parametros: dict, conjuntos: dict, file: str):

    # $CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $J$.

    cc_df = pd.read_excel(
        file, sheet_name='costos_almacenamiento_cargas', usecols='B:G')

    campos = ['empresa', 'ingrediente', 'operador-puerto', 'imp-motonave']

    for campo in campos:
        cc_df[campo] = cc_df[campo].apply(__remover_underscores)

    # regenerar key
    cc_df['key'] = cc_df.apply(lambda field: '_'.join(
        [field[x] for x in campos]), axis=1)

    cc_df = cc_df[cc_df['fecha_corte'].isin(
        conjuntos['fechas'])].copy()

    fechas_dict = {conjuntos['fechas'][x]: x for x in range(
        len(conjuntos['fechas']))}

    cc_df['periodo'] = cc_df['fecha_corte'].map(fechas_dict)

    parametros['costos_almacenamiento'] = {
        f"CC_{cc_df.iloc[i]['key']}_{cc_df.iloc[i]['periodo']}": cc_df.iloc[i]['valor_kg'] for i in range(cc_df.shape[0])}


def __costos_transporte(parametros: dict, file: str):
    # $CF_{lm}$ : Costo fijo de transporte por camión despachado llevando la carga $l$ hasta la unidad de almacenamiento $m$.
    # $ CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.

    fletes = ['fletes_fijos', 'fletes_variables']

    for flete in fletes:

        parametros[flete] = dict()

        df = pd.read_excel(file, sheet_name=flete)

        df = df.melt(id_vars=['operador-puerto-ing'], value_vars=list(df.columns).remove(
            'operador-puerto-ing'), var_name='planta', value_name='costo')

        df['operador'] = df['operador-puerto-ing'].apply(
            lambda x: str(x).split('_')[0])

        df['ingrediente'] = df['operador-puerto-ing'].apply(
            lambda x: str(x).split('_')[1])

        df['key'] = df['operador'] + "_" + \
            df['planta'] + "_" + df['ingrediente']

        values_dict = {df.iloc[i]['key']: df.iloc[i]['costo']
                       for i in range(df.shape[0])}

        parametros[flete] = values_dict


def __venta_intercompany(parametros: dict, file: str):
    # $CW_{lm}$ : Costo de vender una carga perteneciente a una empresa a otra.

    costo_cambio_empresa_df = pd.read_excel(file, 'venta_entre_empresas')

    costo_cambio_empresa_df = costo_cambio_empresa_df.melt(
        id_vars='origen', value_vars=['contegral', 'finca'], var_name='destino')

    parametros['costo_venta_intercompany'] = {
        f"CW_{costo_cambio_empresa_df.iloc[x]['origen']}_{costo_cambio_empresa_df.iloc[x]['destino']}": costo_cambio_empresa_df.iloc[x]['value'] for x in range(costo_cambio_empresa_df.shape[0])}


def __tiempo_transporte(parametros: dict, conjuntos: dict, file: str):

    # $TT_{jk}$ : tiempo en días para transportar la carga desde el puerto $j$ hacia la planta $k$.

    parametros['tiempo_transporte'] = dict()

    for puerto in conjuntos['puertos']:
        for planta in conjuntos['plantas']:
            lista_ua = [ua for ua in conjuntos
                        ['unidades_almacenamiento'] if planta in ua.split('_')[0]]
            for ua in lista_ua:
                parametros.dict['tiempo_transporte'][f"TT_{puerto}_{ua}"] = 0


def __capacidad_almacenamiento_planta(parametros: dict, conjuntos: dict, file: str):

    # $CA_{m}^{i}$ : Capacidad de almacenamiento de la unidad $m$ en toneladas del ingrediente $i$, tenendo en cuenta que $m \in K$.

    inventario_planta_df = pd.read_excel(
        file, sheet_name='unidades_almacenamiento')

    capacidad_ua_df = inventario_planta_df.melt(id_vars=['key'], value_vars=conjuntos['ingredientes'],
                                                var_name='ingrediente', value_name='capacidad').rename(columns={'key': 'unidad_almacenamiento'})

    capacidad_ua_df.fillna(0.0, inplace=True)

    parametros['capacidad_almacenamiento_ua'] = {
        f"CA_{capacidad_ua_df.iloc[x]['ingrediente']}_{capacidad_ua_df.iloc[x]['unidad_almacenamiento']}": capacidad_ua_df.iloc[x]['capacidad'] for x in range(capacidad_ua_df.shape[0])}


def __inventario_planta(parametros: dict, file: str):

    # $II_{m}^{i}$ : Inventario inicial del ingrediente $i$ en la unidad $m$, teniendo en cuenta que $m \in K$

    inventario_planta_df = pd.read_excel(
        file, sheet_name='unidades_almacenamiento')

    parametros['inventario_inicial_ua'] = {
        f"II_{inventario_planta_df.iloc[x]['key']}_{inventario_planta_df.iloc[x]['ingrediente_actual']}": inventario_planta_df.iloc[x]['cantidad_actual'] for x in range(inventario_planta_df.shape[0])}


def __consumo_proyectado(parametros: dict, conjuntos: dict, file: str, usecols: str):

    # $DM_{ki}^{t}$: Demanda del ingrediente $i$ en la planta $k$ durante el día $t$.

    demanda_df = pd.read_excel(
        file, sheet_name='consumo_proyectado', usecols=usecols)

    demanda_df.fillna(0.0, inplace=True)

    demanda_df = demanda_df.melt(
        id_vars=['empresa', 'ingrediente', 'planta'], var_name='fecha', value_name='consumo')

    demanda_df['fecha'] = pd.to_datetime(
        demanda_df['fecha'], format='%d/%m/%Y')

    fechas_dict = {conjuntos['fechas'][x]: str(
        x) for x in range(len(conjuntos['fechas']))}

    demanda_df['periodo'] = demanda_df['fecha'].map(fechas_dict)

    campos = ['empresa', 'planta', 'ingrediente', 'periodo']

    # regenerar key
    demanda_df['key'] = demanda_df.apply(
        lambda field: '_'.join([str(field[x]) for x in campos]), axis=1)

    demanda_dict = {f"DM_{demanda_df.iloc[i]['key']}": demanda_df.iloc[i]['consumo'] for i in range(
        demanda_df.shape[0])}

    parametros['consumo_proyectado'] = demanda_dict


def __safety_stock_planta(parametros: dict, file: str):

    # $SS_{ik}^{t}$ : Inventario de seguridad a tener del ingrediente $i$ en la planta $k$ al final del día $t$.
    ss_df = pd.read_excel(file, sheet_name='consumo_proyectado')

    campos = ['empresa', 'planta', 'ingrediente']

    for campo in campos:
        ss_df[campo] = ss_df[campo].apply(__remover_underscores)

    # regenerar key
    ss_df['key'] = ss_df.apply(lambda field: '_'.join(
        [str(field[x]) for x in campos]), axis=1)

    ss_df.drop(columns=campos, inplace=True)

    ss_df.set_index(keys='key', drop=True, inplace=True)

    ss_df['SS'] = ss_df.apply(np.mean, axis=1)*10

    parametros['safety_stock'] = {
        f'SS_{k}': ss_df.loc[k]['SS'] for k in ss_df.index}


def __costo_asignacion_ingrediantes_ua(parametros: dict, file: str):

    # $CI_{im}^{t}$ : Costo de asignar el ingrediente $i$ a la unidad de almacenamiento $m$ durante el periodo $t$. Si la unidad de almacenamiento no puede contener el ingrediente, este costo será $infinito$.
    pass


def __costo_insatisfaccion_ss(parametros: dict, file: str):
    # $CS_{ik}^{t}$ : Costo de no satisfacer el inventario de seguridad para el ingrediente $i$ en la planta $k$ durante el día $t$.
    # problema.parametros['costo_no_safety_stock'] = {f'CS_{k}':1000000 for k in ss_df.index}
    pass


def __costo_insatisfaccion_demanda(parametros: dict, file: str):
    # $CD_{ik}^{t}$ : Costo de no satisfacer la demanda del ingrediente $i$  en la planta $k$ durante el día $t$.
    # problema.parametros['costo_no_demanda'] = {f'CD_{k}':10000000 for k in ss_df.index}
    pass


def __costo_backorder_planta(parametros: dict, file: str):
    # $CK_{ik}^{t}$ : Costo del backorder del ingrediente $i$  en la planta $k$ durante el día $t$.
    # problema.parametros['costo_backorder'] = {f'CK_{k}':10000 for k in ss_df.index}
    pass


def __transitos_programados_hacia_planta(parametros: dict, file: str):
    # $TR_{im}^{t}$ : Cantidad en tránsito programada para llegar a la unidad de almacenamiento $m$ durante el día $t$,
    pass


def generar_parametros(parametros: dict, conjuntos: dict, file: str, usecols: str) -> dict:

    __inventario_inicial_puerto(parametros=parametros, file=file)

    __llegadas_a_puerto(parametros=parametros, conjuntos=conjuntos, file=file)

    __costo_almacenamiento_puerto(
        parametros=parametros, conjuntos=conjuntos, file=file)

    __costos_transporte(parametros=parametros, file=file)

    __venta_intercompany(parametros=parametros, file=file)

    __tiempo_transporte(parametros=parametros, conjuntos=conjuntos, file=file)

    __capacidad_almacenamiento_planta(
        parametros=parametros, conjuntos=conjuntos, file=file)

    __inventario_planta(parametros=parametros, file=file)

    __consumo_proyectado(parametros=parametros,
                         conjuntos=conjuntos, file=file, usecols=usecols)

    __safety_stock_planta(parametros=parametros, file=file)

    __costo_asignacion_ingrediantes_ua(parametros=parametros, file=file)

    __costo_insatisfaccion_ss(parametros=parametros, file=file)

    __costo_insatisfaccion_demanda(parametros=parametros, file=file)

    __costo_backorder_planta(parametros=parametros, file=file)

    __transitos_programados_hacia_planta(parametros=parametros, file=file)
