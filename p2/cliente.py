import socket
import threading
import tkinter as tk
from tkinter import messagebox
import json
import os
from utilities import Utilities

############################################################################
#CONSTRUCCION DE LA VENTANA
############################################################################
class Ventana():
    def __init__(self, params):
        self.sockt = params["sockt"]
        
        self.plogin = tk.Tk()
        self.plogin.title("Examen 2p")
        self.plogin.geometry("650x350")
        colorFondo = "sky blue"
        self.plogin.configure(bg=colorFondo)
        fuente = ("Arial Black", 12)

        lbl_trama = tk.Label(self.plogin, text="Ingrese Trama:", font=fuente, bg=colorFondo)
        lbl_trama.pack()

        self.entry_trama = tk.Entry(self.plogin, font=fuente, width=50, justify='center')
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
                #print(resp)

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
        self.utils = Utilities()
        
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
#BLOQUE DE INICIO DE SCRIPT LOGIN.PY
############################################################################
parametros = {
    "sockt": ClientSocket({
        "server_ip": "ec2-18-224-165-170.us-east-2.compute.amazonaws.com",
        "server_port": 9999,
    })
}

user = Ventana(parametros)


