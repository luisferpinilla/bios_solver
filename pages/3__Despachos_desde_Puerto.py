import streamlit as st
import pandas as pd
import numpy as np


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep=';', decimal=',').encode('utf-8')


st.set_page_config(layout="wide")

st.write('# Despachos desde puerto')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    problema = st.session_state['problema']

    st.button(label='callback')

    solucion = problema.generar_reporte()

    st.write('## Despachos directos')

    col1, col2 = st.columns(2)

    df = solucion['Despacho directo'].reset_index()

    with col1:

        operadores_list = ['Todos'] + list(df['operador'].unique())

        operador = st.selectbox(label='operador', options=operadores_list)

        if operador != 'Todos':
            df = df[df['operador'] == operador]

    with col2:

        ingredientes_list = ['Todos'] + list(df['ingrediente'].unique())

        ingrediente = st.selectbox(
            label='Ingredientes', options=ingredientes_list)

        if ingrediente != 'Todos':
            df = df[df['ingrediente'] == ingrediente]

    df.set_index(['empresa_origen', 'operador', 'ingrediente',
                 'importacion', 'fecha despacho'], inplace=True)

    st.write(df)

    csv = convert_df(df)

    st.download_button(label='descargar reporte',
                       data=csv,    file_name='despacho_directo.csv',    mime='text/csv')

    st.write('## Despachos desde bodega en puerto')

    df = solucion['Despacho indirecto'].reset_index()

    col1, col2 = st.columns(2)

    with col1:

        operadores_list = ['Todos'] + list(df['operador'].unique())

        print(operadores_list)

        operador = st.selectbox(label='operador', options=operadores_list)

        if operador != 'Todos':
            df = df[df['operador'] == operador]

    with col2:

        ingredientes_list = ['Todos'] + list(df['ingrediente'].unique())

        ingrediente = st.selectbox(
            label='Ingredientes', options=ingredientes_list)

        if ingrediente != 'Todos':

            df = df[df['ingrediente'] == ingrediente]

    df.set_index(['empresa_origen', 'operador', 'ingrediente',
                 'importacion', 'fecha despacho'], inplace=True)

    st.write(df)

    csv2 = convert_df(df)

    st.download_button(label='descargar reporte',
                       data=csv2,    file_name='despacho_bodega.csv',    mime='text/csv')
