from modelo.problema import Problema
from modelo.reporte import Reporte

# if __name__ == '__main__':

file = '0_model_21sept-2_rev.xlsm'

problema = Problema(excel_file_path=file)

problema.generar_sets()

problema.generar_parameters()

problema.generar_vars()

conjuntos = problema.conjuntos
parametros = problema.parametros
variables = problema.variables

problema.generar_target()

problema.gen_constrains()

problema.solve(tlimit=60)

reporte = Reporte(problema=problema)

solucion = problema.generar_reporte()

# reporte.guardar_excel(filename='solucion.xlsx')

# problema.imprimir_modelo_lp('model.lp')
