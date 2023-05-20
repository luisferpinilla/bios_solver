import pulp as pl


def solve_mip_model():
    # Crear el problema
    model = pl.LpProblem("Ejemplo_MIP", pl.LpMinimize)

    # Variables de decisión
    x = pl.LpVariable("x", lowBound=0, cat=pl.LpInteger)
    y = pl.LpVariable("y", lowBound=0, cat=pl.LpInteger)

    # Función objetivo
    model += 2*x + 3*y

    # Restricciones
    model += x + y >= 5
    model += x - y <= 2

    # Resolver el modelo
    model.solve()
    status = pl.LpStatus[model.status]

    # Obtener los resultados
    solution = {
        "status": status,
        "objective": pl.value(model.objective),
        "x": pl.value(x),
        "y": pl.value(y)
    }

    return solution