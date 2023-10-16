import streamlit as st
import pandas as pd
import numpy as np
from modelo.reporte import Reporte


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep=';', decimal=',').encode('utf-8')


st.set_page_config(layout="wide")

st.write('# Inventarios en Planta')

# st.button(label='callback')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    problema = st.session_state['problema']

    reporte = Reporte(problema=problema)

    df = reporte.obtener_fact_inventario_planta()

    st.write('## Inventarios en Planta')

    # st.write(df)

    col1, col2 = st.columns(2)

    with col1:

        # ingredientes_list = ['Todos'] + list(df['ingrediente'].unique())
        ingredientes_list = list(df['ingrediente'].unique())

        ingrediente = st.selectbox(
            label='Ingredientes', options=ingredientes_list)

        # if ingrediente != 'Todos':
        df = df[df['ingrediente'] == ingrediente]

    with col2:

        # plantas_list = ['Todos'] + list(df['planta'].unique())
        plantas_list = list(df['planta'].unique())

        planta = st.selectbox(label='Plantas', options=plantas_list)

        if planta != 'Todos':

            df = df[df['planta'] == planta]

    df.set_index(['empresa', 'planta', 'ingrediente', 'item'], inplace=True)

    st.write(df)

    csv = convert_df(df)

    st.download_button(label='descargar reporte',
                       data=csv,    file_name='inventario_planta.csv',    mime='text/csv')
