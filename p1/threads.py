"""Pregunta 1
En siguiente Código describa como puede reconfigurar para que los hilos no afecten el incremento de 
la variable global y que vayan en secuencia. Realice los cambios en el Código para que se consuma 
respectando la sección critica, haga que el counter vaya del valor a 0.
"""
 
from threading import Thread, Lock
import time

# variables globales x y lock
x = 0
lock = Lock()


# Tarea que los hilos van a realizar
def TareaThread(quien):
    global lock
    global x
    
    for _ in range(100000):
        with lock: #<<<======== indicador de seccion crítica. (solo se permite 1 hilo a la vez)
            time.sleep(0.1)  #<<<==== espera a el loop for imprima valor actual de x
            x += 1



# creando hilos
Thread(name='hilo1', target=TareaThread, args=("hilo1", )).start()
Thread(name='hilo2', target=TareaThread, args=("hilo2", )).start()



if __name__ == "__main__":
    for i in range(10):
        time.sleep(0.1) #<<<==== espera a que uno de los hilos actualize el valor de x
        print("Iteraccion {0}: x = {1}".format(i, x))
