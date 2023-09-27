from modelo.problema import Problema

if __name__ == '__main__':

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
    
    problema.solve()
    
    problema.imprimir_modelo_lp('model.lp')

    solucion = problema.generar_reporte()
