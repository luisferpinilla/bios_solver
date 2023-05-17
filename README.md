# Modelo matemático

## Abstract

## Contexto del problema

### Sets:

$i$ : Macro ingredientes

$j$ : Puertos

$k$ : Plantas

$l$ : Cargas en Puerto

$m$ : Unidades de Almacenamiento

$t$ : día

### Parameters

$DM_{ki}^{t}$: Demanda del ingrediente $i$ en la planta $k$ durante el día $t$

$AR_{l}^{t}$ : Cantidad de ingrediente que va a llegar a la carga $l$ durante el día $t$

$SS_{ik}^{t}$ : Inventario de seguridad a tener del ingrediente $i$ en la planta $k$ al final del día $t$

$CA_{mi}$ : Capacidad de almacenamiento de la unidad $m$ en toneladas del ingrediente $i$

$CC_{l}^{t}$ Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$

$¿?$ Capacidad de mover carga hacia un almacenamiento en puerto

$¿?$ Capacidad de mover carga directa hacia un camión

### Diccionary

$l$ -> $i$ : Para cada carga, determina a cuál ingrediente pertenece

$l$ -> $j$ : Para cada carga, determina a cuál puerto ha llegado

$m$ -> $i$ : Para cada unidad de almacenamiento, determina a

### Variables

$XIP_{l}^{t}$ : Cantidad de la carga $l$ al final del periodo $t$

$XTR_{lm}^{t}$ : Cantidad de carga $l$ a transportar hacia la unidad $m$ durante el día $t$

$XDM_{}^{t}$: Cantidad de producto a sacar de la unidad de almacenamiento para satisfacer la demanda.

$ITR_{lm}^{t}$ : Cantidad de camiones con carga $l$ a transportar hacia la unidad $m$ durante el día $t$

$BSS_{ik}^{t}$ : sí estará permitido que el inventario del ingrediente $i$ en la planta $k$ al final del día $t$ baje por debajo de $SS_{ik}^{t}$

## Función Objetivo:

Función de minimización de costos de:

- Almacenamiento en puerto por corte de facturación,
- Descargue en almacenamiento en puerto,
- Descargue para despacho directo hacia una planta
- Costo variable de transportar cargas desde puertos hacia plantas
- Costo fijo de transportar un camion desde puerto hacia plantas
- Costo de no respetar un inventario mìnimo o de no satisfacer una demanda en una planta
- Costo de mantener una unidad de almacenamiento activa con algun ingrediente

## Restricciones

- Balance de masa en cargas en puerto
- Balance de masa en unidades de almacenamiento por producto en planta
- Asignación de unidades de almacenamiento a ingredientes en el tiempo
- Capacidad de almacenamiento en unidades de almacenamiento
- Mantenimiento del nivel de seguridad de igredientes en plantas

### Balance de masa en

# Preguntas para reunión

La asignación puede intentar minimizar la cantidad de unidades de almacenamiento activas (con algun ingrediente) en vez de intentar usar una combinatoria de estados y asignaciones de las unidades de almacenamiento.
