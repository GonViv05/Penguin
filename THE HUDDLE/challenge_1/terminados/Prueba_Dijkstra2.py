from enum import Enum
import heapq # Para la cola de prioridad de Dijkstra

class TipoCelda(Enum):
    CAMINO = 0
    EDIFICIO = 1
    AGUA = 2
    BLOQUEO = 3

COSTOS = {
    TipoCelda.CAMINO.value: 1,
    TipoCelda.AGUA.value: 3,    
}

SIMBOLOS_MAPA = {
    TipoCelda.CAMINO.value: "⬛",
    TipoCelda.EDIFICIO.value: "🏢",
    TipoCelda.AGUA.value: "💧",
    TipoCelda.BLOQUEO.value: "🚧",
}

def crear_mapa(filas, cols):
    return [[0 for _ in range(cols)] for _ in range(filas)]

def generar_ciudad(mapa, tamanho_bloque):
    filas = len(mapa)
    cols = len(mapa[0])

    for i in range(filas):
        for j in range(cols):
            # Cada "tamanho_bloque" filas o columnas serán calles
            if i % tamanho_bloque == 0 or j % tamanho_bloque == 0:
                mapa[i][j] = TipoCelda.CAMINO.value
            else:
                mapa[i][j] = TipoCelda.EDIFICIO.value
 
def mostrar_mapa(mapa, ruta=None, inicio=None, fin=None):
    # Convierte la lista 'ruta' a un set. Si está vacía o es None, usa un set vacío para seguridad. 
    ruta_set = set(ruta) if ruta else set()

    for i, fila in enumerate(mapa):
        linea = ""
        for j, celda in enumerate(fila):
            pos = (i, j)

            if pos == inicio:
                linea += "🏁 "
            elif pos == fin:
                linea += "📍 "
            elif pos in ruta_set:
                linea += "🚗 "
            else:
                linea += SIMBOLOS_MAPA[celda] + " "
        print(linea)
    print()

def pedir_coordenada(mapa, mensaje):
    filas = len(mapa)
    cols = len(mapa[0])

    while True:
        try: 
            entrada = input(f"{mensaje} (fila,col): ")
            fila, col = map(int, entrada.split(","))

            if 0 <= fila < filas and 0 <= col < cols:
                if mapa[fila][col] == 0:
                    return (fila, col)
                else:
                    print("❌ Esa celda es un obstáculo, elige otra.")
            else:
                print("❌ Coordenadas fuera del mapa.")
        except ValueError:
            print("⚠️ Ingresa en el formato correcto: fila,col (ej: 2,3)")

def dijkstra(mapa, inicio, fin):
    """
    Implementación de Dijkstra usando heapq para encontrar el camino de menor costo.
    
    Args:
        mapa: matriz 2D con tipos de celda
        inicio: tupla (fila, columna) de posición inicial
        fin: tupla (fila, columna) de posición objetivo
        
    Returns:
        Lista de posiciones del camino más corto, o None si no existe
    """
    filas, cols = len(mapa), len(mapa[0])

    # Verifica si el inicio o el fin están en un obstáculo
    if get_costo(mapa[inicio[0]][inicio[1]]) == float('inf') or get_costo(mapa[fin[0]][fin[1]]) == float('inf'):
        return None
    
    # Distancias mínimas conocidas a cada posición
    distancias = { (f,c): float('inf') for f in range(filas) for c in range(cols) }     
    distancias[inicio] = 0
    
    # Para reconstruir el camino
    padres = {inicio: None}
    
    # Conjunto de nodos ya visitados (optimización)
    visitados = set()

    # Cola de prioridad: (costo_acumulado, posición)
    # heapq siempre devuelve el elemento con menor costo primero
    cola_prioridad = [(0, inicio)]

    while cola_prioridad:
        costo_actual, actual = heapq.heappop(cola_prioridad)
        
        # Si ya visitamos este nodo, saltarlo
        if actual in visitados:
            continue
            
        # Marcar como visitado
        visitados.add(actual)

        # ¡Llegamos al destino!
        if actual == fin:
            print(f"🎯 Camino encontrado con costo total: {costo_actual}")
            # Reconstruir ruta siguiendo los padres
            ruta = []
            while actual is not None:
                ruta.append(actual)
                actual = padres.get(actual)
            
            return ruta[::-1]  # Invertir para tener desde inicio a fin
        
        # Explorar vecinos
        fila, col = actual
        movimientos = [(-1,0), (1,0), (0,-1), (0,1)]  # arriba, abajo, izq, der
        
        for df, dc in movimientos:
            nueva_fila, nueva_col = fila + df, col + dc
            vecino = (nueva_fila, nueva_col)

            # Verificar límites del mapa
            if 0 <= nueva_fila < filas and 0 <= nueva_col < cols:
                # Si ya visitamos este vecino, saltarlo
                if vecino in visitados:
                    continue
                    
                costo_movimiento = get_costo(mapa[nueva_fila][nueva_col])
                if costo_movimiento == float('inf'):
                    continue # No se puede mover a un obstáculo
                
                nuevo_costo_total = costo_actual + costo_movimiento
                
                # Si encontramos un camino mejor a este vecino
                if nuevo_costo_total < distancias[vecino]:
                    distancias[vecino] = nuevo_costo_total
                    padres[vecino] = actual
                    heapq.heappush(cola_prioridad, (nuevo_costo_total, vecino))
    
    print("❌ No se encontró camino al destino")
    return None # No se encontró ruta

# Devuelve el costo de moverse a una celda según su tipo
# Si la clave (el valor entero) no existe, devuelve float('inf')
def get_costo(celda_valor):
   return COSTOS.get(celda_valor, float('inf'))

def agregar_obstaculos_usuario(mapa, inicio, fin):
    while True:
        print("\n--- Menú de obstáculos ---")
        print("1: Agregar edificio 🏢")
        print("2: Agregar agua 💧")
        print("3: Agregar zona bloqueada 🚧")
        print("0: Terminar")

        opcion = input("Elige una opción: ")

        if opcion == "0":
            break
        elif opcion in["1","2","3"]:
            try:
                entrada = input("Ingrese coordenadas del obstáculo (fila,col): ")
                fila,col = map(int, entrada.split(","))

                if (fila, col) == inicio or (fila, col) == fin:
                    print("❌ No puedes bloquear el inicio ni el destino.")
                elif 0 <= fila < len(mapa) and 0 <= col < len(mapa[0]):
                    mapa[fila][col] = int(opcion)
                    print(f"✅ Obstáculo agregado en ({fila}, {col})")

                    # Recalcular ruta
                    ruta = dijkstra(mapa, inicio, fin)
                    if ruta:
                        print("Ruta recalculada ✅")
                        mostrar_mapa(mapa, ruta, inicio, fin)
                    else: 
                        print("No hay ruta posible 😥")
                        mostrar_mapa(mapa, None, inicio, fin)
                else: 
                    print("❌ Coordenadas fuera del mapa.")
            except ValueError:
                print("⚠️ Formato incorrecto, usa fila,col (ej: 3,4)")
        else:
            print("⚠️ Opción inválida")       

def validar_entrada_entero(mensaje):
    while True:
        entrada = input(mensaje)
        try:           
            numero_entero = int(entrada)           
            return numero_entero
        except ValueError:           
            print("❌ Entrada no válida. Por favor, ingrese un número entero.")

def main():
    print("🚗🚗 Bienvenido a la calculadora de rutas 🚗🚗")
    filas = validar_entrada_entero("Ingrese el alto del mapa: ")
    cols = validar_entrada_entero("Ingrese el ancho del mapa: ")
    
    mapa = crear_mapa(filas,cols)    
    generar_ciudad(mapa, tamanho_bloque=3)
    mostrar_mapa(mapa)
    
    inicio = pedir_coordenada(mapa, "Ingrese coordenadas de INICIO 🏁")
    fin = pedir_coordenada(mapa, "Ingrese coordenadas de DESTINO 📍")

    ruta = dijkstra(mapa, inicio, fin)

    if ruta:
        print("Ruta encontrada ✅")
        mostrar_mapa(mapa, ruta, inicio, fin)
    else: 
        print("No hay ruta posible")
        
    agregar_obstaculos_usuario(mapa, inicio, fin)    

main()