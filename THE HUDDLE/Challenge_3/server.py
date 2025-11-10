import socket
import threading

#lista con los clientes conectados
clientes_conectados=[]

#el cliente emisor esta en none porque puede que no haya un cliente emisor
def enviar_a_todos(mensaje, cliente_emisor=None):
    #lista con los clientes que se van a remover
    clientes_a_remover = []

    #envia el mensaje a todos los clientes conectados excepto al que lo envio
    for cliente in clientes_conectados:
        if cliente != cliente_emisor:
            try:
                #envia el mensaje
                cliente.send(mensaje)
            except:
                #si hay un error al enviar el mensaje, se agrega el cliente a la lista de remover
                clientes_a_remover.append(cliente)

    #remueve los clientes que no pudieron recibir el mensaje
    for cliente in clientes_a_remover:
        remover_cliente(cliente)

def remover_cliente(cliente):

    #revisa si el cliente esta en la lista de conectados
    if cliente in clientes_conectados:
        #le desconecta a la mierda
        clientes_conectados.remove(cliente)
        cliente.close()

def manejar_cliente(cliente):
    #lo que pasa es que cuando se inicia un hilo se crea un proceso paralelo y el while corre en otro hilo
    while True:
        try:
            mensaje = cliente.recv(1024) #1024 es el tamaño maxima de bytes que se leen de una vez
            if mensaje:
                print("mensaje recibido:", mensaje.decode()) #decodifica el mensaje que llega en bytes a string

                enviar_a_todos(mensaje, cliente_emisor=cliente)
            else:
                remover_cliente(cliente)
                break
        except:
            remover_cliente(cliente)
            break
                                        #TCP
                                        
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#enlaza el servidor con el localhost
server.bind(('127.0.0.1', 5555)) #es un identificador de la aplicacion que esta usando
server.listen() #va a escuchar cuantas conexiones puede aguantar mi pc
print('servidor iniciado...')     
while True:
                #en este punto se queda esperando hasta que un cliente se conecte
    cliente, direccion  = server.accept() 
    #cliente es el socket del cliente que se conecto
    #direccion es la direccion del cliente que se conecto
    print(f"nuevo cliente conectado: {direccion}")
    clientes_conectados.append(cliente)

    Thread = threading.Thread(target=manejar_cliente, args=(cliente,))
    Thread.start() #habilita el thread para que corra en paralelo


