import streamlit as st
from modelo.reporte import Reporte
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta


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


def dibujar_inventario_ingrediente_puerto(df: pd.DataFrame, puerto: str, ingrediente: str) -> go.Figure:
    fig = go.Figure()

    temp = df[(df['ingrediente'] == ingrediente)
              & (df['puerto'] == puerto)].copy()

    temp['key'] = temp['empresa'] + ", " + temp['importacion']

    pivot_temp = temp.pivot_table(index='fecha', columns='key',
                                  values='inventario_kg', aggfunc='sum').reset_index()

    for importacion in pivot_temp.drop(columns=['fecha']).columns:
        fig.add_trace(go.Scatter(
            x=pivot_temp['fecha'],  # x-axis
            y=pivot_temp[importacion],  # y-axis
            mode='lines',  # Connect data points with lines
            name=importacion  # Name in the legend
        )
        )

    fig.add_trace(go.Bar(
        x=temp['fecha'],  # x-axis
        y=temp['despachos_indirectos_kg'],  # y-axis
        name='Despachos indirectos',  # Name in the legend
        hovertext=temp['plantas'],
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=temp['fecha'],  # x-axis
        y=temp['ingreso_bodega'],  # y-axis
        name='Ingreso a Bodega',  # Name in the legend
        marker_color='gray'
    ))

    # Layout parameters
    fig.update_layout(
        title=f'Puerto: {puerto}, Ingrediente: {ingrediente}',  # Title
        xaxis_title='fecha',  # y-axis name
        yaxis_title='Kg',  # x-axis name
        xaxis_tickangle=0,  # Set the x-axis label angle
        showlegend=True,     # Display the legend
        barmode='stack',
        legend=dict(orientation='h',  x=0.5, xanchor='center'),
    )
    return fig


st.title('Analisis')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    problema = st.session_state['problema']

    planta_df = problema.reporte_planta()

    ingrediente_colum, planta_column = st.columns(2)

    with ingrediente_colum:

        ingrediente = st.selectbox(
            label='Ingrediente', options=planta_df['ingrediente'].unique())

    with planta_column:

        planta = st.selectbox(
            label='Planta', options=planta_df['planta'].unique())

    if planta != None and ingrediente != None:

        st.markdown('### Inventarios en Plantas')

        # st.write(df1)
        fig = dibujar_planta(
            df=planta_df, nombre_planta=planta, ingrediente=ingrediente)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('### Inventario en puertos')

        puerto_df = problema.reporte_puerto()

        for puerto in puerto_df['puerto'].unique():

            temp = puerto_df[(puerto_df['puerto'] == puerto) & (
                puerto_df['ingrediente'] == ingrediente)]
            if temp.shape[0] > 0:

                fig = dibujar_inventario_ingrediente_puerto(
                    df=puerto_df, puerto=puerto, ingrediente=ingrediente)

                st.plotly_chart(fig, use_container_width=True)

                # st.write(temp)
