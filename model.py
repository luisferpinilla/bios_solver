import pulp as pu


class Model():

    def __init__(self, definiciones: dict) -> None:

        # Conjuntos
        self._conjuntos = dict()
        # Parametros
        self._parameters = dict()

        # Variables
        self._variables = dict()

        # Definición del modelo
        self._definiciones = definiciones

        # Problema
        self._problema = pu.LpProblem("Bios", sense=pu.const.LpMinimize)

    def construir_parametros(self):
        pass

    def construir_variables(self):
        pass

    def construir_fob(self):
        pass

    def construir_restricciones(self):
        pass

    def resolver(self):
        pass
