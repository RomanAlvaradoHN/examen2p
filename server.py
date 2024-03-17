import socket
import threading
import json
import datetime
import os

############################################################################
#SOCKET SERVER
############################################################################
class ServerSocket:

    #PUESTA EN MARCHA DEL SOCKET SERVIDOR --------------------------------
    def __init__(self, params):
        host = params["server_ip"]
        port = params["server_port"]
        self.utils = params["utils"]

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
                    trama = self.__desglosar_trama(data['trama'])
                    resp = self.__procesar_respuesta(trama)
                    client_socket.send(json.dumps(resp).encode("utf-8"))


                
        except BaseException as errorType:
            self.utils.error_handler(errorType)


    
    
    
    
    
    
    
    
    ############################################################################
    #CONTROLADOR DE TRAMAS
    ############################################################################
    def __desglosar_trama(trama):
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
        resp = {
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
                resp['pais'] = codigos_pais.get(codigo)
            else:
                resp['pais'] = 'País Desconocido'
        else:
            return {'estatus': 'rejected'}
            

        

        #Obtener edad -------------------------------------
        edad = trama[2:4]
        if edad.isnumeric():
            for categoria, rango in categoria_edad:
                if int(edad) in rango:
                    resp['edad'] = categoria
                    resp['anios'] = edad
                    break
        else:
            return {'estatus': 'rejected'}


        
        #Obtener genero -----------------------------------
        if trama[4] in genero:
            resp['genero'] = genero.get(trama[4])
        else:
            return {'estatus': 'rejected'}

        
        
        #Obtener fecha nacimiento -------------------------
        anio = trama[5:9]
        mes = trama[9:11]
        dia = trama[11:13]
        if anio.isnumeric() and mes.isnumeric() and dia.isnumeric():
            resp['fecha_nacimiento'] = datetime.datetime(anio, mes, dia)
        else:
            return {'estatus': 'rejected'}
        

        #Obtener nombre completo -------------------------
        resp["nombre"] = trama[13:].replace('-', ' ')


        return resp






    ############################################################################
    #CONTROLADOR DE RESPUESTAS
    ############################################################################
    def __procesar_respuesta(data):
        persona = ''
        obervacion = ''

        #determinando nivel de adultez ----------------------------------------
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

        
        #obervaciones ---------------------------------------------------------
        fnac = data["fecha_nacimiento"]
        currentdate = datetime.datetime.now()
        real_age = (currentdate.year - fnac.year)
        if real_age != date["anios"]:
            observacion = f"Sin embargo, observo que tu fecha de nacimiento ({fnac.strftime("%d-%m-%Y")}), no concuerda con tu edad de {data["anios"]} años."

        resp = f"Hola {data['nombre']}, veo que eres del país de {data['pais']} y tienes {data['anios']} años, lo que indica que eres {persona}. {obervacion}"


        return data.update({"response": resp})





############################################################################
#Manejador de errores de socket
############################################################################
class Utilities():
    def error_handler(self, e):
        msj = ""

        if(type(e) is KeyboardInterrupt):
            msj = "Script terminado por teclado"

        elif(type(e) is ValueError):
            msj = "Usuario abandonó"

        elif(type(e) is OSError):
            msj = "Direccion en uso. Utilize: ss -ltpn | grep [server_port]"

        elif(type(e) is ConnectionRefusedError):
            msj = "Conexion rechazada. Valide que el servidor este activo y a la escucha"

        elif(type(e) is ConnectionResetError):
            msj = "Cliente desconectado"
            
        elif(type(e) is ModuleNotFoundError):
            msj = "Error con la base de datos:\n{e}"

        else:
            msj = f"Error: {type(e)}\n{e}"

        self.clear_console()
        print(msj + "\n\n")
        exit()


    #Limpiar pantalla =====================================================
    def clear_console(self):
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux, Unix, macOS, POSIX
            os.system('clear')



############################################################################
#BLOQUE DE INICIO DE SCRIPT SERVER.PY
############################################################################
if __name__ == "__main__":

    parametros = {
        "server_ip": '172.31.20.154',
        "server_port": 9999,
        "utils": Utilities()
    }

    server = ServerSocket(parametros)
