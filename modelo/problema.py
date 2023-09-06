from generador_conjuntos import generar_conjuntos
from generador_parametros import generar_parametros
from generador_variables import generar_variables
from generador_restricciones import generar_restricciones
from generador_fobjetivo import generar_fob
from generador_reporte import generar_reporte
import pulp as pu


class Problema():

    def __init__(self, excel_file_path: str) -> None:

        self.file = excel_file_path

        self.conjuntos = dict()

        self.parametros = dict()

        self.variables = dict()

        self.restricciones = dict()

        self.funcion_objetivo = list()

        self.solver = pu.LpProblem("Bios", sense=pu.const.LpMinimize)

        self.usecols = 'B:AH'

        self.status = 'Sin Ejecutar'

    def generar_sets(self):

        print('generando conjuntos')

        generar_conjuntos(problema=self)

    def generar_parameters(self):

        print('generando parametros')

        generar_parametros(problema=self)

    def generar_vars(self):

        print('generando variables')

        generar_variables(problema=self)

    def gen_constrains(self):

        print('generando restricciones')

        generar_restricciones(problema=self)

    def generar_target(self):

        print('generar funcion objetivo')

        generar_fob(problema=self)

    def solve(self):

        print('restolviendo el problema')

        # Agregar función objetivosolver += fobjetivo
        self.solver += self.funcion_objetivo

        # Agregar restricciones
        for name, rest_list in self.restricciones.items():
            print('agregando', name)
            for rest in rest_list:
                # print('agregando restriccion', name, rest)
                solver += rest

        try:

            engine = pu.GLPK_CMD(timeLimit=3600, options=[
                "--mipgap", "0.0001",
                "--tmlim", "3600"])

            self.solver.solve(solver=engine)

        except:
            engine = pu.PULP_CBC_CMD(
                apAbs=0.00000000001,
                timeLimit=3600,
                cuts=False,
                strong=True)

            self.solver.solve(solver=engine)

        self.estatus = pu.LpStatus[solver.status]

    def generar_reporte(self):

        print('generando reporte')

        generar_reporte(self)

    def imprimir_modelo_lp(self, file_output: str):

        self.solver.writeLP(filename='model.lp')
