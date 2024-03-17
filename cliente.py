import socket
import threading
import tkinter as tk
from tkinter import messagebox
import json


############################################################################
#CONSTRUCCION DE LA VENTANA
############################################################################
class Ventana():
    def __init__(self, params):
        self.sockt = params["sockt"]
        
        self.plogin = tk.Tk()
        self.plogin.title("Login")
        self.plogin.geometry("650x350")


        fuente = ("Arial Black", 12)

        lbl_trama = tk.Label(self.plogin, text="Ingrese Trama:", font=fuente, bg=colorFondo)
        lbl_trama.pack()

        self.entry_trama = tk.Entry(self.plogin, font=fuente)
        self.entry_trama.pack()


        boton_ingresar = tk.Button(self.plogin, text="Enviar", command=self.validar_trama, font=fuente, bg='limegreen', fg='white', bd=0)
        boton_ingresar.pack(pady=10)

        self.plogin.mainloop()

    

    #ACCION DE BOTON LOGIN -----------------------------------------------
    def validar_trama(self):
        self.sockt.server_response = None

        self.sockt.send(
            json.dumps({
                "operacion": "consultar-trama",
                "trama": self.entry_trama.get(),
            })            
        )

        while True:
            if not self.sockt.server_response: pass
            else:
                resp = json.loads(self.sockt.server_response)

                if resp["estatus"] != "rejected":
                    messagebox.showinfo("Respuesta", resp["response"])

                else:
                    messagebox.showwarning("Error:", "Trama rechazada")
                    break








############################################################################
#SOCKET CLIENTE
############################################################################
class ClientSocket():
    
    #PUESTA EN MARCHA DEL SOCKET CLIENTE ---------------------------------
    def __init__(self, params):
        server_ip = params["server_ip"]
        server_port = params["server_port"]
        self.utils = params["utils"]
        
        self.server_response = None


        try:
            self.utils.clear_console()
            self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
            self.sockt.connect((server_ip, server_port))
            
            #Nuevo hilo para escuchar al servidor-------------------------
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()            
            
            print("===============================================================")
            print(f"\nSocket Cliente Establecido:\nhost: {server_ip}\nport: {server_port}\n")
            print("===============================================================")

        except BaseException as errorType: 
            self.utils.error_handler(errorType)
            self.server_socket.close()

    #ENVIO DE MENSAJES A SOCKET SERVIDOR ---------------------------------
    def send(self, message):
        self.sockt.send(message.encode("utf-8"))
    
    #RECEPCION DE MENSAJES DEL SOCKET SERVIDOR ---------------------------
    def receive(self):
        while True:
            self.server_response = self.sockt.recv(1024).decode("utf-8")








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
#BLOQUE DE INICIO DE SCRIPT LOGIN.PY
############################################################################
parametros = {
    "sockt": ClientSocket({
        "server_ip": "ec2-3-23-131-140.us-east-2.compute.amazonaws.com",
        "server_port": 9999
    })
}

user = Ventana(parametros)


