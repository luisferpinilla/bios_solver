from problema.problema import Problema
from modelo.validador import Validador
from modelo.visor_parametros import visor_parametros
import streamlit as st
import pandas as pd
import pulp as pu
import os

loaded = False
validated = False


def solicitar_archivo():

    st.write('Seleccionar un archivo para trabajar')

    file = st.file_uploader("Choose a file")

    return file


def validar_archivo(loaded_file: str) -> str:

    validador = Validador(file=loaded_file)

    validador.ejecutar_validaciones()

    with st.expander(label="Resultado de validaciones de forma", expanded=validador.cantidad_errores > 0):

        for k, v in validador.validaciones.items():

            if "OK" in v:
                st.success(f'{k}: {v}', icon="✅")

            else:
                st.error(f'{k}: {v}', icon="🚨")

        if validador.cantidad_errores == 0:
            return 'ok'
        else:
            return 'errors'


def solicitar_parametros_ejecucion():

    with st.form('Configure los siguientes parámetros'):

        tmax = st.slider(label='Tiempo máximo de trabajo en minutos',
                         min_value=5,
                         max_value=60,
                         value=15)

        submitted = st.form_submit_button("Ejecutar Modelo")

    if submitted:

        return tmax


def generar_problema(archivo: str) -> Problema:

    with st.spinner(text='Leyendo archivo'):
        problema = Problema(file=archivo)

    return problema


def ejecutar_modelo(problema: Problema, t_max_minutos=float):

    with st.spinner(text=f'Ejecutando con {t_max_minutos} minutos'):

        estatus = problema.solve(t_limit_minutes=t_max_minutos)

    if estatus != 'Optimal':
        st.error(f'El solucionador reporta {estatus}')
    else:
        st.success(estatus)

    st.session_state['problema'] = problema

    st.session_state['solucion_status'] = estatus


st.set_page_config(
    page_title="BIOS",
    page_icon="👋",
    layout="wide"
)

st.write("# Bienvenido al Optimizador Logístico de Materias Primas Importadas")

st.write('Seleccionar un archivo para trabajar')

file = st.file_uploader("Choose a file")

if file:

    validado = validar_archivo(file)

    if validado:

        if validado == 'ok':

            problema = generar_problema(file)

            tmax = solicitar_parametros_ejecucion()

            if tmax:

                ejecutar_modelo(problema=problema, t_max_minutos=tmax)

    else:
        file = None
        st.error('Debe validar y volver a cargar el archivo')
