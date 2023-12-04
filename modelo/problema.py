from modelo.generador_conjuntos import generar_conjuntos
from modelo.generador_parametros import generar_parametros
from modelo.generador_variables import generar_variables
from modelo.generador_restricciones import generar_restricciones
from modelo.generador_fobjetivo import generar_fob
from modelo.generador_reporte import generar_reporte, guardar_reporte_xlsx
from modelo.visor_parametros import visor_parametros
import pulp as pu
import os


class Problema():

    def __init__(self, excel_file_path: str) -> None:

        self.file = excel_file_path

        self.conjuntos = dict()

        self.parametros = dict()

        self.variables = dict()

        self.restricciones = dict()

        self.target = list()

        self.solver = pu.LpProblem("Bios", sense=pu.const.LpMinimize)

        self.estatus = 'Sin Ejecutar'

    def generar_sets(self):

        print('generando conjuntos')

        generar_conjuntos(problema=self.conjuntos,
                          file=self.file)

    def generar_parameters(self):

        print('generando parametros')

        generar_parametros(parametros=self.parametros, conjuntos=self.conjuntos,
                           file=self.file)

    def generar_vars(self):

        print('generando variables')

        generar_variables(conjuntos=self.conjuntos, parametros=self.parametros,
                          variables=self.variables)

    def gen_constrains(self):

        print('generando restricciones')

        generar_restricciones(restricciones=self.restricciones,
                              conjuntos=self.conjuntos, parametros=self.parametros, variables=self.variables)

    def generar_target(self):

        print('generar funcion objetivo')

        generar_fob(fob=self.target, parametros=self.parametros,
                    conjuntos=self.conjuntos, variables=self.variables)

    def get_revsion_parametros(self):

        if len(self.conjuntos) == 0:
            self.generar_conjuntos()

        if len(self.parametros) == 0:
            self.generador_parametros()

        return visor_parametros(conjuntos=self.conjuntos, parametros=self.parametros)

    def solve(self, engine='coin', gap=0.0, tlimit_seconds=0, gen_lp_file=False):

        print('restolviendo el problema')

        self.estatus = 'Trabajando'

        # Agregar función objetivosolver += fobjetivo
        print('agregando target')
        self.solver += pu.lpSum(self.target)

        # Agregar restricciones
        for name, rest_list in self.restricciones.items():
            print('agregando', name)
            for rest in rest_list:
                # print('agregando restriccion', name, rest)
                self.solver += rest

        print('ejecutando solver')
        cpu_count = max(1, os.cpu_count()-1)
        print(f'usando {cpu_count} núcleos')
        if engine == 'glpk':
            if tlimit_seconds == 0.0:
                if gap == 0.0:
                    engine = pu.GLPK_CMD()

                else:
                    engine = pu.GLPK_CMD(
                        options=['--mipgap', str(gap)])
                    print('ejecutando gap:', gap)
            else:
                if gap == 0.0:
                    engine = pu.COIN_CMD(timeLimit=tlimit_seconds,
                                         threads=cpu_count)
                    print('tlimit:', tlimit_seconds, 'segundos')
                else:
                    engine = pu.COIN_CMD(timeLimit=tlimit_seconds,
                                         threads=cpu_count,
                                         options=[
                                             '--mipgap', str(gap)])
                    print('gap:', gap)
                    print('tlimit:', tlimit_seconds, 'segundos')

            self.solver.solve(solver=engine)

        else:
            if tlimit_seconds == 0.0:
                if gap == 0.0:
                    engine = pu.PULP_CBC_CMD()
                else:
                    engine = pu.PULP_CBC_CMD(gapRel=gap)
                    print('ejecutando gap:', gap)
            else:
                if gap == 0.0:
                    engine = pu.PULP_CBC_CMD(timeLimit=tlimit_seconds)
                    print('tlimit:', tlimit_seconds, 'segundos')

                else:
                    engine = pu.PULP_CBC_CMD(
                        gapRel=gap, timeLimit=tlimit_seconds)
                    print('ejecutando gap:', gap)
                    print('tlimit:', tlimit_seconds, 'segundos')

            self.solver.solve(solver=engine)

        print('solver ejecutado')
        self.estatus = pu.LpStatus[self.solver.status]

        if gen_lp_file:
            self.solver.writeLP(filename='model.lp')

    def generar_reporte(self):

        print('generando reporte')

        return generar_reporte(variables=self.variables, parametros=self.parametros, conjuntos=self.conjuntos)

    def guardar_reporte(self):

        print('guardando reporte')

        reporte = self.generar_reporte()

        guardar_reporte_xlsx(df_dict=reporte)

    def imprimir_modelo_lp(self, file_output: str):

        self.solver.writeLP(filename=file_output)
