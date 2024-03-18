import socket
import threading
import json
import datetime
import os
from utilities import Utilities

############################################################################
#SOCKET SERVER
############################################################################
class ServerSocket:

    client_sockets = []
    

    #PUESTA EN MARCHA DEL SOCKET SERVIDOR --------------------------------
    def __init__(self, params):
        host = params["server_ip"]
        port = params["server_port"]
        self.utils = Utilities()

        try:
            self.utils.clear_console()
            self.clients = []
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)

            #Hilo para recibir los nuevos sockets cliente---------------------------
            threading.Thread(name='th_new_clients', target = self.__client_sockets_listener).start()

            print("====================================================================")
            print(f"\n    Servidor escuchando en {host}:{port} \n")
            print("====================================================================")
        
        except BaseException as errorType:
            self.utils.error_handler(errorType)
            self.server_socket.close()

    
    
    #CONTROLADOR DE NUEVOS SOCKET CLIENTE --------------------------------
    def __client_sockets_listener(self):
        try:
            while True:
                new_socket = self.server_socket.accept()
                print(f"New client connection from {new_socket[1][0]}")
                self.client_sockets.append(new_socket)

                #Hilo para comunicacion de cada sockets cliente---------------
                threading.Thread(name='th_client_controller', target = self.__operation_controller, args=[new_socket]).start()

        except BaseException as errorType:
            self.utils.error_handler(errorType)
            self.server_socket.close()



    #ORQUESTADOR DE OPERACIONES ------------------------------------------
    def __operation_controller(self, client_socket):
        try:
            while True:
                data = json.loads(client_socket[0].recv(1024).decode("utf-8"))                    

                if(data['operacion'] == 'new_message'):
                    for client in self.client_sockets:
                        if client != sender_socket:
                            client.send(data['message'].encode("utf-8"))

        except BaseException as errorType:
            self.utils.error_handler(errorType)
            self.server_socket.close()

 
 







############################################################################
#BLOQUE DE INICIO DE SCRIPT SERVER.PY
############################################################################
if __name__ == "__main__":

    parametros = {
        "server_ip": '172.31.20.154',
        "server_port": 9999,
    }

    server = ServerSocket(parametros)
