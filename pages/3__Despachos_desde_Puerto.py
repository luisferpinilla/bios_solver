import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go


def dibujar_planta(df: pd.DataFrame, nombre_planta: str, ingrediente: str):

    temp = df[(df['planta'] == nombre_planta) &
              (df['ingrediente'] == ingrediente)]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=temp['fecha'],  # x-axis
        y=temp['inventario'],  # y-axis
        mode='lines',  # Connect data points with lines
        name='Inventario'  # Name in the legend
    )
    )

    fig.add_trace(go.Scatter(
        x=temp['fecha'],  # x-axis
        y=temp['capacidad'],  # y-axis
        mode='lines',  # Connect data points with lines
        name='Capacidad Almacenamiento',  # Name in the legend
        line=dict(dash='dash', color='blue')
    ))

    fig.add_trace(go.Bar(
        x=temp['fecha'],
        y=temp['llegada_bodega'],
        name='Despacho Bodega',
        marker_color='green',
        hovertext=temp['importaciones'])
    )

    fig.add_trace(go.Bar(
        x=temp['fecha'],
        y=temp['llegada_directa'],
        name='Despacho Directo',
        marker_color='orange',
        hovertext=temp['importaciones'])
    )

    fig.add_trace(go.Scatter(
        x=temp['fecha'],  # x-axis
        y=temp['safety_stock'],  # y-axis
        mode='lines',  # Connect data points with lines
        name='Safety Stock',  # Name in the legend
        line=dict(dash='dash', color='red')
    ))

    fig.add_trace(go.Bar(
        x=temp['fecha'],  # x-axis
        y=temp['llegada_programada'],  # y-axis
        name='Llegadas Programada',  # Name in the legend
        marker_color='gray'
    ))

    fig.add_trace(go.Bar(
        x=temp['fecha'],  # x-axis
        y=temp['backorder'],  # y-axis
        name='Backorder',  # Name in the legend
        marker_color='red'
    ))

    # Layout parameters
    fig.update_layout(
        title=f'Planta: {nombre_planta}: {ingrediente}',  # Title
        xaxis_title='Fecha',  # y-axis name
        yaxis_title='Kg',  # x-axis name
        xaxis_tickangle=0,  # Set the x-axis label angle
        showlegend=True,     # Display the legend
        barmode='stack',
        legend=dict(orientation='h',  x=0.5, xanchor='center'),
    )
    return fig


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep=';', decimal=',').encode('utf-8')


st.set_page_config(layout="wide")

st.write('# Despachos desde puerto')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    problema = st.session_state['problema']

    st.button(label='callback')

    transporte_df = problema.reporte_transporte()

    transporte_df['fecha'] = pd.to_datetime(transporte_df['fecha'])

    periodos = problema.periodos

    min_date = periodos[0]

    max_date = periodos[list(periodos.keys())[-1]]

    min_date_col, max_date_col, ingrediente_col, tipo_transporte_col = st.columns(
        4)

    with min_date_col:
        start_date = st.date_input(
            label='Fecha Inicial', value=min_date, min_value=min_date, max_value=max_date)

        start_date = datetime(
            start_date.year, start_date.month, start_date.day)

    with max_date_col:
        end_date = st.date_input(
            label='Fecha Final', value=min_date+timedelta(days=7), min_value=min_date, max_value=max_date)

        end_date = datetime(end_date.year, end_date.month, end_date.day)

    with ingrediente_col:
        ingredientes = list(transporte_df['ingrediente'].unique())

        ingrediente = st.selectbox(label='Ingrediente', options=ingredientes)

    with tipo_transporte_col:

        tipos_transporte = list(transporte_df['tipo'].unique())
        tipo_transporte = st.radio(
            label='Tipo Despacho', options=tipos_transporte)

    st.write(
        f'transportes entre {start_date.strftime("%b-%d")} y {end_date.strftime("%b-%d")} del tipo {tipo_transporte}')

    transporte_df = transporte_df[transporte_df['ingrediente'] == ingrediente]

    transporte_df = transporte_df[transporte_df['tipo'] == tipo_transporte]

    transporte_df = transporte_df[(transporte_df['fecha'] >= start_date) & (
        transporte_df['fecha'] <= end_date)]

    transporte_df['pl'] = transporte_df['empresa_destino'].apply(lambda x: x[0:3]) + \
        "_" + transporte_df['planta'].apply(lambda x: x)

    transporte_df = pd.pivot_table(data=transporte_df,
                                   index=['empresa_origen',
                                          'puerto', 'importacion'],
                                   values='camiones',
                                   columns='pl',
                                   aggfunc='sum'
                                   )

    st.write(transporte_df)

    planta_df = problema.reporte_planta()

    for planta in list(planta_df['planta'].unique()):
        with st.expander(label=planta, expanded=False):

            fig = dibujar_planta(
                df=planta_df, nombre_planta=planta, ingrediente=ingrediente)
            st.plotly_chart(fig, use_container_width=True)
