import tkinter as tk
from tkinter import messagebox
import collections

# --- Constantes para la GUI y el Algoritmo ---
FILAS_DEFAULT = 30
COLUMNAS_DEFAULT = 30
TAMANO_CELDA = 20 # Píxeles

# Definiciones de estado para la grilla y la GUI
VACIO = 0    
PARED = 1    
ENTRADA = 2  
SALIDA = 3   
CAMINO = 4  

COLORES = {
    VACIO: "white",
    PARED: "black",
    ENTRADA: "green",
    SALIDA: "red",
    CAMINO: "blue",
}

class PathfindingGUI:

    def __init__(self, master):
        self.master = master
        master.title("Visualizador Challenge 1 (BFS)")

        self.filas = FILAS_DEFAULT
        self.columnas = COLUMNAS_DEFAULT
        self.grilla = self._crear_grilla_logica(self.filas, self.columnas)
        self.entrada_pos = None
        self.salida_pos = None
        
        # Estado de colocación: 0=ninguno, 1=ENTRADA, 2=SALIDA, 3=PARED
        self.modo_colocacion = PARED 

        # Crear los widgets de la interfaz
        self._crear_widgets()
        self._dibujar_grilla_inicial()
        
        # Asociar eventos de ratón al Canvas
        self.canvas.bind("<Button-1>", self._manejar_clic_izquierdo)
        self.canvas.bind("<B1-Motion>", self._manejar_clic_izquierdo) # Para arrastrar paredes
        self.canvas.bind("<Button-3>", self._manejar_clic_derecho)
        

## --- Lógica de la Grilla y Tkinter ---

    def _crear_grilla_logica(self, filas, columnas):
        """Crea la estructura de datos (matriz) para el algoritmo."""
        # Inicializa la grilla con estados VACIO (0)
        return [[VACIO for _ in range(columnas)] for _ in range(filas)]

    def _crear_widgets(self):
        """Configura los elementos de la interfaz de usuario."""
        
        # Marco para controles de tamaño
        frame_tamano = tk.Frame(self.master)
        frame_tamano.pack(pady=5)
        
        # Controles para filas
        tk.Label(frame_tamano, text="Filas:").pack(side=tk.LEFT, padx=5)
        self.entry_filas = tk.Entry(frame_tamano, width=5)
        self.entry_filas.insert(0, str(self.filas))
        self.entry_filas.pack(side=tk.LEFT, padx=5)
        
        # Controles para columnas
        tk.Label(frame_tamano, text="Columnas:").pack(side=tk.LEFT, padx=5)
        self.entry_columnas = tk.Entry(frame_tamano, width=5)
        self.entry_columnas.insert(0, str(self.columnas))
        self.entry_columnas.pack(side=tk.LEFT, padx=5)
        
        # Botón para aplicar cambios
        tk.Button(frame_tamano, text="Aplicar Tamaño", command=self._cambiar_tamano_grilla).pack(side=tk.LEFT, padx=10)
        
        # Canvas principal para dibujar la grilla
        canvas_width = self.columnas * TAMANO_CELDA
        canvas_height = self.filas * TAMANO_CELDA
        self.canvas = tk.Canvas(self.master, width=canvas_width, height=canvas_height, bg="lightgray")
        self.canvas.pack(padx=10, pady=10)

        # Marco para los botones de control
        frame_controles = tk.Frame(self.master)
        frame_controles.pack(pady=10)

        # Botones para seleccionar qué colocar
        tk.Label(frame_controles, text="Modo:").pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_controles, text="Entrada (E)", command=lambda: self._cambiar_modo(ENTRADA)).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_controles, text="Salida (S)", command=lambda: self._cambiar_modo(SALIDA)).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_controles, text="Pared (W)", command=lambda: self._cambiar_modo(PARED)).pack(side=tk.LEFT, padx=5)
        
        # Botón de ejecutar
        tk.Button(frame_controles, text="🔍 Buscar Camino", bg="yellow", command=self.ejecutar_busqueda).pack(side=tk.LEFT, padx=15)

        # Botón de Reset
        tk.Button(frame_controles, text="🧹 Limpiar Todo", command=self.reset).pack(side=tk.LEFT, padx=5)
        
        # Etiqueta de estado
        self.estado_label = tk.Label(self.master, text=f"Modo actual: Pared (Clic Izquierdo)")
        self.estado_label.pack(pady=5)
        
    def _dibujar_grilla_inicial(self):
        """Dibuja todos los rectángulos de la grilla en el canvas."""
        self.canvas_items = {}
        for r in range(self.filas):
            for c in range(self.columnas):
                x1 = c * TAMANO_CELDA
                y1 = r * TAMANO_CELDA
                x2 = x1 + TAMANO_CELDA
                y2 = y1 + TAMANO_CELDA
                # Dibuja el rectángulo y guarda su ID en el diccionario
                item_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORES[VACIO], outline="gray")
                self.canvas_items[(r, c)] = item_id

    def _actualizar_celda_gui(self, r, c, estado):
        """Actualiza el color de una celda en el Canvas según su nuevo estado."""
        color = COLORES.get(estado, "purple") # Usa un color por defecto si el estado es desconocido
        self.canvas.itemconfig(self.canvas_items[(r, c)], fill=color)

    def _cambiar_modo(self, modo):
        """Cambia el modo de colocación actual."""
        self.modo_colocacion = modo
        nombre_modo = {ENTRADA: "Entrada", SALIDA: "Salida", PARED: "Pared"}.get(modo, "Pared")
        self.estado_label.config(text=f"Modo actual: {nombre_modo} (Clic Izquierdo)")

    def _mapear_coordenadas(self, event_x, event_y):
        """Convierte las coordenadas de píxel a coordenadas de grilla (fila, columna)."""
        c = event_x // TAMANO_CELDA
        r = event_y // TAMANO_CELDA
        
        if 0 <= r < self.filas and 0 <= c < self.columnas:
            return r, c
        return None, None

    def _manejar_clic_izquierdo(self, event):
        """
        Maneja el clic izquierdo (o arrastre).
        Coloca la ENTRADA, SALIDA o PARED según el modo actual.
        """
        r, c = self._mapear_coordenadas(event.x, event.y)
        if r is None: return

        nuevo_estado = self.modo_colocacion
        
        # Lógica especial para Entrada y Salida (solo puede haber uno de cada)
        if nuevo_estado == ENTRADA:
            if self.entrada_pos:
                # Limpiar el anterior
                r_old, c_old = self.entrada_pos
                self.grilla[r_old][c_old] = VACIO
                self._actualizar_celda_gui(r_old, c_old, VACIO)
            self.entrada_pos = (r, c)
        elif nuevo_estado == SALIDA:
            if self.salida_pos:
                # Limpiar el anterior
                r_old, c_old = self.salida_pos
                self.grilla[r_old][c_old] = VACIO
                self._actualizar_celda_gui(r_old, c_old, VACIO)
            self.salida_pos = (r, c)

        # Aplicar el nuevo estado a la grilla y la GUI
        self.grilla[r][c] = nuevo_estado
        self._actualizar_celda_gui(r, c, nuevo_estado)

    def _manejar_clic_derecho(self, event):
        """Maneja el clic derecho para eliminar un elemento (convertir a VACIO)."""
        r, c = self._mapear_coordenadas(event.x, event.y)
        if r is None: return
        
        estado_actual = self.grilla[r][c]

        # Si el elemento a borrar es la Entrada o la Salida, actualiza las referencias
        if estado_actual == ENTRADA:
            self.entrada_pos = None
        elif estado_actual == SALIDA:
            self.salida_pos = None

        # Cambiar el estado a vacío y actualizar la GUI
        self.grilla[r][c] = VACIO
        self._actualizar_celda_gui(r, c, VACIO)
        
## --- Lógica del Algoritmo BFS ---

    def bfs(self):
        """Implementación de BFS"""
        if not self.entrada_pos or not self.salida_pos:
            messagebox.showerror("Error", "Debes colocar la Entrada (E) y la Salida (S).")
            return None

        filas, columnas = self.filas, self.columnas
        inicio = self.entrada_pos
        fin = self.salida_pos

        cola = collections.deque([(inicio, [inicio])])
        visitados = set([inicio])
        
        # Reiniciar colores del camino anterior (cualquier cosa que no sea E, S o W)
        for r in range(filas):
            for c in range(columnas):
                estado = self.grilla[r][c]
                if estado not in [ENTRADA, SALIDA, PARED]:
                    self.grilla[r][c] = VACIO
                    self._actualizar_celda_gui(r, c, VACIO)
                    
        self.master.update()

        while cola: #mientras la cola tenga elementos
            (fila_actual, col_actual), camino_actual = cola.popleft()

            if (fila_actual, col_actual) == fin:
                return camino_actual

            direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Arriba, abajo, izquierda, derecha

            for df, dc in direcciones:
                nueva_fila, nueva_col = fila_actual + df, col_actual + dc
                nueva_posicion = (nueva_fila, nueva_col)

                if 0 <= nueva_fila < filas and 0 <= nueva_col < columnas and nueva_posicion not in visitados:
                    estado = self.grilla[nueva_fila][nueva_col]

                    # NO pasar por PAREDES
                    if estado == PARED:
                        continue
                        
                    visitados.add(nueva_posicion)
                    nuevo_camino = list(camino_actual)
                    nuevo_camino.append(nueva_posicion)
                    cola.append((nueva_posicion, nuevo_camino))
                    
                    # VISUALIZACIÓN: Marcar las celdas visitadas (no es el camino final)
                    if estado != SALIDA:
                         self.grilla[nueva_fila][nueva_col] = VACIO # Se visita, pero se deja 'VACIO' temporalmente para no interferir
                         #self._actualizar_celda_gui(nueva_fila, nueva_col, VACIO) # Mantiene el color blanco/vacío
                         self._actualizar_celda_gui(nueva_fila, nueva_col, 5) # Si quieres un color temporal para 'visitado'
                         
                    self.master.update()

        return None # No se encontró un camino

    def ejecutar_busqueda(self):
        """Inicia la búsqueda de caminos y visualiza el resultado."""
        camino = self.bfs()

        if camino:
            # Marcar el camino final
            for r, c in camino:
                if self.grilla[r][c] not in [ENTRADA, SALIDA]:
                    self.grilla[r][c] = CAMINO
                    self._actualizar_celda_gui(r, c, CAMINO)
            messagebox.showinfo("¡Éxito!", "¡Camino más corto encontrado!")
        else:
            messagebox.showinfo("Fallido", "¡No se encontró un camino!")
    
    def _cambiar_tamano_grilla(self):
        """Cambia el tamaño de la grilla según los valores de los entries."""
        try:
            nuevas_filas = int(self.entry_filas.get())
            nuevas_columnas = int(self.entry_columnas.get())
            
            # Validar rangos
            if nuevas_filas < 5 or nuevas_filas > 100:
                messagebox.showerror("Error", "Las filas deben estar entre 5 y 100")
                return
            if nuevas_columnas < 5 or nuevas_columnas > 100:
                messagebox.showerror("Error", "Las columnas deben estar entre 5 y 100")
                return
            
            # Actualizar dimensiones
            self.filas = nuevas_filas
            self.columnas = nuevas_columnas
            
            # Recrear la grilla lógica
            self.grilla = self._crear_grilla_logica(self.filas, self.columnas)
            self.entrada_pos = None
            self.salida_pos = None
            
            # Redimensionar el canvas
            canvas_width = self.columnas * TAMANO_CELDA
            canvas_height = self.filas * TAMANO_CELDA
            self.canvas.config(width=canvas_width, height=canvas_height)
            
            # Redibujar la grilla
            self.canvas.delete("all")
            self._dibujar_grilla_inicial()
            
            messagebox.showinfo("Éxito", f"Grilla cambiada a {self.filas}x{self.columnas}")
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa números válidos")
            
    def reset(self):
        """Reinicia la grilla y las variables de control."""
        self.grilla = self._crear_grilla_logica(self.filas, self.columnas)
        self.entrada_pos = None
        self.salida_pos = None
        self.canvas.delete("all")
        self._dibujar_grilla_inicial()



# --- Ejecución del Programa ---
#master.update()
root = tk.Tk()
app = PathfindingGUI(root)
root.mainloop()
