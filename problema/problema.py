import pulp as pu
import pandas as pd
from datetime import datetime
from problema.asignador_capacidad import AsignadorCapacidad
from tqdm import tqdm
import os


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
        self.codigo_planta = ''
        self.ingrediente_actual = None
        self.cantidad_actual = 0.0
        self.capacidad_kg = 0.0

    def establecer_capacidad_almacenamiento(self, ingrediente: str, cantidad: float):
        """Asigna la capacidad de almacenamiento para un ingrediente dato

        Args:
            ingrediente (Ingrediente): Ingrediente a asignar
            cantidad (float): cantidad máxima almacenable
        """
        self.capacidad_kg[ingrediente] = cantidad

    def __str__(self) -> str:
        return f'{self.codigo_planta}_{self.codigo}'


class Importacion():
    def __init__(self,
                 empresa: str,
                 puerto: str,
                 operador: str,
                 codigo: str,
                 ingrediente: str,
                 valor_cif: float,
                 inventario_inicial: float,
                 periodos: dict) -> None:

        self.empresa = empresa
        self.puerto = puerto
        self.operador = operador
        self.codigo = codigo
        self.ingrediente = ingrediente
        self.valor_cif = valor_cif
        self.inventario_inicial = inventario_inicial
        self.periodos = periodos

        self.vencimientos = dict()
        # vencimientos[periodo]
        self.inventario_al_cierre = dict()
        # invenario_al_cierre[periodo]
        self.llegadas_a_puerto = dict()
        # llegadas_a_puerto[periodo]

        self.despachos_a_planta = dict()
        # LPVAR despachos_a_planta[periodo]

        self.restricciones = list()

        self.terminos_fobj = list()

    def establecer_vencimiento(self, periodo: int, costo_por_kg: float):
        """ingresa un costo por kilogramo a cobrar por vencimiento durante el periodo dado

        Args:
            periodo (int): periodo en el que se aplicará el vencimiento
            costo_por_kg (float): Costo aplicado durante el vencimiento
        """
        self.vencimientos[periodo] = costo_por_kg

    def obtener_vencimiento(self, periodo: int) -> float:
        """returna el vencimiento para el periodo dado

        Args:
            periodo (int): periodo solicitado

        Returns:
            float: costo establecido por kilogramo
        """
        if periodo in self.vencimientos.keys():
            return self.vencimientos[periodo]
        return 0.0

    def agregar_llegada_en_barco(self, periodo: int, cantidad: pu.LpVariable):
        """adiciona variables de llegada de material para la importacion
        Args:
            periodo (int): periodo de llegada
            cantidad (pu.LpVariable): Variable de llegada de material
        """
        self.llegadas_a_puerto[periodo] = cantidad

    def agregar_despacho_a_planta(self, despacho_var: pu.LpVariable, periodo: int):
        """Agrega Variables de despacho

        Args:
            despacho_var (pu.LpVariable): variable de despacho
            periodo (int): periodo dado
        """
        if not periodo in self.despachos_a_planta.keys():
            self.despachos_a_planta[periodo] = list()
        self.despachos_a_planta[periodo].append(despacho_var)

    def obtener_despacchos_a_planta(self, periodo: int) -> list:
        """retorna una lista con las variables de despacho para cada planta

        Args:
            periodo (int): periodo consultado

        Returns:
            list: lista con las variables de despacho
        """
        if not periodo in self.despachos_a_planta.keys():
            return self.despachos_a_planta[periodo]
        return list()

    def build_variables(self):
        """Construye la lista de variables de inventario
        """
        for periodo, fecha in self.periodos.items():

            xip_name = f'xip_{self.empresa}_{self.operador}_{self.ingrediente}_{self.codigo}_{periodo}'

            xip_var = pu.LpVariable(name=xip_name,
                                    lowBound=0.0,
                                    cat=pu.LpContinuous)

            self.inventario_al_cierre[periodo] = xip_var

    def build_lp_model_components(self):
        """Genera las restricciones y función objetivo que aporta al problema
        """

        # xip = xip(t-1) + llegadas - despachos
        # xip + despachos = xip(t-1) + llegadas

        for periodo, fecha in self.periodos.items():

            left = list()
            right = list()

            xip = self.inventario_al_cierre[periodo]
            left.append(xip)

            despachos = self.obtener_despacchos_a_planta(periodo=periodo)
            for despacho in despachos:
                left.append(34000*despacho)

            if periodo == 0:
                xip_t1 = self.inventario_inicial
            else:
                xip_t1 = self.inventario_al_cierre[periodo-1]
            right.append(xip_t1)

            if periodo in self.llegadas_a_puerto.keys():
                llegadas = self.llegadas_a_puerto[periodo]
                for llegada in llegadas:
                    right.append(llegada)

            rest = (pu.lpSum(left) == pu.lpSum(
                right), f'inventario_{self.empresa}_{self.operador}_{self.ingrediente}_{self.codigo}_{periodo}')

            self.restricciones.append(rest)

            # Funcion objetivo
            costo_vencimiento = self.obtener_vencimiento[periodo]
            if costo_vencimiento > 0.0:
                self.terminos_fobj.append(costo_vencimiento*xip)

    def __str__(self) -> str:
        return f'{self.empresa}_{self.puerto}_{self.operador}_{self.codigo}_{self.ingrediente}'


class Planta():
    def __init__(self,
                 nombre: str,
                 periodos: dict,
                 costo_backorder=800,
                 costo_exceso_capacidad=400,
                 costo_incumplir_safety_stock=200) -> None:

        self.nombre = nombre
        self.empresa = None
        self.periodos = periodos
        self.turno = 0.0
        self.cantidad_plataformas = 0
        self.tiempo_descargue_igredientes_por_minuto = dict()
        self.tiempo_limpieza_en_minutos = 0
        self.ingredientes_set = set()  # lista de ingredientes que se manejan en la planta
        self.consumo_material = dict()  # consumo_material[material][periodo]
        self.safety_stock_dias = dict()  # safety_stock_dias[material]
        # safety_stock_cantidad[material][periodo]
        self.safety_stock_cantidad = dict()
        # safety_stock_cantidad[ingrediente][periodo]
        self.inventario_inicial = dict()  # inventario_inicial[material]
        # LPVAR inventario_al_cierre[material][periodo]
        self.llegadas_programadas_material = dict()
        # llegadas_programadas_material[material][periodo]
        self.lista_llegadas_modelo = dict()
        # LPVAR lista_llegadas_modelo[material][periodo]
        self.inventario_al_cierre = dict()
        # LPVAR backirder_al_cierre[material][periodo]
        self.backorder_al_cierre = dict()
        # LPVAR unidades_almacanamiento[codigo][ingrediente]
        self.incumplimiento_ss_al_cierre = dict()
        # LPVAR incumplimiento_ss_al_cierre[material][periodo]
        self.incumplimiento_cap_max = dict()
        # LPVAR incumplimiento_cap_max[ingrediente][periodo]
        self.costo_backorder = costo_backorder
        # capacidad_almacenamiento[ingrediente][periodo]
        self.costo_exceso_capacidad = costo_exceso_capacidad
        self.costo_incumplir_ss = costo_incumplir_safety_stock
        self.capacidad_almacenamiento = dict()
        self.expresiones_funcion_objetivo = list()
        self.lista_restricciones = list()

    def establecer_tiempo_desgarge(self, ingrediente: str, minutos: float):
        # print(f'  Estableciendo tiempo de descarge para {ingrediente} en {minutos} minutos')
        self.tiempo_descargue_igredientes_por_minuto[ingrediente] = minutos
        self.ingredientes_set.add(ingrediente)

    def establecer_tiempo_limpieza(self, minutos: float):
        # print(f'  Estableciendo tiempo de limpieza para {ingrediente} en {minutos} minutos')
        self.tiempo_limpieza_en_minutosminutos = minutos

    def establecer_llegadas_material(self, ingrediente: str, periodo: int, cantidad: float):
        """configura la cantidad de material que BIOS ya ha planeado despachar

        Args:
            ingrediente (Ingrediente): ingrediente programado para llegar a la planta
            periodo (int): periodo en el que se espera la llegada
            cantidad (float): cantidad que se ha programado para llegar
        """

        if not ingrediente in self.llegadas_programadas_material.keys():
            self.llegadas_programadas_material[ingrediente] = dict()

        self.llegadas_programadas_material[ingrediente][periodo] = cantidad

    def obtener_maxima_capacidad_recepcion_camiones(self, ingrediente: str) -> int:
        """Retorna la cantidad maxima de camiones que se pueden recibir en un dia

        Returns:
            str: ingrediente al que se quiere revisar la capacidad de recepcion
        """

        if ingrediente in self.tiempo_descargue_igredientes_por_minuto.keys():
            return int((self.turno * self.cantidad_plataformas)/self.tiempo_descargue_igredientes_por_minuto[ingrediente])

        return 0

    def obtener_llegada_material(self, ingrediente: str, periodo: int) -> float:
        """obtiene la cantidad programada para llegar a planta. en caso que no haya registro retorna 0.0

        Args:
            ingrediente (str): nombre del ingrediente
            periodo (int): periodo

        Returns:
            float: cantidad programada para llegar
        """

        if ingrediente in self.llegadas_programadas_material.keys():
            if periodo in self.llegadas_programadas_material[ingrediente].keys():
                return self.llegadas_programadas_material[ingrediente][periodo]

        return 0.0

    def establecer_consumo(self, ingrediente: str, periodo: int, kilogramos: int):

        if not ingrediente in self.consumo_material.keys():
            self.consumo_material[ingrediente] = dict()

        self.consumo_material[ingrediente][periodo] = kilogramos

    def obtener_consumo(self, ingrediente: str, periodo: int) -> float:
        """Obtiene el consumo proyectado del ingrediente en un periodo

        Args:
            ingrediente (str): nombre del ingrediente
            periodo (int): periodo a consultar

        Returns:
            float: consumo proyectado del ingrediente para el periodo dado en kilogramos
        """

        if ingrediente in self.consumo_material.keys():
            if periodo in self.consumo_material[ingrediente].keys():
                return self.consumo_material[ingrediente][periodo]

        return 0.0

    def obtener_consumo_promedio_diario(self, ingrediente: str) -> float:

        suma = 0.0
        for periodo in self.periodos:
            suma += self.obtener_consumo(ingrediente=ingrediente,
                                         periodo=periodo)

        nnums = len(self.periodos)

        if nnums > 0.0:
            return suma/nnums
        else:
            return 0.0

    def establecer_safety_stock_dias(self, ingrediente: str, dias: float):

        if dias > 0:
            if not ingrediente in self.safety_stock_dias.keys():
                self.safety_stock_dias[ingrediente] = dict()

            self.safety_stock_dias[ingrediente] = dias
            self.ingredientes_set.add(ingrediente)

    def obtener_safety_stock_dias(self, ingrediente: str) -> float:
        if ingrediente in self.safety_stock_dias.keys():
            return self.safety_stock_dias[ingrediente]

        return 0.0

    def obtener_safety_stock_cantidad(self, ingrediente: str) -> float:
        return self.obtener_consumo_promedio_diario(ingrediente)*self.obtener_safety_stock_dias(ingrediente=ingrediente)

    def adicionar_capacidad_almacenamiento(self, ingrediente: str, cantidad_kg: float):

        if not ingrediente in self.capacidad_almacenamiento.keys():
            self.capacidad_almacenamiento[ingrediente] = cantidad_kg
        else:
            self.capacidad_almacenamiento[ingrediente] += cantidad_kg

    def obtener_capacidad_almacenamiento(self, ingrediente: str):

        if ingrediente in self.capacidad_almacenamiento.keys():
            return self.capacidad_almacenamiento[ingrediente]

        return 0.0

    def adicionar_inventario_inicial(self, ingrediente: str, cantidad_kg: float):
        """Adiciona inventario inicial a la planta.

        Args:
            ingrediente (str): codigo del ingrediente a adicionar
            cantidad_kg (float): cantidad en kilogramos a adicionar
        """
        if ingrediente in self.inventario_inicial.keys():
            self.inventario_inicial[ingrediente] += cantidad_kg
        else:
            self.inventario_inicial[ingrediente] = cantidad_kg

    def obtener_inventario_inicial(self, ingrediente: str) -> float:
        """Obtiene el inventario inicial en planta del ingrediente dado

        Args:
            ingrediente (str): nombre del ingrediente

        Returns:
            float: cantidad de ingrediente en el inventario inicial
        """
        if ingrediente in self.inventario_inicial.keys():
            return self.inventario_inicial[ingrediente]

        return 0.0

    def establecer_var_llegada_material(self, material: str, periodo: int, var_llegada: pu.LpVariable):
        """Agrega variables de llegada de material desde puerto

        Args:
            material (str): ingrediente que se planea recibir
            periodo (int): periodo en el que llega la carga
            var_llegada (pu.LpVariable): variable LP transporte
        """

        if not material in self.lista_llegadas_modelo:
            self.lista_llegadas_modelo[material] = dict()

        if not periodo in self.lista_llegadas_modelo[material].keys():
            self.lista_llegadas_modelo[material][periodo] = list()

        self.lista_llegadas_modelo[material][periodo].append(var_llegada)

    def obtener_vars_llegadas_material(self, material: str, periodo: int) -> list:

        if material in self.lista_llegadas_modelo.keys():
            if periodo in self.lista_llegadas_modelo[material].keys():
                return self.lista_llegadas_modelo[material][periodo]

        return list()

    def _buid_vars(self):

        # Construir las variables de planta
        for ingrediente in self.ingredientes_set:
            # Obtener parametros que no dependen del tiempo

            # inventario inicial
            ii = self.obtener_inventario_inicial(ingrediente=ingrediente)

            # consumo promerio
            dmavg_par = self.obtener_consumo_promedio_diario(
                ingrediente=ingrediente)

            # inventario de seguridad
            ss = self.obtener_safety_stock_cantidad(ingrediente=ingrediente)

            # si el inventario inicial es 0 y no hay consumo promedio, no vamos a agregar variables al respecto

            if ii > 0.0 or dmavg_par > 0:

                # para cada ingrediente, agregar diccioanrio para los periodos
                self.inventario_al_cierre[ingrediente] = dict()
                self.incumplimiento_cap_max[ingrediente] = dict()
                self.backorder_al_cierre[ingrediente] = dict()
                if ss > 0.0:
                    self.incumplimiento_ss_al_cierre[ingrediente] = dict()

                for periodo in self.periodos:

                    # crear varibles
                    # agregar variables de inventario al cierre
                    xiu = pu.LpVariable(name=f'XIU_{self.nombre}_{ingrediente}_{periodo}',
                                        lowBound=0.0,
                                        cat=pu.LpContinuous)

                    self.inventario_al_cierre[ingrediente][periodo] = xiu

                    # agregar variables de backorder
                    xbk = pu.LpVariable(name=f'XBK_{self.nombre}_{ingrediente}_{periodo}',
                                        lowBound=0.0,
                                        cat=pu.LpContinuous)
                    self.backorder_al_cierre[ingrediente][periodo] = xbk

                    # agregar variable de exceso de inventario
                    xmx = pu.LpVariable(name=f'XMX_{self.nombre}_{ingrediente}_{periodo}',
                                        lowBound=0.0,
                                        cat=pu.LpContinuous)

                    self.incumplimiento_cap_max[ingrediente][periodo] = xmx

                    # agregar variables de no cumplimiento de safety stock
                    if ss > 0:
                        var_name = f'XSS_{self.nombre}_{ingrediente}_{periodo}]'
                        xss = pu.LpVariable(name=var_name,
                                            lowBound=0.0,
                                            cat=pu.LpContinuous)

                        self.incumplimiento_ss_al_cierre[ingrediente][periodo] = xss

    def build_lp_model_components(self):
        """Construye las variables de planta, restricciones y componentes de la función objetivo 
        requeridas para el problema
        """
        self.lista_restricciones = list()

        # Construir las variables de planta
        for ingrediente in self.inventario_al_cierre.keys():

            # Obtener parametros que no dependen del tiempo
            # inventario inicial
            ii = self.obtener_inventario_inicial(ingrediente=ingrediente)

            # consumo promerio
            dmavg_par = self.obtener_consumo_promedio_diario(
                ingrediente=ingrediente)

            # si el inventario inicial es 0 y no hay consumo promedio, no vamos a agregar variables al respecto
            if ii > 0.0 or dmavg_par > 0:

                for periodo in self.periodos:

                    # Obtener términos de restriccion
                    # Demanda a satisfacer
                    dm_t = self.obtener_consumo(
                        ingrediente=ingrediente, periodo=periodo)
                    # Transito actual a planta
                    ttp_t = self.obtener_llegada_material(
                        ingrediente=ingrediente, periodo=periodo)
                    # lista de variables de transporte que el modelo envia
                    itdr_t_vars = self.obtener_vars_llegadas_material(
                        material=ingrediente, periodo=periodo)
                    # capacidad de almacenamiento
                    cap_almacenamiento_par = self.obtener_capacidad_almacenamiento(
                        ingrediente=ingrediente)
                    # inventario de seguridad
                    ss = self.obtener_safety_stock_cantidad(
                        ingrediente=ingrediente)
                    # variable de inventario actual xiu
                    xiu = self.inventario_al_cierre[ingrediente][periodo]
                    # inventario al cierre anterior
                    if periodo > 0:
                        xiu_ant = self.inventario_al_cierre[ingrediente][periodo-1]
                    else:
                        xiu_ant = ii
                    # backorder
                    xbk = self.backorder_al_cierre[ingrediente][periodo]
                    # varible de exceso de capacidad
                    xmx = self.incumplimiento_cap_max[ingrediente][periodo]
                    # Costo backorder
                    costo_back = self.costo_backorder
                    # Costo no safety stock
                    costo_ss = self.costo_incumplir_ss
                    # Costo exceso capacidad
                    costo_cap = self.costo_exceso_capacidad

                    # Funcion objetivo
                    # Agregar la expresión sobre el backorder a la función objetivo
                    self.expresiones_funcion_objetivo.append(costo_back*xbk)
                    # agregar la expresion sobre el exceso de inventario a la función objetivo
                    self.expresiones_funcion_objetivo.append(costo_cap*xmx)
                    # agregar la expresion sobre el no cumplimiento del invenario de seguridad
                    if ss > 0.0:
                        xss = self.incumplimiento_ss_al_cierre[ingrediente][periodo]
                        self.expresiones_funcion_objetivo.append(costo_ss*xss)

                    # Restricciones

                    # Balance de masa
                    # XIU = XIU(t-1) + llegadaProgramada + llegadasPlaneadas + XBK - DM
                    # XIU + DM = XIU(t-1) + llegadaProgramada + llegadasPlaneadas + XBK
                    left_expresion = list()
                    right_expresion = list()

                    nombre_rest = f'inv_{self.nombre}_al_cierre_{ingrediente}_{periodo}'

                    # xiu
                    left_expresion.append(xiu)

                    # + DM demanda del periodo
                    left_expresion.append(dm_t)

                    # xiu_(t-1)
                    right_expresion.append(xiu_ant)

                    # + ttp llegadasProgramadas
                    right_expresion.append(ttp_t)

                    # + llegadas planeadas
                    for itdr_var in itdr_t_vars:
                        right_expresion.append(34000*itdr_var)

                    # + XBK Backorder
                    right_expresion.append(xbk)

                    # Generar restriccion
                    rest = (pu.lpSum(left_expresion) ==
                            pu.lpSum(right_expresion), nombre_rest)

                    self.lista_restricciones.append(rest)

                    # Restriccion de capacidad de almacenamiento
                    # xiu < cap + xmx
                    nombre_rest = f'No_exceder_almacenamiento_en_{self.nombre}_de_{ingrediente}_en_{periodo}'
                    rest = (xiu <= cap_almacenamiento_par + xmx, nombre_rest)
                    self.lista_restricciones.append(rest)

                    # Restriccion de SS
                    if ss > 0:
                        nombre_rest = f'cumplir_ss_en_{self.nombre}_de_{ingrediente}_en_{periodo}'
                        xss = self.incumplimiento_ss_al_cierre[ingrediente][periodo]
                        rest = (xiu >= ss + xss)
                        self.lista_restricciones.append(rest)

        # Restriccion de capacidad de recepcion
        # sum(itdr_t_vars)*tiempo_ingrediente <= toperacion_dia*plataforma - tiempo_limpieza
        for periodo, fecha in self.periodos.items():

            left_expresion = list()
            right_expresion = list()

            for ingrediente, temp in self.inventario_al_cierre.items():

                tiempo_ingrediente = self.tiempo_descargue_igredientes_por_minuto[ingrediente]
                tiempo_limpieza = self.tiempo_limpieza_en_minutos
                cantidad_plataformas = self.cantidad_plataformas
                tiempo_operativo = self.turno

                itdr_t_vars = self.obtener_vars_llegadas_material(
                    material=ingrediente, periodo=periodo)

                for itdr in itdr_t_vars:
                    # tiempo_limpieza * itdr
                    left_expresion.append(
                        tiempo_ingrediente*itdr + tiempo_limpieza)

                # Agregar tiempo de limpieza por cada ingrediente recibido
                if len(itdr_t_vars) > 0:
                    left_expresion.append(tiempo_limpieza)

            if len(left_expresion) > 0:
                right_expresion.append(tiempo_operativo*cantidad_plataformas)
                rest_name = f'Tiempo_recepcion_{self.nombre}_{periodo}'
                rest = (pu.lpSum(left_expresion) <=
                        pu.lpSum(right_expresion), rest_name)

                self.lista_restricciones.append(rest)

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
    def __init__(self, nombre: str, puerto: str) -> None:
        self.nombre = nombre
        self.puerto = puerto


class Barco():
    def __init__(self, empresa: str,
                 importacion: str,
                 puerto: str,
                 operador: str,
                 ingrediente: str,
                 periodo_llegada: int,
                 cantidad_kg: float,
                 valor_cif: float,
                 costo_directo: float,
                 costo_bodegaje: float,
                 periodos=dict,
                 rata_desgarge=5000000,
                 capacidad_camion=34000) -> None:

        self.empresa = empresa
        self.importacion = importacion
        self.puerto = puerto
        self.operador = operador
        self.ingrediente = ingrediente
        self.periodo_llegada = periodo_llegada
        self.periodo_partida = -1
        self.cantidad_kg = cantidad_kg
        self.valor_cif = valor_cif
        self.llegadas = dict()
        self.periodos = periodos
        self.rata_descarge = rata_desgarge
        self.capacidad_camion = capacidad_camion
        self.costo_bodegaje = costo_bodegaje
        self.costo_despacho_directo = costo_directo
        self.lista_despacho_directo = dict()
        # LPVAR lista_despacho_directo[periodo] lista
        self.bodegaje = dict()
        # LPVAR cantidad que se queda en bodega de puerto

        self.lista_restricciones = list()
        self.expresiones_funcion_objetivo = list()

        ultimo_periodo = max(self.periodos.keys())

        while cantidad_kg > 0:

            var_name = f'xpl_{self.empresa}_{self.puerto}_{self.operador}_{self.importacion}_{self.ingrediente}_{periodo_llegada}'

            if cantidad_kg >= rata_desgarge and periodo_llegada < ultimo_periodo:

                bodegaje_var = pu.LpVariable(name=var_name,
                                             lowBound=0,
                                             upBound=self.rata_descarge + 1,
                                             cat=pu.LpInteger)

                self.bodegaje[periodo_llegada] = bodegaje_var

                self.llegadas[periodo_llegada] = rata_desgarge

                cantidad_kg -= rata_desgarge

            else:

                bodegaje_var = pu.LpVariable(name=var_name,
                                             lowBound=0,
                                             upBound=self.rata_descarge + 1,
                                             cat=pu.LpInteger)

                self.bodegaje[periodo_llegada] = bodegaje_var

                self.llegadas[periodo_llegada] = cantidad_kg

                cantidad_kg -= cantidad_kg

            periodo_llegada += 1

        self.periodo_partida = periodo_llegada

    def establecer_despachos_directos(self, periodo: int, despacho: pu.LpVariable):
        """recibe una variable de despacho directo y la tiene en cuenta en las restricciones de balance de masa en puerto

        Args:
            periodo (int): periodo en el que llega la carga
            despacho (pu.LpVariable): variable de despacho
        """
        if not periodo in self.lista_despacho_directo.keys():
            self.lista_despacho_directo[periodo] = list()
        self.lista_despacho_directo[periodo].append(despacho)

    def obtener_despachos_directos(self, periodo: int) -> list:
        """entrega la lista de variables de despacho directo hacia alguna planta para un periodo dado

        Args:
            periodo (int): periodo a consultar

        Returns:
            list: lista de variables de salida
        """
        if periodo in self.lista_despacho_directo.keys():
            return self.lista_despacho_directo[periodo]
        return list()

    def establecer_envio_a_bodega(self, periodo: int, bodegaje: pu.LpVariable):
        """recibe una variable para bodegaje en un periodo

        Args:
            periodo (int): periodo de bodegaje
            bodegaje (pu.LpVariable): variable sobre bodegaje
        """

        if not periodo in self.bodegaje.keys():
            self.bodegaje[periodo] = list()
        self.bodegaje[periodo].append(bodegaje)

    def obtener_envios_a_bodega(self) -> dict:
        """Entrega los envios a bodega correspondientes

        Returns:
            dict: diccionario con los envios a bodega indexados por periodo
        """
        return self.bodegaje

    def build_lp_components(self):

        # Costos de despacho directo
        for periodo, lista in self.lista_despacho_directo.items():
            for itd in lista:
                self.expresiones_funcion_objetivo.append(
                    self.costo_despacho_directo*itd)

        for periodo, xpl in self.bodegaje.items():
            if self.periodo_partida == periodo:
                self.expresiones_funcion_objetivo.append(
                    self.costo_bodegaje*xpl)

        # Balance de masa bif
        # xpl_t + despachos_directos_t == llegada_t
        for periodo, llegada_t in self.llegadas.items():

            if periodo in self.bodegaje.keys():

                rest_name = f'balance_masa_bif_{self.empresa}_{self.puerto}_{self.importacion}_{self.ingrediente}_{periodo}'

                xpl_t = self.bodegaje[periodo]

                despachos_directos_t = self.obtener_despachos_directos(
                    periodo=periodo)

                despachos_directos_t = [
                    34000*lp_variable for lp_variable in despachos_directos_t]

                rest = (xpl_t + pu.lpSum(despachos_directos_t)
                        == llegada_t, rest_name)

                self.lista_restricciones.append(rest)


class Importacion():
    def __init__(self, empresa: str,
                 puerto: str,
                 codigo: str,
                 operador: str,
                 ingrediente: str,
                 valor_cif: float,
                 costo_bodegaje: float,
                 periodos: dict) -> None:

        self.periodos = periodos
        self.empresa = empresa
        self.puerto = puerto
        self.codigo = codigo
        self.operador = operador
        self.ingrediente = ingrediente
        self.perido_llegada = 1000
        self.periodo_partida = -1
        self.inventario_inicial = 0.0
        self.valor_cif = valor_cif
        self.costo_bodegaje = costo_bodegaje
        self.costo_vencimiento = dict()
        # costo_vencimiento[periodo]
        self.variables_bodegaje = dict()
        # LPVAR variables_bodegaje[periodo]
        self.variables_despacho = dict()
        # LPVAR variables_despacho[periodo]
        self.inventario_al_cierre = dict()
        # LPVAR inventario_al_cierre[periodo]

        self.lista_restricciones = list()

        self.lista_parametros_obj = list()

    def establecer_costo_vencimiento(self, periodo: int, valor: float):
        """Establece el valor a cobrarse al vencimiento

        Args:
            periodo (int): periodo del cobro
            valor (float): cantidad cobrada por kilogramo vencido
        """
        self.costo_vencimiento[periodo] = valor

    def obtener_costo_vencimiento(self, periodo) -> float:
        """Regresa el costo por vencimiento a cobrar por kilo en un periodo dado

        Args:
            periodo (int): periodo a consultar

        Returns:
            float: valor cobrado por kilogramo en el periodo dado
        """
        if periodo in self.costo_vencimiento.keys():
            return self.costo_vencimiento[periodo]
        return 0.0

    def establecer_inventario_inicial(self, cantidad: float):
        self.perido_llegada = -1
        self.inventario_inicial = cantidad

    def agregar_llegada_de_bodegaje(self, periodo: int, llegada: pu.LpVariable):

        if periodo < self.perido_llegada:
            self.perido_llegada = periodo

        if self.periodo_partida < periodo:
            self.periodo_partida = periodo

        if not periodo in self.variables_bodegaje.keys():
            self.variables_bodegaje[periodo] = llegada
        else:
            print("error")

    def agregar_despacho_a_planta(self, periodo: int, despacho: pu.LpVariable):
        if not periodo in self.variables_despacho.keys():
            self.variables_despacho[periodo] = list()

        self.variables_despacho[periodo].append(despacho)

    def obtener_despachos_a_planta(self, periodo: int) -> list():
        if periodo in self.variables_despacho.keys():
            return self.variables_despacho[periodo]

        return list()

    def build_vars(self):

        # Variables de cierre de inventario
        for periodo in self.periodos.keys():
            # if periodo >= self.perido_llegada:

            # Crear variable de inventario al final del día
            xip_name = f'xip_{self.empresa}_{self.ingrediente}_{self.codigo}_{periodo}'
            xip_var = pu.LpVariable(name=xip_name,
                                    lowBound=0.0,
                                    cat=pu.LpContinuous)
            self.inventario_al_cierre[periodo] = xip_var

    def buid_lp_components(self):

        # Balance de masa de invenarios
        # xip = xip(t-1) + llegadas - salidas
        # xip -salidas = xip(t-1) + llegadas

        for periodo in self.periodos:

            left_expresion = list()
            right_expresion = list()

            # xip
            xip_t = self.inventario_al_cierre[periodo]
            left_expresion.append(xip_t)

            # xip(t-1)
            if periodo == 0:
                xip_t1 = self.inventario_inicial
                right_expresion.append(xip_t1)
            else:
                xip_t1 = self.inventario_al_cierre[periodo-1]
            right_expresion.append(xip_t1)

            # Llegada
            if periodo in self.variables_bodegaje.keys():
                xpl_t = self.variables_bodegaje[periodo]
                right_expresion.append(xpl_t)

            # Despachos
            despachos_t = self.obtener_despachos_a_planta(periodo=periodo)
            for despacho_t in despachos_t:
                left_expresion.append(34000*despacho_t)

            rest_name = f'balance_{self.empresa}_{self.ingrediente}_{self.codigo}_{periodo}'

            rest = (pu.lpSum(left_expresion) ==
                    pu.lpSum(right_expresion), rest_name)

            self.lista_restricciones.append(rest)

            # Costo de vencimientos
            costo_vencimiento = self.obtener_costo_vencimiento(
                periodo=periodo)

            if costo_vencimiento > 0.0:
                self.lista_parametros_obj.append(costo_vencimiento*xip_t)

            # costos de bodegaje, inventario al momento de la partida del barco
            if periodo == self.periodo_partida:
                self.lista_parametros_obj.append(
                    self.costo_bodegaje*xip_t)

    def fill_dimension_importaciondf(self, dict_to_fill: dict):

        dict_to_fill['empresa'].append(self.empresa)
        dict_to_fill['puerto'].append(self.puerto)
        dict_to_fill['importacion'].append(self.codigo)
        dict_to_fill['operador'].append(self.operador)
        dict_to_fill['ingrediente'].append(self.ingrediente)
        dict_to_fill['periodo_atraque'].append(self.perido_llegada)
        dict_to_fill['periodo_partida'].append(self.periodo_partida)
        dict_to_fill['inventario_inicial'].append(self.inventario_inicial)
        dict_to_fill['valor_cif'].append(self.valor_cif)
        dict_to_fill['costo_bodegaje'].append(self.costo_bodegaje)

    def fill_fact_inventario_puerto(self, dict_to_fill: dict):

        for periodo, fecha in self.periodos.items():
            dict_to_fill['empresa'].append(self.empresa)
            dict_to_fill['puerto'].append(self.puerto)
            dict_to_fill['importacion'].append(self.codigo)
            dict_to_fill['operador'].append(self.operador)
            dict_to_fill['ingrediente'].append(self.ingrediente)
            inventario_al_cierre = self.inventario_al_cierre[periodo].varValue
            dict_to_fill['inventario_al_cierre'].append(inventario_al_cierre)
            dict_to_fill['periodo'].append(periodo)
            dict_to_fill['fecha'].append(fecha)

    @property
    def id(self) -> str:
        return f'{self.empresa}_{self.operador}_{self.ingrediente}_{self.codigo}'

    def __str__(self) -> str:
        return self.id


class Transporte():
    def __init__(self,
                 barcos: dict,
                 importaciones: dict,
                 plantas: dict,
                 fletes: dict,
                 intercompany: dict,
                 periodos: dict) -> None:

        self.barcos = barcos
        self.importaciones = importaciones
        self.plantas = plantas
        self.periodos = periodos
        self.fletes = fletes
        self.intercompany = intercompany

        self.lista_retricciones = list()
        self.lista_fobj = list()

    def build(self):

        ultimo_periodo = max(self.periodos.keys())

        # Crear variables Despacho directo
        for periodo, fecha in self.periodos.items():
            for nombre_barco, barco in self.barcos.items():
                for nombre_planta, planta in self.plantas.items():

                    dm_t = planta.obtener_consumo_promedio_diario(
                        ingrediente=barco.ingrediente)
                    ca = planta.obtener_capacidad_almacenamiento(
                        ingrediente=barco.ingrediente)

                    intercompany = self.intercompany[barco.empresa][planta.empresa] * \
                        barco.valor_cif

                    itd_name = f'despacho_directo_{barco.empresa}_{barco.puerto}_{barco.operador}_{barco.importacion}_{barco.ingrediente}_{planta.nombre}_{periodo}'
                    maxima_cantidad_camiones = planta.obtener_maxima_capacidad_recepcion_camiones(
                        ingrediente=barco.ingrediente)

                    # Si en este periodo el barco esta entregando material
                    activo = periodo in barco.llegadas.keys()

                    # Despachar solo si hay capacidad, consumo y el despacho llega dentro del horizonte
                    if activo and dm_t > 0 and ca > 0 and maxima_cantidad_camiones > 0 and periodo + 2 < ultimo_periodo:
                        # Crear la variable
                        itd = pu.LpVariable(name=itd_name,
                                            lowBound=0,
                                            upBound=maxima_cantidad_camiones,
                                            cat=pu.LpInteger)

                        # Entregar variable a barco
                        barco.establecer_despachos_directos(
                            periodo=periodo, despacho=itd)

                        # entregar variable a planta
                        planta.establecer_var_llegada_material(
                            material=barco.ingrediente, periodo=periodo+2, var_llegada=itd)

                        # Costo flete
                        flete_por_kg = self.fletes[barco.puerto][barco.operador][
                            barco.ingrediente][nombre_planta] + intercompany
                        self.lista_fobj.append(34000*flete_por_kg*itd)

        # Crear variables Despacho bodega
        for periodo, fecha in self.periodos.items():
            for codigo_importacion, importacion in self.importaciones.items():
                for nombre_planta, planta in self.plantas.items():

                    dm_t = planta.obtener_consumo_promedio_diario(
                        ingrediente=barco.ingrediente)
                    ca = planta.obtener_capacidad_almacenamiento(
                        ingrediente=barco.ingrediente)

                    intercompany = self.intercompany[importacion.empresa][planta.empresa] * \
                        importacion.valor_cif

                    itr_name = f'despacho_bodega_{importacion.empresa}_{importacion.puerto}_{importacion.operador}_{importacion.codigo}_{importacion.ingrediente}_{planta.nombre}_{periodo}'
                    maxima_cantidad_camiones = planta.obtener_maxima_capacidad_recepcion_camiones(
                        ingrediente=barco.ingrediente)

                    # Despachar solo si hay capacidad, consumo y el despacho llega dentro del horizonte
                    if dm_t > 0 and ca > 0 and maxima_cantidad_camiones > 0 and periodo + 2 < ultimo_periodo:
                        # Crear la variable
                        itr = pu.LpVariable(name=itr_name,
                                            lowBound=0,
                                            upBound=maxima_cantidad_camiones,
                                            cat=pu.LpInteger)

                        # Entregar variable a importacion
                        importacion.agregar_despacho_a_planta(
                            periodo=periodo,
                            despacho=itr)

                        # entregar variable a planta
                        planta.establecer_var_llegada_material(
                            material=importacion.ingrediente, periodo=periodo+2, var_llegada=itr)

                        # Costo flete

                        flete_por_kg = self.fletes[importacion.puerto][
                            importacion.operador][importacion.ingrediente][nombre_planta] + intercompany
                        self.lista_fobj.append(34000*flete_por_kg*itr)


class Problema():

    def __init__(self, file: str) -> None:
        self.file = file

        self.rata_desgarge_puertos = 5000000
        self.capacidad_camion = 34000

        self.periodos = dict()
        self.periodos_df = None

        self.ingredientes = dict()
        self.ingredientes_df = None

        self.empresas = dict()
        self.empresas_df = None

        self.plantas = dict()
        self.plantas_df = None

        self.unidades_almacenamiento = dict()
        self.unidades_almacenamiento_df = None

        self.consumo_planta = dict()
        self.consumo_planta_df = None

        self.safety_stock = dict()
        self.safety_stock_df = None

        self.transitos_planta = dict()
        self.transitos_planta_df = dict()

        self.puertos = dict()
        self.puertos_df = None

        self.operadores = dict()

        self.importaciones = dict()
        self.importaciones_df = None

        self.barcos = dict()
        self.barcos_df = None

        self.fletes = dict()
        self.fletes_df = None

        self.intercompany = dict()
        self.intercompany_df = None

        self.transporte = None

        self.solver = pu.LpProblem(
            name='minimizar_costo_logístico',
            sense=pu.const.LpMinimize)

        self.status = 'No Solved'

        self._cargar_periodos()
        self._cargar_ingredientes()
        self._cargar_plantas()
        self._cargar_unidades_almacenamiento()
        self._cargar_consumo_planta()
        self._cargar_safety_stock()
        self._cargar_transitos_planta()
        self._cargar_operadores()
        self._cargar_transitos_a_puerto()
        self._cargar_inventarios_puerto()
        self._cargar_costos_almacenamiento_puerto()
        self._cargar_fletes()
        self._cargar_intercompany()
        self._cargar_transportes()
        self._cargar_importaciones()

        self._buid()

    def _cargar_periodos(self):
        self.periodos_df = pd.read_excel(
            self.file, sheet_name='consumo_proyectado')

        columns = self.periodos_df.columns

        columns_to_remove = ['key', 'empresa', 'ingrediente', 'planta']

        dates = [datetime.strptime(x, '%d/%m/%Y')
                 for x in columns if not x in columns_to_remove]

        dates = sorted(dates)

        self.periodos = {x: dates[x] for x in range(len(dates))}

        periodos_dict = dict()
        periodos_dict['periodo'] = list()
        periodos_dict['fecha'] = list()

        for periodo, fecha in self.periodos.items():
            periodos_dict['periodo'].append(periodo)
            periodos_dict['fecha'].append(fecha)

        self.periodos_df = pd.DataFrame(periodos_dict)

    def _cargar_ingredientes(self):

        self.ingredientes_df = pd.read_excel(
            self.file, sheet_name='ingredientes')

        for i in self.ingredientes_df.index:
            ingrediente = Ingrediente(
                nombre=self.ingredientes_df.loc[i]['nombre'])
            self.ingredientes[ingrediente.nombre] = ingrediente

    def _cargar_plantas(self):

        # Cargar archivo de plantas y empresas

        self.plantas_df = pd.read_excel(self.file, sheet_name='plantas')

        # Cargar empresas
        empresas_dict = dict()
        empresas_dict['nombre'] = list()

        for nombre_empresa in list(self.plantas_df['empresa'].unique()):
            empresa = Empresa(nombre=nombre_empresa)
            self.empresas[nombre_empresa] = empresa
            empresas_dict['nombre'].append(nombre_empresa)

        self.empresas_df = pd.DataFrame(empresas_dict)
        # Cargar plantas

        for i in self.plantas_df.index:

            planta = Planta(
                nombre=self.plantas_df.loc[i]['planta'],
                periodos=self.periodos)

            empresa = self.empresas[self.plantas_df.loc[i]['empresa']]

            empresa.add_planta(planta=planta)

            for ingrediente in self.ingredientes:
                planta.cantidad_plataformas = self.plantas_df.loc[i]['plataformas']

                planta.establecer_tiempo_desgarge(
                    ingrediente, self.plantas_df.loc[i][ingrediente])

                planta.establecer_tiempo_limpieza(
                    minutos=self.plantas_df.loc[i]['minutos_limpieza'])

                planta.turno = self.plantas_df.loc[i]['operacion_minutos']

                self.plantas[planta.nombre] = planta

    def _cargar_unidades_almacenamiento(self):

        # Obtener la capacidad luego de aplicar algoritmo
        asignador = AsignadorCapacidad(file=self.file)

        self.unidades_almacenamiento_df = asignador.obtener_unidades_almacenamiento()

        for codigo, ingrediente in self.ingredientes.items():
            self.unidades_almacenamiento_df[codigo] = self.unidades_almacenamiento_df[codigo].fillna(
                0.0)

        for i in self.unidades_almacenamiento_df.index:
            codigo_unidad = self.unidades_almacenamiento_df.loc[i]['unidad_almacenamiento']
            nombre_planta = self.unidades_almacenamiento_df.loc[i]['planta']
            nombre_ingrediente = self.unidades_almacenamiento_df.loc[i]['ingrediente_actual']
            cantidad_ingrediente = self.unidades_almacenamiento_df.loc[i]['cantidad_actual']
            capacidad_ingrediente = self.unidades_almacenamiento_df.loc[i][nombre_ingrediente]

            unidad = Unidad_Almacenamiento(codigo=codigo_unidad)
            unidad.ingrediente_actual = nombre_ingrediente
            unidad.cantidad_actual = cantidad_ingrediente
            unidad.capacidad_kg = capacidad_ingrediente

            planta = self.plantas[nombre_planta]

            planta.adicionar_capacidad_almacenamiento(ingrediente=nombre_ingrediente,
                                                      cantidad_kg=capacidad_ingrediente)

            planta.adicionar_inventario_inicial(ingrediente=nombre_ingrediente,
                                                cantidad_kg=cantidad_ingrediente)

    def _cargar_consumo_planta(self):
        self.consumo_planta_df = pd.read_excel(
            self.file, sheet_name='consumo_proyectado')

        columns = self.consumo_planta_df.columns

        columns_to_remove = ['key', 'empresa', 'ingrediente', 'planta']

        dates = [x for x in columns if not x in columns_to_remove]

        self.consumo_planta_df = pd.melt(frame=self.consumo_planta_df,
                                         id_vars=['planta', 'ingrediente'],
                                         value_vars=dates,
                                         value_name='consumo',
                                         var_name='fecha')

        self.consumo_planta_df['fecha'] = self.consumo_planta_df['fecha'].apply(
            lambda x: datetime.strptime(x, '%d/%m/%Y'))

        self.consumo_planta_df['periodo'] = self.consumo_planta_df['fecha'].map(
            {v: k for k, v in self.periodos.items()})

        for i in self.consumo_planta_df.index:
            # Obtener paramatetros de consumo para enviarlos a la planta
            nombre_planta = self.consumo_planta_df.loc[i]['planta']
            nombre_ingrediente = self.consumo_planta_df.loc[i]['ingrediente']
            periodo = self.consumo_planta_df.loc[i]['periodo']
            cantidad_ingrediente = self.consumo_planta_df.loc[i]['consumo']

            if cantidad_ingrediente > 0:
                planta = self.plantas[nombre_planta]
                planta.establecer_consumo(ingrediente=nombre_ingrediente,
                                          periodo=periodo,
                                          kilogramos=cantidad_ingrediente)

    def _cargar_safety_stock(self):

        self.safety_stock_df = pd.read_excel(
            io=self.file, sheet_name='safety_stock')

        for i in self.safety_stock_df.index:
            nombre_planta = self.safety_stock_df.loc[i]['planta']
            nombre_ingrediente = self.safety_stock_df.loc[i]['ingrediente']
            dias_ss = self.safety_stock_df.loc[i]['dias_ss']

            planta = self.plantas[nombre_planta]
            planta.establecer_safety_stock_dias(
                ingrediente=nombre_ingrediente, dias=dias_ss)

    def _cargar_transitos_planta(self):

        self.transitos_planta_df = pd.read_excel(
            io=self.file, sheet_name='tto_plantas')

        self.transitos_planta_df['periodo'] = self.transitos_planta_df['fecha_llegada'].map(
            {v: k for k, v in self.periodos.items()})

        for i in self.transitos_planta_df.index:
            nombre_planta = self.transitos_planta_df.loc[i]['planta']
            nombre_ingrediente = self.transitos_planta_df.loc[i]['ingrediente']
            cantidad = self.transitos_planta_df.loc[i]['cantidad']
            periodo = self.transitos_planta_df.loc[i]['periodo']

            planta = self.plantas[nombre_planta]
            planta.establecer_llegadas_material(ingrediente=nombre_ingrediente,
                                                periodo=periodo,
                                                cantidad=cantidad)

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

            operador = Operador(nombre=nombre_operador, puerto=puerto.nombre)
            self.operadores[nombre_operador] = operador

            puerto.operadores[operador.nombre] = operador

    def _cargar_inventarios_puerto(self):

        df = pd.read_excel(self.file, sheet_name='inventario_puerto')

        # df = df[df['fecha_llegada'] <= self.periodos[0]]

        df['importacion'] = df['importacion'].apply(
            lambda x: str(x).replace(' ', ''))

        operacion_port_df = pd.read_excel(
            self.file,
            sheet_name='costos_operacion_portuaria')

        operacion_port_df = operacion_port_df.pivot_table(values='valor_kg',
                                                          index=['operador',
                                                                 'puerto',
                                                                 'ingrediente'],
                                                          columns=[
                                                              'tipo_operacion'],
                                                          fill_value=0.0,
                                                          aggfunc="sum").reset_index()

        df = pd.merge(left=df,
                      right=operacion_port_df,
                      left_on=['operador',
                               'puerto', 'ingrediente'],
                      right_on=['operador',
                                'puerto', 'ingrediente'],
                      how='left')

        for i in df.index:
            importacion = Importacion(empresa=df.loc[i]['empresa'],
                                      puerto=df.loc[i]['puerto'],
                                      codigo=df.loc[i]['importacion'],
                                      operador=df.loc[i]['operador'],
                                      ingrediente=df.loc[i]['ingrediente'],
                                      valor_cif=df.loc[i]['valor_cif_kg'],
                                      costo_bodegaje=df.loc[i]['bodega'],
                                      periodos=self.periodos)

            if not importacion.id in self.importaciones.keys():
                self.importaciones[importacion.id] = importacion
            else:
                importacion = self.importaciones[importacion.id]

            importacion.establecer_inventario_inicial(
                cantidad=df.loc[i]['cantidad_kg'])

    def _cargar_transitos_a_puerto(self):

        tto_df = pd.read_excel(self.file, sheet_name='tto_puerto')

        tto_df['periodo'] = tto_df['fecha_llegada'].map(
            {v: k for k, v in self.periodos.items()})

        operacion_port_df = pd.read_excel(
            self.file,
            sheet_name='costos_operacion_portuaria')

        operacion_port_df = operacion_port_df.pivot_table(values='valor_kg',
                                                          index=['operador',
                                                                 'puerto',
                                                                 'ingrediente'],
                                                          columns=[
                                                              'tipo_operacion'],
                                                          fill_value=0.0,
                                                          aggfunc="sum").reset_index()

        self.barcos_df = pd.merge(left=tto_df,
                                  right=operacion_port_df,
                                  left_on=['operador',
                                           'puerto', 'ingrediente'],
                                  right_on=['operador',
                                            'puerto', 'ingrediente'],
                                  how='left')

        self.barcos_df['importacion'] = self.barcos_df['importacion'].apply(
            lambda x: str(x).replace(' ', ''))

        for i in tto_df.index:
            nombre_empresa = self.barcos_df.loc[i]['empresa']
            importacion = self.barcos_df.loc[i]['importacion']
            codigo_operador = self.barcos_df.loc[i]['operador']
            nombre_puerto = self.barcos_df.loc[i]['puerto']
            nombre_ingrediente = self.barcos_df.loc[i]['ingrediente']
            periodo = self.barcos_df.loc[i]['periodo']
            cantidad_kg = self.barcos_df.loc[i]['cantidad_kg']
            valor_cif = self.barcos_df.loc[i]['valor_kg']
            costo_bodegaje = self.barcos_df.loc[i]['bodega']
            costo_despacho_directo = self.barcos_df.loc[i]['directo']

            barco = Barco(empresa=nombre_empresa,
                          importacion=importacion,
                          puerto=nombre_puerto,
                          operador=codigo_operador,
                          ingrediente=nombre_ingrediente,
                          periodo_llegada=periodo,
                          cantidad_kg=cantidad_kg,
                          valor_cif=valor_cif,
                          costo_directo=costo_despacho_directo,
                          costo_bodegaje=costo_bodegaje,
                          periodos=self.periodos,
                          rata_desgarge=self.rata_desgarge_puertos,
                          capacidad_camion=self.capacidad_camion)

            # barco = Barco()

            importacion = Importacion(codigo=barco.importacion,
                                      puerto=barco.puerto,
                                      empresa=barco.empresa,
                                      periodos=self.periodos,
                                      operador=barco.operador,
                                      ingrediente=barco.ingrediente,
                                      valor_cif=barco.valor_cif,
                                      costo_bodegaje=costo_bodegaje)

            if not importacion.id in self.importaciones.keys():
                self.importaciones[importacion.id] = importacion
            else:
                importacion = self.importaciones[importacion.id]

            # Cargar las variables de envio a bodega
            for periodo_envio, variable_bodegaje in barco.obtener_envios_a_bodega().items():

                importacion.agregar_llegada_de_bodegaje(periodo=periodo_envio,
                                                        llegada=variable_bodegaje)

            self.barcos[f'{barco.empresa}_{barco.ingrediente}_{barco.importacion}'] = barco

        # print(self.barcos_df)

    def _cargar_costos_almacenamiento_puerto(self):

        df = pd.read_excel(
            self.file, sheet_name='costos_almacenamiento_cargas')

        df['importacion'] = df['importacion'].apply(
            lambda x: str(x).replace(' ', ''))

        periodos_map = {k: v for v, k in self.periodos.items()}

        df['periodo'] = df['fecha_corte'].map(periodos_map)

        for i in df.index:
            importacion = Importacion(empresa=df.loc[i]['empresa'],
                                      puerto=df.loc[i]['puerto'],
                                      codigo=df.loc[i]['importacion'],
                                      operador=df.loc[i]['operador'],
                                      ingrediente=df.loc[i]['ingrediente'],
                                      valor_cif=0.0,
                                      costo_bodegaje=0.0,
                                      periodos=self.periodos)

            periodo = df.loc[i]['periodo']
            costo = df.loc[i]['valor_kg']

            if not importacion.id in self.importaciones.keys():
                self.importaciones[importacion.id] = importacion
            else:
                importacion = self.importaciones[importacion.id]

            importacion.establecer_costo_vencimiento(
                periodo=periodo, valor=costo)

    def _cargar_fletes(self):

        self.fletes_df = pd.read_excel(
            io=self.file, sheet_name='fletes_cop_per_kg')

        id_vars = ['puerto', 'operador', 'ingrediente']

        value_vars = self.fletes_df.drop(columns=id_vars).columns

        self.fletes_df = pd.melt(frame=self.fletes_df,
                                 id_vars=id_vars,
                                 value_vars=value_vars,
                                 var_name='planta',
                                 value_name='costo')

        self.fletes_df['scaled_values'] = 4 * \
            self.fletes_df['costo']/max(self.fletes_df['costo'])

        for i in self.fletes_df.index:

            puerto = self.fletes_df.loc[i]['puerto']
            operador = self.fletes_df.loc[i]['operador']
            ingrediente = self.fletes_df.loc[i]['ingrediente']
            planta = self.fletes_df.loc[i]['planta']
            costo = self.fletes_df.loc[i]['scaled_values']

            if not puerto in self.fletes.keys():
                self.fletes[puerto] = dict()

            if not operador in self.fletes[puerto].keys():
                self.fletes[puerto][operador] = dict()

            if not ingrediente in self.fletes[puerto][operador].keys():
                self.fletes[puerto][operador][ingrediente] = dict()

            if not planta in self.fletes[puerto][operador][ingrediente].keys():
                self.fletes[puerto][operador][ingrediente][planta] = costo

    def _cargar_intercompany(self):

        self.intercompany_df = pd.read_excel(
            self.file, sheet_name='venta_entre_empresas')

        self.intercompany_df = pd.melt(frame=self.intercompany_df,
                                       id_vars='origen',
                                       value_vars=['contegral', 'finca'],
                                       var_name='destino',
                                       value_name='intercompany')

        for i in self.intercompany_df.index:
            origen = self.intercompany_df.loc[i]['origen']
            destino = self.intercompany_df.loc[i]['destino']
            valor = self.intercompany_df.loc[i]['intercompany']

            if not origen in self.intercompany.keys():
                self.intercompany[origen] = dict()

            if not destino in self.intercompany[origen].keys():
                self.intercompany[origen][destino] = valor

    def _cargar_transportes(self):

        self.transporte = Transporte(barcos=self.barcos,
                                     importaciones=self.importaciones,
                                     plantas=self.plantas,
                                     fletes=self.fletes,
                                     intercompany=self.intercompany,
                                     periodos=self.periodos)

    def _cargar_importaciones(self):
        dict_df = dict()
        dict_df['empresa'] = list()
        dict_df['puerto'] = list()
        dict_df['importacion'] = list()
        dict_df['operador'] = list()
        dict_df['ingrediente'] = list()
        dict_df['periodo_atraque'] = list()
        dict_df['periodo_partida'] = list()
        dict_df['inventario_inicial'] = list()
        dict_df['valor_cif'] = list()
        dict_df['costo_bodegaje'] = list()

        for codigo, importacion in self.importaciones.items():
            importacion.fill_dimension_importaciondf(dict_df)

        self.importaciones_df = pd.DataFrame(dict_df)

    def _buid(self):

        exp_fobj_list = list()
        rest_list = list()

        # Variables de transporte
        self.transporte.build()

        for item in self.transporte.lista_retricciones:
            rest_list.append(item)

        for item in self.transporte.lista_fobj:
            exp_fobj_list.append(item)

        # Construir variables
        print('Construyendo variables de planta')
        for nombre_planta, planta in tqdm(self.plantas.items()):
            # print('building vars', nombre_planta)
            planta._buid_vars()

        print('Construyendo componentes del modelo de planta')
        for nombre_planta, planta in tqdm(self.plantas.items()):
            # print('build lp model components', nombre_planta)
            planta.build_lp_model_components()
            exp_fobj_list += planta.expresiones_funcion_objetivo
            rest_list += planta.lista_restricciones

        print('Construyendo componentes de material llegando')
        for nombre_barco, barco in tqdm(self.barcos.items()):
            # print('build lp components', nombre_barco)
            barco.build_lp_components()
            exp_fobj_list += barco.expresiones_funcion_objetivo
            rest_list += barco.lista_restricciones

        print('Construyendo componentes de inventario en puerto')
        for nombre_importacion, importacion in tqdm(self.importaciones.items()):
            # print('build lp components', nombre_importacion)
            importacion.build_vars()
            importacion.buid_lp_components()
            exp_fobj_list += importacion.lista_parametros_obj
            rest_list += importacion.lista_restricciones

        # Agregar función objetivo
        self.solver += pu.lpSum(exp_fobj_list)

        # Agregando las restricciones
        print('Agregando restricciones al modelo')
        for rest in tqdm(rest_list):
            self.solver += rest

    def reporte_planta(self) -> pd.DataFrame:

        df_dict = dict()
        df_dict['planta'] = list()
        df_dict['ingrediente'] = list()
        df_dict['periodo'] = list()
        df_dict['fecha'] = list()
        df_dict['llegada_programada'] = list()
        df_dict['llegada_directa'] = list()
        df_dict['llegada_bodega'] = list()
        df_dict['consumo'] = list()
        df_dict['safety_stock'] = list()
        df_dict['inventario'] = list()
        df_dict['costo_backorder'] = list()
        df_dict['backorder'] = list()
        df_dict['capacidad'] = list()
        df_dict['costo_exceso_capacidad'] = list()
        df_dict['importaciones'] = list()

        for nombre_planta, planta in self.plantas.items():
            for ingrediente in planta.inventario_al_cierre.keys():
                for periodo, fecha in planta.periodos.items():

                    llegadas = planta.obtener_vars_llegadas_material(
                        material=ingrediente, periodo=periodo)

                    llegadas_directas = sum(
                        [34000*x.varValue for x in llegadas if 'directo' in x.name])
                    llegadas_bodega = sum(
                        [34000*x.varValue for x in llegadas if 'bodega' in x.name])

                    importaciones_directas = (
                        f"{x.name.split('_')[5]} ({x.varValue})" for x in llegadas if 'directo' in x.name and x.varValue > 0)
                    importaciones_bodega = (
                        f"{x.name.split('_')[5]} ({x.varValue})" for x in llegadas if 'bodega' in x.name and x.varValue > 0)

                    importaciones = f"Directas: [{', '.join(importaciones_directas)}]; Indirectas: [{', '.join(importaciones_bodega)}]"

                    df_dict['planta'].append(planta.nombre)
                    df_dict['ingrediente'].append(ingrediente)
                    df_dict['periodo'].append(periodo)
                    df_dict['fecha'].append(fecha)
                    df_dict['llegada_programada'].append(
                        planta.obtener_llegada_material(ingrediente=ingrediente, periodo=periodo))
                    df_dict['llegada_directa'].append(llegadas_directas)
                    df_dict['llegada_bodega'].append(llegadas_bodega)
                    df_dict['consumo'].append(
                        planta.obtener_consumo(ingrediente, periodo))
                    df_dict['safety_stock'].append(
                        planta.obtener_safety_stock_cantidad(ingrediente=ingrediente))
                    df_dict['inventario'].append(
                        planta.inventario_al_cierre[ingrediente][periodo].varValue)
                    df_dict['backorder'].append(
                        planta.backorder_al_cierre[ingrediente][periodo].varValue)
                    df_dict['costo_backorder'].append(planta.costo_backorder)
                    df_dict['capacidad'].append(
                        planta.obtener_capacidad_almacenamiento(ingrediente=ingrediente))
                    df_dict['costo_exceso_capacidad'].append(
                        planta.costo_backorder)
                    df_dict['importaciones'].append(importaciones)

        df = pd.DataFrame(df_dict)

        df['DIO'] = df['inventario']/df['consumo']
        df['Capacidad_DIO'] = df['capacidad']/df['consumo']

        return df

    def reporte_transporte(self) -> pd.DataFrame:

        df_dict = dict()
        df_dict['fecha'] = list()
        df_dict['camiones'] = list()
        # df_dict['dato'] = list()

        fields = {
            0: 'variable',
            1: 'tipo',
            2: 'empresa_origen',
            3: 'puerto',
            4: 'operador',
            5: 'importacion',
            6: 'ingrediente',
            7: 'planta',
            8: 'periodo'
        }

        for indice, titulo in fields.items():
            df_dict[titulo] = list()

        for nombre_planta, planta in self.plantas.items():
            for ingrediente in self.ingredientes.keys():
                for periodo, fecha in self.periodos.items():
                    llegadas = planta.obtener_vars_llegadas_material(
                        material=ingrediente, periodo=periodo)

                    for variable in llegadas:
                        if variable.varValue > 0:
                            campos = variable.name.split('_')
                            df_dict['fecha'].append(fecha)
                            df_dict['camiones'].append(variable.varValue)
                            # df_dict['dato'].append(str(variable))

                            for indice, titulo in fields.items():
                                df_dict[titulo].append(campos[indice])

        transporte_df = pd.DataFrame(df_dict)

        transporte_df = pd.merge(left=transporte_df,
                                 right=self.plantas_df[['empresa', 'planta']].rename(
                                     columns={'empresa': 'empresa_destino'}),
                                 left_on=['planta'],
                                 right_on=['planta'],
                                 how='inner')

        transporte_df = pd.merge(
            left=transporte_df,
            right=self.fletes_df.rename(
                columns={'costo': 'costo_flete_por_kg'}),
            left_on=['puerto', 'operador', 'ingrediente', 'planta'],
            right_on=['puerto', 'operador', 'ingrediente', 'planta'],
            how='left'
        )

        transporte_df['kg_despachados'] = 34000*transporte_df['camiones']

        transporte_df = pd.merge(
            left=transporte_df,
            right=self.intercompany_df,
            left_on=['empresa_origen', 'empresa_destino'],
            right_on=['origen', 'destino'],
            how='left').drop(columns=['origen', 'destino'])

        transporte_df = pd.merge(left=transporte_df,
                                 right=self.importaciones_df[[
                                     'empresa', 'puerto', 'importacion', 'operador', 'ingrediente', 'valor_cif']],
                                 left_on=['empresa_origen', 'puerto',
                                          'importacion', 'operador', 'ingrediente'],
                                 right_on=[
                                     'empresa', 'puerto', 'importacion', 'operador', 'ingrediente'],
                                 how='left')

        return transporte_df

    def reporte_puerto(this) -> pd.DataFrame:

        fields = {
            0: 'tipo',
            1: 'empresa',
            2: 'ingrediente',
            3: 'importacion',
            4: 'periodo'
        }

        df_dict = dict()
        df_dict['fecha'] = list()
        df_dict['puerto'] = list()
        df_dict['inventario_kg'] = list()
        df_dict['costo_vencimiento_kg'] = list()
        df_dict['despachos_indirectos'] = list()
        df_dict['despachos_indirectos_kg'] = list()
        df_dict['plantas'] = list()
        df_dict['ingreso_bodega'] = list()

        for indice, titulo in fields.items():
            df_dict[titulo] = list()

        for importacion_name, importacion in this.importaciones.items():
            for periodo, inventario_var in importacion.inventario_al_cierre.items():

                despachos = importacion.obtener_despachos_a_planta(
                    periodo=periodo)

                despachos_totales = sum(
                    [x.varValue for x in despachos if 'bodega' in x.name])

                if periodo in importacion.variables_bodegaje.keys():
                    bodegaje = importacion.variables_bodegaje[periodo].varValue
                else:
                    bodegaje = 0.0

                despachos_directos = (
                    f"{x.name.split('_')[7]} ({x.varValue})" for x in despachos if x.varValue > 0)

                plantas = f"Directos: [{', '.join(despachos_directos)}]"

                fecha = this.periodos[periodo]
                campos = inventario_var.name.split('_')
                df_dict['fecha'].append(fecha)
                df_dict['puerto'].append(importacion.puerto)
                df_dict['inventario_kg'].append(inventario_var.varValue)
                df_dict['despachos_indirectos'].append(despachos_totales)
                df_dict['despachos_indirectos_kg'].append(
                    34000*despachos_totales)
                df_dict['ingreso_bodega'].append(bodegaje)
                df_dict['plantas'].append(plantas)

                if periodo in importacion.costo_vencimiento.keys():
                    df_dict['costo_vencimiento_kg'].append(
                        importacion.costo_vencimiento[periodo])
                else:
                    df_dict['costo_vencimiento_kg'].append(0.0)

                for indice, titulo in fields.items():
                    df_dict[titulo].append(campos[indice])

        df = pd.DataFrame(df_dict)

        df['costo_total_vencimiento'] = df['inventario_kg'] * \
            df['costo_vencimiento_kg']

        return df

    def solve(self, t_limit_minutes: int) -> str:

        cpu_count = max(1, os.cpu_count()-1)
        gap = 1000000

        config_solver = pu.PULP_CBC_CMD(
            timeLimit=60*t_limit_minutes,
            gapAbs=gap,
            warmStart=False,
            threads=cpu_count)

        print('Cantidad de cpu:', cpu_count)
        print('gap:', gap)
        print('t_limit:', t_limit_minutes, 'minutos')

        self.solver.solve(solver=config_solver)
        # problema.solver.solve()

        return pu.LpStatus[self.solver.status]


if __name__ == '__main__':

    problema = Problema(file='model_template_1205v2.xlsm')

    # problema.solver.writeLP(filename='model2.lp')
    print(problema.solve(t_limit_minutes=3))
