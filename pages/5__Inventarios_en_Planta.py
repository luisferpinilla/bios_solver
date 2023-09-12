import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.write('# Inventarios en Planta')

st.button(label='callback')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    problema = st.session_state['problema']

    solucion = problema.generar_reporte()

    df = solucion['Almacenamiento en Planta']

    st.write('## Inventarios en Planta')

    col1, col2 = st.columns(2)

    with col1:

        ingredientes_list = ['Todos'] + list(df['ingrediente'].unique())

        ingrediente = st.selectbox(
            label='Ingredientes', options=ingredientes_list)

        if ingrediente != 'Todos':
            df = df[df['ingrediente'] == ingrediente]

    with col2:

        plantas_list = ['Todos'] + list(df['planta'].unique())

        planta = st.selectbox(label='Plantas', options=plantas_list)

        if planta != 'Todos':

            df = df[df['planta'] == planta]

    st.write(df)
