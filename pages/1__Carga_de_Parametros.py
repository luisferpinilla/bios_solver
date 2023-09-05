from datetime import datetime
import pulp as pu
from modelador.generador_conjuntos import generar_conjuntos
from modelador.generador_parametros import generar_parametros
from modelador.generador_variables import generar_variables
from modelador.generador_restricciones import generar_restricciones
from modelador.generador_fobjetivo import generar_fob
from modelador.generador_reporte import generar_reporte
from validador import Validador


import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.title('Visualizador BIOS')


def generar_problema(file: str):

    problema = dict()

    generar_conjuntos(problema=problema, file=file)

    generar_parametros(problema=problema, file=file)

    variables = generar_variables(problema)

    restricciones = generar_restricciones(problema, variables)

    fobjetivo = generar_fob(problema, variables)

    return fobjetivo, restricciones, problema, variables


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

    if validador.cantidad_errores == 0:

        problema = dict()

        cols_consumo_proyectado_periods = 'B:R'

        progress_bar = st.progress(value=0, text='Generando conjuntos')

        generar_conjuntos(problema=problema, file=file,
                          usecols=cols_consumo_proyectado_periods)

        progress_bar.progress(value=5, text='Generando lista de parámetros')

        generar_parametros(problema=problema, file=file,
                           usecols=cols_consumo_proyectado_periods)

        progress_bar.progress(value=20, text='Generando lista de variables')

        variables = generar_variables(problema)

        progress_bar.progress(
            value=40, text='Construyendo lista de restricciones')

        restricciones = generar_restricciones(problema, variables)

        progress_bar.progress(value=50, text='Construyendo función objetivo')

        fobjetivo = generar_fob(problema, variables)

        progress_bar.progress(
            value=70, text='Ejecutando el soluccionador del modelo')

        # Problema
        solver = pu.LpProblem("Bios", sense=pu.const.LpMinimize)

        # Agregar función objetivosolver += fobjetivo
        solver += fobjetivo

        # Agregar restricciones
        for name, rest_list in restricciones.items():
            for rest in rest_list:
                # print('agregando restriccion', name, rest)
                solver += rest

        try:

            glpk = pu.GLPK_CMD(timeLimit=100, options=[
                               # "--mipgap", "0.00000000001",
                               "--tmlim", "100000"])

            solver.solve(solver=glpk)

        except:

            print('No se puede usar GLPK')

            cbc = pu.PULP_CBC_CMD(
                # gapAbs=0.00000000001,
                timeLimit=60,
                cuts=False,
                strong=True)
            solver.solve()

        estatus = pu.LpStatus[solver.status]

        solver.write(filename='model.lp')

        if estatus == 'Infeasible':
            st.error('El solucionador reporta infeasibilidad')

        progress_bar.progress(value=90, text='Generando reporte de resultados')

        solucion = generar_reporte(problema, variables)

        progress_bar.progress(value=95, text='Generando reporte de resultados')

        st.session_state['solucion'] = solucion

        progress_bar.progress(
            value=96, text='Cargando parámetros del problema')

        st.session_state['problema'] = problema

        progress_bar.progress(value=97, text='Variables de estatus')

        st.session_state['solucion_status'] = estatus

        progress_bar.progress(value=100, text='Modelo ejecutado completamente')
