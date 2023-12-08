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


def dibujar_inventario_puerto(df: pd.DataFrame):

    filtros = ['empresa', 'operador', 'importacion', 'ingrediente', 'item']

    fechas = list(df.drop(columns=['Previo'] + filtros).columns)

    names = [datetime.strptime(x, '%Y-%m-%d') for x in fechas]
    names = [names[0]-timedelta(days=1)] + names
    names = [x.strftime(format='%b-%d') for x in names]

    df = df.reset_index().groupby(['ingrediente', 'item'])[
        ['Previo'] + fechas].sum().reset_index()

    # Values of each group

    # despachos_directas_kg = list(df[df['item']=='kilos_despachados_directo'].drop(columns=['ingrediente', 'item']).iloc[0])
    despachos_desde_bodega_kg = list(df[df['item'] == 'kilos_despachados_bodega'].drop(
        columns=['ingrediente', 'item']).iloc[0])

    despachos_directos_kg = list(df[df['item'] == 'kilos_despachados_directo'].drop(
        columns=['ingrediente', 'item']).iloc[0])
    inventario_al_cierre = list(df[df['item'] == 'inventario_al_cierre_kg'].drop(
        columns=['ingrediente', 'item']).iloc[0])
    bodegaje_puerto_kg = list(df[df['item'] == 'bodegaje_puerto_kg'].drop(
        columns=['ingrediente', 'item']).iloc[0])
    # consumo_proyectado = list(df[df['item']=='consumo_kg'].drop(columns=['ingrediente', 'item']).iloc[0])
    # safety_stock = list(df[df['item']=='safety_stock'].drop(columns=['ingrediente', 'item']).iloc[0])
    # target = list(df[df['item']=='Target'].drop(columns=['ingrediente', 'item']).iloc[0])

    fig, ax = plt.subplots(figsize=(12, 4))

    fig.suptitle(f'Inventarios de {ingrediente} en puerto', fontsize=14)

    ax.set_xlabel('Fecha')
    ax.set_ylabel('Kg')

    ax.plot(names, inventario_al_cierre,
            color='green',
            label='Inventario al cierre')
    ax.bar(names, bodegaje_puerto_kg,
           color='gray',
           width=1,
           label='Bodegaje en puerto')
    ax.bar(names,
           despachos_desde_bodega_kg,
           color='orange',
           width=1,
           label='Despachos desde bodega')
    ax.bar(names,
           despachos_directos_kg,
           color='blue',
           width=1,
           label='Despachos directos')

    fig.autofmt_xdate()

    plt.legend()

    # Show graphic
    return fig


st.title('Analisis')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    problema = st.session_state['problema']

    planta_df = problema.reporte_planta()

    st.write(planta_df)

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
        '''
        df2 = puerto_df[puerto_df['ingrediente'] == ingrediente]

        if df2.shape[0] > 0:
            fig2 = dibujar_inventario_puerto(df2)
            st.pyplot(fig2)
        else:
            st.write('No data')

        transporte_df = reporte.obtener_fact_transporte()
        st.write(transporte_df)
        '''
