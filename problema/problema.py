import pulp as pu
import pandas as pd
from datetime import datetime


class Ingrediente():
    def __init__(self, nombre: str) -> None:
        self.nombre = nombre

    def __str__(self) -> str:
        return self.nombre


class Periodo():
    def __init__(self, periodo: int, fecha: datetime) -> None:
        self.periodo = periodo
        self.fecha = fecha

    def __str__(self) -> str:
        return self.fecha.strftime('%M-%d')


class Unidad_Almacenamiento():
    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        self.planta = None
        self.capacidad_kg = dict()
        self.asignacion_ingredientes = dict()
        self.cantidad_actual = 0.0

    def establecer_capacidad_almacenamiento(self, ingrediente: Ingrediente, cantidad: float):
        """Asigna la capacidad de almacenamiento para un ingrediente dato

        Args:
            ingrediente (Ingrediente): Ingrediente a asignar
            cantidad (float): cantidad máxima almacenable
        """
        self.capacidad_kg[ingrediente.nombre] = cantidad

    def establecer_asgignacion_ingredientes(self, ingrediente: Ingrediente, periodo: Periodo):
        self.asignacion_ingredientes[periodo] = ingrediente

    def __str__(self) -> str:
        return f'{self.planta}_{self.codigo}'


class Planta():
    def __init__(self, nombre: str) -> None:
        print(f'Creando planta: {nombre}')
        self.nombre = nombre
        self.empresa = None
        self.minutos_operacion = 0.0
        self.cantidad_plataformas = 0
        self.tiempo_descargue_igredientes_por_minuto = dict()
        self.tiempo_limpieza_en_minutos = dict()
        self.consumo_material = dict()
        self.inventario_al_cierre = dict()
        self.unidades_almacenamiento = list()

    def establecer_inventario_inicial(self, ingrediente: Ingrediente, inventario_inicial: float):
        print(
            f'  Agregando inventario inicial de {ingrediente} en {inventario_inicial}')
        self.inventarios_inicial[ingrediente.nombre] = inventario_inicial

    def establecer_tiempo_desgarge(self, ingrediente: Ingrediente, minutos: float):
        print(
            f'  Estableciendo tiempo de descarge para {ingrediente} en {minutos} minutos')
        self.tiempo_descargue_igredientes_por_minuto[ingrediente] = minutos

    def establecer_tiempo_limpieza(self, ingrediente: Ingrediente, minutos: float):
        print(
            f'  Estableciendo tiempo de limpieza para {ingrediente} en {minutos} minutos')

    def add_unidad_almacenamiento(self, unidad: Unidad_Almacenamiento):
        self.unidades_almacenamiento.append(unidad)
        unidad.planta = self
        print(f' agregando unidad de almacenamiento {unidad}')

    def establecer_consumo(self, ingrediente: Ingrediente, periodo: int, kilogramos: int):

        if not ingrediente.nombre in self.consumo_material.keys():
            self.consumo_material[ingrediente.nombre] = dict()

        self.consumo_material[ingrediente.nombre][periodo] = kilogramos

    def __str__(self) -> str:
        return self.nombre


class Empresa():
    def __init__(self, nombre: str) -> None:
        self.nombre = nombre
        self.plantas = dict()

    def add_planta(self, planta: Planta):
        if not planta.nombre in self.plantas.keys():
            self.plantas[planta.nombre] = planta
            planta.empresa = self.nombre


class Puerto():
    def __init__(self, nombre: str, codigo: str) -> None:
        self.nombre = nombre
        self.codigo = codigo
        self.operadores = dict()

    def __str__(self) -> str:
        return self.nombre


class Operador():
    def __init__(self, nombre: str) -> None:
        self.nombre = nombre
        self.puerto = None

    def establecer_puerto(self, puerto: Puerto):
        self.puerto = puerto


class Problema():

    def __init__(self, file: str) -> None:
        self.file = file

        self.ingredientes = dict()
        self.ingredientes_df = None

        self.empresas = dict()
        self.empresas_df = None

        self.plantas = dict()
        self.plantas_df = None

        self.unidades_almacenamiento = dict()
        self.unidades_almacenamiento_df = None

        self.puertos = dict()
        self.puertos_df = None

        self._cargar_ingredientes()
        self._cargar_empresas()
        self._cargar_plantas()
        self._cargar_unidades_almacenamiento()
        self._cargar_operadores()

    def _cargar_ingredientes(self):

        self.ingredientes_df = pd.read_excel(
            self.file, sheet_name='ingredientes')

        for i in self.ingredientes_df.index:
            ingrediente = Ingrediente(
                nombre=self.ingredientes_df.loc[i]['nombre'])
            self.ingredientes[ingrediente.nombre] = ingrediente

    def _cargar_empresas(self):

        self.empresas_df = pd.read_excel(io=self.file, sheet_name='empresas')

        for i in self.empresas_df.index:
            empresa = Empresa(nombre=self.empresas_df.loc[i]['empresa'])
            self.empresas[empresa.nombre] = empresa

    def _cargar_plantas(self):

        self.plantas_df = pd.read_excel(self.file, sheet_name='plantas')

        for i in self.plantas_df.index:

            planta = Planta(self.plantas_df.loc[i]['planta'])
            empresa = self.empresas[self.plantas_df.loc[i]['empresa']]
            empresa.add_planta(planta=planta)

            for ingrediente in self.ingredientes:
                planta.cantidad_plataformas = self.plantas_df.loc[i]['plataformas']

                planta.establecer_tiempo_desgarge(
                    ingrediente, self.plantas_df.loc[i]['operación_minutos'])
                planta.establecer_tiempo_limpieza(
                    ingrediente, self.plantas_df.loc[i]['operación_minutos'])

                self.plantas[planta.nombre] = planta

    def _cargar_unidades_almacenamiento(self):

        self.unidades_almacenamiento_df = pd.read_excel(
            self.file, sheet_name='unidades_almacenamiento')

        for i in self.unidades_almacenamiento_df.index:
            codigo_unidad = self.unidades_almacenamiento_df.loc[i]['unidad_almacenamiento']
            nombre_planta = self.unidades_almacenamiento_df.loc[i]['planta']
            planta = self.plantas[nombre_planta]
            nombre_ingrediente = self.unidades_almacenamiento_df.loc[i]['ingrediente_actual']
            cantidad_ingrediente = self.unidades_almacenamiento_df.loc[i]['cantidad_actual']
            unidad = Unidad_Almacenamiento(codigo=codigo_unidad)

            if nombre_ingrediente != 0:
                ingrediente = self.ingredientes[nombre_ingrediente]
                unidad.cantidad_actual = 0
            unidad.cantidad_actual = cantidad_ingrediente
            unidad = Unidad_Almacenamiento(codigo=codigo_unidad)

            unidad.establecer_asgignacion_ingredientes(
                ingrediente=ingrediente, periodo=0)
            planta.add_unidad_almacenamiento(unidad)

    def _cargar_operadores(self):

        self.puertos_df = pd.read_excel(self.file, sheet_name='operadores')

        for i in self.puertos_df.index:
            nombre_puerto = self.puertos_df.loc[i]['nombre_puerto']
            codigo_puerto = self.puertos_df.loc[i]['puerto']
            nombre_operador = self.puertos_df.loc[i]['operador']

            if not nombre_puerto in self.puertos.keys():
                puerto = Puerto(nombre=nombre_puerto, codigo=codigo_puerto)
            else:
                puerto = self.puertos[nombre_puerto]

            operador = Operador(nombre=nombre_operador)

            puerto.operadores[operador.nombre] = operador
