#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 05:31:41 2023

@author: luispinilla
"""
import pandas as pd
import json


class Validador():

    def __init__(self, file: str):

        self.file = file
        self.cantidad_errores = 0
        self.validaciones = dict()

    def _validar_nombres_columnas(self):

        with open("modelo/file_structure.json") as file:
            paginas_dict = json.load(file)

        # print(paginas_dict)

        errors_list = list()

        for tab, columns in paginas_dict.items():
            df = pd.read_excel(self.file, sheet_name=tab)
            for column in columns:
                if not column in df.columns:
                    errors_list.append(
                        f'la columna "{column}" de la página "{tab}" parece faltar o estar mál escrita')

        if len(errors_list) > 0:
            self.validaciones[
                'Columnas en archivo'] = f"Error, las siguientes columnas no se encontraron: {', '.join(errors_list)}"
            self.cantidad_errores += 1
        else:
            self.validaciones['Columnas en archivo'] = 'OK, el archivo parece tener las columnas y las pestañas completas'

    def _validar_ingredientes(self):

        df = pd.read_excel(io=self.file, sheet_name='ingredientes')

        self.ingredientes = list(df['nombre'].unique())

        if len(self.ingredientes) == df.shape[0]:
            self.validaciones['nombre'] = "OK, La lista de ingredientes tiene nombres únicos"
        else:
            self.validaciones['nombre'] = "Error, La lista de ingredientes tiene nombres duplicados"
            self.cantidad_errores += 1

    def _validar_empresas(self):

        df = pd.read_excel(io=self.file, sheet_name='empresas')

        self.empresas = list(df['empresa'].unique())

        if len(self.empresas) == df.shape[0]:
            self.validaciones['conteo empresas'] = "OK, las empresas tienen nombre único"
        else:
            self.cantidad_errores += 1
            self.validaciones['conteo empresas'] = "Error, las empresas tienen nombres duplicados"

    def _validar_plantas(self):

        df = pd.read_excel(io=self.file, sheet_name='plantas')

        self.plantas = list(df['planta'].unique())

        empresas = list(df['empresa'].unique())

        if len(self.plantas) == df.shape[0]:
            self.validaciones['conteo plantas'] = "OK, las plantas tienen nombres únicos"
        else:
            self.validaciones['conteo plantas'] = "Error, las plantas tienen nombres duplicados, deben ser únicos"

        # Probar que todas las empresas tengan empresa asociada
        if df[df['empresa'].isna()].shape[0] == 0:
            self.validaciones['plantas con empresas'] = "OK, todas las plantas tienen una empresa asociada"
        else:
            self.cantidad_errores += 1
            self.validaciones['plantas con empresas'] = "Error, Hay plantas sin empresa propietaria"

        # probar que las plantas pertenezcan a una empresa de la lista
        plantas_sin_empresa = [x for x in empresas if not x in self.empresas]

        if len(plantas_sin_empresa) == 0:
            self.validaciones['plantas en empresas'] = "OK, todas las plantas pertenecen a una empresa de la lista"
        else:
            self.cantidad_errores += 1
            self.validaciones['plantas en empresas'] = "Error, alguna empresa no cruza con la lista de empresas"

    def _validar_operadores(self):

        df = pd.read_excel(io=self.file, sheet_name='operadores')

        self.puertos = list(df['puerto'].unique())

        self.operadores = list(df['operador'].unique())

        if len(self.operadores) == df.shape[0]:
            self.validaciones['operadores únicos'] = "OK, los operadores son únicos"
        else:
            self.validaciones['operadores únicos'] = "Error, los operadores no son únicos"

        print(self.operadores)

        for operador in self.operadores:
            campos = operador.split('-')
            nombre = campos[0]
            puerto = campos[1]

            if not puerto in self.puertos:
                self.cantidad_errores += 1
                self.validaciones[
                    'operadores y puertos'] = "Error, el puerto {puerto} no esta en la lista de puertos"

    def _validar_fletes(self):

        campos_fletes = ['fletes_variables', 'fletes_fijos']

        for campo_flete in campos_fletes:

            # campo_flete = campos_fletes[0]

            df = pd.read_excel(io=self.file, sheet_name=campo_flete)

            fletes = list(df['operador-puerto-ing'].unique())

            for flete in fletes:

                # flete = fletes[0]

                operador = flete.split('_')[0].split('-')[0]
                puerto = flete.split('_')[0].split('-')[1]
                ingrediente = flete.split('_')[1]

                if not f'{operador}-{puerto}' in self.operadores:
                    self.cantidad_errores += 1
                    self.validaciones[f'{campo_flete} y operadores'] = f"Error, el operador {operador}-{puerto} en la tabla de fletes variables no se encuentra en la lista de operadores"

                if not puerto in self.puertos:
                    self.cantidad_errores += 1
                    self.validaciones[f'{campo_flete} y puertos'] = f"Error, el puerto {puerto} no se encuetra en la lista de puertos"

                if not ingrediente in self.ingredientes:
                    self.cantidad_errores += 1
                    self.validaciones[f'{campo_flete} e ingredientes'] = f"Error, el ingrediente {ingrediente} no se encuetra en la lista de ingredientes"

    def _validar_demanda(self):

        df = pd.read_excel(io=self.file, sheet_name='consumo_proyectado')

        ingredientes = list(df['ingrediente'].unique())

        plantas = list(df['planta'].unique())

        ingredientes_no_encontrados = [
            x for x in ingredientes if not x in self.ingredientes]

        print(ingredientes_no_encontrados)

        plantas_no_encontradas = [x for x in plantas if not x in self.plantas]

        if len(ingredientes_no_encontrados) > 0:
            self.cantidad_errores += 1
            self.validaciones[
                'demanda de ingredientes'] = f"Error, los ingredientes {ingredientes_no_encontrados} no se encuetran en la lista de ingredientes"

        else:
            self.validaciones['demanda de ingredientes'] = "OK, ingredientes en demanda correctamente nombrados"

        if len(plantas_no_encontradas) > 0:
            self.cantidad_errores += 1
            self.validaciones['demanda por plantas'] = f"Error, las plantas {plantas_no_encontradas} no se encuentran en la lista de plantas"
        else:
            self.validaciones['demanda por plantas'] = "OK, las plantas se encontraron en la lista de plantas"

    def _validar_safety_stock(self):

        df = pd.read_excel(io=self.file, sheet_name='safety_stock')

        ingredientes = list(df['ingrediente'].unique())

        plantas = list(df['planta'].unique())

        ingredientes_no_encontrados = [
            x for x in ingredientes if not x in self.ingredientes]

        plantas_no_encontradas = [x for x in plantas if not x in self.plantas]

        if len(ingredientes_no_encontrados) > 0:
            self.cantidad_errores += 1
            self.validaciones[
                'Safety stock de ingredientes'] = f"Error, los ingredientes {ingredientes_no_encontrados} no se encuetran en la lista de ingredientes"

        else:
            self.validaciones['Safety stock de ingredientes'] = "OK, ingredientes en safety stock fueron correctamente nombrados"

        if len(plantas_no_encontradas) > 0:
            self.cantidad_errores += 1
            self.validaciones['Safety Stock por plantas'] = f"Error, las plantas {plantas_no_encontradas} no se encuentran en la lista de plantas"
        else:
            self.validaciones['Safety Stock por plantas'] = "OK, las plantas se encontraron en la lista de plantas"

    def _validar_no_exceder_capacidad_almacenamiento(self):

        df = pd.read_excel(self.file, sheet_name='unidades_almacenamiento')

        ingredientes = [
            x for x in df['ingrediente_actual'].unique() if x in df.columns]

        count = 0

        unidades = list()

        for ingrediente in ingredientes:

            temp = df[df['ingrediente_actual'] == ingrediente]

            temp = temp[temp['cantidad_actual'] > temp[ingrediente]]

            for i in temp.index:
                unidades.append(
                    f"unidad {temp.loc[i]['unidad_almacenamiento']} en {temp.loc[i]['planta']}")

            count += temp.shape[0]

        if len(unidades) > 0:
            self.cantidad_errores += 1
            self.validaciones[
                'Capacidad en Unidades de Almacenamiento'] = f"Error, las siguientes unidades {unidades} tienen valores erróneos sobre la capacidad de almacenamiento"
        else:
            self.validaciones['Capacidad en Unidades de Almacenamiento'] = "OK, las capacidades estan sobre las cantidades de inventario"

    def _validar_no_duplicados_consumos(self):

        df = pd.read_excel(io=self.file, sheet_name='consumo_proyectado')

        df['key'] = 'key'

        df = df.groupby(['planta', 'ingrediente'])[
            ['key']].count().reset_index()

        df = df[df['key'] > 1]

        if df.shape[0] > 0:
            self.cantidad_errores += 1
            self.validaciones['Conteos en consumos proyectados'] = "Error, la pestaña de consumos proyectados tiene valores duplicados en cuanto a ingrediente y planta"
        else:
            self.validaciones['Conteos en consumos proyectados'] = "OK, Consumos proyectaos sin duplicados"

    def ejecutar_validaciones(self):

        self._validar_nombres_columnas()

        self._validar_ingredientes()

        # self._validar_empresas()

        # self._validar_plantas()

        # self._validar_operadores()

        # self._validar_fletes()

        # self._validar_demanda()

        # self._validar_safety_stock()

        self._validar_no_exceder_capacidad_almacenamiento()

        self._validar_no_duplicados_consumos()
