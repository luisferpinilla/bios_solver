from modelo.problema import Problema
from modelo.reporte import Reporte
from modelo.visor_parametros import visor_parametros
import pandas as pd

# if __name__ == '__main__':

file = 'model_template.xlsm'

problema = Problema(excel_file_path=file)

problema.generar_sets()

problema.generar_parameters()

problema.generar_vars()

problema.generar_target()

problema.gen_constrains()

df = visor_parametros(conjuntos=problema.conjuntos, parametros=problema.parametros)

problema.solve(engine='coin', gap=0.02, tlimit_seconds=60*15)

reporte = Reporte(problema=problema)

reporte.guardar_excel('gap002.xlsx')

df_dict = reporte.df_dict


fact_inventario_planta = reporte.obtener_cruce_inventarios_planta()
fact_inventario_puerto = reporte.obtener_cruce_inventario_puerto()

with pd.ExcelWriter('borrame.xlsx') as writer:
    fact_inventario_planta.to_excel(writer, sheet_name='plantas')
    fact_inventario_puerto.to_excel(writer, sheet_name='puertos')

conjuntos = problema.conjuntos
parametros = problema.parametros
variables = problema.variables


# df_dict = reporte.obtener_dataframes(filename='reporte.xlsx')

# solucion = problema.generar_reporte()


# reporte.guardar_excel(filename='solucion.xlsx')

problema.imprimir_modelo_lp('model.lp')
