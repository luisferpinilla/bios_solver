import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.write('# Plan propuesto de despachos')


def formatear(solucion: str, parametro: str, variable: str) -> pd.DataFrame:

    d_renamer = {'unidad_almacenamiento': 'Unidad',
                 'planta': 'Planta',
                 'ingrediente': 'Ingrediente'}

    values = 'valor'

    index_temp = ['Variable',
                  'Planta',
                  'Ingrediente',
                  'Unidad']

    column = 'periodo'

    df = solucion[parametro]

    df['Variable'] = variable

    df.rename(columns=d_renamer, inplace=True)

    index = [x for x in df.columns if x in index_temp]

    df = df.pivot_table(index=index, columns=column,
                        values=values, aggfunc=np.sum).reset_index()

    return df


def __backorder(solucion: dict) -> pd.DataFrame:

    backorder_df = solucion['XBK']

    renamer = {'ingrediente': 'Empresa',
               'empresa': 'Planta', 'planta': 'Ingrediente', }

    # Renombrar columnas
    backorder_df.rename(columns=renamer, inplace=True)

    backorder_df['Variable'] = 'Backorder esperado'

    backorder_df = backorder_df.pivot_table(index=['Variable', 'Planta', 'Ingrediente'],
                                            columns='periodo', values='valor', aggfunc=np.sum).reset_index()

    st.write(backorder_df)

    return backorder_df


def _preparar_inventario_planta(solucion):

    # Columnas a mostrar:
    # Ingrediente | Planta | Unidad | Variable | periodos ->

    demanda_stock_df = formatear(
        solucion=solucion, parametro='XDM', variable='Demanda durante el día')

    inventario_planta_df = formatear(
        solucion=solucion, parametro='XIU', variable='Inventario al final del día')

    safety_stock_df = formatear(
        solucion=solucion, parametro='BSS', variable='Cumple inventario al final del día')

    safety_stock_pr_df = formatear(
        solucion=solucion, parametro='safety_stock', variable='safety stock')

    backorder_df = __backorder(solucion=solucion)

    consumo_proyectado_df = formatear(
        solucion=solucion, parametro='consumo_proyectado', variable='Demanda Total')

    inventario_to_show = pd.concat(
        [demanda_stock_df,
         inventario_planta_df,
         consumo_proyectado_df,
         safety_stock_df,
         backorder_df])

    inventario_to_show.sort_values(['Planta',
                                    'Ingrediente',
                                    'Unidad', 'Variable'], inplace=True)

    inventario_to_show['Unidad'].fillna('--', inplace=True)

    return inventario_to_show


if not 'solucion' in st.session_state.keys():

    st.write('Go to Main page and load a file')

else:

    solucion = st.session_state['solucion']

    tab1, tab2, tab3 = st.tabs(
        ['Inventario Planta', 'Despachos desde Puerto', 'Inventario Puerto'])

    with tab1:

        inventario_to_show = _preparar_inventario_planta(solucion=solucion)

        tab1_col1, tab1_col2 = st.columns(2)

        with tab1_col1:
            planta = st.selectbox(label='Planta', options=['all']+list(
                inventario_to_show['Planta'].unique()))

        with tab1_col2:
            ingredientes = st.selectbox(label='Ingrediente', options=['all']+list(
                inventario_to_show['Ingrediente'].unique()))

        if planta != 'all':
            inventario_to_show = inventario_to_show[inventario_to_show['Planta'] == planta]
            inventario_to_show.drop(['Planta'], axis=1, inplace=True)

        if ingredientes != 'all':
            inventario_to_show = inventario_to_show[inventario_to_show['Ingrediente'] == ingredientes]
            inventario_to_show.drop(['Ingrediente'], axis=1, inplace=True)

        st.write(inventario_to_show)

    despachos_df = pd.concat([solucion['XTR'], solucion['XTD']])

    despachos_df = despachos_df[despachos_df['valor'] > 0]

    despachos_df['tipo'] = despachos_df['tipo'].map(
        {'XTD': 'Directo Barco->Planta', 'XTR': 'Bodega Puerto->Planta'})

    despachos_df['Intercompany'] = despachos_df.apply(
        lambda x: 'Sí' if x['empresa_origen'] == x['empresa_destino'] else 'No', axis=1)

    despachos_df = despachos_df[['tipo', 'ingrediente', 'empresa_origen', 'puerto', 'Intercompany',
                                 'planta', 'unidad_almacenamiento', 'periodo', 'valor']]

    with tab2:

        tab2_col1, tab2_col2, tab2_col3, tabl2_col4 = st.columns(4)

        with tab2_col1:
            empresa_origen = st.selectbox(label='Empresa propietaria', options=['all']+list(
                despachos_df['empresa_origen'].unique()))

        with tab2_col2:
            ingrediente_despachado = st.selectbox(
                label='Ingrediente Despachado', options=['all']+list(despachos_df['ingrediente'].unique()))

        with tab2_col3:
            planta_destino = st.selectbox(
                label='Planta Destino', options=['all']+list(despachos_df['planta'].unique()))

        with tabl2_col4:
            intercompany = st.selectbox(
                label='Intercompany?', options=['all']+list(despachos_df['Intercompany'].unique()))

            despachos_to_show = despachos_df.copy()

        if empresa_origen != 'all':
            despachos_to_show = despachos_to_show[despachos_to_show['empresa_origen'] == empresa_origen].copy(
            )

        if ingrediente_despachado != 'all':
            despachos_to_show = despachos_to_show[despachos_to_show['ingrediente']
                                                  == ingrediente_despachado].copy()

        if planta_destino != 'all':
            despachos_to_show = despachos_to_show[despachos_to_show['planta'] == planta_destino].copy(
            )

        if intercompany != 'all':
            despachos_to_show = despachos_to_show[despachos_to_show['Intercompany'] == intercompany].copy(
            )

        despachos_to_show = despachos_to_show.pivot_table(index=['tipo', 'ingrediente', 'empresa_origen', 'puerto', 'Intercompany',
                                                                 'planta'],
                                                          columns='periodo',
                                                          values='valor', aggfunc=np.sum)

        st.write(despachos_to_show)

    with tab3:

        inventario_puerto_df = solucion['XIP']

        inventario_puerto_df['Variable'] = 'Inventario en Puerto'

        st.write(inventario_puerto_df)
