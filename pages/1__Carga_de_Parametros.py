from modelo.problema import Problema
from modelo.validador import Validador
import streamlit as st

st.set_page_config(layout="wide")

st.title('Visualizador BIOS')
# label='Seleccione un motor de solución', options=['coin', 'glpk'])

uploaded_file = st.file_uploader("Choose a file")

file = uploaded_file


if file is None:

    st.write('Debe seleccionar un archivo')

else:

    with st.form('Configure los siguientes parámetros'):

        tmax = st.slider(label='Tiempo máximo de trabajo en minutos',
                         min_value=10, max_value=60, value=30)

        st.session_state['upload_file'] = uploaded_file

        validador = Validador(file=file)

        validador.ejecutar_validaciones()

        with st.expander(label="Resultado de validaciones", expanded=validador.cantidad_errores > 0):

            for k, v in validador.validaciones.items():

                if "OK" in v:
                    st.success(f'{k}: {v}', icon="✅")
                else:
                    st.error(f'{k}: {v}', icon="🚨")

        if validador.cantidad_errores == 0:

            submitted = st.form_submit_button("Ejecutar Modelo")

            if submitted:

                problema = Problema(excel_file_path=file)

                progress_bar = st.progress(value=0, text='Generando conjuntos')

                problema.generar_sets()

                progress_bar.progress(
                    value=5, text='Generando lista de parámetros')

                problema.generar_parameters()

                progress_bar.progress(
                    value=20, text='Generando lista de variables')

                problema.generar_vars()

                progress_bar.progress(
                    value=40, text='Construyendo lista de restricciones')

                problema.gen_constrains()

                progress_bar.progress(
                    value=50, text='Construyendo función objetivo')

                problema.generar_target()

                progress_bar.progress(
                    value=70, text='Ejecutando el soluccionador del modelo')

                # problema.solve(engine='coin', tlimit=60 * tmax)
                problema.solve(tlimit=tmax*60)

                if problema.estatus == 'Infeasible':
                    st.error('El solucionador reporta Infactibilidad')

                progress_bar.progress(value=90, text='Escribiendo modelo LP')

                # problema.imprimir_modelo_lp('model.lp')

                # problema.guardar_reporte()

                progress_bar.progress(
                    value=96, text='Cargando parámetros del problema')

                st.session_state['problema'] = problema

                progress_bar.progress(value=97, text='Variables de estatus')

                st.session_state['solucion_status'] = problema.estatus

                progress_bar.progress(
                    value=100, text='Modelo ejecutado completamente')

                st.write(problema.estatus)

        else:
            st.warning(
                body='Debe Resolver las validaciones antes de poder ejecutar el Solucionador del Modelo')
