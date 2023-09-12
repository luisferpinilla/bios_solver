import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.write('# Inventarios en Puerto')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    st.button(label='callback')

    problema = st.session_state['problema']

    solucion = problema.generar_reporte()

    st.write('## Inventarios en Puerto al final del día')

    df = solucion['Inventario en Puerto']

    df = df.reset_index()

    df = df.sort_values(
        ['empresa', 'ingrediente', 'operador', 'importacion', 'variable'])

    ingrediente_list = ['Todos'] + list(df['ingrediente'].unique())

    ingrediente = st.selectbox(label='Ingredientes', options=ingrediente_list)

    if ingrediente != 'Todos':
        df = df[df['ingrediente'] == ingrediente]

    df = df.set_index(['empresa', 'ingrediente', 'operador',
                      'importacion', 'variable']).fillna(0.0)

    st.write(df)
