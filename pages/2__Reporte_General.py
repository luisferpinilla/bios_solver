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


def _periodos(solucion: dict) -> pd.DataFrame:

    periodos = solucion['periodos']
    periodos.rename(
        columns={'nombre_variable': 'periodo', 'valor': 'fecha'}, inplace=True)

    periodos = periodos[['periodo', 'fecha']]

    periodos['periodo'] = periodos['periodo'].apply(lambda x: str(x))

    periodos['fecha'] = periodos['fecha'].apply(
        lambda x: f'{x.year}-{x.month}-{x.day}')

    return periodos


def __reporte_costo_almacenamiento(solucion: dict) -> pd.DataFrame:

    inventario_df = solucion['XIP']

    periodos_df = _periodos(solucion=solucion)

    costos_df = solucion['costos_almacenamiento']

    inventario_df = inventario_df[['empresa', 'puerto', 'motonave',
                                  'ingrediente', 'periodo', 'valor']].rename(columns={'valor': 'toneladas almacenadas'})

    costos_df = costos_df[['empresa', 'puerto', 'motonave',
                          'ingrediente', 'periodo', 'valor']].rename(columns={'valor': 'costo por tonelada'})

    df = pd.merge(left=inventario_df,
                  right=costos_df,
                  how='left',
                  left_on=['empresa', 'puerto', 'motonave',
                           'ingrediente', 'periodo'],
                  right_on=['empresa', 'puerto', 'motonave',
                            'ingrediente', 'periodo']).fillna(0.0)

    df = pd.merge(left=df,
                  right=periodos_df,
                  how='left',
                  left_on=['periodo'],
                  right_on=['periodo'])

    df['Costo total'] = df['costo por tonelada']*df['toneladas almacenadas']

    return df


def __reporte_costo_transporte(solucion: dict) -> pd.DataFrame:

    transporte_directo_df = solucion['XTD']
    transporte_bodega_df = solucion['XTR']

    fletes_fijos_df = solucion['fletes_fijos']
    fletes_fijos_df = fletes_fijos_df[['puerto', 'planta', 'valor']]
    fletes_fijos_df.rename(columns={'valor': 'costo fijo'}, inplace=True)

    fletes_variables_df = solucion['fletes_variables']
    fletes_variables_df = fletes_variables_df[['puerto', 'planta', 'valor']]
    fletes_variables_df.rename(
        columns={'valor': 'costo por tonelada'}, inplace=True)

    periodos_df = _periodos(solucion=solucion)

    # Ventas intercompany
    intercompany_df = solucion['costo_venta_intercompany']

    intercompany_df.rename(
        columns={'valor': 'costo intercompany'}, inplace=True)

    intercompany_df['empresa_origen'] = intercompany_df['nombre_variable'].apply(
        lambda x: str(x).split('_')[1])
    intercompany_df['empresa_destino'] = intercompany_df['nombre_variable'].apply(
        lambda x: str(x).split('_')[2])

    intercompany_df = intercompany_df[[
        'empresa_origen', 'empresa_destino', 'costo intercompany']]

    # unir ambos despachos de transporte en uno solo
    df = pd.concat([transporte_bodega_df, transporte_directo_df])
    # eliminar ceros inneceesarios
    df = df[df['valor'] > 0.0]

    # cambiar nombre para evitar conflictos
    df.rename(columns={'valor': 'Toneladas despachadas'}, inplace=True)

    # unir los desapchos con los valores de fletes
    df = pd.merge(left=df, right=intercompany_df, how='left',
                  left_on=['empresa_origen', 'empresa_destino'],
                  right_on=['empresa_origen', 'empresa_destino'])

    df = pd.merge(left=df, right=fletes_fijos_df, how='left',
                  left_on=['puerto', 'planta'],
                  right_on=['puerto', 'planta'])

    df = pd.merge(left=df, right=fletes_variables_df, how='left',
                  left_on=['puerto', 'planta'],
                  right_on=['puerto', 'planta'])

    df = pd.merge(left=df, right=periodos_df, how='left',
                  left_on=['periodo'],
                  right_on=['periodo'])

    df.fillna(0.0, inplace=True)

    # calcular costo de envio
    df['Costo Total Transporte'] = df['costo fijo'] + \
        df['costo por tonelada']*df['Toneladas despachadas']

    # Calcular intercompany
    df['Costo Total Intercompany'] = df['Toneladas despachadas'] * \
        df['costo intercompany']

    # reordenar para presentación
    df = df[['empresa_origen', 'empresa_destino', 'puerto', 'motonave', 'ingrediente', 'planta', 'Toneladas despachadas', 'fecha',
             'costo fijo', 'costo por tonelada', 'Costo Total Transporte', 'costo intercompany', 'Costo Total Intercompany']]

    return df


def __backorder(solucion: dict) -> pd.DataFrame:

    backorder_df = solucion['XBK']

    renamer = {'ingrediente': 'Empresa',
               'empresa': 'Planta', 'planta': 'Ingrediente'}

    # Renombrar columnas
    backorder_df.rename(columns=renamer, inplace=True)

    backorder_df['Variable'] = 'Backorder esperado'

    backorder_df = backorder_df.pivot_table(index=['Variable', 'Planta', 'Ingrediente'],
                                            columns='periodo', values='valor', aggfunc=np.sum).reset_index()

    return backorder_df


def __inventario_planta_arrivals(solucion: dict) -> pd.DataFrame:

    df = pd.concat([solucion['XTD'], solucion['XTR']])

    df = df.pivot_table(values='valor', index=[
                        'ingrediente', 'planta', 'unidad_almacenamiento'], columns='periodo', aggfunc=np.sum).reset_index()

    df.rename(columns={'ingrediente': 'Ingrediente',
                       'empresa_destino': 'Empresa',
                       'planta': 'Planta',
                       'unidad_almacenamiento': 'Unidad'}, inplace=True)

    df['Variable'] = 'Llegadas desde puerto'

    return df


def __safety_stock(solucion: dict) -> pd.DataFrame:

    ss_df = solucion['BSS']

    # Renombrar columnas
    # ss_df.rename(columns=renamer, inplace=True)

    ss_df['Variable'] = 'Cumple SS'

    ss_df = ss_df.pivot_table(index=['Variable', 'Planta', 'Ingrediente'],
                              columns='periodo', values='valor', aggfunc=np.sum).reset_index()

    return ss_df


def __safety_stock_valor(solucion: dict) -> pd.DataFrame:

    ss_df = solucion['safety_stock']

    d_renamer = {'unidad_almacenamiento': 'Unidad',
                 'planta': 'Planta',
                 'ingrediente': 'Ingrediente'}

    # Renombrar columnas
    ss_df.rename(columns=d_renamer, inplace=True)

    ss_df['Variable'] = 'Valor SS'

    # st.write(ss_df)

    # ss_df = ss_df.groupby(['Variable', 'Planta', 'Ingrediente']
    #                          columns='periodo', values='valor', aggfunc=np.sum).reset_index()

    return ss_df


def _preparar_inventario_planta(solucion: dict) -> pd.DataFrame:

    # Columnas a mostrar:
    # Ingrediente | Planta | Unidad | Variable | periodos ->

    demanda_stock_df = formatear(
        solucion=solucion, parametro='XDM', variable='Demanda durante el día')

    inventario_planta_df = formatear(
        solucion=solucion, parametro='XIU', variable='Inventario al final del día')

    arrivals_df = __inventario_planta_arrivals(solucion=solucion)

    safety_stock_df = formatear(
        solucion=solucion, parametro='BSS', variable='Cumple inventario al final del día')

    safety_stock_df = __safety_stock(solucion=solucion)

    # ss_valor_df = __safety_stock_valor(solucion=solucion)

    backorder_df = __backorder(solucion=solucion)

    consumo_proyectado_df = formatear(
        solucion=solucion, parametro='consumo_proyectado', variable='Demanda Total')

    inventario_to_show = pd.concat(
        [demanda_stock_df,
         arrivals_df,
         inventario_planta_df,
         consumo_proyectado_df,
         safety_stock_df,
         # ss_valor_df,
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

    tab1, tab2, tab3, tab4 = st.tabs(
        ['Inventario Planta', 'Despachos desde Puerto', 'Inventario Puerto', 'Reporte de Costos'])

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

    with tab4:

        st.markdown('## Costeo de la propuesta de despacho')

        with st.expander(label='Configuraciones', expanded=False):
            mostrar_detalle_almacenamiento = st.checkbox(
                label='Mostrar todos los registros de corte de inventario')

        costos_almacenamiento_df = __reporte_costo_almacenamiento(
            solucion=solucion)

        costos_transporte_df = __reporte_costo_transporte(solucion=solucion)

        if not mostrar_detalle_almacenamiento:
            costos_almacenamiento_df = costos_almacenamiento_df[
                costos_almacenamiento_df['costo por tonelada'] > 0.0]

        tab4_col1, tab4_col2, tab4_col3, tab4_col4, tab4_col5 = st.columns(5)

        with tab4_col1:
            costo_total_almacenamiento = costos_almacenamiento_df['Costo total'].sum(
            )
            st.metric(label='Costo total almacenamiento',
                      value=costo_total_almacenamiento, help='Valor total a las fechas de corte')

        with tab4_col2:
            costo_transporte = costos_transporte_df['Costo Total Transporte'].sum(
            )
            st.metric(label='Costo total transporte',
                      value=costo_transporte, help='Costo fijo más variable')

        with tab4_col3:
            costo_intercompany = costos_transporte_df['Costo Total Intercompany'].sum(
            )
            st.metric(label='Costo venta intercompany',
                      value=costo_intercompany, help='Costo fijo más variable')

        with tab4_col4:
            toneladas_despachadas = costos_transporte_df['Toneladas despachadas'].sum(
            )
            st.metric(label='Total toneladas despachadas',
                      value=toneladas_despachadas,
                      help='Toneladas despachadas en 30 días')

        with tab4_col5:
            costo_total_relevante = costo_total_almacenamiento + \
                costo_transporte + costo_intercompany
            st.metric(label='Costo total relevante', value=costo_total_relevante,
                      help='Toneladas despachadas en 30 días')

        st.button('callback')

        st.markdown('### Detalle de costo de almacenamiento')
        st.write(costos_almacenamiento_df)

        st.markdown('### Detalle del costo de transporte')
        st.write(costos_transporte_df)
