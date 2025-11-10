import heapq

# Tipos de terreno y sus costos
LIBRE = 0      # Camino libre - costo 1
EDIFICIO = 1   # Edificio - no se puede pasar
AGUA = 2       # Agua - costo 3
BLOQUEO = 3    # Zona bloqueada - no se puede pasar

# Costos de movimiento
COSTOS = {
    LIBRE: 1,
    AGUA: 3,
    EDIFICIO: 999,  # Muy caro = no se puede pasar
    BLOQUEO: 999    # Muy caro = no se puede pasar
}

# Símbolos para mostrar el mapa
SIMBOLOS = {
    LIBRE: "⬛",
    EDIFICIO: "🏢", 
    AGUA: "💧",
    BLOQUEO: "🚧"
}

def crear_mapa(filas, columnas):
    """Crea un mapa vacío de tamaño filas x columnas"""
    return [[LIBRE for _ in range(columnas)] for _ in range(filas)]

def mostrar_mapa(mapa, camino=None, inicio=None, fin=None):
    """Muestra el mapa en pantalla con el camino marcado"""
    print("\n" + "="*50)
    
    # Convertir camino a set para búsqueda rápida
    camino_set = set(camino) if camino else set()
    
    for fila in range(len(mapa)):
        linea = ""
        for col in range(len(mapa[0])):
            pos = (fila, col)
            
            if pos == inicio:
                linea += "🏁 "      # Inicio
            elif pos == fin:
                linea += "🎯 "      # Fin
            elif pos in camino_set:
                linea += "🚗 "      # Camino
            else:
                linea += SIMBOLOS[mapa[fila][col]] + " "
        print(linea)
    print("="*50 + "\n")

def dijkstra_simple(mapa, inicio, fin):
    """
    Algoritmo de Dijkstra simplificado usando heapq
    
    ¿Cómo funciona?
    1. Empezamos en 'inicio' con costo 0
    2. Usamos una cola de prioridad que siempre nos da el nodo más barato
    3. Para cada nodo, exploramos sus vecinos
    4. Si encontramos un camino más barato a un vecino, lo actualizamos
    5. Repetimos hasta encontrar el destino
    """
    filas = len(mapa)
    columnas = len(mapa[0])
    
    # Cola de prioridad: (costo_total, posicion_actual, camino_hasta_aqui)
    cola = [(0, inicio, [inicio])]
    
    # Recordar las mejores distancias encontradas
    mejores_costos = {inicio: 0}
    
    print(f"🚀 Buscando camino desde {inicio} hasta {fin}")
    
    while cola:
        costo_actual, posicion, camino = heapq.heappop(cola)
        fila, col = posicion
        
        # ¡Llegamos al destino!
        if posicion == fin:
            print(f"✅ ¡Camino encontrado! Costo total: {costo_actual}")
            return camino
        
        # Si ya encontramos un camino mejor a esta posición, saltarla
        if costo_actual > mejores_costos.get(posicion, float('inf')):
            continue
        
        # Explorar vecinos: arriba, abajo, izquierda, derecha
        vecinos = [
            (fila-1, col),  # Arriba
            (fila+1, col),  # Abajo
            (fila, col-1),  # Izquierda
            (fila, col+1)   # Derecha
        ]
        
        for nueva_fila, nueva_col in vecinos:
            # ¿Está dentro del mapa?
            if 0 <= nueva_fila < filas and 0 <= nueva_col < columnas:
                nueva_pos = (nueva_fila, nueva_col)
                
                # ¿Cuánto cuesta moverse a esta celda?
                costo_movimiento = COSTOS[mapa[nueva_fila][nueva_col]]
                
                # Si es muy caro (edificio/bloqueo), no ir
                if costo_movimiento >= 999:
                    continue
                
                nuevo_costo = costo_actual + costo_movimiento
                
                # ¿Es mejor que lo que teníamos antes?
                if nuevo_costo < mejores_costos.get(nueva_pos, float('inf')):
                    mejores_costos[nueva_pos] = nuevo_costo
                    nuevo_camino = camino + [nueva_pos]
                    heapq.heappush(cola, (nuevo_costo, nueva_pos, nuevo_camino))
    
    print("❌ No se encontró camino")
    return None

def agregar_obstaculos(mapa):
    """Permite al usuario agregar obstáculos interactivamente"""
    print("\n🛠️  Agregar obstáculos al mapa:")
    print("1 = Edificio 🏢")
    print("2 = Agua 💧") 
    print("3 = Bloqueo 🚧")
    print("0 = Terminar")
    
    while True:
        try:
            tipo = input("\n¿Qué tipo de obstáculo? (0-3): ")
            if tipo == "0":
                break
            
            fila = int(input("Fila: "))
            col = int(input("Columna: "))
            
            if 0 <= fila < len(mapa) and 0 <= col < len(mapa[0]):
                mapa[fila][col] = int(tipo)
                print(f"✅ Obstáculo agregado en ({fila}, {col})")
                mostrar_mapa(mapa)
            else:
                print("❌ Posición fuera del mapa")
                
        except ValueError:
            print("❌ Por favor ingresa números válidos")

def main():
    """Función principal del programa"""
    print("🗺️  CALCULADORA DE RUTAS CON DIJKSTRA")
    print("Encuentra el camino más barato entre dos puntos\n")
    
    # Crear mapa
    try:
        filas = int(input("Tamaño del mapa - Filas: "))
        cols = int(input("Tamaño del mapa - Columnas: "))
    except ValueError:
        print("Usando tamaño por defecto: 8x8")
        filas, cols = 8, 8
    
    mapa = crear_mapa(filas, cols)
    
    # Agregar algunos obstáculos de ejemplo
    if filas >= 5 and cols >= 5:
        mapa[2][2] = EDIFICIO
        mapa[2][3] = AGUA
        mapa[3][2] = AGUA
        print("Se agregaron algunos obstáculos de ejemplo")
    
    mostrar_mapa(mapa)
    
    # Pedir inicio y fin
    try:
        print("\n📍 Posición de INICIO:")
        inicio_fila = int(input("Fila: "))
        inicio_col = int(input("Columna: "))
        inicio = (inicio_fila, inicio_col)
        
        print("\n🎯 Posición de DESTINO:")
        fin_fila = int(input("Fila: "))
        fin_col = int(input("Columna: "))
        fin = (fin_fila, fin_col)
        
    except ValueError:
        print("Usando posiciones por defecto")
        inicio = (0, 0)
        fin = (filas-1, cols-1)
    
    # Buscar camino
    camino = dijkstra_simple(mapa, inicio, fin)
    
    if camino:
        print(f"\n🎉 ¡Ruta encontrada en {len(camino)} pasos!")
        mostrar_mapa(mapa, camino, inicio, fin)
    else:
        print("\n😞 No hay camino posible")
        mostrar_mapa(mapa, None, inicio, fin)
    
    # Opción para agregar más obstáculos
    if input("\n¿Quieres agregar obstáculos? (s/n): ").lower() == 's':
        agregar_obstaculos(mapa)
        
        # Recalcular ruta
        print("\n🔄 Recalculando ruta...")
        nuevo_camino = dijkstra_simple(mapa, inicio, fin)
        if nuevo_camino:
            mostrar_mapa(mapa, nuevo_camino, inicio, fin)
        else:
            mostrar_mapa(mapa, None, inicio, fin)

if __name__ == "__main__":
    main()