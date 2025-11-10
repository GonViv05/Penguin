import socket
import threading

clientes_conectados=[]
                                       
def enviar_a_todos(mensaje, cliente_emisor=None):

    clientes_a_remover = []

    for cliente in clientes_conectados:
        if cliente != cliente_emisor:
            try:
                cliente.send(mensaje)
            except:
                clientes_a_remover.append(cliente)

    for cliente in clientes_a_remover:
        remover_cliente(cliente)

def remover_cliente(cliente):
    if cliente in clientes_conectados:
        clientes_conectados.remove(cliente)
        cliente.close()

def manejar_cliente(cliente):
    #lo que pasa es que cuando se inicia un hilo se crea un proceso paralelo y el while corre en otro hilo
    while True:
        try:
            mensaje = cliente.recv(1024) #1024 es el tamaño del mensaje en bits
            if mensaje:
                print("mensaje recibido:", mensaje.decode())

                enviar_a_todos(mensaje, cliente_emisor=cliente)
            else:
                remover_cliente(cliente)
                break
        except:
            remover_cliente(cliente)
            break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#setsockopt - permite configurar el socket
#SOL_SOCKET - nivel de la opcion de socket
#SO_REUSEADDR - permite reutilizar la direccion y el puerto
#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilizar el puerto
server.bind(('127.0.0.1', 5555)) #es un identificador de la aplicacion que esta usando
server.listen() #va a escuchar cuantas conexiones puede aguantar mi pc
print('servidor iniciado...')      

while True:
    cliente, direccion = server.accept()
    print(f"nuevo cliente conectado: {direccion}")
    clientes_conectados.append(cliente)

    Thread = threading.Thread(target=manejar_cliente, args=(cliente,))
    Thread.daemon = True  # Hilos demonio para que se cierren con el programa principal
    Thread.start() #

