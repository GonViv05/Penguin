import socket
import threading
#el cliente tiene dos threading corriendo, uno para enviar y otro para recibir 
import time

def cliente():
    try:                        #AF_INET es ip v4 / SOCK_STREA Mes TCP
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect(('127.0.0.1', 5555))
        print("Conectado al servidor de chat!")
        
    except ConnectionRefusedError: #en caso de que se quiera ejecutar el cliente sin que el servidor este corriendo
        print("No se pudo conectar al servidor. ¿Está ejecutándose?")
        return
    except Exception as e: #cualquier otro error
        print(f"Error: {e}")
        return
    
    def recibir_mensajes():
        while True:
            try:          #recibe en bytes y lo decodifica a utf-8 (string)
                mensaje = cliente.recv(1024).decode('utf-8')
                if not mensaje: #si el mensaje esta vacio, se desconecto el servidor
                    print("\nServidor desconectado")
                    break
                print(f"\n📨 {mensaje}\nTú: ", end="") #imprime el mensaje y lo termina
            except (ConnectionResetError, BrokenPipeError): #si el servidor se cierra abruptamente
                print("\nConexión con el servidor perdida")
                break
            except Exception as e: #cualquier otro error
                print(f"\nError recibiendo mensaje: {e}")
                break
    
    def enviar_mensajes():
        while True:
            try:
                mensaje = input("Tú: ") #input siempre devuelve string
                if mensaje.lower() == 'salir':
                    print("Saliendo del chat...")
                    cliente.close() #cierra la conexion
                    break
                
                cliente.send(mensaje.encode('utf-8')) #convierte el string a bytes
                time.sleep(0.5)  # Pequeña pausa para no saturar
                
            except (BrokenPipeError, OSError):
                print("No conectado al servidor")
                break
            except KeyboardInterrupt: #cuando haces ctrl+c
                print("\nSaliendo...")
                cliente.close() #cierra la conexion
                break
    
    # Iniciar hilo receptor
    hilo_receptor = threading.Thread(target=recibir_mensajes) 
    hilo_receptor.daemon = True  # Permite que el hilo se cierre al salir del programa
    hilo_receptor.start()
    
    # Hilo principal para enviar
    enviar_mensajes()

cliente()


