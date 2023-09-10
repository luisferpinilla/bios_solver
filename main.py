from modelo.problema import Problema

if __name__ == '__main__':

    file = './model_rev_20230831.xlsm'

    problema = Problema(excel_file_path=file)

    problema.generar_sets()

    problema.generar_parameters()

    problema.generar_vars()

    problema.gen_constrains()

    problema.generar_target()

    problema.solve(gen_lp_file=True)

    solucion = problema.generar_reporte()
