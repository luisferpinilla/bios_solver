import pulp as pu
from modelador.generador_conjuntos import generar_conjuntos
from modelador.generador_parametros import generar_parametros
from modelador.generador_variables import generar_variables
from modelador.generador_restricciones import generar_restricciones
from modelador.generador_fobjetivo import generar_fob
# from modelador.generador_reporte import generar_reporte, guardar_data


def generar_problema(file: str):

    problema = dict() 

    generar_conjuntos(problema=problema, file=file)

    generar_parametros(problema=problema, file=file)

    variables = generar_variables(problema)

    restricciones = generar_restricciones(problema, variables)

    fobjetivo = generar_fob(problema, variables)

    return fobjetivo, restricciones, problema, variables


def test():
    
    [x for x in variables['BSS'].keys() if 'union' in x]
    
    [x for x in problema['conjuntos']['unidades_almacenamiento'] if 'union' in x]





if __name__ == '__main__':

    file = './model_rev_20230831.xlsm'
    # Problema
    solver = pu.LpProblem("Bios", sense=pu.const.LpMinimize)

    fobjetivo, restricciones, problema, variables = generar_problema(file=file)

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

    # generar_reporte(problema=problema, variables=variables)

    guardar_data(problema, variables)
