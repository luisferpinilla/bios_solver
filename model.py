import pulp as pu

class Model():

    def __init__(self, definiciones:dict) -> None:
        
        # Parametros
        self._DM_kit = dict()
        self._AR_lt = dict()
        self._SS_ikt = dict()
        
        # Diccionarios
        self._l_i = dict()
        self._l_j = dict()
        self._m_i = dict()

        # Variables

        # Modelo
        self.definiciones = definiciones
        self.problema = pu.LpProblem("Bios", sense=pu.const.LpMinimize)


    def construir_variables(self):
        pass

    def construir_fob(self):
        pass

    def construir_restricciones(self):
        pass




