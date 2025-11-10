import socket
import threading

def recibir(sock):
    while True:
        try:
            datos = sock.recv(1024)
            if not datos:
                print("Conexión cerrada por el servidor.")
                break
            print(datos.decode())
        except Exception as e:
            print("Error al recibir:", e)
            break
    sock.close()

def cliente():
    host = "127.0.0.1"  # Cambia a la IP del servidor si estás en otra PC
    puerto = 8000

    sock = socket.socket()
    sock.connect((host, puerto))
    print(f"Conectado al servidor {host}:{puerto}")

    nombre = input("Ingresa tu nombre: ").strip()
    if not nombre:
        print("Debes ingresar un nombre.")
        sock.close()
        return

    sock.sendall(nombre.encode())  # Enviar nombre al servidor
    print("Nombre enviado, puedes comenzar a chatear.")

    hilo = threading.Thread(target=recibir, args=(sock,))
    hilo.daemon = True
    hilo.start()

    try:
        while True:
            msg = input()
            if msg.lower() == "/salir":
                break
            if not msg.strip():
                continue
            try:
                sock.sendall(msg.encode())
            except Exception as e:
                print("Error al enviar:", e)
                break
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print("Desconectado del servidor.")


cliente()
