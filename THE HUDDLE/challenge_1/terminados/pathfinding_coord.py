import collections
import os

# --- Funciones para la Grilla y la Interacción por Terminal ---

def crear_grilla(filas: int, columnas: int) -> list[list[str]]:
    """
    Crea una nueva grilla 2D.
    
    Parámetros:
        filas (int): El número de filas de la grilla.
        columnas (int): El número de columnas de la grilla.
        
    Retorna:
        list[list[str]]: Una matriz de listas (la grilla), inicializada con '.'
                         para representar espacios vacíos.
    """
    return [['.' for _ in range(columnas)] for _ in range(filas)]

def imprimir_grilla(grilla: list[list[str]]):
    """
    Imprime la grilla en la consola, limpiando la pantalla antes para una mejor visualización.
    
    Parámetros:
        grilla (list[list[str]]): La matriz de grilla actual a imprimir.
    """
    os.system('cls' if os.name == 'nt' else 'clear')  # Limpia la pantalla (para Windows o Unix)
    print("--- Estado Actual de la Grilla ---")
    for fila in grilla:
        print(' '.join(fila))
    print()  # Imprime una línea en blanco para separar el contenido

def pedir_coordenadas(mensaje: str, filas: int, columnas: int) -> tuple[int, int]:
    """
    Solicita al usuario que ingrese coordenadas válidas para la grilla.
    
    Parámetros:
        mensaje (str): El mensaje a mostrar al usuario (p. ej., "Ingresa las coordenadas para la ENTRADA").
        filas (int): El número total de filas de la grilla.
        columnas (int): El número total de columnas de la grilla.
        
    Retorna:
        tuple[int, int]: Una tupla con las coordenadas válidas (fila, columna) ingresadas por el usuario.
    """
    while True:
        try:
            coord = input(f"{mensaje} (fila, columna): ").split(',')
            fila, columna = int(coord[0].strip()), int(coord[1].strip())
            if 0 <= fila < filas and 0 <= columna < columnas:
                return fila, columna
            else:
                print("Coordenadas fuera de los límites de la grilla. ¡Intenta de nuevo!")
        except (ValueError, IndexError):
            print("Formato de coordenadas incorrecto. Usa 'fila,columna'.")

def colocar_elemento(grilla: list[list[str]], elemento: str):
    """
    Permite al usuario colocar múltiples elementos (paredes, agua) en la grilla.
    
    Parámetros:
        grilla (list[list[str]]): La grilla en la que se colocarán los elementos.
        elemento (str): El símbolo del elemento a colocar ('W' para pared, 'A' para agua, etc.).
    """
    while True:
        posicion = input(f"¿Quieres colocar un {elemento}? (s/n): ").lower()
        if posicion == 'n':
            break
        elif posicion == 's':
            fila, columna = pedir_coordenadas(f"Ingresa las coordenadas para {elemento}", len(grilla), len(grilla[0]))
            grilla[fila][columna] = elemento
            imprimir_grilla(grilla)  # Actualiza la visualización después de cada colocación
        else:
            print("Entrada no válida. Por favor, responde 's' o 'n'.")

# --- Algoritmo de Búsqueda en Amplitud (BFS) ---

def bfs(grilla: list[list[str]], inicio: tuple[int, int], fin: tuple[int, int]) -> list[tuple[int, int]] | None:
    """
    Implementa el algoritmo de búsqueda en anchura (BFS) para encontrar el camino más corto.
    
    BFS es un algoritmo de búsqueda de grafos que explora todos los nodos vecinos a la misma profundidad
    en el árbol de búsqueda antes de pasar a la siguiente profundidad. Esto garantiza que 
    encuentra el camino más corto en una grilla sin pesos.
    
    Parámetros:
        grilla (list[list[str]]): La matriz 2D que representa el mapa.
        inicio (tuple[int, int]): Las coordenadas de la celda de inicio.
        fin (tuple[int, int]): Las coordenadas de la celda de destino.
        
    Retorna:
        list[tuple[int, int]] | None: Una lista de tuplas con las coordenadas del camino más corto, 
                                      o None si no se encuentra un camino.
    """
    filas, columnas = len(grilla), len(grilla[0])
    
    # Cola de doble terminación para almacenar tuplas: (posición_actual, camino_hasta_aqui)
    cola = collections.deque([(inicio, [inicio])])
    
    # Un conjunto para almacenar las posiciones visitadas y evitar procesar celdas repetidamente
    visitados = set([inicio])

    while cola:
        # Extraer la primera celda y el camino de la cola
        (fila_actual, col_actual), camino_actual = cola.popleft()

        # Condición de éxito: si la celda actual es la de destino, el camino está completo
        if (fila_actual, col_actual) == fin:
            return camino_actual

        # Movimientos posibles: arriba, abajo, izquierda, derecha (sin diagonales)
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for df, dc in direcciones:
            nueva_fila, nueva_col = fila_actual + df, col_actual + dc
            nueva_posicion = (nueva_fila, nueva_col)

            # 1. Verificar si la nueva posición es válida (dentro de los límites)
            # 2. Verificar si la nueva posición no ha sido visitada aún
            if 0 <= nueva_fila < filas and 0 <= nueva_col < columnas and nueva_posicion not in visitados:
                
                elemento = grilla[nueva_fila][nueva_col]
                
                # Ignorar paredes ('W')
                if elemento == 'W':
                    continue
                
                # Para este BFS simple, 'A' (agua) y '.' (vacío) son tratadas como transitables
                if elemento == 'A' or elemento == '.':
                    visitados.add(nueva_posicion)
                    nuevo_camino = list(camino_actual)
                    nuevo_camino.append(nueva_posicion)
                    cola.append((nueva_posicion, nuevo_camino))
    
    return None # Si la cola se vacía y no se llegó al destino, no hay camino


# --- Lógica Principal del Programa ---


# 1. Configurar la grilla (pedir dimensiones al usuario)
while True:
    try:
        grilla_filas = int(input("Ingresa el número de filas para la grilla: "))
        grilla_columnas = int(input("Ingresa el número de columnas para la grilla: "))
        if grilla_filas > 0 and grilla_columnas > 0:
            break
        else:
            print("El número de filas y columnas debe ser mayor que cero.")
    except ValueError:
        print("Entrada no válida. Por favor, ingresa un número entero.")
        
grilla = crear_grilla(grilla_filas, grilla_columnas)
print("\n--- Grilla Inicial ---")
imprimir_grilla(grilla)

# 2. Colocar elementos (entrada, salida, paredes y agua)
print("\n--- Colocando elementos ---")

entrada_pos = pedir_coordenadas("Ingresa las coordenadas para la ENTRADA (E)", grilla_filas, grilla_columnas)
grilla[entrada_pos[0]][entrada_pos[1]] = 'E'
imprimir_grilla(grilla)

salida_pos = pedir_coordenadas("Ingresa las coordenadas para la SALIDA (S)", grilla_filas, grilla_columnas)
grilla[salida_pos[0]][salida_pos[1]] = 'S'
imprimir_grilla(grilla)

colocar_elemento(grilla, 'W')
colocar_elemento(grilla, 'A')

print("\n--- Grilla Final con todos los elementos ---")
imprimir_grilla(grilla)

# 3. Ejecutar BFS y mostrar el resultado
print("\n--- Buscando el camino con BFS ---")
camino = bfs(grilla, entrada_pos, salida_pos)

if camino:
    # Marcar el camino encontrado con '0'
    for r, c in camino:
        if grilla[r][c] not in ['E', 'S']:
            grilla[r][c] = '0'
    
    print("\n--- Camino encontrado ---")
    imprimir_grilla(grilla)
    print("\nEl camino más corto se ha marcado con '0'.")
else:
    print("\n¡No se encontró un camino desde la entrada hasta la salida!")