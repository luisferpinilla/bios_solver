import streamlit as st
import pandas as pd


def _procesar_parametros(parametros: dict, campos: list):

    par_dict = dict()
    par_dict['name'] = list()
    par_dict['value'] = list()

    for parametro, value in parametros.items():
        par_dict['name'].append(parametro)
        par_dict['value'].append(value)

    df = pd.DataFrame(par_dict)

    for i in range(len(campos)):
        campo = campos[i]

        df[campo] = df['name'].apply(lambda x: str(x).split('_')[i])

    df = df[campos + ['value']]

    return df


st.set_page_config(layout="wide")

st.write('# Parámetros cargados')

problema = st.session_state['problema']

st.button(label='Callback')

fechas_list = problema['conjuntos']['fechas']

fechas_map = {str(i): fechas_list[i] for i in range(len(fechas_list))}

with st.expander(label='Costos de almacenamiento'):

    parametros = problema['parametros']['costos_almacenamiento']

    campos = ['tipo', 'empresa', 'ingrediente',
              'operador', 'importacion', 'periodo']

    df = _procesar_parametros(parametros=parametros, campos=campos)

    df['periodo'] = df['periodo'].map(fechas_map)

    df = df.pivot_table(index=['empresa', 'operador', 'importacion', 'ingrediente'],
                        columns='periodo',
                        values='value',
                        aggfunc=sum).reset_index().fillna(0.0)

    st.write(df)

with st.expander(label='Costos de Transporte'):

    parametros = problema['parametros']['fletes_variables']

    campos = ['operador', 'empresa', 'planta', 'ingrediente']

    df = _procesar_parametros(parametros=parametros, campos=campos)

    df = df.pivot_table(index=['operador', 'ingrediente'],
                        columns='planta',
                        values='value', aggfunc=sum)

    st.write(df)

with st.expander(label='Inventario inicial de cargas'):

    parametros = problema['parametros']['inventario_inicial_cargas']

    campos = ['tipo', 'empresa', 'operador', 'importacion', 'ingrediente']

    df = _procesar_parametros(parametros=parametros, campos=campos)

    df = df[['empresa', 'operador', 'importacion', 'ingrediente', 'value']]

    st.write(df)

with st.expander(label='Llegada de cargas a puerto'):

    parametros = problema['parametros']['llegadas_cargas']

    campos = ['tipo', 'empresa', 'operador',
              'importacion', 'ingrediente', 'periodo']

    df = _procesar_parametros(parametros=parametros, campos=campos)

    df = df[['empresa', 'operador', 'importacion',
             'ingrediente', 'periodo', 'value']]

    st.write(df)

with st.expander(label='Consumo Proyectado'):

    parametros = problema['parametros']['consumo_proyectado']

    campos = ['tipo', 'empresa', 'planta',
              'ingrediente', 'periodo']

    df = _procesar_parametros(parametros=parametros, campos=campos)

    df['periodo'] = df['periodo'].map(fechas_map)

    df = df.pivot_table(index=['empresa', 'planta', 'ingrediente'],
                        columns='periodo', values='value').reset_index()

    st.write(df)


# st.write(problema)
