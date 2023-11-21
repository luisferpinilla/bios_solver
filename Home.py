from modelo.problema import Problema
from modelo.validador import Validador
from modelo.visor_parametros import visor_parametros
import streamlit as st
import pandas as pd


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

    problema = Problema(excel_file_path=archivo)

    progress_bar = st.progress(value=0, text='Generando conjuntos')

    problema.generar_sets()

    progress_bar.progress(value=20, text='Generando lista de parámetros')

    problema.generar_parameters()

    progress_bar.progress(value=40, text='Generando lista de variables')

    problema.generar_vars()

    progress_bar.progress(value=60, text='Construyendo lista de restricciones')

    problema.gen_constrains()

    progress_bar.progress(value=80, text='Construyendo función objetivo')

    problema.generar_target()

    progress_bar.progress(
        value=100, text='Problema Generado')

    return problema


def ejecutar_modelo(problema: Problema, t_max_minutos=float, gap_minimo=0.025):

    with st.spinner(text='Ejecutando'):
        problema.solve(
            engine='coin', tlimit_seconds=t_max_minutos*60, gap=gap_minimo)

    if problema.estatus != 'Optimal':
        st.error(f'El solucionador reporta {problema.estatus}')
    else:
        st.success(problema.estatus)

    st.session_state['problema'] = problema

    st.session_state['solucion_status'] = problema.estatus


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

            df = visor_parametros(
                conjuntos=problema.conjuntos, parametros=problema.parametros)

            if df.shape[0] > 0:

                with st.expander(label='Valicacion de capacidades y cantidades', expanded=True):

                    df = df[['consumo_medio_kg',
                            'ss_kg',
                             'ss_dias',
                             'capacidad_kg',
                             'capacidad_dias',
                             'capacidad_recepcion_kg',
                             'capacidad_recepcion_dias',
                             'Val0', 'Val1', 'Val2', 'Val3']]

                    st.write(df)

                    st.write(
                        'Val0: La capacidad de almacenamiento de la planta es 0')
                    st.write(
                        'Val1: Si el inventario de seguridad supera la capacidad')
                    st.write(
                        'Val2: La capacidad de recepción es inferior a 34 Toneladas')
                    st.write(
                        'Val3: La capacidad asignada no es suficiente para guardar un inventario de seguridad más un camión')
            tmax = solicitar_parametros_ejecucion()

            if tmax:

                ejecutar_modelo(problema=problema,
                                gap_minimo=0.02, t_max_minutos=60*tmax)

    else:
        file = None
        st.error('Debe validar y volver a cargar el archivo')
