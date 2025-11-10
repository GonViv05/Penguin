# juego_gato_raton.py
# Explicación completa para principiantes absolutos

"""
JUEGO DEL GATO Y EL RATÓN - EXPLICACIÓN COMPLETA

Este es un juego donde un gato trata de atrapar a un ratón en un tablero.
El ratón también puede tratar de encontrar queso para ganar.
"""

# IMPORTAR BIBLIOTECAS (HERRAMIENTAS QUE NECESITAMOS)

# os: Nos permite interactuar con el sistema operativo (limpiar la pantalla)
import os

# time: Nos permite hacer pausas y medir tiempos
import time

# random: Nos permite generar números aleatorios (para el queso)
import random

# math: Nos da funciones matemáticas (como infinito)
import math

# CONFIGURACIÓN DEL JUEGO (REGLAS Y MEDIDAS)

def pedir_tamano_tablero():
    while True:
        try:
            ancho = int(input("¿Cuántas columnas quieres que tenga el tablero? (mínimo 4, máximo 20): "))
            alto = int(input("¿Cuántas filas quieres que tenga el tablero? (mínimo 4, máximo 20): "))
            if 4 <= ancho <= 20 and 4 <= alto <= 20:
                return ancho, alto
            else:
                print("Por favor, elige valores entre 4 y 20.")
        except ValueError:
            print("Por favor, ingresa un número válido.")

ANCHO_TABLERO = 8  
ALTO_TABLERO = 8

# Número máximo de turnos antes de que el juego termine
MAX_TURNOS = 15

# Qué tan inteligente es la computadora (profundidad de búsqueda)
PROFUNDIDAD_MAXIMA = 4

# MOVIMIENTOS POSIBLES (CÓMO SE PUEDEN MOVER LOS PERSONAJES)

# Lista de todos los movimientos posibles en 8 direcciones:
# (-1, 0) = Arriba
# (1, 0)  = Abajo  
# (0, -1) = Izquierda
# (0, 1)  = Derecha
# (-1, -1) = Diagonal superior izquierda
# (1, 1)   = Diagonal inferior derecha
# (-1, 1)  = Diagonal superior derecha
# (1, -1)  = Diagonal inferior izquierda
MOVIMIENTOS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

# TECLADO (QUÉ TECLAS USAR PARA MOVERSE)

# Diccionario que relaciona teclas con movimientos:
TECLAS_MOVIMIENTO = {
    'w': (-1, 0, "Arriba"),          # Tecla W = mover arriba
    's': (1, 0, "Abajo"),            # Tecla S = mover abajo
    'a': (0, -1, "Izquierda"),       # Tecla A = mover izquierda
    'd': (0, 1, "Derecha"),          # Tecla D = mover derecha
    'q': (-1, -1, "Diagonal superior izquierda"),  # Tecla Q
    'e': (-1, 1, "Diagonal superior derecha"),     # Tecla E
    'z': (1, -1, "Diagonal inferior izquierda"),   # Tecla Z
    'c': (1, 1, "Diagonal inferior derecha")       # Tecla C
}

# CLASE PRINCIPAL DEL JUEGO (EL "CEREBRO" DEL JUEGO)

class JuegoGatoRaton:
    # CONSTRUCTOR (INICIALIZA EL JUEGO)
    def __init__(self, ancho_tablero, alto_tablero):
        self.ancho_tablero = ancho_tablero
        self.alto_tablero = alto_tablero
        # Posición inicial del ratón: esquina inferior derecha
        self.pos_raton = (self.alto_tablero - 1, self.ancho_tablero - 1)
        # Posición inicial del gato: esquina superior izquierda  
        self.pos_gato = (0, 0)
        # Empezamos en el turno 1
        self.turno_actual = 1
        # El jugador puede elegir ser el gato o el ratón
        # El juego no ha terminado todavía
        self.juego_terminado = False
        # Generamos una posición aleatoria para el queso
        self.pos_queso = self.generar_posicion_queso()
    
    # GENERAR POSICIÓN DEL QUESO (COLOCAR EL QUESO EN EL TABLERO)
    def generar_posicion_queso(self):
        # Seguimos intentando hasta encontrar una posición válida
        while True:
            # Generamos una posición aleatoria (fila y columna)
            pos = (random.randint(0, self.alto_tablero-1), random.randint(0, self.ancho_tablero-1))
            # Verificamos que no esté donde están el gato o el ratón
            if pos != self.pos_raton and pos != self.pos_gato:
                return pos  # Esta posición es buena, la devolvemos
    
    # MOVIMIENTOS VÁLIDOS (QUÉ MOVIMIENTOS PUEDE HACER UN PERSONAJE)
    def movimientos_validos(self, posicion):
        """Devuelve todos los movimientos válidos desde una posición dada"""
        fila, col = posicion
        movimientos_posibles = []
        for delta_fia, delta_columna in MOVIMIENTOS:
            nueva_fila = fila + delta_fia
            nueva_columna = col + delta_columna
            if 0 <= nueva_fila < self.alto_tablero and 0 <= nueva_columna < self.ancho_tablero:
                movimientos_posibles.append((nueva_fila, nueva_columna))
        return movimientos_posibles
    
    # LIMPIAR CONSOLA (BORRAR LA PANTALLA PARA MOSTRAR NUEVO ESTADO)
    def limpiar_consola(self):
        """Limpia la consola según el sistema operativo"""
        # Si estamos en Windows, usamos 'cls', sino 'clear' (Linux/Mac)
        os.system('cls' if os.name == 'nt' else 'clear')
    
    # MOSTRAR TABLERO (DIBUJAR EL ESTADO ACTUAL DEL JUEGO)
    def mostrar_tablero(self):
        """Muestra el tablero de juego con las posiciones actuales"""
        print("🎮 Turno {}".format(self.turno_actual))
        print("Gato: 🐱 | Ratón: 🐭 | Queso: 🧀")
        print("-" * (self.ancho_tablero * 2 + 2))
        for fila in range(self.alto_tablero):
            linea = ""
            for columna in range(self.ancho_tablero):
                posicion = (fila, columna)
                if posicion == self.pos_raton and posicion == self.pos_gato:
                    linea += "💥"
                elif posicion == self.pos_raton and posicion == self.pos_queso:
                    linea += "🐭🧀"
                elif posicion == self.pos_gato:
                    linea += "🐱"
                elif posicion == self.pos_raton:
                    linea += "🐭"
                elif posicion == self.pos_queso:
                    linea += "🧀"
                else:
                    linea += ". "
            print(linea)
        print("-" * (self.ancho_tablero * 2 + 2))
    
    # MOSTRAR CONTROLES (EXPLICAR QUÉ TECLAS USAR)
    def mostrar_controles(self):
        """Muestra los controles disponibles"""
        print("\nControles de movimiento:")
        print("w - Arriba    a - Izquierda    s - Abajo    d - Derecha")
        print("q - Diagonal superior izquierda  e - Diagonal superior derecha")
        print("z - Diagonal inferior izquierda  c - Diagonal inferior derecha")
        print("x - Salir del juego")
    
    # DISTANCIA MANHATTAN (MEDIR DISTANCIA ENTRE DOS PUNTOS)
    def distancia_manhattan(self, pos1, pos2):
        """Calcula la distancia Manhattan entre dos posiciones"""
        # La distancia Manhattan es la suma de las diferencias en filas y columnas
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    # EVALUAR ESTADO (QUÉ TAN BUENA ES UNA SITUACIÓN PARA EL RATÓN)
    def evaluar_estado(self, es_turno_raton):
        """
        Evalúa el estado actual del juego para el algoritmo minimax
        Ahora el ratón busca el queso y evita al gato.
        """
        if self.pos_raton == self.pos_gato:
            return -1000 if es_turno_raton else 1000  # Muy malo para el ratón
        if self.pos_raton == self.pos_queso:
            return 1000 if es_turno_raton else -1000  # Muy bueno para el ratón

        dist_gato = self.distancia_manhattan(self.pos_raton, self.pos_gato)
        dist_queso = self.distancia_manhattan(self.pos_raton, self.pos_queso)
        # El ratón quiere acercarse al queso y alejarse del gato
        # Mientras más cerca del queso (dist_queso pequeño), mejor
        # Mientras más lejos del gato (dist_gato grande), mejor
        score = (5 * dist_gato) - (15 * dist_queso)
        return score
    
    # ALGORITMO MINIMAX (CÓMO LA COMPUTADORA TOMA DECISIONES INTELIGENTES)
    def minimax(self, profundidad, es_turno_raton):
        """
        Implementación clásica del algoritmo minimax
        """
        # Si llegamos al límite de profundidad o el juego terminó
        if profundidad == 0 or self.pos_raton == self.pos_gato:
            return self.evaluar_estado(es_turno_raton), None

        mejor_movimiento = None

        if es_turno_raton:
            max_eval = -math.inf
            movimientos = self.movimientos_validos(self.pos_raton)
            for movimiento in movimientos:
                pos_raton_original = self.pos_raton
                self.pos_raton = movimiento  
                eval, _ = self.minimax(profundidad - 1, False)
                self.pos_raton = pos_raton_original
                if eval > max_eval:
                    max_eval = eval
                    mejor_movimiento = movimiento
            return max_eval, mejor_movimiento
        else:
            min_eval = math.inf
            movimientos = self.movimientos_validos(self.pos_gato)
            for movimiento in movimientos:
                pos_gato_original = self.pos_gato
                self.pos_gato = movimiento
                eval, _ = self.minimax(profundidad - 1, True)
                self.pos_gato = pos_gato_original
                if eval < min_eval:
                    min_eval = eval
                    mejor_movimiento = movimiento
            return min_eval, mejor_movimiento
    
    # MOVER JUGADOR (MANEJAR EL MOVIMIENTO DEL JUGADOR HUMANO)
    def mover_jugador(self, es_gato):
        """Maneja el movimiento del jugador humano"""
        pos_actual = self.pos_gato if es_gato else self.pos_raton
        personaje = "gato" if es_gato else "ratón"
        while True:
            self.mostrar_controles()
            tecla = input(f"\nMovimiento del {personaje} ({self.pos_gato if es_gato else self.pos_raton}): ").lower()
            if tecla == 'x':
                self.juego_terminado = True
                return pos_actual
            if tecla in TECLAS_MOVIMIENTO:
                delta_fia, delta_columna, desc = TECLAS_MOVIMIENTO[tecla]
                nueva_fila = pos_actual[0] + delta_fia
                nueva_columna = pos_actual[1] + delta_columna
                if 0 <= nueva_fila < self.alto_tablero and 0 <= nueva_columna < self.ancho_tablero:
                    return (nueva_fila, nueva_columna)
                else:
                    print("Movimiento inválido. No puedes salir del tablero.")
            else:
                print("Tecla no válida. Usa una de las teclas indicadas.")
    
    # VERIFICAR FIN DEL JUEGO (COMPROBAR SI ALGUIEN GANÓ)
    def verificar_fin_juego(self):
        """Verifica si el juego ha terminado y muestra el mensaje apropiado"""
        # Si el gato atrapó al ratón
        if self.pos_raton == self.pos_gato:
            self.limpiar_consola()
            self.mostrar_tablero()
            print("💀 ¡El gato atrapó al ratón! Fin del juego.")
            return True
        
        # Si el ratón encontró el queso
        elif self.pos_raton == self.pos_queso:
            self.limpiar_consola()
            self.mostrar_tablero()
            print("🧀 ¡El ratón encontró el queso y ganó! 🧀")
            return True
        
        # Si se acabaron los turnos
        elif self.turno_actual > MAX_TURNOS:
            self.limpiar_consola()
            self.mostrar_tablero()
            print("🎉 ¡El ratón escapó después de {} turnos!".format(MAX_TURNOS))
            return True
        
        # Si el juego sigue
        return False
    
    # JUGAR TURNO (EJECUTAR UN TURNO COMPLETO DEL JUEGO)
    def jugar_turno(self):
        """Ejecuta un turno completo del juego"""
        self.limpiar_consola()
        self.mostrar_tablero()

        # TURNO DEL GATO
        if self.jugador_es_gato:
            self.pos_gato = self.mover_jugador(True)
        else:
            print("Turno del gato (IA)...")
            time.sleep(1)
            _, self.pos_gato = self.minimax(min(3, MAX_TURNOS - self.turno_actual), False)

        # Verificamos si el juego terminó después del movimiento del gato
        if self.verificar_fin_juego() or self.juego_terminado:
            self.turno_actual += 1
            return False

        # TURNO DEL RATÓN
        if not self.jugador_es_gato:
            self.pos_raton = self.mover_jugador(False)
        else:
            print("Turno del ratón (IA)...")
            time.sleep(1)
            _, self.pos_raton = self.minimax(min(3, MAX_TURNOS - self.turno_actual), True)

        self.turno_actual += 1
        return not self.verificar_fin_juego()
    
    # ELEGIR PERSONAJE (PERMITIR AL JUGADOR ELEGIR QUÉ PERSONAJE CONTROLAR)
    def elegir_personaje(self):
        """Permite al jugador elegir su personaje"""
        self.limpiar_consola()
        print("=" * 40)
        print("       JUEGO DEL GATO Y EL RATÓN")
        print("=" * 40)
        
        # Seguimos preguntando hasta que elija una opción válida
        while True:
            eleccion = input("¿Quieres ser el gato (g) o el ratón (r)? ").strip().lower()
            
            if eleccion in ["g", "gato"]:
                self.jugador_es_gato = True
                break
            elif eleccion in ["r", "raton", "ratón"]:
                self.jugador_es_gato = False
                break
            else:
                print("Por favor, elige 'g' para gato o 'r' para ratón.")
    
    # JUGAR (FUNCIÓN PRINCIPAL QUE EJECUTA EL JUEGO COMPLETO)
    def jugar(self):
        """Función principal que ejecuta el juego completo"""
        # El jugador elige qué personaje controlar
        self.elegir_personaje()
        
        # Bucle principal del juego
        while self.turno_actual <= MAX_TURNOS and not self.juego_terminado:
            # Jugamos un turno
            if not self.jugar_turno():
                break  # Si el juego terminó, salimos del bucle
            
            # Pequeña pausa entre turnos para que el jugador pueda ver
            if not self.juego_terminado:
                time.sleep(0.5)
        
        # Preguntamos si quiere jugar de nuevo
        if not self.juego_terminado:
            again = input("\n¿Quieres jugar again? (s/n): ").strip().lower()
            if again in ["s", "si", "sí"]:
                # Reiniciamos el juego con el mismo tamaño de tablero
                self.__init__(self.ancho_tablero, self.alto_tablero)
                self.jugar()


# EJECUTAR EL JUEGO (CUANDO SE EJECUTA ESTE ARCHIVO DIRECTAMENTE)


print("Bienvenido al juego del Gato y el Ratón!")
ancho, alto = pedir_tamano_tablero()
juego = JuegoGatoRaton(ancho, alto)
juego.jugar()
