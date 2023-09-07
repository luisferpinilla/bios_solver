import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.write('# Despachos desde puerto')

if not 'solucion' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    st.button(label='callback')

    solucion = st.session_state['solucion']

    df = solucion['Despacho directo']

    df = df[df['kilos_despachados'] > 0]

    st.write('## Despachos directos')

    st.write(df)

    df = solucion['Despacho desde Bodega']

    df = df[df['kilos_despachados'] > 0]

    st.write('## Despachos desde bodega en puerto')

    st.write(df)
