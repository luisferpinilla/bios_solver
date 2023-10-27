from modelo.problema import Problema
from modelo.reporte import Reporte

# if __name__ == '__main__':

file = '0_model_23oct-rev.xlsm'

problema = Problema(excel_file_path=file)

problema.generar_sets()

problema.generar_parameters()

problema.generar_vars()

problema.generar_target()

problema.gen_constrains()

problema.solve(tlimit=300)

reporte = Reporte(problema=problema)

df_dict = reporte.df_dict


fact_inventario_planta = reporte.obtener_fact_inventario_planta()
fact_inventario_puerto = reporte.obtener_fact_inventario_puerto()

conjuntos = problema.conjuntos
parametros = problema.parametros
variables = problema.variables


# df_dict = reporte.obtener_dataframes(filename='reporte.xlsx')

# solucion = problema.generar_reporte()


# reporte.guardar_excel(filename='solucion.xlsx')

problema.imprimir_modelo_lp('model.lp')
