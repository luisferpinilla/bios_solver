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

    # col1, col2 = st.columns(2)

    # with col1:

    # ingredientes_list = list(df['ingrediente'].unique())

    # ingredientes = st.selectbox(
    #    label='Ingredientes', options=ingredientes_list)

    # with col2:

    #    plantas_list = list(df['planta'].unique())

    #   plantas = st.selectbox(label='Plantas', options=plantas_list)

    st.write('### Inventarios al final del día')
    # st.write(df[(df['ingrediente'] == ingredientes)
    #         & (df['planta'] == plantas)])

    st.write(df)
    st.write('## Backorder')

    df = solucion['Backorder']

    # df = df[df['value'] > 0]

    # df = df.pivot_table(index=['ingrediente', 'planta'],
    #                    columns='periodo', values='Backorder', aggfunc=sum).reset_index()

    # st.write(df[(df['ingrediente'] == ingredientes)
    #         & (df['planta'] == plantas)])
