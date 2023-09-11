import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.write('# Despachos desde puerto')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    problema = st.session_state['problema']

    st.button(label='callback')

    solucion = problema.generar_reporte()

    df = solucion['Despacho directo']

    st.write('## Despachos directos')

    st.write(df)

    df = solucion['Despacho desde Bodega']

    st.write('## Despachos desde bodega en puerto')

    st.write(df)
