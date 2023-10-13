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
        periodos_dict['id_periodo'] = list()
        periodos_dict['value'] = list()

        fechas_dict = {f: self.problema.conjuntos['fechas'][f] for f in range(
            len(self.problema.conjuntos['fechas']))}

        for k, v in fechas_dict.items():
            periodos_dict['id_periodo'].append(k)
            periodos_dict['value'].append(v)

        df = pd.DataFrame(periodos_dict)
        df_dict['calendario'] = df

        return df_dict

    def guardar_excel(self, filename: str):

        with pd.ExcelWriter(path=filename) as writer:

            for sheet_name, dataframe in tqdm(self.self.df_dict.items()):

                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

    def obtener_modelo_dimensional(self) -> dict:
        # Leer inventario de planta
        inventario_planta_df = self.df_dict['inventario_planta'].copy()
        print(inventario_planta_df.shape)
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
        print(transitos_planta_df.shape)
        transitos_planta_df = transitos_planta_df[transitos_planta_df['kg'] > 0]
        transitos_planta_df = transitos_planta_df.groupby(
            ['empresa', 'planta', 'ingrediente', 'periodo'])[['kg']].sum()
        transitos_planta_df.reset_index(inplace=True)
        transitos_planta_df.rename(
            columns={'kg': 'transitos_kg', 'empresa': 'empresa'}, inplace=True)

        # Totalizar las llegadas directas a la planta
        llegadas_directas_planta_df = self.df_dict['llegadas_directas'].copy()
        print(llegadas_directas_planta_df.shape)
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
        print(llegadas_por_bodega_planta_df.shape)
        llegadas_por_bodega_planta_df = llegadas_por_bodega_planta_df[
            llegadas_por_bodega_planta_df['kg'] > 0]
        llegadas_por_bodega_planta_df = llegadas_por_bodega_planta_df.groupby(
            ['empresa_destino', 'planta', 'ingrediente', 'periodo'])[['kg']].sum()
        llegadas_por_bodega_planta_df.reset_index(inplace=True)
        llegadas_por_bodega_planta_df.rename(
            columns={'kg': 'llegadas_por_bodega_kg', 'empresa_destino': 'empresa'}, inplace=True)

        # Obtener el consumo proyectado
        consumo_proyectado_df = self.df_dict['consumo_proyectado'].copy()
        print(consumo_proyectado_df.shape)
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
        print('fact antes del join llegadas directas',
              fact_inventario_planta.shape)
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=transitos_planta_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)
        print('fact antes del join', fact_inventario_planta.shape)

        # Agregar las llegadas directas a Fact inventarios planta
        print('fact antes del join llegadas directas',
              fact_inventario_planta.shape)
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=llegadas_directas_planta_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)
        print('fact antes del join', fact_inventario_planta.shape)

        # Agregar las llegadas por bodega a Fact inventarios planta
        print('fact antes del join llegadas por puerto',
              fact_inventario_planta.shape)
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=llegadas_por_bodega_planta_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)
        print('fact antes del join', fact_inventario_planta.shape)

        # Agregar el consumo proyectado a Fact inventarios planta
        print('fact antes del join llegadas por puerto',
              fact_inventario_planta.shape)
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=consumo_proyectado_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)
        print('fact antes del join', fact_inventario_planta.shape)

        # Agregar Safey Stock a Fact inventarios planta
        print('fact antes del join llegadas por puerto',
              fact_inventario_planta.shape)
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=safety_stock_df,
                                          left_on=['empresa',
                                                   'planta', 'ingrediente'],
                                          right_on=['empresa',
                                                    'planta', 'ingrediente'],
                                          how='left').fillna(0.0)
        print('fact antes del join', fact_inventario_planta.shape)

        # Agregar alarma de Safey Stock a Fact inventarios planta
        print('fact antes del join llegadas por puerto',
              fact_inventario_planta.shape)
        fact_inventario_planta = pd.merge(left=fact_inventario_planta,
                                          right=alarma_ss_df,
                                          left_on=['empresa', 'planta',
                                                   'ingrediente', 'periodo'],
                                          right_on=['empresa', 'planta',
                                                    'ingrediente', 'periodo'],
                                          how='left').fillna(0.0)
        print('fact antes del join', fact_inventario_planta.shape)

        fact_inventario_planta = pd.melt(frame=fact_inventario_planta,
                                         id_vars=['empresa', 'planta',
                                                  'ingrediente', 'periodo'],
                                         value_vars=['inventario_al_cierre_kg',
                                                     'transitos_kg', 'llegadas_directas_kg',
                                                     'llegadas_por_bodega_kg', 'consumo_kg', 'safety_stock',
                                                     'alarma_safety_stock'],
                                         value_name='kg', var_name='item')
        fact_inventario_planta = fact_inventario_planta.pivot_table(values='kg',
                                                                    index=[
                                                                        'empresa', 'planta', 'ingrediente', 'item'],
                                                                    columns='periodo',
                                                                    aggfunc="sum").reset_index()
