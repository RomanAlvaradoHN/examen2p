import socket
import threading
import json
import os
from utilities import Utilities





############################################################################
#CONTROL PRINCIPAL
############################################################################
class ControlPrincipal():
    def __init__(self, params):
        self.__sockt = params["sockt"]
        self.__utils = Utilities()
    
        self.__utils.clear_console()
        self.nombre = input("Ingrese su nombre: ")
        self.__utils.clear_console()
        print(f"Hello {self.nombre}, wellcome to Socket Messenger\n--------------------------------------------------")
       
        #Nuevo hilo para enviar mensajes del cliente ---------------------
        threading.Thread(name='user_messages', target=self.__user_messages).start()

        #Nuevo hilo para manejar las respuesta del servidor --------------
        threading.Thread(name='server_responses', target=self.__server_responses).start()

        

    
    #control de mensajes que envía del usuario ----------------------------
    def __user_messages(self):    
        while True:
            msj = input()
            
            if (msj.lower() == 'exit'):
                
                break

            #with self.__sockt.lock:
            self.__sockt.server_response = None

            self.__sockt.send(
                json.dumps({
                    'operacion': 'new_message',
                    'msg': (self.nombre + ': ' + msj)
                })
            )

    
    
    #control de respuestas del servidor ----------------------------------
    def __server_responses(self):
        while True:
            if(not self.__sockt.server_response): continue

            print(self.__sockt.server_response['message'])

            self.__sockt.server_response = None










############################################################################
#SOCKET CLIENTE
############################################################################
class ClientSocket():
    
    #PUESTA EN MARCHA DEL SOCKET CLIENTE ---------------------------------
    def __init__(self, params):
        self.__server_ip = params["server_ip"]
        self.__server_port = params["server_port"]
        self.__utils = Utilities()
        
        self.lock = threading.Lock()
        self.server_response = None

        try:
            self.__utils.clear_console()
            self.__sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
            self.__sockt.connect((self.__server_ip, self.__server_port))

            threading.Thread(name='th_client_socket_receiver', target=self.receive).start()

            print("===============================================================")
            print(f"\nSocket Cliente Establecido:\nhost: {self.__server_ip}\nport: {self.__server_port}\n")
            print("===============================================================")

        except BaseException as errorType: 
            self.__utils.error_handler(errorType)
            self.__socket.close()

    
    
    
    #ENVIO DE MENSAJES A SOCKET SERVIDOR ---------------------------------
    def send(self, message):
        self.__sockt.send(message.encode("utf-8"))
    
    
    
    
    #RECEPCION DE MENSAJES DEL SOCKET SERVIDOR ---------------------------
    def receive(self):
        while True:
            self.server_response = json.loads(self.__sockt.recv(1024).decode("utf-8"))










############################################################################
#BLOQUE DE INICIO DE SCRIPT LOGIN.PY
############################################################################
parametros = {
    "sockt": ClientSocket({
        "server_ip": "ec2-13-59-197-55.us-east-2.compute.amazonaws.com",
        "server_port": 9999,
    })
}

user = ControlPrincipal(parametros)


