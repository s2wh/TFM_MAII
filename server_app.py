
# Comunicacion
import socket
import pickle
import struct
# import imutils
# Hilos
from threading import Thread
# StereoPi
from picamera import PiCamera
import time
import cv2
import numpy as np
import json
from stereovision.calibration import StereoCalibrator
from stereovision.calibration import StereoCalibration
from datetime import datetime

print(f"numpy  {np.__version__}.")
print(f"OpenCV {cv2.__version__}.")

#----------------------------------------------------------------------------
# STEREOPI
#----------------------------------------------------------------------------
# Depth map default preset
SWS = 5
PFS = 5
PFC = 29
MDS = -30
NOD = 160
TTH = 100
UR = 10
SR = 14
SPWS = 100
focal_distance = 2571
dist_centros_opticos = 6.54

# Camera settimgs
cam_width = 1280
cam_height = 480

# Final image capture settings
scale_ratio = 0.5

# Camera resolution height must be dividable by 16, and width by 32
cam_width = int((cam_width+31)/32)*32
cam_height = int((cam_height+15)/16)*16
print ("Used camera resolution: "+str(cam_width)+" x "+str(cam_height))

# Buffer for captured image settings
img_width = int (cam_width * scale_ratio)
img_height = int (cam_height * scale_ratio)
capture = np.zeros((img_height, img_width, 4), dtype=np.uint8)
print ("Scaled image resolution: "+str(img_width)+" x "+str(img_height))

# Initialize the camera
camera = PiCamera(stereo_mode='side-by-side',stereo_decimate=False)
camera.resolution=(cam_width, cam_height)
camera.framerate = 20    #20 original
camera.hflip = True

# Implementing calibration data
print('Read calibration data and rectifying stereo pair...')
calibration = StereoCalibration(input_folder='calib_result')

disparity = np.zeros((img_width, img_height), np.uint8)
disparity_global = np.ones((img_width, img_height), np.uint8)
sbm = cv2.StereoBM_create(numDisparities=0, blockSize=21)

def stereo_depth_map(rectified_pair):
    global disparity_global    
    dmLeft = rectified_pair[0]
    dmRight = rectified_pair[1]
    disparity = sbm.compute(dmLeft, dmRight)
    local_max = disparity.max()
    local_min = disparity.min()
    disparity_global = np.copy(disparity)
    disparity_grayscale = (disparity-local_min)*(65535.0/(local_max-local_min))
    disparity_fixtype = cv2.convertScaleAbs(disparity_grayscale, alpha=(255.0/65535.0))
    disparity_color = cv2.applyColorMap(disparity_fixtype, cv2.COLORMAP_JET)
    #cv2.imshow("Image", disparity_color)
    key = cv2.waitKey(1) & 0xFF   
    if key == ord("q"):
        quit();
    return disparity_color

def load_map_settings( fName ):
    global SWS, PFS, PFC, MDS, NOD, TTH, UR, SR, SPWS, loading_settings
    print('Loading parameters from file...')
    f=open(fName, 'r')
    data = json.load(f)
    SWS=data['SADWindowSize']
    PFS=data['preFilterSize']
    PFC=data['preFilterCap']
    MDS=data['minDisparity']
    NOD=data['numberOfDisparities']
    TTH=data['textureThreshold']
    UR=data['uniquenessRatio']
    SR=data['speckleRange']
    SPWS=data['speckleWindowSize']    
    #sbm.setSADWindowSize(SWS)
    sbm.setPreFilterType(1)
    sbm.setPreFilterSize(PFS)
    sbm.setPreFilterCap(PFC)
    sbm.setMinDisparity(MDS)
    sbm.setNumDisparities(NOD)
    sbm.setTextureThreshold(TTH)
    sbm.setUniquenessRatio(UR)
    sbm.setSpeckleRange(SR)
    sbm.setSpeckleWindowSize(SPWS)
    f.close()
    print ('Parameters loaded from file '+fName)

load_map_settings ("3dmap_set.txt")

#----------------------------------------------------------------------------
# COMUNICACION
#----------------------------------------------------------------------------
frame_height = img_height
frame_width = int(img_width/2)
frameA = np.zeros((frame_height, frame_width, 4), dtype=np.uint8)
frameB = np.zeros((frame_height, frame_width, 4), dtype=np.uint8)
frameC = np.zeros((frame_height, frame_width, 4), dtype=np.uint8)
frameD = np.zeros((frame_height, frame_width, 4), dtype=np.uint8)
print("frame_height: ", frame_height)
print("frame_width:  ", frame_width)

host_ip = "192.168.1.43"    #Raspy
port = 10050
portA = port +1
portB = port +2
portC = port +3
portD = port +4
portB_aux = port +5

def communication_thread_A():
    # Server socket
    # create an INET, STREAMing socket
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_name  = socket.gethostname()
    print('HOST (A) IP:',host_ip)
    print('HOST (A) PORT:',portA)
    socket_address = (host_ip,portA)
    print('Socket (A) created')
    #bind the socket to the host. 
    #The values passed to bind() depend on the address family of the socket
    server_socket.bind(socket_address)
    print('Socket (A) bind complete')
    #listen() enables a server to accept() connections
    #listen() has a backlog parameter. 
    #It specifies the number of unaccepted connections that the system will allow before refusing new connections.
    server_socket.listen(5)
    print('Socket (A) now listening')

    while True:
        client_socket,addr = server_socket.accept()
        print('Connection (A) from:',addr)
        if client_socket:            
            while(True):                
                a = pickle.dumps(frameA)
                message = struct.pack("Q",len(a))+a
                client_socket.sendall(message)                


def communication_thread_B():
    # Server socket
    # create an INET, STREAMing socket
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_name  = socket.gethostname()
    print('HOST (B) IP:',host_ip)
    print('HOST (B) PORT:',portB)
    socket_address = (host_ip,portB)
    print('Socket (B) created')
    #bind the socket to the host. 
    #The values passed to bind() depend on the address family of the socket
    server_socket.bind(socket_address)
    print('Socket (B) bind complete')
    #listen() enables a server to accept() connections
    #listen() has a backlog parameter. 
    #It specifies the number of unaccepted connections that the system will allow before refusing new connections.
    server_socket.listen(5)
    print('Socket (B) now listening')

    while True:
        client_socket,addr = server_socket.accept()
        print('Connection (B) from:',addr)
        if client_socket:            
            while(True):                
                a = pickle.dumps(frameB)
                message = struct.pack("Q",len(a))+a
                client_socket.sendall(message)


def communication_thread_C():
    # Server socket
    # create an INET, STREAMing socket
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_name  = socket.gethostname()
    print('HOST (C) IP:',host_ip)
    print('HOST (C) PORT:',portC)
    socket_address = (host_ip,portC)
    print('Socket (C) created')
    #bind the socket to the host. 
    #The values passed to bind() depend on the address family of the socket
    server_socket.bind(socket_address)
    print('Socket (C) bind complete')
    #listen() enables a server to accept() connections
    #listen() has a backlog parameter. 
    #It specifies the number of unaccepted connections that the system will allow before refusing new connections.
    server_socket.listen(5)
    print('Socket (C) now listening')

    while True:
        client_socket,addr = server_socket.accept()
        print('Connection (C) from:',addr)
        if client_socket:            
            while(True):                
                a = pickle.dumps(frameC)
                message = struct.pack("Q",len(a))+a
                client_socket.sendall(message)


def communication_thread_D():
    # Server socket
    # create an INET, STREAMing socket
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_name  = socket.gethostname()
    print('HOST (D) IP:',host_ip)
    print('HOST (D) PORT:',portD)
    socket_address = (host_ip,portD)
    print('Socket (D) created')
    #bind the socket to the host. 
    #The values passed to bind() depend on the address family of the socket
    server_socket.bind(socket_address)
    print('Socket (D) bind complete')
    #listen() enables a server to accept() connections
    #listen() has a backlog parameter. 
    #It specifies the number of unaccepted connections that the system will allow before refusing new connections.
    server_socket.listen(5)
    print('Socket (D) now listening')

    while True:
        client_socket,addr = server_socket.accept()
        print('Connection (D) from:',addr)
        if client_socket:            
            while(True):                
                a = pickle.dumps(frameD)
                message = struct.pack("Q",len(a))+a
                client_socket.sendall(message) 


def communication_thread_B_aux():
    # Server socket
    # create an INET, STREAMing socket
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_name  = socket.gethostname()
    print('HOST (B_aux) IP:',host_ip)
    print('HOST (B_aux) PORT:',portB_aux)
    socket_address = (host_ip,portB_aux)
    print('Socket (B_aux) created')
    #bind the socket to the host. 
    #The values passed to bind() depend on the address family of the socket
    server_socket.bind(socket_address)
    print('Socket (B_aux) bind complete')
    #listen() enables a server to accept() connections
    #listen() has a backlog parameter. 
    #It specifies the number of unaccepted connections that the system will allow before refusing new connections.
    server_socket.listen(5)
    print('Socket (B_aux) now listening')

    while True:
        client_socket,addr = server_socket.accept()
        print('Connection (B_aux) from:',addr)
        if client_socket:            
            while(True):                
                a = pickle.dumps(frameB_aux)
                message = struct.pack("Q",len(a))+a
                client_socket.sendall(message)

#----------------------------------------------------------------------------
# PROCESADO DE IMAGEN
#----------------------------------------------------------------------------
def main_thread():        
    global disparity_global
    global frameA
    global frameB
    global frameC
    global frameD
    global frameB_aux
    t_communication_A.start()
    t_communication_B.start()
    t_communication_C.start()
    t_communication_D.start()
    t_communication_B_aux.start()
    
    while(True):
        for frame in camera.capture_continuous(capture, format="bgra", use_video_port=True, resize=(img_width,img_height)):
            t1 = datetime.now()
            #Guardamos el frame en dos variables auxiliares
            pair_img_color = frame
            pair_img = cv2.cvtColor (frame, cv2.COLOR_BGR2GRAY)
            
            #Rectificamos imágenes
            imgLeft_color = pair_img_color [0:img_height,0:int(img_width/2)] #Y+H and X+W
            imgRight_color = pair_img_color [0:img_height,int(img_width/2):img_width] #Y+H and X+W
            imgLeft = pair_img [0:img_height,0:int(img_width/2)] #Y+H and X+W
            imgRight = pair_img [0:img_height,int(img_width/2):img_width] #Y+H and X+W
            
            #Rectificamos imágenes
            rectified_pair = calibration.rectify((imgLeft, imgRight))
            rectified_pair_aux = np.copy(rectified_pair)
            
            #Calculamos disparidad (disparity_global) y mapa de profundidad (disparity_depth)
            disparity_depth = stereo_depth_map(rectified_pair)        

            #Normalización a valores positivos de la disparidad
            local_min = disparity_global.min()
            local_max = disparity_global.max()
            disparity_positive_values = (disparity_global - local_min)*(local_max /(local_max - local_min)) + 1 #sumamos una unidad para evitar divisiones entre cero 
            
            #Cálculo de la matriz de profundidad
            aux_calc = focal_distance * dist_centros_opticos
            matriz_profundidad = np.divide(aux_calc, disparity_positive_values)
            
            #Cálculo de la profundidad de los puntos centrales (10x10)
            sub_matriz = matriz_profundidad[155:166][115:126]
            media_prof_central = np.mean(sub_matriz)
                        
            #Texto en imagen
            aux_frame = np.copy(rectified_pair_aux[0])
            texto = str(media_prof_central)
            if media_prof_central < 60:
                texto = "MIN"
            if media_prof_central > 300:
                texto = "MAX"               
            ubicacion = (160,120)
            font = cv2.FONT_HERSHEY_TRIPLEX
            tamLetra = 1
            colorLetra = (255,255,255)
            grosorLetra = 1
            cv2.putText(aux_frame, texto, ubicacion, font, tamLetra, colorLetra, grosorLetra)

            #Generación de imágenes para cada modo
            frameA = imgLeft_color
            frameB = rectified_pair[0]
            frameC = aux_frame
            frameD = disparity_depth
            frameB_aux = disparity_positive_values
            
            t2 = datetime.now()
            # print ("DM build time: " + str(t2-t1))
   
#----------------------------------------------------------------------------
# CONFIGURACION DE HILOS
#----------------------------------------------------------------------------

# Create the shared queue and launch both threads
t_main              = Thread(target = main_thread)
t_communication_A   = Thread(target = communication_thread_A)
t_communication_B   = Thread(target = communication_thread_B)
t_communication_C   = Thread(target = communication_thread_C)
t_communication_D   = Thread(target = communication_thread_D)
t_communication_B_aux   = Thread(target = communication_thread_B_aux)
t_main.start()

