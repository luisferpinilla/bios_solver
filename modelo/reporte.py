from modelo.problema import Problema
import pandas as pd
import pulp as pu


class Reporte():
    def __init__(self, problema: Problema) -> None:
        self.problema = problema

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

    def guardar_excel(self, filename: str):

        with pd.ExcelWriter(path=filename) as writer:
            
            # Variables

            campos = ['tipo', 'empresa', 'operador', 'importacion', 'ingrediente', 'periodo']
            data = self.problema.variables['XPL']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Kg_Almacenados_puerto')
            df.to_excel(
                writer, sheet_name='Almacenamiento_puerto', index=False)

            campos = ['tipo', 'empresa_origen', 'operador', 'importacion',
                      'ingrediente', 'emrpesa_destino', 'planta', 'periodo']
            data = self.problema.variables['XTD']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Kg_despachados_directo')
            df.to_excel(writer, sheet_name='Despachos_directos', index=False)

            campos = ['tipo', 'empresa_origen', 'operador', 'importacion',
                      'ingrediente', 'emrpesa_destino', 'planta', 'periodo']
            data = self.problema.variables['XTR']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Kg_despachados_bodega')
            df.to_excel(writer, sheet_name='Despachos_bodega', index=False)

            campos = ['tipo', 'empresa_origen', 'operador', 'importacion',
                      'ingrediente', 'emrpesa_destino', 'planta', 'periodo']
            data = self.problema.variables['ITD']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Cantidad_camiones_directo')
            df.to_excel(writer, sheet_name='Camiones_despachados_directo', index=False)

            campos = ['tipo', 'empresa_origen', 'operador', 'importacion',
                      'ingrediente', 'emrpesa_destino', 'planta', 'periodo']
            data = self.problema.variables['ITR']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Cantidad_camiones_bodega')
            df.to_excel(writer, sheet_name='Camiones_despachados_bodega', index=False)
            

            campos = ['tipo', 'empresa_origen', 'operador', 'importacion',
                      'ingrediente', 'emrpesa_destino', 'planta', 'periodo']
            data = self.problema.variables['XAR']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Kg_recibidos_bodega')
            df.to_excel(
                writer, sheet_name='llegadas_desde_bodega', index=False)

            campos = ['tipo', 'empresa_origen', 'operador', 'importacion',
                      'ingrediente', 'emrpesa_destino', 'planta', 'periodo']
            data = self.problema.variables['XAD']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Kg_recibidos_directo')
            df.to_excel(writer, sheet_name='Llegadas_directas', index=False)
            
            campos = ['tipo', 'empresa', 'operador', 'importacion', 'ingrediente', 'periodo']
            data = self.problema.variables['XIP']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Kilos_al_cierre')
            df.to_excel(writer, sheet_name='Inventario_puerto', index=False)
            
  
            campos = ['tipo', 'empresa', 'planta', 'ingrediente', 'periodo']
            data = self.problema.variables['XIU']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Kilos_al_cierre')
            df.to_excel(writer, sheet_name='Inventario_plantas', index=False)
            
            campos = ['tipo', 'empresa', 'planta', 'ingrediente', 'periodo']
            data = self.problema.variables['BSS']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Alarma_SafetyStock')
            df.to_excel(writer, sheet_name='SafeyStock', index=False)  
            
            campos = ['tipo', 'empresa', 'planta', 'ingrediente', 'periodo']
            data = self.problema.variables['XBK']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Kilos_Backorder')
            df.to_excel(writer, sheet_name='Backorder_plantas', index=False)
            
            # Parametros
            campos = ['tipo', 'empresa', 'operador', 'importación', 'ingrediente', 'periodo']
            data = self.problema.parametros['llegadas_cargas']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Kilos_llegando_puerto')
            df.to_excel(writer, sheet_name='Llegadas_puerto', index=False)

            campos = ['tipo', 'empresa_origen', 'empresa_destino']
            data = self.problema.parametros['costo_venta_intercompany']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Porcentaje_Intercompany')
            df.to_excel(writer, sheet_name='costo_venta_intercompany', index=False)  
            
            campos = ['tipo', 'operador', 'ingrediente']
            data = self.problema.parametros['costos_operacion_bodega']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Costo_OP_almacenamiento')
            df.to_excel(writer, sheet_name='costos_operacion_bodega', index=False)            
            
            campos = ['tipo', 'operador', 'ingrediente']
            data = self.problema.parametros['costos_operacion_directo']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Costo_OP_DespachoDirecto')
            df.to_excel(writer, sheet_name='costos_operacion_directo', index=False)            
            
            # Costos de fletes
            campos = ['tipo', 'operador', 'empresa', 'planta', 'ingrediente']
            data = self.problema.parametros['fletes_variables']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Flete_variable_Kg')
            df.to_excel(writer, sheet_name='fletes_variables', index=False) 
            
            campos = ['tipo', 'operador', 'empresa', 'planta', 'ingrediente']
            data = self.problema.parametros['fletes_fijos']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='Flete_fijo_camion')
            df.to_excel(writer, sheet_name='fletes_fijos', index=False) 
            
            campos = ['tipo', 'empresa', 'planta', 'ingrediente', 'periodo']
            data = self.problema.parametros['consumo_proyectado']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='consumo_proyectado')
            df.to_excel(writer, sheet_name='consumo_proyectado', index=False) 
            
            campos = ['tipo', 'empresa', 'operador', 'importacion', 'ingrediente', 'periodo']
            data = self.problema.parametros['costos_almacenamiento']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='costos_almacenamiento_cierre')
            df.to_excel(writer, sheet_name='Costos_almacenamiento_puerto', index=False) 
                   
            campos = ['tipo', 'empresa', 'planta', 'ingrediente']
            data = self.problema.parametros['inventario_inicial_ua']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='inventario_inicial_planta')
            df.to_excel(writer, sheet_name='inventario_inicial_planta', index=False) 
            
            campos = ['tipo', 'empresa', 'operador', 'importacion', 'ingrediente']
            data = self.problema.parametros['inventario_inicial_cargas']
            df = self.__convertir_a_dataframe(
                data=data, campos=campos, value_name='inventario_inicial_puerto')
            df.to_excel(writer, sheet_name='inventario_inicial_puerto', index=False)
            