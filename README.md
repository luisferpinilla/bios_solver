# Modelo matemático

## Abstract

El presente documento contiene el modelo matemático de programación lineal mixta que describe la situación de almacenamiento, transporte y demanda de macro ingredientes para la compañia Grupo BIOS.

## Contexto del problema

Grupo BIOS es un grupo de empresas dedicadas a la fabricación de productos agrícolas destinados a diferentes propósitos. Para efectos de dicha fabricación emplea varias materias primas que son procesadas en 13 plantas al interior de Colombia y que tienen origen en el extranjero.

Dado el origen de las materias primas, surgen una serie de operaciones logísticas para colocalas en las plantas con sus correspondientes costos y restricciones asociadas.

El modelo matemático descrito a continuación ayudará un usuario experto en la operación de Grupo BIOS a encontrar el mejor conjunto de decisiones que conduzcan a causar el menor costo logistico durante un periodo dado. Dichas decisiones estan asociadas específicamente con:

- La cantidad de materias primas a almacenar en puerto;
- la cantidad de materias primas a despachar entre el puerto y las 13 plantas y;
- la unidad de almacenamiento en donde se almacenará la materia prima que llega a las plantas y las que se usarán para cumplir con la demanda proyectada de consumo.

El modelo matemático no tendrá como objetivo responder a preguntas o cuestiones adicionales relacioandas con otras decisiones o aspectos relacionados, por ejemplo:

- la cantidad de materias primas a comprar;
- la cantidad de materias primas a consumir para fabricar el producto terminado;
- la forma como se mezclarán las materias primas en las plantas;
- los esquemas de negociación de tarifas de almacenamiento, transporte;
- ni ningún otro aspecto del negocio que no haya sido explícitamente discutido, aprobado y costeado por parte de WA Solutions, Esteban Restrepo y Luis Fernando Pinilla.

```mermaid
graph LR;


    Barco --AR--> Almacenamiento
    Almacenamiento --XTR--> Planta
    Almacenamiento --XIP--> Almacenamiento
    UnidadAlmacenamieto --XIU--> Planta
    Planta --DM--> Consumos
```

### Sets:

$e$ : Empresas

$i$ : Ingredientes

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

$CC_{l}^{t}$ : Costo de almacenamiento de la carga $l$ por tonelada a cobrar al final del día $t$ en el puerto $$

$CT_{lm}$ : Costo de transporte por tonelada despachada de la carga $l$ hasta la unidad de almacenamiento $m$.

$CF_{lm}$ : Costo fijo de transporte por camión despachado llevando la carga $l$ hasta la unidad de almacenamiento $m$.

$CW_{lm}$ : Costo de vender una carga perteneciente a una empresa a otra.

$CS_{ik}^{t}$ : Costo de no satisfacer el inventario de seguridad para el ingrediente $i$ en la planta $k$ durante el día $t$

$CD_{ik}^{t}$ : Costo de no satisfacer la demanda del ingrediente $i$  en la planta $k$ durante el día $t$

### Diccionary

$l$ -> $i$ : Para cada carga, determina a cuál ingrediente pertenece

$l$ -> $j$ : Para cada carga, determina a cuál puerto ha llegado

$m$ -> $i$ : Para cada unidad de almacenamiento, determina a qué macro incrediente $i$ pertenece

$k$ -> $e$ : Para cada planta, determina a qué empresa $e$ pertenece

### Variables

$XIP_{l}^{t}$ : Cantidad de la carga $l$ en puerto al final del periodo $t$

$XTR_{lm}^{t}$ : Cantidad de carga $l$ en puerto a transportar hacia la unidad $m$ durante el día $t$

$XTI_{lm}^{t}$ : Cantidad de camiones con carga $l$ a despachar hacia la unidad $m$ durante el día $t$

$XIU_{m}^{t}$ : Cantidad de ingrediente almacenado en la unidad de almacenameinto $m$ al final del periodo $t$

$XDM_{im}^{t}$: Cantidad de producto $i$ a sacar de la unidad de almacenamiento $m$ para satisfacer la demanda e el día $t$.

$ITR_{lm}^{t}$ : Cantidad de camiones con carga $l$ a transportar hacia la unidad $m$ durante el día $t$

$BSS_{ik}^{t}$ : sí se cumple que el inventario del ingrediente $i$ en la planta $k$ al final del día $t$ esté sobre el nivel de seguridad $SS_{ik}^{t}$

$BCD_{ik}^{t}$ : sí estará permitido que la demanda de un ingrediente $i$ no se satisfaga en la planta $k$ al final del día $t$

$X$ : si 

## Función Objetivo:

Función de minimización de costos de:

- Almacenamiento en puerto por corte de facturación,
- Costo variable de transportar cargas desde puertos hacia plantas
- Costo fijo de transportar un camion desde puerto hacia plantas
- Costo de no respetar un inventario de seguridad de un ingrediente en una planta
- Costo de no satisfacer una demanda en una planta
- Costo de mantener una unidad de almacenamiento activa con algun ingrediente
- Costo de vender una cantidad de ingrediente desde una empresa a otra durante el transporte.

### Almacenamiento en puerto por corte de Facturación:

Dado que las cargas almacenadas en el puerto causan un costo de almacenamiento que suma al costo total, la suma de los productos escalares entre el costo de almacenamiento colocado a cada carga $l$ en el tiempo y la cantidad almacenada al final del día $t$, nos dará el componente del costo del almacenamiento en el puerto. Así:

$$\sum_{l}^{t}{CC_{l}^{t} \cdot XIP_{l}^{t}}$$

### Costo variable de transportar cargas desde puertos hacia plantas

Existe una tabla de fletes que muestra el costo por tonelada a enviar desde plantas hacia los puertos. dado que no esta definido el costo desde una carga en particular en un puerto hacia una unidad de almacenamiento, asumiremos que el costo de despacho de carga entre puertos y fábricas se puede aplicar de esta manera. Así las cosas usaremos los diccionarios para saber qué cargas están en qué puerto y cuáles unidades de almacenamiento están en qué fábrica.

$$ \sum_{l \in j}{XTR_{lm}^{t}} \cdot CT_{lm} \forall t, m \in k $$

### Costo fijo de transportar un camion desde puerto hacia plantas

Aunque las negociaciones están dadas por toneada, existe la posibilidad que se decida en el modelo despachar una cantidad muy baja en un camión, lo que se verá como un error del modelo. La forma de evitar este comportamiento es asignar un valor fijo por camión, de esta manera el modelo intentará despachar cantidades razonables en cada camión. Esta expresión en la función objetivo debe estar atada a una restricción sobre la cantidad de camiones y toneladas a despachar

$$ \sum_{l E }^{}{XTR_{lm}^{t}} \cdot CF_{lm} \forall t$$

### Costo de no respetar un inventario de seguridad de un ingrediente en una planta

$$ \sum_{ik}^{t}{CS_{ik}^{y} \cdot BSS_{ik}^{t} \forall ikt} $$

### Costo de no satisfacer una demanda en una planta

$$ \sum_{ik}^{t}{CD_{ik}^{t} \cdot BCD_{ik}^{t} \forall ikt} $$

### Costo de mantener una unidad de almacenamiento activa con algun ingrediente

Pendiente por modelar

## Restricciones

### Balance de masa en cargas en puerto

La cantidad de inventario para la carga $l$ al final del periodo $t$ será el inventario del periodo anterior, más las llegadas en el periodo actual menos todos los envios hacia las unidades de almacenamiento:

$$ XIP_{l}^{t} = XIP_{l}^{t-1} + AR_{l}^{t} - \sum_{m}{XTR_{lm}^{t}}: \forall{ \mathbb{t \in T}}$$

### Capacidad de carga de los camiones

Asumiremos que los camiones no pueden transportar más de 34 toneladas en cada viaje.

$$ XTR_{lm}^{t} \leq 34 \cdot XTI_{lm}^{t} $$

### Balance de masa en unidades de almacenamiento por producto en planta

El inventario en las unidades de almacenamiento $m$ al final de un día $t$ es igual al inventario al final del día anterior más las llegadas desde cualquier carga $l$, menos la cantidad de producto a sacar desde la unidad $m$.

$$ XIU_{m}^{t} = XIU_{m}^{t-1} + \sum_{l}{XTR_{lm}^{t}} - XDM_{km}^{t}: \forall{\mathbb{t \in T}}$$

### Satisfaccion de la demanda

Dado que el modelo debe decidir la cantidad de producto $i$ que debe extraerse de cada almacenamiento $m$, la suma de todas las cantidades a extraer deberá ser igual a la demanda del ingrediente $i$ en la planta $k$.

$$ \sum_{m \in i}^{t}{XDM_{m}^{t}} = DM_{ki}^{t} \cdot BCD_{ik}^{t} $$

### Asignación de unidades de almacenamiento a ingredientes en el tiempo

Pendiente por formular

### Capacidad de almacenamiento en unidades de almacenamiento

$$ XIU_{m}^{t} \leq CA_{mi} $$

### Mantenimiento del nivel de seguridad de igredientes en plantas

$$ \sum_{m \in i}^{t}{XDM_{m}^{t}} \geq SS_{ki}^{t} \cdot (1-BSS_{ik}^{t}) $$

