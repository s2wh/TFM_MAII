
# Comunicacion
import socket
import pickle
import struct
# Hilos
from threading import Thread
# Imagen
import cv2
import numpy as np
# Interfaz
from tkinter import *
from tkinter import messagebox
# Otras librerías
from functools import partial
import sys
import time

print('numpy ', np.__version__)
print('opencv', cv2.__version__)

# ------------------------------------------------------------------------
# INTERFAZ
# ------------------------------------------------------------------------
root = Tk()
root.title("Stereopi sensor interface")

show_window_A = False
show_window_B = False
show_window_C = False
show_window_D = False

def exitApp():
	answer = messagebox.askquestion("Exit", "Do you want to exit?")
	if answer == "yes":
		root.destroy()
        
def appInfo():
	pass

def tryDisconnection():
    root.destroy()
        
def tryConnection():	    
    print("Arrancando hilos de comunicacion...")
    t_modo_A.start()
    t_modo_B.start()    
    t_modo_C.start()
    t_modo_D.start()
    t_modo_B_aux.start()
	
def sensorMode_A():
    global show_window_A      
    if show_window_A == True:         
         show_window_A = False
         txt.insert(END, "\n" + "Modo A dectivado")
    else:        
        show_window_A = True
        txt.insert(END, "\n" + "Modo A activado")
    print("show_window_A", show_window_A)
     
def sensorMode_B():
    global show_window_B      
    if show_window_B == True:        
         show_window_B = False
         txt.insert(END, "\n" + "Modo B deactivado")
    else:        
        show_window_B = True
        txt.insert(END, "\n" + "Modo B activado")
    print("show_window_B", show_window_B)
    
def sensorMode_C():
    global show_window_C      
    if show_window_C == True:         
         show_window_C = False
         txt.insert(END, "\n" + "Modo C dectivado")
    else:        
        show_window_C = True
        txt.insert(END, "\n" + "Modo C activado")
    print("show_window_C", show_window_C)

def sensorMode_D():
    global show_window_D      
    if show_window_D == True:         
         show_window_D = False
         txt.insert(END, "\n" + "Modo D dectivado")
    else:        
        show_window_D = True
        txt.insert(END, "\n" + "Modo D activado")
    print("show_window_D", show_window_D)

# BARRA DE MENU ---------------------------------------------------
barMenu = Menu(root)
root.config(menu=barMenu, width=600, height=600)
menuFile = Menu(barMenu, tearoff=0)
menuFile.add_command(label="Exit", command=exitApp)
menuConnection = Menu(barMenu, tearoff=0)
menuConnection.add_command(label="Connect")
menuConnection.add_command(label="Dissconet")
menuInfo = Menu(barMenu, tearoff=0)
menuInfo.add_command(label="Info", command=appInfo)
barMenu.add_cascade(label="File", menu=menuFile)
barMenu.add_cascade(label="Connection", menu=menuConnection)
barMenu.add_cascade(label="Info", menu=menuInfo)
# CORE ------------------------------------------------------------
myFrame = Frame(root, width=600, height=600)
myFrame.pack()
# TEXTO -----------------------------------------------------------
TITLE_COLOR = "#000000"	#EAECEE"
FONT = "Helvetica 14"
myText = Label(myFrame, fg=TITLE_COLOR, font=FONT, text="\n\nSTEREOPI SENSOR INTERFACE\n\n")
myText.grid(row=0, column=0, columnspan=4, padx=0, pady=0)
# BOTONES ---------------------------------------------------------
connectButton = Button(myFrame, text="Connect", command=tryConnection)
connectButton.grid(row=1, column=1, padx=10, pady=25)
disconnectButton = Button(myFrame, text="Close Program", command=tryDisconnection)
disconnectButton.grid(row=1, column=2, padx=10, pady=25)
mode1Button = Button(myFrame, text="MODO A", command=sensorMode_A)
mode1Button.grid(row=2, column=0, padx=10, pady=10)
mode2Button = Button(myFrame, text="MODO B", command=sensorMode_B)
mode2Button.grid(row=2, column=1, padx=10, pady=10)
mode3Button = Button(myFrame, text="MODO C", command=sensorMode_C)
mode3Button.grid(row=2, column=2, padx=10, pady=10)
mode4Button = Button(myFrame, text="MODO D", command=sensorMode_D)
mode4Button.grid(row=2, column=3, padx=10, pady=10)
# CUADRO DE TEXTO --------------------------------------------------
BG_GRAY = "#ABB2B9"
BG_COLOR = "#ffffff"	#17202A"
TEXT_COLOR = "#000000"	#EAECEE"
FONT = "Helvetica 10"
txt = Text(myFrame, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, width=60, height=10)
txt.grid(row=3, column=0, columnspan=4, padx=10, pady=10)
scrollbar = Scrollbar(txt)
scrollbar.place(relheight=1, relx=0.974)

# ------------------------------------------------------------------------
#   COMUNICACION
# ------------------------------------------------------------------------
# Client socket
host_ip = "192.168.1.43"    # Raspy
port = 10050    # Port to listen on (non-privileged ports are > 1023)
portA = port +1
portB = port +2
portC = port +3
portD = port +4
portB_aux = port +5

def thread_modo_A():
    _port = portA
    print("portA:", _port)
    # create an INET, STREAMing socket : 
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # now connect to the web server on the specified port number
    client_socket.connect((host_ip,_port)) 
    print("Conectado (A): " + str(host_ip) + ":" + str(_port))
    txt.insert(END, "\n" + "Conectado modo A")
    #'b' or 'B 'produces an instance of the bytes type instead of the str type used in handling binary data from network connections
    data = b""
    # Q: unsigned long long integer(8 bytes)
    payload_size = struct.calcsize("Q")
    # Flag de estado de la ventana
    is_window_A_open = False

    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4*1024)
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += client_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)

        if show_window_A == True:  
            is_window_A_open = True          
            cv2.imshow("Receiving (A)...",frame)
            key = cv2.waitKey(10) 
            if key  == 13:  #ENTER KEY
                break
        else:
             if is_window_A_open == True:          
                print("Destruimos ventana A")                
                cv2.destroyWindow('Receiving (A)...')
                is_window_A_open = False
                print("Ventana A destruida")
    client_socket.close()


def thread_modo_B():
    _port = portB
    print("portB:", _port)
    # create an INET, STREAMing socket : 
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # now connect to the web server on the specified port number
    client_socket.connect((host_ip,_port)) 
    print("Conectado (B): " + str(host_ip) + ":" + str(_port))
    txt.insert(END, "\n" + "Conectado modo B")
    #'b' or 'B 'produces an instance of the bytes type instead of the str type used in handling binary data from network connections
    data = b""
    # Q: unsigned long long integer(8 bytes)
    payload_size = struct.calcsize("Q")
    # Flag de estado de la ventana
    is_window_B_open = False

    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4*1024)
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += client_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)

        if show_window_B == True:  
            is_window_B_open = True          
            cv2.imshow("Receiving (B)...",frame)
            key = cv2.waitKey(10) 
            if key  == 13:  #ENTER KEY
                break
        else:
             if is_window_B_open == True:          
                print("Destruimos ventana B")                
                cv2.destroyWindow('Receiving (B)...')
                is_window_B_open = False
                print("Ventana B destruida")
    client_socket.close()


def thread_modo_C():
    _port = portC
    print("portC:", _port)
    # create an INET, STREAMing socket : 
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # now connect to the web server on the specified port number
    client_socket.connect((host_ip,_port)) 
    print("Conectado (C): " + str(host_ip) + ":" + str(_port))
    txt.insert(END, "\n" + "Conectado modo C")
    #'b' or 'B 'produces an instance of the bytes type instead of the str type used in handling binary data from network connections
    data = b""
    # Q: unsigned long long integer(8 bytes)
    payload_size = struct.calcsize("Q")
    # Flag de estado de la ventana
    is_window_C_open = False

    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4*1024)
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += client_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)

        if show_window_C == True:  
            is_window_C_open = True          
            cv2.imshow("Receiving (C)...",frame)
            key = cv2.waitKey(10) 
            if key  == 13:  #ENTER KEY
                break
        else:
             if is_window_C_open == True:          
                print("Destruimos ventana C")                
                cv2.destroyWindow('Receiving (C)...')
                is_window_C_open = False
                print("Ventana C destruida")
    client_socket.close()


def thread_modo_D():
    _port = portD
    print("portD:", _port)
    # create an INET, STREAMing socket : 
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # now connect to the web server on the specified port number
    client_socket.connect((host_ip,_port)) 
    print("Conectado (D): " + str(host_ip) + ":" + str(_port))
    txt.insert(END, "\n" + "Conectado modo D")
    #'b' or 'B 'produces an instance of the bytes type instead of the str type used in handling binary data from network connections
    data = b""
    # Q: unsigned long long integer(8 bytes)
    payload_size = struct.calcsize("Q")
    # Flag de estado de la ventana
    is_window_D_open = False

    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4*1024)
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += client_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)

        if show_window_D == True:  
            is_window_D_open = True          
            cv2.imshow("Receiving (D)...",frame)
            key = cv2.waitKey(10) 
            if key  == 13:  #ENTER KEY
                break
        else:
             if is_window_D_open == True:          
                print("Destruimos ventana D")                
                cv2.destroyWindow('Receiving (D)...')
                is_window_D_open = False
                print("Ventana D destruida")
    client_socket.close()

def thread_modo_B_aux():
    _port = portB_aux
    print("portB_aux:", _port)
    # create an INET, STREAMing socket : 
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # now connect to the web server on the specified port number
    client_socket.connect((host_ip,_port)) 
    print("Conectado (B_aux): " + str(host_ip) + ":" + str(_port))
    #'b' or 'B 'produces an instance of the bytes type instead of the str type used in handling binary data from network connections
    data = b""
    # Q: unsigned long long integer(8 bytes)
    payload_size = struct.calcsize("Q")
    # Flag de estado de la ventana
    is_window_B_open = False

    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4*1024)
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += client_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)   
        matriz_prof = np.mean(frame)
        print("Valor medio profundidad: ", matriz_prof)
        print(type(matriz_prof))         
    client_socket.close()

# ------------------------------------------------------------------------
#   HILO PRINCIPAL
# ------------------------------------------------------------------------
def main_thread():
    print("Ejecutándose hilo principal vacio")
    while True:
        pass  
    
#---------------------------------------------------------------------------
# CONFIGURACION DE HILOS E INTERFAZ
#---------------------------------------------------------------------------
# Creación de los hilos
t_main = Thread(target = main_thread)
t_modo_A = Thread(target = thread_modo_A)
t_modo_B = Thread(target = thread_modo_B)
t_modo_C = Thread(target = thread_modo_C)
t_modo_D = Thread(target = thread_modo_D)
t_modo_B_aux = Thread(target = thread_modo_B_aux)
# Arranque del hilo principal
t_main.start()
# Inicio del loop
root.mainloop()