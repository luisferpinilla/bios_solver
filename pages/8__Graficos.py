import streamlit as st
from modelo.reporte import Reporte 
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta




def dibujar_inventario_planta(df:pd.DataFrame):

    filtros = ['empresa', 'planta', 'ingrediente', 'item']

    names = [datetime.strptime(x, '%Y-%m-%d')  for x in df.drop(columns=['Previo'] + filtros).columns]
    names = [names[0]-timedelta(days=1)] + names
    names = [x.strftime(format='%b-%d') for x in names]

    # Values of each group
    llegadas_directas_kg = list(df[df['item']=='llegadas_directas_kg'].drop(columns=filtros).iloc[0])
    llegadas_por_bodega_kg = list(df[df['item']=='llegadas_por_bodega_kg'].drop(columns=filtros).iloc[0])
    inventario_al_cierre = list(df[df['item']=='inventario_al_cierre_kg'].drop(columns=filtros).iloc[0])
    transitos_a_bodega = list(df[df['item']=='transitos_kg'].drop(columns=filtros).iloc[0])
    consumo_proyectado = list(df[df['item']=='consumo_kg'].drop(columns=filtros).iloc[0])
    safety_stock = list(df[df['item']=='safety_stock'].drop(columns=filtros).iloc[0])
    target = list(df[df['item']=='Target'].drop(columns=filtros).iloc[0])
    
    fig, ax = plt.subplots(figsize=(12, 4))

    fig.suptitle(f'Inventarios de {ingrediente} en {planta}', fontsize=14)

    ax.set_xlabel('Fecha')
    ax.set_ylabel('Kg')

    ax.plot(names, target, label='Inventario Objetivo')
    ax.plot(names, inventario_al_cierre, label='Inventario al cierre')
    ax.plot(names, consumo_proyectado, label='Consumo Proyectado')
    ax.plot(names, safety_stock, color='red', linestyle='dashed', label='Inventario de seguridad')
    ax.bar(names, llegadas_directas_kg, color='blue', width=1, label='Llegadas directas')
    ax.bar(names, llegadas_por_bodega_kg, color='orange', width=1, label='Llegadas indirectas')
    ax.bar(names, transitos_a_bodega, color='red', width=1, label='Llegadas programadas')

    fig.autofmt_xdate()

    plt.legend()
    
    # Show graphic
    return fig

def dibujar_inventario_puerto(df:pd.DataFrame):

    filtros = ['empresa', 'operador', 'importacion', 'ingrediente', 'item']

    fechas = list(df.drop(columns=['Previo'] + filtros).columns)

    names = [datetime.strptime(x, '%Y-%m-%d')  for x in fechas]
    names = [names[0]-timedelta(days=1)] + names
    names = [x.strftime(format='%b-%d') for x in names]

    df = df.reset_index().groupby(['ingrediente', 'item'])[['Previo'] + fechas].sum().reset_index()

    # Values of each group
    # despachos_directas_kg = list(df[df['item']=='kilos_despachados_directo'].drop(columns=['ingrediente', 'item']).iloc[0])
    despachos_desde_bodega_kg = list(df[df['item']=='kilos_despachados_bodega'].drop(columns=['ingrediente', 'item']).iloc[0])
    inventario_al_cierre = list(df[df['item']=='inventario_al_cierre_kg'].drop(columns=['ingrediente', 'item']).iloc[0])
    bodegaje_puerto_kg = list(df[df['item']=='bodegaje_puerto_kg'].drop(columns=['ingrediente', 'item']).iloc[0])
    #consumo_proyectado = list(df[df['item']=='consumo_kg'].drop(columns=['ingrediente', 'item']).iloc[0])
    #safety_stock = list(df[df['item']=='safety_stock'].drop(columns=['ingrediente', 'item']).iloc[0])
    #target = list(df[df['item']=='Target'].drop(columns=['ingrediente', 'item']).iloc[0])
    
    fig, ax = plt.subplots(figsize=(12, 4))

    fig.suptitle(f'Inventarios de {ingrediente} en puerto', fontsize=14)

    ax.set_xlabel('Fecha')
    ax.set_ylabel('Kg')

    #ax.plot(names, target, label='Inventario Objetivo')
    ax.plot(names, inventario_al_cierre, label='Inventario al cierre')
    ax.bar(names, bodegaje_puerto_kg, label='Bodegaje en puerto')
    # ax.plot(names, safety_stock, color='red', linestyle='dashed', label='Inventario de seguridad')
    # ax.bar(names, despachos_directas_kg, color='blue', width=1, label='Despachos directos')
    ax.bar(names, despachos_desde_bodega_kg, color='orange', label='Despachos desde bodega')
    #ax.bar(names, transitos_a_bodega, color='red', width=1, label='Llegadas programadas')

    fig.autofmt_xdate()

    plt.legend()
    
    # Show graphic
    return fig




st.title('Analisis')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:

    problema = st.session_state['problema']
    reporte = Reporte(problema=problema)
    planta_df = reporte.obtener_fact_inventario_planta()
    puerto_df = reporte.obtener_fact_inventario_puerto()

    
    ingrediente_colum, planta_column  = st.columns(2)

    with ingrediente_colum:

        ingrediente = st.selectbox(label='Ingrediente', options=planta_df['ingrediente'].unique())

    with planta_column:

        planta = st.selectbox(label='Planta', options=planta_df['planta'].unique())

    if planta != None and ingrediente != None:

        st.markdown('## Inventarios en Plantas')
        df1 = planta_df[(planta_df['ingrediente']==ingrediente)&(planta_df['planta']==planta)]
        fig = dibujar_inventario_planta(df1)
        st.pyplot(fig)

        st.markdown('## Inventario en puertos')        
        df2 = puerto_df[puerto_df['ingrediente']==ingrediente]
        fig2 = dibujar_inventario_puerto(df2)
        st.pyplot(fig2)

        st.write(puerto_df)

    



    


