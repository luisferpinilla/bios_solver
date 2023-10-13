from modelo.problema import Problema
import pandas as pd
import pulp as pu
import json
from tqdm import tqdm


class Reporte():
    def __init__(self, problema: Problema) -> None:
        self.problema = problema
        self.df_dict = self.obtener_dataframes()

    def __convertir_a_dataframe(self, data: dict, campos: list, value_name='value') -> pd.DataFrame:

        # Estructura para convertir a Dataframe
        data_dict = {'key': list(), 'value': list()}

        # copiar data en el formato requerido por la estructura
        for key, value in data.items():
            data_dict['key'].append(key)

            if type(value) == pu.LpVariable:
                data_dict['value'].append(value.varValue)
            else:
                data_dict['value'].append(value)

        # convertir data_dict a dataframe de dos columnas
        df = pd.DataFrame(data_dict)

        # Separar los keys en los campos entregados
        for i in range(len(campos)):
            df[campos[i]] = df['key'].apply(lambda x: str(x).split('_')[i])

        df.rename(columns={'value': value_name}, inplace=True)

        # Eliminar la clave inicial
        df.drop(columns=['key'], inplace=True)

        return df[campos + [value_name]]

    def obtener_dataframes(self) -> dict:

        with open('./modelo/report_structure.json') as file:
            data = json.load(file)

        df_dict = dict()

        for k, v in tqdm(data.items()):

            campos = v['fields']
            if v['type'] == 'variable':
                data = self.problema.variables[k]
            else:
                data = self.problema.parametros[k]
            df = self.__convertir_a_dataframe(
                data=data,
                campos=campos,
                value_name=v['output_name'])

            df_dict[v['sheet_name']] = df

        # Guardar peridos
        periodos_dict = dict()
        periodos_dict['periodo'] = list()
        periodos_dict['value'] = list()

        fechas_dict = {str(f): self.problema.conjuntos['fechas'][f] for f in range(
            len(self.problema.conjuntos['fechas']))}

        for k, v in fechas_dict.items():
            periodos_dict['periodo'].append(k)
            periodos_dict['value'].append(v)

        df = pd.DataFrame(periodos_dict)
        df_dict['calendario'] = df

        return df_dict

    def guardar_excel(self, filename: str):

        with pd.ExcelWriter(path=filename) as writer:

            for sheet_name, dataframe in tqdm(self.self.df_dict.items()):

                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

    def obtener_fact_inventario_planta(self) -> dict:
        # Leer inventario de planta
        inventario_planta_df = self.df_dict['inventario_planta'].copy()
        inventario_planta_df.rename(
            columns={'kg': 'inventario_al_cierre_kg'}, inplace=True)
        inventario_planta_df.drop(columns=['tipo'], inplace=True)

        # Obtener el inventario
        inventario_inicial_planta_df = self.df_dict['inv_inicial_planta'].copy(
        )
        inventario_inicial_planta_df.rename(
            columns={'kg': 'inventario_al_cierre_kg'}, inplace=True)
        inventario_inicial_planta_df.drop(columns=['tipo'], inplace=True)
        inventario_inicial_planta_df['periodo'] = '-1'

        # Concatenar el inventario en la fact inventario planta
        fact_inventario_planta = pd.concat(
            [inventario_inicial_planta_df, inventario_planta_df])

        # Totalizar los transitos
        transitos_planta_df = self.df_dict['transito_a_planta']
        transitos_planta_df = transitos_planta_df[transitos_planta_df['kg'] > 0]
        transitos_planta_df = transitos_planta_df.groupby(
            ['empresa', 'planta', 'ingrediente', 'periodo'])[['kg']].sum()
        transitos_planta_df.reset_index(inplace=True)
        transitos_planta_df.rename(
            columns={'kg': 'transitos_kg', 'empresa': 'empresa'}, inplace=True)

        # Totalizar las llegadas directas a la planta
        llegadas_directas_planta_df = self.df_dict['llegadas_directas'].copy()
        llegadas_directas_planta_df = llegadas_directas_planta_df[
            llegadas_directas_planta_df['kg'] > 0]
        llegadas_directas_planta_df = llegadas_directas_planta_df.groupby(
            ['empresa_destino', 'planta', 'ingrediente', 'periodo'])[['kg']].sum()
        llegadas_directas_planta_df.reset_index(inplace=True)
        llegadas_directas_planta_df.rename(
            columns={'kg': 'llegadas_directas_kg', 'empresa_destino': 'empresa'}, inplace=True)

        # Totalizar las llegadas por bodega puerto a la planta
        llegadas_por_bodega_planta_df = self.df_dict['llegadas_bodega_puerto'].copy(
        )
        llegadas_por_bodega_planta_df = llegadas_por_bodega_planta_df[
            llegadas_por_bodega_planta_df['kg'] > 0]
        llegadas_por_bodega_planta_df = llegadas_por_bodega_planta_df.groupby(
            ['empresa_destino', 'planta', 'ingrediente', 'periodo'])[['kg']].sum()
        llegadas_por_bodega_planta_df.reset_index(inplace=True)
        llegadas_por_bodega_planta_df.rename(
            columns={'kg': 'llegadas_por_bodega_kg', 'empresa_destino': 'empresa'}, inplace=True)

        # Obtener el consumo proyectado
        consumo_proyectado_df = self.df_dict['consumo_proyectado'].copy()
        consumo_proyectado_df.drop(columns=['tipo'], inplace=True)
        consumo_proyectado_df.rename(
            columns={'kg': 'consumo_kg'}, inplace=True)

        # Safety Stock
        safety_stock_df = self.df_dict['safety_stock'].copy()
        safety_stock_df.drop(columns=['tipo'], inplace=True)

        # Alarma por safety Stock
        alarma_ss_df = self.df_dict['alarma_safety_stock'].copy()
        alarma_ss_df.drop(columns=['tipo'], inplace=True)

        # Agregar los transitos a Fact inventarios planta
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=transitos_planta_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)

        # Agregar las llegadas directas a Fact inventarios planta
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=llegadas_directas_planta_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)

        # Agregar las llegadas por bodega a Fact inventarios planta
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=llegadas_por_bodega_planta_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)

        # Agregar el consumo proyectado a Fact inventarios planta
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=consumo_proyectado_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)

        # Agregar Safey Stock a Fact inventarios planta
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=safety_stock_df,
                                          left_on=['empresa',
                                                   'planta', 'ingrediente'],
                                          right_on=['empresa',
                                                    'planta', 'ingrediente'],
                                          how='left').fillna(0.0)

        # Agregar alarma de Safey Stock a Fact inventarios planta
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=alarma_ss_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)

        fact_inventario_planta = pd.melt(frame=fact_inventario_planta,
                                         id_vars=['empresa', 'planta',
                                                  'ingrediente', 'periodo'],
                                         value_vars=['inventario_al_cierre_kg',
                                                     'transitos_kg', 'llegadas_directas_kg',
                                                     'llegadas_por_bodega_kg', 'consumo_kg', 'safety_stock',
                                                     'alarma_safety_stock'],
                                         value_name='kg', var_name='item')
        fact_inventario_planta['periodo'] = fact_inventario_planta['periodo'].astype(
            int)

        fact_inventario_planta['kg'] = fact_inventario_planta['kg'].apply(
            lambda x: round(x, 0))

        fact_inventario_planta = fact_inventario_planta.pivot_table(values='kg',
                                                                    index=[
                                                                        'empresa', 'planta', 'ingrediente', 'item'],
                                                                    columns='periodo',
                                                                    aggfunc="sum").reset_index()
        # Traer el calendario
        calendario_df = self.df_dict['calendario'].copy()

        # Armar un map para hacer un rename
        date_map = {int(calendario_df.loc[r]['periodo']): calendario_df.loc[r]['value'].strftime(
            '%Y-%m-%d') for r in calendario_df.index}
        date_map[-1] = 'Previo'
        fact_inventario_planta.rename(columns=date_map, inplace=True)

        return fact_inventario_planta

    def obtener_fact_inventario_puerto(self) -> dict:
        # Fletes variables
        fletes_variables_df = self.df_dict['flete_variable'].copy()
        fletes_variables_df.drop(columns=['tipo'], inplace=True)
        fletes_variables_df.rename(
            columns={'costo_por_kg': 'costo_flete_por_kg'}, inplace=True)

        # fletes fijos
        fletes_fijos_df = self.df_dict['flete_fijo'].copy()
        fletes_fijos_df.drop(columns=['tipo'], inplace=True)
        fletes_fijos_df.rename(
            columns={'costo_por_camion': 'costo_flete_por_camion'}, inplace=True)

        # intercompany
        intercompany_df = self.df_dict['costo_intercompany'].copy()
        intercompany_df.drop(columns=['tipo'], inplace=True)

        # Costo de almacenamiento en bodega de puerto
        costo_almacenamiento_df = self.df_dict['costo_almacenamiento_puerto'].copy(
        )
        costo_almacenamiento_df.drop(columns=['tipo'], inplace=True)
        costo_almacenamiento_df.rename(
            columns={'costo_por_kg': 'costo_corte_por_kg'}, inplace=True)

        # Valor CIF de la carga
        valor_cif_df = self.df_dict['valor_cif'].copy()
        valor_cif_df.drop(columns=['tipo'], inplace=True)

        # Llegadas al puerto
        llegadas_puerto_df = self.df_dict['Llegadas_a_puerto'].copy()
        llegadas_puerto_df.drop(columns=['tipo'], inplace=True)
        llegadas_puerto_df.rename(
            columns={'kg': 'descarga_barco_kg'}, inplace=True)

        # Costo de operación portuaria por despacho directo
        costo_op_directo_df = self.df_dict['cost_oportuaria_directo'].copy()
        costo_op_directo_df.drop(columns=['tipo'], inplace=True)
        costo_op_directo_df.rename(
            columns={'costo_por_kg': 'costo_portuario_directo_kg'}, inplace=True)

        # Costo de operación portuaria por despacho directo
        costo_op_bodegaje_df = self.df_dict['costo_oportuaria_bodegaje'].copy()
        costo_op_bodegaje_df.drop(columns=['tipo'], inplace=True)
        costo_op_bodegaje_df.rename(
            columns={'costo_por_kg': 'costo_portuario_bodegaje_kg'}, inplace=True)

        # Inventario inicial
        inventario_inicial_puerto_df = self.df_dict['inv_inicial_cargas'].copy(
        )
        inventario_inicial_puerto_df.drop(columns=['tipo'], inplace=True)
        inventario_inicial_puerto_df.rename(
            columns={'kg': 'inventario_al_cierre_kg'}, inplace=True)
        inventario_inicial_puerto_df['periodo'] = '-1'

        # Inventario en puerto
        inventario_puerto_df = self.df_dict['inventario_puerto'].copy()
        inventario_puerto_df.drop(columns=['tipo'], inplace=True)
        inventario_puerto_df.rename(
            columns={'kg': 'inventario_al_cierre_kg'}, inplace=True)
        print(inventario_puerto_df.shape)
        inventario_puerto_df.head()

        # Armar el fact del inventario en puerto
        fact_inventario_puerto = pd.concat(
            [inventario_inicial_puerto_df, inventario_puerto_df])

        # Despachos directos
        despacho_directo_df = self.df_dict['despacho_directo'].copy()
        despacho_directo_df.drop(columns=['tipo'])
        despacho_directo_df.rename(
            columns={'cantidad_camiones': 'cantidad_camiones_directo'}, inplace=True)
        despacho_directo_df['kilos_despachados_directo'] = 34000 * \
            despacho_directo_df['cantidad_camiones_directo']

        # Colocar costos de operación por depacho directo
        despacho_directo_df = pd.merge(left=despacho_directo_df,
                                       right=costo_op_directo_df,
                                       left_on=['operador', 'ingrediente'],
                                       right_on=['operador', 'ingrediente'],
                                       how='left')

        # Colocar fletes variables al despacho directo
        despacho_directo_df = pd.merge(left=despacho_directo_df,
                                       right=fletes_variables_df,
                                       left_on=['operador', 'ingrediente',
                                                'empresa_destino', 'planta'],
                                       right_on=['operador', 'ingrediente',
                                                 'empresa', 'planta'],
                                       how='left').drop(columns=['empresa'])

        # Colocar fletes fijos al despacho directo
        despacho_directo_df = pd.merge(left=despacho_directo_df,
                                       right=fletes_fijos_df,
                                       left_on=['operador', 'ingrediente',
                                                'empresa_destino', 'planta'],
                                       right_on=['operador', 'ingrediente',
                                                 'empresa', 'planta'],
                                       how='left').drop(columns=['empresa'])

        # Colocar valor Cif
        despacho_directo_df = pd.merge(left=despacho_directo_df,
                                       right=valor_cif_df,
                                       left_on=['empresa_origen', 'operador',
                                                'importacion', 'ingrediente'],
                                       right_on=['empresa', 'operador',
                                                 'importacion', 'ingrediente'],
                                       how='left').drop(columns=['empresa'])

        # Colocar costo intercompany al despacho directo
        despacho_directo_df = pd.merge(left=despacho_directo_df,
                                       right=intercompany_df,
                                       left_on=['empresa_origen',
                                                'empresa_destino'],
                                       right_on=['empresa_origen',
                                                 'empresa_destino'],
                                       how='left')

        # Calcular el costo portuario por despacho directo
        despacho_directo_df['costo_portuario_directo_total'] = despacho_directo_df['costo_portuario_directo_kg'] * \
            despacho_directo_df['kilos_despachados_directo']
        despacho_directo_df['costo_fletes_directo'] = despacho_directo_df['costo_flete_por_kg']*despacho_directo_df['kilos_despachados_directo'] + despacho_directo_df['costo_flete_por_camion'] * \
            despacho_directo_df['cantidad_camiones_directo']
        despacho_directo_df['costo_intercompany_directo'] = despacho_directo_df['valor_cif'] * \
            despacho_directo_df['porcentaje_intercompany'] * \
            despacho_directo_df['kilos_despachados_directo']

        # Totalizar despachos directos
        despacho_directo_df = despacho_directo_df.groupby(['empresa_origen',
                                                           'operador',
                                                           'importacion',
                                                           'ingrediente',
                                                           'periodo'])[['cantidad_camiones_directo',
                                                                        'kilos_despachados_directo',
                                                                        'costo_portuario_directo_total',
                                                                        'costo_fletes_directo',
                                                                        'costo_intercompany_directo']].sum().reset_index().rename(columns={'empresa_origen': 'empresa'})

        # Despachos desde bodega
        despacho_bodega_df = self.df_dict['despacho_bodega'].copy()
        despacho_bodega_df.drop(columns=['tipo'])
        despacho_bodega_df.rename(
            columns={'cantidad_camiones': 'cantidad_camiones_bodega'}, inplace=True)
        despacho_bodega_df['kilos_despachados_bodega'] = 34000 * \
            despacho_bodega_df['cantidad_camiones_bodega']

        # Colocar fletes variables al despacho desde bodega
        despacho_bodega_df = pd.merge(left=despacho_bodega_df,
                                      right=fletes_variables_df,
                                      left_on=['operador', 'ingrediente',
                                               'empresa_destino', 'planta'],
                                      right_on=['operador', 'ingrediente',
                                                'empresa', 'planta'],
                                      how='left').drop(columns=['empresa'])

        # Colocar fletes fijos al despacho desde bodega
        despacho_bodega_df = pd.merge(left=despacho_bodega_df,
                                      right=fletes_fijos_df,
                                      left_on=['operador', 'ingrediente',
                                               'empresa_destino', 'planta'],
                                      right_on=['operador', 'ingrediente',
                                                'empresa', 'planta'],
                                      how='left').drop(columns=['empresa'])

        # Colocar valor Cif
        despacho_bodega_df = pd.merge(left=despacho_bodega_df,
                                      right=valor_cif_df,
                                      left_on=['empresa_origen', 'operador',
                                               'importacion', 'ingrediente'],
                                      right_on=['empresa', 'operador',
                                                'importacion', 'ingrediente'],
                                      how='left').drop(columns=['empresa'])

        # Colocar costo intercompany al despacho desde bodega
        despacho_bodega_df = pd.merge(left=despacho_bodega_df,
                                      right=intercompany_df,
                                      left_on=['empresa_origen',
                                               'empresa_destino'],
                                      right_on=['empresa_origen',
                                                'empresa_destino'],
                                      how='left')

        # Calcular el costo portuario por despacho desde bodega
        despacho_bodega_df['costo_fletes_bodega'] = despacho_bodega_df['costo_flete_por_kg']*despacho_bodega_df['kilos_despachados_bodega'] + despacho_bodega_df['costo_flete_por_camion'] * \
            despacho_bodega_df['cantidad_camiones_bodega']
        despacho_bodega_df['costo_intercompany_bodega'] = despacho_bodega_df['valor_cif'] * \
            despacho_bodega_df['porcentaje_intercompany'] * \
            despacho_bodega_df['kilos_despachados_bodega']

        # Totalizar despachos desde bodega
        despacho_bodega_df = despacho_bodega_df.groupby(['empresa_origen',
                                                        'operador',
                                                         'importacion',
                                                         'ingrediente',
                                                         'periodo'])[['cantidad_camiones_bodega',
                                                                      'kilos_despachados_bodega',
                                                                     'costo_fletes_bodega',
                                                                      'costo_intercompany_bodega']].sum().reset_index().rename(columns={'empresa_origen': 'empresa'})

        # Operacion de almacenamiento en puerto
        bodegaje_puerto_df = self.df_dict['entradas_bodega_puerto'].copy()
        bodegaje_puerto_df.drop(columns=['tipo'], inplace=True)
        bodegaje_puerto_df.rename(
            columns={'kg': 'bodegaje_puerto_kg'}, inplace=True)

        # Unir inventarios en puerto con Costos de almacenamiento
        fact_inventario_puerto = pd.merge(left=fact_inventario_puerto,
                                          right=costo_almacenamiento_df,
                                          left_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          right_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          how='left')

        # Unir inventarios en puerto con llegadas en barco
        fact_inventario_puerto = pd.merge(left=fact_inventario_puerto,
                                          right=llegadas_puerto_df,
                                          left_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          right_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          how='left')

        # Colocarle a Fact los bodegajes en puerto
        fact_inventario_puerto = pd.merge(left=fact_inventario_puerto,
                                          right=costo_op_bodegaje_df,
                                          left_on=['operador', 'ingrediente'],
                                          right_on=['operador', 'ingrediente'],
                                          how='left')

        # Colocarle a Fact los despachos directos
        fact_inventario_puerto = pd.merge(left=fact_inventario_puerto,
                                          right=despacho_directo_df,
                                          left_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          right_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          how='left')

        # Colocarle a Fact los despachos desde bodega
        fact_inventario_puerto = pd.merge(left=fact_inventario_puerto,
                                          right=despacho_bodega_df,
                                          left_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          right_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          how='left')

        # Colocarle a Fact los bodegajes en puerto
        fact_inventario_puerto = pd.merge(left=fact_inventario_puerto,
                                          right=bodegaje_puerto_df,
                                          left_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          right_on=[
                                              'empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                          how='left')

        # Calcular Costos
        fact_inventario_puerto['costo_portuario_bodegaje_total'] = fact_inventario_puerto['bodegaje_puerto_kg'] * \
            fact_inventario_puerto['costo_portuario_bodegaje_kg']

        fact_inventario_puerto = fact_inventario_puerto.melt(id_vars=['empresa', 'operador', 'importacion', 'ingrediente', 'periodo'],
                                                             value_vars=['inventario_al_cierre_kg', 'costo_corte_por_kg',
                                                                         'descarga_barco_kg', 'costo_portuario_bodegaje_kg',
                                                                         'cantidad_camiones_directo', 'kilos_despachados_directo',
                                                                         'costo_portuario_directo_total', 'costo_fletes_directo',
                                                                         'costo_intercompany_directo', 'cantidad_camiones_bodega',
                                                                         'kilos_despachados_bodega', 'costo_fletes_bodega',
                                                                         'costo_intercompany_bodega', 'bodegaje_puerto_kg',
                                                                         'costo_portuario_bodegaje_total'],
                                                             value_name='kg', var_name='item')
        fact_inventario_puerto['periodo'] = fact_inventario_puerto['periodo'].astype(
            int)
        fact_inventario_puerto['kg'] = fact_inventario_puerto['kg'].apply(
            lambda x: round(x, 0))
        fact_inventario_puerto = fact_inventario_puerto.pivot_table(values='kg',
                                                                    index=[
                                                                        'empresa', 'operador', 'importacion', 'ingrediente', 'item'],
                                                                    columns='periodo',
                                                                    aggfunc="sum").reset_index()

        # Traer el calendario
        calendario_df = self.df_dict['calendario'].copy()

        # Armar un map para hacer un rename
        date_map = {int(calendario_df.loc[r]['periodo']): calendario_df.loc[r]['value'].strftime(
            '%Y-%m-%d') for r in calendario_df.index}
        date_map[-1] = 'Previo'
        fact_inventario_puerto.rename(columns=date_map, inplace=True)

        return fact_inventario_puerto
