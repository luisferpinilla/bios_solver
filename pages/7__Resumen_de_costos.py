import streamlit as st


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep=';', decimal=',').encode('utf-8')


st.set_page_config(layout="wide")

st.write('# Resumen de costos')

st.button(label='callback')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    with st.spinner(text='Construyendo reporte'):

        problema = st.session_state['problema']

        solucion = problema.generar_reporte()

        # problema.guardar_reporte()

        ca_df = solucion['costo_almacenamiento']

        ca_df['costo_almacenamiento'] = ca_df['costo_almacenamiento'].apply(
            lambda x: round(x, 0))
        ca_df['kilos'] = ca_df['kilos'].apply(
            lambda x: round(x, 0))

        ca_df['costo_kilo'] = ca_df['costo_kilo'].apply(
            lambda x: round(x, 2))

        coa_df = solucion['Costo_operacion_almacenamiento']

        coa_df['cantidad_kg'] = coa_df['cantidad_kg'].apply(
            lambda x: round(x, 0))

        coa_df['costo_op_almacenamiento'] = coa_df['costo_op_almacenamiento'].apply(
            lambda x: round(x, 2))

        coa_df['CostoTotal'] = coa_df['CostoTotal'].apply(
            lambda x: round(x, 0))

        coa_df = coa_df[coa_df['CostoTotal'] > 0]

        cod_df = solucion['Costo_operacion_despacho']

        cod_df['CostoTotal'] = cod_df['CostoTotal'].apply(
            lambda x: round(x, 0))

        cod_df = cod_df[cod_df['CostoTotal'] > 0]

        cftd_df = solucion['costos_transporte']

        cftd_df['CostoTotal'] = cftd_df['CostoTotal'].apply(
            lambda x: round(x, 0))

        cftd_df = cftd_df[cftd_df['CostoTotal'] > 0]

        costo_almacenamiento_col, costo_op_alacenamiento_col, costo_op_despacho_col, costo_flete_col = st.columns(
            4)

        with costo_almacenamiento_col:

            costo_almacenamiento = ca_df['costo_almacenamiento'].sum()

            st.metric(label='Costos de Almacenamiento',
                      value=f"{round(costo_almacenamiento/1000000,0)} MM")

        with costo_op_alacenamiento_col:

            costo_op_alacenamiento = coa_df['CostoTotal'].sum()

            st.metric(label="Descarge a bodega",
                      value=f"{round(costo_op_alacenamiento/1000000, 2)} MM")

        with costo_op_despacho_col:

            costo_op_despacho = cod_df['CostoTotal'].sum()

            st.metric(label="Operación despacho",
                      value=f"{round(costo_op_despacho/1000000, 2)} MM")

        with costo_flete_col:

            costo_transporte = cftd_df['CostoTotal'].sum()

            st.metric(label="Costos de transporte",
                      value=f"{round(costo_transporte/1000000, 2)} MM")

            costo_total = costo_almacenamiento + costo_op_alacenamiento + \
                costo_op_despacho + costo_transporte

            st.metric(label="Costos Total",
                      value=f"{round(costo_total/1000000, 2)} MM")

        with st.expander(label='Costos de almacenamiento'):
            st.write(ca_df)

            csv = convert_df(ca_df)

            st.download_button(label='descargar reporte',
                               data=csv,    file_name='data.csv',    mime='text/csv')

        with st.expander(label='Descarge a bodega'):

            st.write(coa_df)

            csv2 = convert_df(coa_df)

            st.download_button(label='descargar reporte',
                               data=csv2,    file_name='data.csv',    mime='text/csv')

        with st.expander(label='Operación despacho'):

            st.write(cod_df)

            csv3 = convert_df(cod_df)

            st.download_button(label='descargar reporte',
                               data=csv3,    file_name='data.csv',    mime='text/csv')

        with st.expander(label='Costos de transporte'):

            st.write(cftd_df)

            csv3 = convert_df(cftd_df)

            st.download_button(label='descargar reporte',
                               data=csv3,    file_name='data.csv',    mime='text/csv')
