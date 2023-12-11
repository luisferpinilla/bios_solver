import streamlit as st


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep=';', decimal=',').encode('utf-8')


st.set_page_config(layout="wide")

st.write('# Saldos en puerto')

st.button(label='callback')

if not 'problema' in st.session_state.keys():
    st.write('Go to Main page and load a file')
else:
    problema = st.session_state['problema']

    solucion = problema.generar_reporte()

    df = solucion['Inventario en Puerto'].reset_index()

    df = df[df['variable'] == 'Inventario al final del día']

    last_column = df.columns[-1]

    df = df[['empresa', 'ingrediente', 'operador', 'importacion', last_column]]

    df = df[df[last_column] < 34000].sort_values(last_column, ascending=False)

    df.set_index(['empresa', 'ingrediente', 'operador',
                 'importacion'], drop=True, inplace=True)

    df.rename(
        columns={last_column: f'Kilos al final de {last_column}'}, inplace=True)

    st.write(
        'Las siguientes cargas en puerto se espera que terminen con menos de 34 toneladas:')

    st.write(df)

    csv2 = convert_df(df)

    st.download_button(label='descargar reporte',
                       data=csv2,    file_name='saldos_planta.csv',    mime='text/csv')
