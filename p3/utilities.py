import socket
import threading
import json
import os


############################################################################
#CONTROL DE EXCEPCIONES
############################################################################
class Utilities():

    #Manejador de errores de socket =======================================
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

        #self.clear_console()
        print(msj + "\n\n")
        exit()


    #Limpiar pantalla =====================================================
    def clear_console(self):
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux, Unix, macOS, POSIX
            os.system('clear')