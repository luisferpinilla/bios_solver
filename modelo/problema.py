from modelo.generador_conjuntos import generar_conjuntos
from modelo.generador_parametros import generar_parametros
from modelo.generador_variables import generar_variables
from modelo.generador_restricciones import generar_restricciones
from modelo.generador_fobjetivo import generar_fob
from modelo.generador_reporte import generar_reporte, guardar_reporte
import pulp as pu


class Problema():

    def __init__(self, excel_file_path: str) -> None:

        self.file = excel_file_path

        self.conjuntos = dict()

        self.parametros = dict()

        self.variables = dict()

        self.restricciones = dict()

        self.target = list()

        self.solver = pu.LpProblem("Bios", sense=pu.const.LpMinimize)

        self.usecols = 'B:AH'

        self.status = 'Sin Ejecutar'

    def generar_sets(self):

        print('generando conjuntos')

        generar_conjuntos(problema=self.conjuntos,
                          file=self.file, usecols=self.usecols)

    def generar_parameters(self):

        print('generando parametros')

        generar_parametros(parametros=self.parametros, conjuntos=self.conjuntos,
                           file=self.file, usecols=self.usecols)

    def generar_vars(self):

        print('generando variables')

        generar_variables(conjuntos=self.conjuntos, variables=self.variables)

    def gen_constrains(self):

        print('generando restricciones')

        generar_restricciones(restricciones=self.restricciones,
                              conjuntos=self.conjuntos, parametros=self.parametros, variables=self.variables)

    def generar_target(self):

        print('generar funcion objetivo')

        generar_fob(fob=self.target, parametros=self.parametros,
                    conjuntos=self.conjuntos, variables=self.variables)

    def solve(self, engine='coin', gap=0.05, tlimit=60, gen_lp_file=False):

        print('restolviendo el problema')

        self.estatus = 'Trabajando'

        # Agregar función objetivosolver += fobjetivo
        self.solver += pu.lpSum(self.target)

        # Agregar restricciones
        for name, rest_list in self.restricciones.items():
            print('agregando', name)
            for rest in rest_list:
                # print('agregando restriccion', name, rest)
                self.solver += rest

        if engine == 'glpk':
            engine = pu.GLPK_CMD(timeLimit=tlimit, options=[
                '--mipgap', str(gap)])
            self.solver.solve(solver=engine)
        else:
            engine = pu.PULP_CBC_CMD(
                gapRel=gap,
                timeLimit=tlimit,
                cuts=False,
                strong=True)
            self.solver.solve(solver=engine)

        self.estatus = pu.LpStatus[self.solver.status]

        if gen_lp_file:
            self.solver.writeLP(filename='model.lp')

    def generar_reporte(self):

        print('generando reporte')

        return generar_reporte(variables=self.variables, parametros=self.parametros, conjuntos=self.conjuntos)

    def guardar_reporte(self):

        print('guardando reporte')

        reporte = self.generar_reporte()

        guardar_reporte(df_dict=reporte)

    def imprimir_modelo_lp(self, file_output: str):

        self.solver.writeLP(filename=file_output)
