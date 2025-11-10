import heapq
import collections
def dijkstra(inicio,fin,mapa):
    filas,columnas = len(mapa),len(mapa[0])

    visitados = set()
    
    visitados.add(inicio)
    
    cola = []
    heapq.heappush(cola (0, inicio[0],inicio[1], [inicio]))



    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while cola:
        costo_actual, fila_actual, columna_actual, camino_actual = heapq.heappop(cola)

        if (fila_actual,columna_actual) == fin:
            return camino_actual, costo_actual
        
        if (fila_actual, columna_actual) in visitados:
            continue

        for df, dc in direcciones:
            nueva_fila,nueva_columna = fila_actual + df, columna_actual + dc
            nueva_pos = (nueva_fila,nueva_columna)

            if 0 <= nueva_fila < filas and 0 <= nueva_columna < columnas:

                if mapa[nueva_fila][nueva_columna] != 1 and nueva_pos not in visitados:
                    costo_movimiento = 1
                    nuevo_costo = costo_actual + costo_movimiento
                    visitados.add(nueva_pos)
                    nuevo_camino = camino_actual + [nueva_pos]

                    heapq.heappush(cola (nuevo_costo,nueva_fila,nueva_columna,nuevo_camino))

def BFS(mapa,inicio,fin):
    filas, columnas = len(mapa), len(mapa[0])

    visitados = set()
    visitados.add(inicio)

    cola = collections.deque([(inicio[inicio])])
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while cola:
        (fila_actual,columna_actual), camino_actual = cola.popleft()
        
        if (fila_actual,columna_actual) == fin:
            return camino_actual
        
        for df, dc in direcciones:

            nueva_fila,nueva_columna = fila_actual + df, columna_actual + dc
            nueva_posicion = (nueva_fila,nueva_columna)

            if 0 <= nueva_fila < filas and 0 <= nueva_columna < columnas and nueva_posicion not in visitados:
                estado = mapa[nueva_fila][nueva_columna]

                if estado == 1:
                    continue

                visitados.add(nueva_posicion)
                nuevo_camino = camino_actual + [nueva_posicion]
                cola.append((nueva_posicion,nuevo_camino))

        return None

'''Uso de algoritmo A*'''
# Función Heurística (h(n)): Distancia de Manhattan
def distancia_manhattan(fila1, col1, fila2, col2):
    """Calcula la distancia de Manhattan (h(n))."""
    return abs(fila1 - fila2) + abs(col1 - col2)

# La función A*
def a_star(mapa, inicio, fin):
    filas, cols = len(mapa), len(mapa[0])
    
    # 1. Calculamos la heurística inicial para el nodo de inicio
    h_inicial = distancia_manhattan(inicio[0], inicio[1], fin[0], fin[1])
    # f(n) = g(n) + h(n) => f(inicio) = 0 + h_inicial
    f_inicial = h_inicial

    # Cola de Prioridad: (f_costo, g_costo, fila, col, camino)
    cola = []
    heapq.heappush(cola, (f_inicial, 0, inicio[0], inicio[1], [inicio]))
    
    # Diccionario para rastrear el mejor g_costo encontrado hasta ahora para cada nodo
    # Esto es crucial para la eficiencia y para actualizar caminos
    g_costos = {inicio: 0}
    
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while cola:
        # 2. Sacamos el nodo con el menor f_costo (la mejor prioridad)
        f_costo, g_costo_actual, fila, col, camino = heapq.heappop(cola)

        # Condición de Parada
        if (fila, col) == fin:
            return camino, g_costo_actual
        
        # Opcional: No necesitamos volver a procesar un nodo si ya hemos encontrado
        # un camino con un g_costo menor o igual que el actual (ya que A* lo garantiza)
        if g_costo_actual > g_costos.get((fila, col), float('inf')):
            continue
        
        # Iterar sobre los vecinos (direcciones)
        for df, dc in direcciones:
            nueva_fila, nueva_col = fila + df, col + dc
            
            # Verificar límites y si no es una pared (asumiendo que 1 es pared)
            if 0 <= nueva_fila < filas and 0 <= nueva_col < cols and mapa[nueva_fila][nueva_col] != 1:
                
                costo_movimiento = 1
                # 3. Calculamos el nuevo g_costo
                nuevo_g_costo = g_costo_actual + costo_movimiento
                
                coordenada_vecina = (nueva_fila, nueva_col)
                
                # A*: ¿Este nuevo camino al vecino es mejor que cualquiera que tuviéramos antes?
                if nuevo_g_costo < g_costos.get(coordenada_vecina, float('inf')):
                    
                    # Actualizar el mejor costo real (g) encontrado hasta ahora
                    g_costos[coordenada_vecina] = nuevo_g_costo
                    
                    # 4. Calcular el nuevo f_costo = g(n) + h(n)
                    h_costo = distancia_manhattan(nueva_fila, nueva_col, fin[0], fin[1])
                    nuevo_f_costo = nuevo_g_costo + h_costo
                    
                    # Actualizar camino (solo para rastrear la solución)
                    nuevo_camino = camino + [coordenada_vecina]
                    
                    # 5. Agregar a la cola con el nuevo f_costo como prioridad
                    heapq.heappush(cola, (nuevo_f_costo, nuevo_g_costo, nueva_fila, nueva_col, nuevo_camino))
                    
    return None # No se encontró camino