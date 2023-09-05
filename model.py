import pulp as pu
from modelador.generador_conjuntos import generar_conjuntos
from modelador.generador_parametros import generar_parametros
from modelador.generador_variables import generar_variables
from modelador.generador_restricciones import generar_restricciones
from modelador.generador_fobjetivo import generar_fob
from modelador.generador_reporte import generar_reporte



if __name__ == '__main__':

    file = './model_rev_20230831.xlsm'
    
    problema = dict() 

    generar_conjuntos(problema=problema, file=file)

    generar_parametros(problema=problema, file=file)

    variables = generar_variables(problema)

    restricciones = generar_restricciones(problema, variables)

    fobjetivo = generar_fob(problema, variables)
    
    # Problema
    solver = pu.LpProblem("Bios", sense=pu.const.LpMinimize)

    # Agregar función objetivo
    solver += fobjetivo

    # Agregar restricciones
    for name, rest_list in restricciones.items():
        for rest in rest_list:
            # print('agregando restriccion', name, rest)
            solver += rest

    solver.writeLP(filename='model.lp')

    glpk = pu.GLPK_CMD(timeLimit=100, options=[
                       "--mipgap", "0.00000000001", "--tmlim", "100000"])

    try:
        solver.solve(solver=glpk)
    except:
        print('No se puede usar GLPK')

        cbc = pu.PULP_CBC_CMD(gapAbs=0.00000000001,
                              timeLimit=60, cuts=False, strong=True)
        solver.solve()

    solucion = generar_reporte(problema, variables)
