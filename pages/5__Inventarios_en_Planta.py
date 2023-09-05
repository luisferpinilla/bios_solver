import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.write('# Inventarios en Planta')

if not 'solucion' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    st.button(label='callback')

    solucion = st.session_state['solucion']

    df = solucion['Almacenamiento en Planta']

    df = df[df['value'] > 0]

    df = df.pivot_table(index=['planta', 'ingrediente', 'unidad'],
                        columns='periodo', values='value', aggfunc=sum).reset_index()

    st.write('## Inventarios en Planta')

    col1, col2 = st.columns(2)

    with col1:

        ingredientes_list = list(df['ingrediente'].unique())

        ingredientes = st.multiselect(
            label='Ingredientes', options=ingredientes_list, default=ingredientes_list)

    with col2:

        plantas_list = list(df['planta'].unique())

        plantas = st.multiselect(
            label='Plantas', options=plantas_list, default=plantas_list)

    st.write('### Inventarios al final del día')
    st.write(df[(df['ingrediente'].isin(ingredientes))
             & (df['planta'].isin(plantas))])

    st.write('## Backorder')

    df = solucion['Backorder']

    # df = df[df['value'] > 0]

    df = df.pivot_table(index=['ingrediente', 'planta'],
                        columns='periodo', values='Backorder', aggfunc=sum).reset_index()

    st.write(df)
