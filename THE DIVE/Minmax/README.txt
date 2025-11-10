JUEGO DEL GATO Y EL RATÓN

Descripción general:
--------------------
Este proyecto implementa un juego de consola donde un gato y un ratón se mueven en un tablero de 8x8 casillas. El objetivo del gato es atrapar al ratón, mientras que el ratón puede ganar si logra llegar al queso (que aparece en una posición aleatoria) o si sobrevive una cantidad máxima de turnos.

Características principales:
---------------------------
- El jugador puede elegir si quiere controlar al gato o al ratón.
- El tablero se muestra en consola, con íconos para el gato, el ratón, el queso y la colisión.
- El ratón y el gato pueden moverse en 8 direcciones (vertical, horizontal y diagonal).
- El queso aparece en una posición aleatoria al inicio de cada partida.
- El juego termina si:
  - El gato atrapa al ratón (ambos en la misma casilla).
  - El ratón llega al queso.
  - Se alcanza el número máximo de turnos y el ratón no fue atrapado.
- El jugador humano mueve usando teclas (w, a, s, d, q, e, z, c) y puede salir con 'x'.
- La IA usa el algoritmo minimax con poda alpha-beta para tomar decisiones inteligentes.

Estructura del código:
----------------------
- El código está organizado en una clase principal `JuegoGatoRaton` que contiene toda la lógica del juego.
- Hay funciones para mostrar el tablero, manejar los movimientos, verificar el fin del juego y ejecutar el algoritmo minimax.
- El archivo puede ejecutarse directamente y comenzará el juego en la consola.

Cómo jugar:
-----------
1. Ejecuta el archivo `gatoyraton.py`
2. Elige si quieres ser el gato o el ratón.
3. Usa las teclas indicadas para moverte.
4. El objetivo depende del personaje:
   - Si eres el gato: atrapa al ratón.
   - Si eres el ratón: llega al queso o sobrevive hasta el final.
