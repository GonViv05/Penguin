import heapq

def dijkstra(inicio,fin,mapa):

    filas,columnas = len(mapa),len(mapa[0])

    visitados = set([inicio])
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    cola = []
    heapq.heappush(cola (0, inicio[0],inicio[1], [inicio]))

    while cola:
        costo_actual, fila_actual, columna_actual, camino_actual = heapq.heappop(cola)

        if (fila_actual, columna_actual) == fin:
            return costo_actual, camino_actual
 
        if (fila_actual, columna_actual) in visitados:
            continue

        for df, dc in direcciones:
            nueva_fila,nueva_columna = fila_actual + df, columna_actual + dc
            nueva_pos = (nueva_fila,nueva_columna)

            if 0 <= nueva_fila < filas and 0 <= nueva_columna < columnas and nueva_pos not in visitados:
                estado = mapa[nueva_fila][nueva_columna]

                if estado == 1:
                    continue

                costo_movimiento = 1

                nuevo_costo = costo_actual + costo_movimiento
                nuevo_camino = camino_actual + [nueva_pos]
                heapq.heappush(cola (nuevo_costo, nueva_pos, camino_actual))
        return None


