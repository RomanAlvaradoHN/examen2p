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
            client_socket_thread = threading.Thread(target = self.__client_sockets_listener)
            client_socket_thread.start()

            print("====================================================================")
            print(f"\n    Servidor escuchando en {host}:{port} \n")
            print("====================================================================")
        
        except BaseException as errorType:
            self.utils.error_handler(errorType)


    
    #CONTROLADOR DE NUEVOS SOCKET CLIENTE --------------------------------
    def __client_sockets_listener(self):
        try:
            while True:
                new_socket = self.server_socket.accept()

                print(f"New client connection from {new_socket[1][0]}")

                #Hilo para comunicacion de cada sockets cliente---------------
                client_operations_thread = threading.Thread(target = self.__operation_controller, args=[new_socket])
                client_operations_thread.start()

        except BaseException as errorType:
            self.utils.error_handler(errorType)






    #ORQUESTADOR DE OPERACIONES ------------------------------------------
    def __operation_controller(self, new_socket):
        try:
            client_socket, client_address = new_socket

            while True:
                data = json.loads(client_socket.recv(1024).decode("utf-8"))

                if data["operacion"] == "consultar-trama":
                    resp = self.__procesar_respuesta(data['trama'])
                    client_socket.send(json.dumps(resp).encode("utf-8"))


                
        except BaseException as errorType:
            self.utils.error_handler(errorType)









    ############################################################################
    #CONTROLADOR DE TRAMAS
    ############################################################################
    def __desglosar_trama(self, trama):
        trama = trama.strip().upper() #elimina espacios en blanco en los extremos y convete a mayusculas

        #Definicion de categorias, rangos y codigos -------
        codigos_pais = {
            "01": "Honduras",
            "02": "Costa Rica",
            "03": "Mexico"
        }
        
        categoria_edad = {
            "Menor de Edad": range(1, 19),
            "Adulto": range(19, 51),
            "Tercera Edad": range(51, 151)
        }

        genero = {
            "M": "Masculino",
            "F": "Femenino"
        }

        
        #Inicializar objeto respuesta ---------------------
        desgloce = {
            "estatus": "ok",
            "pais": '',
            "anios": '',
            "edad": '',
            "genero": '',
            "fecha_nacimiento": '',
            "nombre": ''
        }


        #Obtener pais -------------------------------------
        codigo = trama[:2]
        if codigo.isnumeric():
            if codigo in codigos_pais:
                desgloce['pais'] = codigos_pais.get(codigo)
            else:
                desgloce['pais'] = 'País Desconocido'
        else:
            return {'estatus': 'rejected'}
            

        

        #Obtener edad -------------------------------------
        edad = trama[2:4]
        if edad.isnumeric():
            for categoria, rango in categoria_edad.items():
                if int(edad) in rango:
                    desgloce['edad'] = categoria
                    desgloce['anios'] = edad
                    break
        else:
            return {'estatus': 'rejected'}


        
        #Obtener genero -----------------------------------
        if trama[4] in genero:
            desgloce['genero'] = genero.get(trama[4])
        else:
            return {'estatus': 'rejected'}

        
        
        #Obtener fecha nacimiento -------------------------
        anio = trama[5:9]
        mes = trama[9:11]
        dia = trama[11:13]
        if anio.isnumeric() and mes.isnumeric() and dia.isnumeric():
            anio = int(anio, 10)
            mes = int(mes, 10)
            dia = int(dia, 10)
            
            if (mes in range(1, 13)) and (dia in range(1,32)):
                desgloce['fecha_nacimiento'] = {'anio': anio, 'mes': mes, 'dia': dia}
            else:
                return {'estatus': 'rejected'}
        else:
            return {'estatus': 'rejected'}
        

        #Obtener nombre completo -------------------------
        desgloce["nombre"] = trama[13:].replace('-', ' ')


        return desgloce








    


    ############################################################################
    #CONTROLADOR DE RESPUESTAS
    ############################################################################
    def __procesar_respuesta(self, trama):
        data = self.__desglosar_trama(trama)

        if(not data['estatus'] == 'rejected'):
            
            #determinando nivel de adultez ----------------------------------------
            persona = ''

            if data['genero'] == 'Femenino' and data['edad'] == 'Menor de Edad':
                persona = "una niña menor de edad"

            elif data['genero'] == 'Masculino' and data['edad'] == 'Menor de Edad':
                persona = "un niño menor de edad"
            
            elif data['genero'] == 'Femenino' and data['edad'] == 'Adulto':
                persona = "una mujer adulta mayor de edad"

            elif data['genero'] == 'Masculino' and data['edad'] == 'Adulto':
                persona = "un hombre adulto mayor de edad"
            
            elif data['genero'] == 'Femenino' and data['edad'] == 'Tercera Edad':
                persona = "una señora de tercera edad"

            elif data['genero'] == 'Masculino' and data['edad'] == 'Tercera Edad':
                persona = "un señor de tercera edad"

            

            #definiendo mensaje ---------------------------------------------------
            msj = f"Hola {data['nombre']}, veo que eres del país de {data['pais']} y tienes {data['anios']} años, lo que indica que eres {persona}."


            #obervaciones (coherencia de edad)--------------------------------------
            aux = data["fecha_nacimiento"]
            fnac = datetime.date(aux['anio'], aux['mes'], aux['dia'])
            real_age = (datetime.date.today().year - aux['anio'])
        
            if real_age != data["anios"]:
                msj += f" Sin embargo, observo que tu fecha de nacimiento ({fnac.strftime('%d-%m-%Y')}), no concuerda con tu edad de {data['anios']} años."

            
            
            #añadir mensaje en la respuesta del cliente ----------------------------
            data.update({'response': msj})

        return data


    
    
    










############################################################################
#BLOQUE DE INICIO DE SCRIPT SERVER.PY
############################################################################
if __name__ == "__main__":

    parametros = {
        "server_ip": '172.31.20.154',
        "server_port": 9999,
    }

    server = ServerSocket(parametros)
