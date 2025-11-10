import selectors
import socket

sel = selectors.DefaultSelector()
usuarios = {}

def aceptar(sock):
    conn, _ = sock.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, recibir_nombre)

def recibir_nombre(conn):
    try:
        datos = conn.recv(1024)
        if not datos:
            return desconectar(conn)

        # Separar posible nombre y mensaje juntos
        partes = datos.decode().split("\n", 1)
        nombre = partes[0].strip()
        usuarios[conn] = nombre
        print(f"{nombre} conectado.")
        enviar_todos(f"{nombre} se unió al chat", conn)

        sel.modify(conn, selectors.EVENT_READ, leer_mensaje)

        # Si había más datos después del nombre, los procesa como mensaje
        if len(partes) > 1 and partes[1].strip():
            procesar_mensaje(conn, partes[1].strip())

    except Exception as e:
        print("Error al recibir nombre:", e)
        desconectar(conn)

def leer_mensaje(conn):
    try:
        datos = conn.recv(1024)
        if not datos:
            return desconectar(conn)
        procesar_mensaje(conn, datos.decode().strip())
    except Exception as e:
        print("Error al leer mensaje:", e)
        desconectar(conn)

def procesar_mensaje(conn, msg):
    nombre = usuarios.get(conn, "Desconocido")
    print(f"{nombre}: {msg}")
    enviar_todos(f"{nombre}: {msg}", conn)

def enviar_todos(msg, emisor=None):
    for c in list(usuarios):
        try:
            if c != emisor:
                c.sendall(msg.encode())
        except:
            desconectar(c)

def desconectar(conn):
    nombre = usuarios.pop(conn, None)
    try:
        sel.unregister(conn)
    except:
        pass
    conn.close()
    if nombre:
        print(f"{nombre} desconectado.")
        enviar_todos(f"{nombre} salió del chat")

# --- Servidor principal ---
s = socket.socket()
s.bind(("127.0.0.1", 8000))
s.listen()
s.setblocking(False)
sel.register(s, selectors.EVENT_READ, aceptar)

print("Servidor activo en 127.0.0.1:8000")
while True:
    for key, _ in sel.select():
        key.data(key.fileobj)
