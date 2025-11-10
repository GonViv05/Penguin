import tkinter as tk
from tkinter import messagebox, simpledialog
from collections import deque

# --- Constantes ---
VACIO, PARED, ENTRADA, SALIDA, CAMINO = 0, 1, 2, 3, 4
COLORES = {
    VACIO: "white",
    PARED: "black",
    ENTRADA: "green",
    SALIDA: "red",
    CAMINO: "blue"
}
TAMANO_CELDA = 20


# =====================================================
# CLASE MAPA
# =====================================================
class Mapa:
    def __init__(self, filas, columnas):
        self. filas = filas
        self.columnas = columnas
        self.grid = [[VACIO for _ in range(columnas)] for _ in range(filas)]
        self.entrada = None
        self.salida = None

    def dentro_limite(self, r, c):
        return 0 <= r < self.filas and 0 <= c < self.columnas

    def establecer(self, r, c, tipo):
        """Coloca un tipo en la celda (r,c), controlando duplicados de entrada/salida."""
        if not self.dentro_limite(r, c):
            return
        
        # No permitir sobreescribir entrada/salida existente con paredes al arrastrar
        if tipo == PARED and self.grid[r][c] in [ENTRADA, SALIDA]:
            return
            
        if tipo == ENTRADA:
            # Si ya existe una entrada en otra posición, eliminarla
            if self.entrada and self.entrada != (r, c):
                r0, c0 = self.entrada
                self.grid[r0][c0] = VACIO
            self.entrada = (r, c)
        elif tipo == SALIDA:
            # Si ya existe una salida en otra posición, eliminarla
            if self.salida and self.salida != (r, c):
                r0, c0 = self.salida
                self.grid[r0][c0] = VACIO
            self.salida = (r, c)
        self.grid[r][c] = tipo

    def limpiar_camino(self):
        for r in range(self.filas):
            for c in range(self.columnas):
                if self.grid[r][c] == CAMINO:
                    self.grid[r][c] = VACIO

    def reiniciar(self):
        self.grid = [[VACIO for _ in range(self.columnas)] for _ in range(self.filas)]
        self.entrada = None
        self.salida = None


# =====================================================
# CLASE BUSCADOR DE RUTAS (BFS)
# =====================================================
class BuscadorDeRutas:
    def __init__(self, mapa: Mapa):
        self.mapa = mapa

    def bfs(self):
        inicio, fin = self.mapa.entrada, self.mapa.salida
        if not inicio or not fin:
            return None

        cola = deque([inicio])
        predecesor = {inicio: None}

        while cola:
            actual = cola.popleft()
            if actual == fin:
                return self._reconstruir_camino(predecesor, fin)

            r, c = actual
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if self._accesible(nr, nc) and (nr, nc) not in predecesor:
                    predecesor[(nr, nc)] = actual
                    cola.append((nr, nc))
        return None

    def _accesible(self, r, c):
        return self.mapa.dentro_limite(r, c) and self.mapa.grid[r][c] != PARED

    def _reconstruir_camino(self, predecesor, fin):
        camino = []
        actual = fin
        while actual:
            camino.append(actual)
            actual = predecesor[actual]
        camino.reverse()
        return camino


# =====================================================
# CLASE INTERFAZ (Tkinter)
# =====================================================
class InterfazApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Visualizador BFS (3 clases)")

        # Pedir tamaño del mapa al usuario
        self.filas = simpledialog.askinteger("Configuración", "Ingrese cantidad de filas (5-50):", minvalue=5, maxvalue=50)
        self.columnas = simpledialog.askinteger("Configuración", "Ingrese cantidad de columnas (5-50):", minvalue=5, maxvalue=50)
        if not self.filas or not self.columnas:
            messagebox.showinfo("Cancelado", "No se creó el mapa.")
            master.destroy()
            return

        self.mapa = Mapa(self.filas, self.columnas)
        self.modo = PARED

        self.canvas = tk.Canvas(master, width=self.columnas * TAMANO_CELDA, height=self.filas * TAMANO_CELDA, bg="lightgray")
        self.canvas.pack(padx=10, pady=10)

        self._crear_controles()
        self._dibujar_grilla()

        self.canvas.bind("<Button-1>", self._clic_izquierdo)
        self.canvas.bind("<B1-Motion>", self._clic_izquierdo)
        self.canvas.bind("<Button-3>", self._clic_derecho)

    # --- UI helpers ---
    def _crear_controles(self):
        frame = tk.Frame(self.master)
        frame.pack(pady=5)

        for texto, tipo in [("Entrada (E)", ENTRADA), ("Salida (S)", SALIDA), ("Pared (W)", PARED)]:
            tk.Button(frame, text=texto, command=lambda t=tipo: self._cambiar_modo(t)).pack(side=tk.LEFT, padx=5)

        tk.Button(frame, text="Buscar Ruta", bg="yellow", command=self._buscar_ruta).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="Reiniciar", command=self._reiniciar).pack(side=tk.LEFT, padx=5)

        self.estado = tk.Label(self.master, text="Modo actual: Pared")
        self.estado.pack(pady=5)

    def _dibujar_grilla(self):
        self.rects = {}
        for r in range(self.filas):
            for c in range(self.columnas):
                x1, y1 = c * TAMANO_CELDA, r * TAMANO_CELDA
                x2, y2 = x1 + TAMANO_CELDA, y1 + TAMANO_CELDA
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORES[VACIO], outline="gray")
                self.rects[(r, c)] = rect

    def _actualizar_celda(self, r, c):
        tipo = self.mapa.grid[r][c]
        self.canvas.itemconfig(self.rects[(r, c)], fill=COLORES[tipo])
    
    def _refrescar_todas_celdas(self):
        """Refresca todas las celdas del canvas"""
        for r in range(self.filas):
            for c in range(self.columnas):
                self._actualizar_celda(r, c)

    def _cambiar_modo(self, modo):
        self.modo = modo
        nombre = {ENTRADA: "Entrada", SALIDA: "Salida", PARED: "Pared"}[modo]
        self.estado.config(text=f"Modo actual: {nombre}")

    # --- Eventos ---
    def _clic_izquierdo(self, event):
        c, r = event.x // TAMANO_CELDA, event.y // TAMANO_CELDA
        if not self.mapa.dentro_limite(r, c):
            return
        self.mapa.establecer(r, c, self.modo)
        self._refrescar_todas_celdas()  # Refrescar todo para mostrar cambios en entrada/salida anterior

    def _clic_derecho(self, event):
        c, r = event.x // TAMANO_CELDA, event.y // TAMANO_CELDA
        if not self.mapa.dentro_limite(r, c):
            return
        if self.mapa.entrada == (r, c):
            self.mapa.entrada = None
        if self.mapa.salida == (r, c):
            self.mapa.salida = None
        self.mapa.grid[r][c] = VACIO
        self._actualizar_celda(r, c)

    # --- Lógica ---
    def _buscar_ruta(self):
        self.mapa.limpiar_camino()
        buscador = BuscadorDeRutas(self.mapa)
        ruta = buscador.bfs()

        if not ruta:
            messagebox.showinfo("Sin camino", "No se encontró un camino válido.")
            return

        for r, c in ruta:
            if self.mapa.grid[r][c] not in [ENTRADA, SALIDA]:
                self.mapa.grid[r][c] = CAMINO
                self._actualizar_celda(r, c)

        messagebox.showinfo("Éxito", "Camino encontrado correctamente.")

    def _reiniciar(self):
        self.mapa.reiniciar()
        for r in range(self.filas):
            for c in range(self.columnas):
                self._actualizar_celda(r, c)


# =====================================================
# EJECUCIÓN
# =====================================================

root = tk.Tk()
app = InterfazApp(root)
root.mainloop()