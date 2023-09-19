
# Para cada planta





# Fase inicial
# 1) Hacer una lista de las cargas que estén llegando según el modelo de fase 1,
#    Ordénelas por fecha de llegada, tamaño de importación (desc) y código de 
#    importación
# 2) Haga una lista de las nidades de almacenamiento vacias
# 3) Haga una lista de las unidades de almacenamiento con inventario

# Fase iterativa
# 4) Asigne la demanda diaria a cada unidad de almacenamiento on carga. Si una
#    UA se desocupa, márquela como no utilizable por los siguientes 3 días completos.
     # Si el inventario no alcanza, deje pendiente la demanda de ese día
# 5) Tome la siguiente carga en la lista
# 6) Seeccuone una UA vacia y disponible, un conjunto tal que la suma de sus 
#    capacidades deje la menor cantidad de espacio disponible luego de su asignación
# 7) repita desde 4. Si el despacho no es posble; re-ejecute el modelo y disminuya
#    el ponderado de capacidad. Repita nuevamente todo el proceso.