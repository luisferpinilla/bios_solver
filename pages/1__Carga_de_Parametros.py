from modelo.problema import Problema
from modelo.validador import Validador
import streamlit as st

st.set_page_config(layout="wide")

st.title('Visualizador BIOS')

col2, col3 = st.columns(2)

# with col1:
#    motor_solucion = st.radio(
#        label='Seleccione un motor de solución', options=['coin', 'glpk'])

with col2:
    tmax = st.slider(label='Tiempo máximo de trabajo en minutos',
                     min_value=1, max_value=30, value=15)

with col3:
    gap_solver = st.slider(label='Porcentaje GAP',
                           min_value=1, max_value=20, value=5)

uploaded_file = st.file_uploader("Choose a file")

st.session_state['upload_file'] = uploaded_file

file = uploaded_file

if file is None:

    st.write('Debe seleccionar un archivo')

else:

    validador = Validador(file=file)

    validador.ejecutar_validaciones()

    with st.expander(label="Resultado de validaciones", expanded=validador.cantidad_errores > 0):

        for k, v in validador.validaciones.items():

            if "OK" in v:
                st.success(f'{k}: {v}', icon="✅")
            else:
                st.error(f'{k}: {v}', icon="🚨")

    st.button(label='callback')

    if validador.cantidad_errores == 0:

        problema = Problema(excel_file_path=file)

        cols_consumo_proyectado_periods = 'B:R'

        progress_bar = st.progress(value=0, text='Generando conjuntos')

        problema.generar_sets()

        progress_bar.progress(value=5, text='Generando lista de parámetros')

        problema.generar_parameters()

        progress_bar.progress(value=20, text='Generando lista de variables')

        problema.generar_vars()

        progress_bar.progress(
            value=40, text='Construyendo lista de restricciones')

        problema.gen_constrains()

        progress_bar.progress(value=50, text='Construyendo función objetivo')

        problema.generar_target()

        progress_bar.progress(
            value=70, text='Ejecutando el soluccionador del modelo')

        problema.solve(engine='glpk', tlimit=60 *
                       tmax, gap=gap_solver/100)

        estatus = problema.status

        if estatus == 'Infeasible':
            st.error('El solucionador reporta infeasibilidad')

        progress_bar.progress(value=90, text='Escribiendo modelo LP')

        problema.imprimir_modelo_lp('model.lp')

        progress_bar.progress(
            value=96, text='Cargando parámetros del problema')

        st.session_state['problema'] = problema

        progress_bar.progress(value=97, text='Variables de estatus')

        st.session_state['solucion_status'] = estatus

        progress_bar.progress(value=100, text='Modelo ejecutado completamente')
