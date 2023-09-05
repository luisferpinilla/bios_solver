import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.write('# Inventarios en Puerto')

if not 'solucion' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    st.button(label='callback')

    solucion = st.session_state['solucion']

    df = solucion['Inventario en Puerto']

    df = df[df['value'] > 0]

    st.write('## Inventarios en Puerto')

    st.write(df)
