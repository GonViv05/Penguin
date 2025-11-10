import heapq
import tkinter as tk
from tkinter import messagebox

def dijkstra_con_heapq(grilla, inicio, fin):
    """
    Implementación de Dijkstra usando heapq para encontrar el camino de menor costo.
    
    Args:
        grilla: matriz 2D donde 0=libre, 1=pared
        inicio: tupla (fila, columna) de posición inicial
        fin: tupla (fila, columna) de posición objetivo
        
    Returns:
        camino: lista de posiciones del camino más corto, o None si no existe
    """
    filas, columnas = len(grilla), len(grilla[0])
    
    # Cola de prioridad: (costo_acumulado, fila, columna, camino_hasta_aqui)
    cola = []
    heapq.heappush(cola, (0, inicio[0], inicio[1], [inicio]))
    
    # Set de nodos visitados para evitar ciclos
    visitados = set()
    
    # Direcciones: arriba, abajo, izquierda, derecha
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while cola:
        costo_actual, fila, col, camino = heapq.heappop(cola)
        
        # Si llegamos al destino
        if (fila, col) == fin:
            return camino
        
        # Si ya visitamos este nodo, saltarlo
        if (fila, col) in visitados:
            continue
            
        # Marcar como visitado
        visitados.add((fila, col))
        
        # Explorar vecinos
        for df, dc in direcciones:
            nueva_fila, nueva_col = fila + df, col + dc
            
            # Verificar límites
            if 0 <= nueva_fila < filas and 0 <= nueva_col < columnas:
                # Verificar que no sea pared y no esté visitado
                if grilla[nueva_fila][nueva_col] != 1 and (nueva_fila, nueva_col) not in visitados:
                    
                    # Costo del movimiento (puedes personalizarlo)
                    costo_movimiento = 1  # Costo uniforme, o puedes usar grilla[nueva_fila][nueva_col]
                    nuevo_costo = costo_actual + costo_movimiento
                    nuevo_camino = camino + [(nueva_fila, nueva_col)]
                    
                    # Agregar a la cola de prioridad
                    heapq.heappush(cola, (nuevo_costo, nueva_fila, nueva_col, nuevo_camino))
    
    return None  # No se encontró camino

# Ejemplo de uso con diferentes tipos de terreno
def dijkstra_con_terrenos(grilla_costos, inicio, fin):
    """
    Dijkstra donde cada celda tiene un costo diferente de atravesar.
    
    Args:
        grilla_costos: matriz donde cada número representa el costo de pasar por esa celda
                      999 = pared (costo muy alto)
    """
    filas, columnas = len(grilla_costos), len(grilla_costos[0])
    
    # Cola: (costo_total, fila, col, camino)
    cola = []
    heapq.heappush(cola, (0, inicio[0], inicio[1], [inicio]))
    
    # Diccionario de distancias mínimas conocidas
    distancias = {inicio: 0}
    
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while cola:
        costo_actual, fila, col, camino = heapq.heappop(cola)
        
        # Si encontramos el objetivo
        if (fila, col) == fin:
            return camino, costo_actual
        
        # Si ya encontramos un camino mejor a este nodo, saltarlo
        if costo_actual > distancias.get((fila, col), float('inf')):
            continue
        
        # Explorar vecinos
        for df, dc in direcciones:
            nueva_fila, nueva_col = fila + df, col + dc
            
            if 0 <= nueva_fila < filas and 0 <= nueva_col < columnas:
                costo_terreno = grilla_costos[nueva_fila][nueva_col]
                
                # Si es pared (costo 999), saltarlo
                if costo_terreno >= 999:
                    continue
                
                nuevo_costo_total = costo_actual + costo_terreno
                
                # Si encontramos un camino mejor a este vecino
                if nuevo_costo_total < distancias.get((nueva_fila, nueva_col), float('inf')):
                    distancias[(nueva_fila, nueva_col)] = nuevo_costo_total
                    nuevo_camino = camino + [(nueva_fila, nueva_col)]
                    heapq.heappush(cola, (nuevo_costo_total, nueva_fila, nueva_col, nuevo_camino))
    
    return None, float('inf')  # No se encontró camino

# Ejemplos de prueba
if __name__ == "__main__":
    print("=== Ejemplo 1: Grilla binaria (0=libre, 1=pared) ===")
    
    # Grilla simple
    grilla_simple = [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0]
    ]
    
    inicio = (0, 0)
    fin = (4, 4)
    
    camino = dijkstra_con_heapq(grilla_simple, inicio, fin)
    if camino:
        print(f"Camino encontrado: {camino}")
        print(f"Longitud del camino: {len(camino)}")
    else:
        print("No se encontró camino")
    
    print("\n" + "="*50)
    print("=== Ejemplo 2: Grilla con costos de terreno ===")
    
    # Grilla con diferentes costos de terreno
    # 1=normal, 2=pasto alto, 3=lodo, 5=agua poco profunda, 999=pared
    grilla_terrenos = [
        [1, 2, 999, 1, 1],
        [1, 999, 999, 2, 1],
        [1, 1, 2, 3, 999],
        [999, 999, 1, 5, 1],
        [1, 1, 1, 999, 1]
    ]
    
    camino_terrenos, costo_total = dijkstra_con_terrenos(grilla_terrenos, inicio, fin)
    if camino_terrenos:
        print(f"Camino con terrenos: {camino_terrenos}")
        print(f"Costo total del viaje: {costo_total}")
    else:
        print("No se encontró camino")
    
    print("\n" + "="*50)
    print("=== Ventajas de usar heapq para Dijkstra ===")
    print("1. Siempre procesa primero el nodo con menor costo")
    print("2. Garantiza encontrar el camino óptimo")
    print("3. Eficiente: O((V + E) log V) vs BFS simple O(V + E)")
    print("4. Maneja automáticamente la priorización por costo")
    print("5. Perfecto para grillas con diferentes tipos de terreno")