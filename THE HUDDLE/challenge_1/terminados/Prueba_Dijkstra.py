import heapq
 

def dijkstra(mapa, inicio, fin):
    filas = cols = len(mapa), len(mapa[0])

    cola = []
    #creeamos la cola de prioridad
    #le agregamos como dato inicial el nodo de inicio 
    #le agregamos el costo 0, la fila y la columna de la coordenada de inicio
    #le agregamos una lista que tenga solo inci0
    heapq.heappush(cola, (0, inicio[0], inicio[1], [inicio]))
    visitados = set()
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]


    while cola:

        #sacamos el costo actual, la fila, la columna y el camino
        costo_actual, fila, col, camino = heapq.heappop(cola)

        #si la fila 
        if(fila,cola) == fin:
            return camino, costo_actual
        
        #Si fila y columna esta en visitados
        if (fila,col) in visitados:
            continue
        
        #un for que crea delta fila ycolumna por cada valor de direcciones
        for df, dc in direcciones:
            
            #creamos las nuevas filas y columnas
            nueva_fila, nueva_col = fila + df, col + dc

            #Si esta dentro de los limites
            if 0 <= nueva_fila < filas and 0 <= nueva_col < col:
                
                #Verificamos si la posicion no es una pared o un visitado
                if mapa[nueva_fila][nueva_col] != 1 and (nueva_fila, nueva_col) not in visitados:

                    costo_movimiento = 1
                    #creamos un nuevo cosrto con el costo actual y el costo del movimiento
                    nuevo_costo = costo_actual + costo_movimiento
                    
                    #creamos un nuevo camino con el camino actual y las nuevas filas y columnas
                    nuevo_camino = camino + [(nueva_fila,nueva_col)]

                    #agregamos a la cola el (nuevo costo, la nueva fila y columna y el nuevo camino)    
                    heapq.heappush(cola,(nuevo_costo,nueva_fila,nueva_col,nuevo_camino))
        return None

