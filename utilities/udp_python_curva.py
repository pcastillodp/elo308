"""
_____________________________________________________
|   -Conexion de UDP con la base de datos en MySQL  |
|    -Crear archivo CSV                             |
|---------------------------------------------------|

"""
#Librerias
import sys
import pymysql
import csv
import socket
import datetime
#Ajustables
file_name = ".\\monitoreo4.csv"  # archivo csv

UDP_IP = "192.168.100.9" # ip del computador que recibe datos (mismo que el que corre este script)
UDP_PORT = 1234
#UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
#creacion de archivo CSV
texto = open(file_name,'w')
#estado = "T,"+String(Input_d)+","+String(d_ref)+","+String(vel_ref)+","+String(Input_vel)+","+String(Input_theta)+","+String(Output_d)+","+String(Output_vel)+","+String(Output_theta);
 
#texto.write('Timestamp,Robot,Delta_muestra,Input_d,d_ref,vel_ref,Input_vel,Input_theta,Output_d,Output_vel,Output_theta,curvatura,vel_crucero,curvatura_predecesor,control'+'\n')
texto.write('Timestamp,Robot,Input_vel, vel_ref, error_vel, Output_vel,kp_vel,ki_vel,kd_vel, Input_theta, theta_ref, error_theta, Output_theta,kp_theta,ki_theta,kd_theta,Input_d, d_ref, error_d, Output_d,kp_d,ki_d,kd_d, '+'\n')

texto.close()

while True:
    data, addr = sock.recvfrom(4096) # buffer size is 1024 byte
    testo = str(data.decode('utf-8'))
    texto = open(file_name,"a")
    texto.write(str(datetime.datetime.now()) + "," + testo +'\n')
    texto.close()
    print(testo)
    
