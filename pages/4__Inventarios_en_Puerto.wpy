import streamlit as st
import pandas as pd
import numpy as np
from modelo.reporte import Reporte

st.set_page_config(layout="wide")

st.write('# Inventarios en Puerto')


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep=';', decimal=',').encode('utf-8')


if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    # st.button(label='callback')

    problema = st.session_state['problema']

    reporte = Reporte(problema=problema)

    df = reporte.obtener_fact_inventario_puerto()

    st.write('## Inventarios en Puerto al final del día')

    ingrediente_column, operador_column, importacion_column  = st.columns(3)

    with ingrediente_column:

        ingrediente_list = ['Todos'] + list(df['ingrediente'].unique())

        ingrediente = st.selectbox(
            label='Ingredientes', options=ingrediente_list)

        if ingrediente != 'Todos':
            df = df[df['ingrediente'] == ingrediente]

    with operador_column:

        operador_list = ['Todos'] + list(df['operador'].unique())

        operador = st.selectbox(label='Operador', options=operador_list)

        if operador != 'Todos':
            df = df[df['operador'] == operador]

    with importacion_column:

        importacion_list = ['Todos'] + list(df['importacion'].unique())

        importacion = st.selectbox(
            label='Importacion', options=importacion_list)

        if importacion != 'Todos':
            df = df[df['importacion'] == importacion]

    with st.expander(label='Item Selector'):

        item_list = list(df['item'].unique())

        item = st.multiselect(label='Item', options=item_list, default=item_list)

        if item != 'Todos':
            df = df[df['item'].isin(item)]

    df.set_index(['empresa', 'operador', 'importacion',
                 'ingrediente', 'item'], inplace=True)

    st.write(df)

    csv = convert_df(df)

    st.download_button(label='descargar reporte',
                       data=csv,    file_name='inventario_puerto.csv',    mime='text/csv')
