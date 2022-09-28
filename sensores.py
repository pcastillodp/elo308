# coding=utf-8
from cmath import pi
import configuracion
import actuadores
import gl

import Adafruit_ADS1x15
import smbus
import Encoder
import RPi.GPIO as GPIO
import VL53L0X
import time

i2c = smbus.SMBus(configuracion.channel)
adc = Adafruit_ADS1x15.ADS1115(busnum = 1)
tof = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=0x29)

v_r = [0.0]*5
v_l = [0.0]*5
s_r = [0.0]*5
s_l = [0.0]*5
a_s = 0.0
b_s = 0.0
c_s = 0.0
a_sl = 0.0
a_sr = 0.0
b_sl = 0.0
b_sr = 0.0
c_sl = 0.0
c_sr = 0.0
a_curvatura = 0.0
b_curvatura = 0.0
c_curvatura = 0.0

def calibrarSensores():		#calibrar sensores IR
	if(gl.flag_debug):
		print("calibrando")
	vcal = gl.velocidad_calibracion #velocidad del motor para la calibracion
	gl.maximo = [0]*16 
	gl.minimo = [32000]*16
	
	if(gl.flag_debug):
		print("Obteniendo maximos y minimos..")
	while(abs(configuracion.radioRueda*pi*(configuracion.encoderD.read()- configuracion.encoderL.read())*configuracion.N/(configuracion.CPR*configuracion.l))<4*pi):
		actuadores.motor(-vcal,vcal)
		if(gl.flag_debug):
			print(abs(configuracion.radioRueda*pi*(configuracion.encoderD.read()- configuracion.encoderL.read())*configuracion.N/(configuracion.CPR*configuracion.l)))

		for s in range(16):
			GPIO.output(configuracion.S0, s&0x01) # 0001
			GPIO.output(configuracion.S1, s&0x02) # 0010
			GPIO.output(configuracion.S2, s&0x04) # 0100
			GPIO.output(configuracion.S3, s&0x08) # 1000
			valor = adc.read_adc(0, gain=configuracion.GAIN)
			gl.maximo[s] = valor if (valor > gl.maximo[s]) else (gl.maximo[s])
			gl.minimo[s] = valor if (valor < gl.minimo[s]) else (gl.minimo[s])
			time.sleep(0.001)

	if(gl.flag_debug):	
		print("listo, ahora voy a volver a la linea")
	GPIO.output(configuracion.S0, 4&0x01) # para volver al centro de la linea
	GPIO.output(configuracion.S1, 4&0x02) 
	GPIO.output(configuracion.S2, 4&0x04) 
	GPIO.output(configuracion.S3, 4&0x08) 

	while(((1-2*configuracion.linea)*100*(adc.read_adc(0, gain=configuracion.GAIN) - gl.minimo[2]) / (gl.maximo[2]-gl.minimo[2]) + 100*configuracion.linea ) < 80 ):
		#print((1-2*configuracion.linea)*100*(adc.read_adc(0, gain=configuracion.GAIN) - minimo[2]) / (maximo[2]-minimo[2]) + 100*configuracion.linea )
		actuadores.motor(vcal,-vcal)

	actuadores.motor(0,0)

def configuracionSensorD():		#habilitar y configurar sensor de distancia
	tof.open()
	tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
	timing = tof.get_timing()
	if timing < 20000:
		timing = 20000

def distancia():				#mide la distancia 
	dist = (tof.get_distance()/10) - configuracion.offsetSensorD #en cm, se le resta el offset
	if (dist > configuracion.sat_d):	#se satura en sat_d
		dist=configuracion.sat_d
	if(abs(dist - configuracion.d_ref)<= 3*gl.varianzaD):
		gl.distFiltro = gl.distFiltro*(1 - gl.alphaD) + dist*gl.alphaD
	#falta quitarle que entrege un valor muy distinto al leido anteriormente
	return gl.distFiltro



	
def velocidades():	#calcula velocidades, y la entrada del controlador PID de velocidad
	gl.t_actual = time.time() - gl.t_svel	#tiempo transcurrido desde ultima actualizacion de calculo de velocidad en s
	if(gl.t_actual >= 0.01):	#cada 10 ms
		v_r[1]=v_r[0]
		v_r[2]=v_r[1]
		v_r[3]=v_r[2]
		v_r[4]=v_r[3]
		v_l[1]=v_l[0]
		v_l[2]=v_l[1]
		v_l[3]=v_l[2]
		v_l[4]=v_l[3]
		v_r[0]=(2*pi*configuracion.radioRueda*configuracion.encoderD.read()*configuracion.N)/(gl.t_actual*configuracion.CPR); # ENCODERS:28CPR---CAJA_REDUCTORA:100:1  [cm/s]
		v_l[0]=(2*pi*configuracion.radioRueda*configuracion.encoderL.read()*configuracion.N)/(gl.t_actual*configuracion.CPR); # ENCODERS:28CPR---CAJA_REDUCTORA:100:1  [cm/s]
		configuracion.encoderD.write(0)
		configuracion.encoderL.write(0)
		gl.t_svel = time.time()
	#curva=2.3333*abs(((0.9*(v_r[1]+v_r[2]+v_r[3]+v_r[4])/4) + 0.1*v_r[0])-((0.9*(v_l[1]+v_l[2]+v_l[3]+v_l[4])/4) + 0.1*v_l[0]))
	v_r[0]=(0.2*(v_r[1]+v_r[2]+v_r[3]+v_r[4])/4) + 0.8*v_r[0]	#filtra velocidades que se escapen
	v_l[0]=(0.2*(v_l[1]+v_l[2]+v_l[3]+v_l[4])/4) + 0.8*v_l[0]
	gl.Input_vel=0.5*(v_r[0]+v_l[0])*3 # [cm/s]	#promedio de velocidades actuales R y L
	#ang_vel=0.5*(v_r[0]-v_l[0])/configuracion.l
	#gl.t_actual = time.time() - gl.t_arco
	#s_l+=abs(v_l[0]*configuracion.t_actual)
	#s_r+=abs(v_r[0]*configuracion.t_actual)
	#gl.t_arco= time.time()
	#s=0.5*(s_r+s_l)
	#if(s<10 & configuracion.Input_vel<0.1):
	#	#radio_curva=0
	#	s_l=0
	#	s_r=0
	#elif(s>=10):
		#radio_curva=abs((0.5*(s_r-s_l))/(configuracion.l*s))
	#	s_l=0
	#	s_r=0

def obtenerPosicion (direccion):	#obtienela longitud de arco que existe entre la linea y el centro de los sensores, respecto al eje de giro
	sensorNormalizado = [0]*16
	inte =  [0]*16
	sum1 = 0
	area = 0
	if (direccion == 1):	#direccion 0:hacia atras 1:hacia delante
		for s in range(8):	#mido los sensores IR de delante
			GPIO.output(configuracion.S0, s&0x01) # 0001
			GPIO.output(configuracion.S1, s&0x02) # 0010
			GPIO.output(configuracion.S2, s&0x04) # 0100
			GPIO.output(configuracion.S3, s&0x08) # 1000
			sensorNormalizado[s] = ((1-2*configuracion.linea)*100*(adc.read_adc(0, gain=configuracion.GAIN)-gl.minimo[s])/(gl.maximo[s] -gl.minimo[s]))+100*configuracion.linea		#normaliza entre 0 a 100
			if (sensorNormalizado[s]<30):
				sensorNormalizado[s]=0
	else:
		for s in range(8):	#mido los sensores IR de atras
			GPIO.output(configuracion.S0, (s+8)&0x01) # 00010000
			GPIO.output(configuracion.S1, (s+8)&0x02) # 00100000
			GPIO.output(configuracion.S2, (s+8)&0x04) # 01000000
			GPIO.output(configuracion.S3, (s+8)&0x08) # 10000000
			sensorNormalizado[s] = ((1-2*configuracion.linea)*100*(adc.read_adc(0, gain=configuracion.GAIN)-gl.minimo[s+8])/(gl.maximo[s+8] -gl.minimo[s+8]))+100*configuracion.linea
			if (sensorNormalizado[s]<30):
				sensorNormalizado[s]=0
	for s in range(8):
		inte[s]=8*sensorNormalizado[s]-0.04*sensorNormalizado[s]*sensorNormalizado[s]  	#cambia el rango de 200 a 400 linealizando el comportamiento del sensor 
	
	sum1=-28*inte[0] - 20*inte[1] - 12*inte[2] - 4*inte[3] + 4*inte[4] + 12*inte[5] + 20*inte[6] + 28*inte[7]	#pondera las posiciones del sensor
	area=inte[0]+inte[1]+inte[2]+inte[3]+inte[4]+inte[5]+inte[6]+inte[7]
	if(area==0):	#ya no esta sobre la linea
		gl.parar = "si"
		return 0
	else:
		gl.parar = "no"
		return sum1/area #centroide, mientras mas cercano a 0 mas centrado en la linea

def curvaturaPista():
	global a_sl, a_sr, a_s, a_curvatura 
	global b_sl, b_sr, b_s, b_curvatura 
	global c_sl, c_sr, c_s, c_curvatura 
	gl.t_actual = time.time() - gl.t_arco
	if(gl.t_actual>=0.02):	#han transcurrido 20 ms
		a_sl += v_l[0]*gl.t_actual
		a_sr += v_r[0]*gl.t_actual
		b_sl += v_l[0]*gl.t_actual
		b_sr += v_r[0]*gl.t_actual
		c_sl += v_l[0]*gl.t_actual
		c_sr += v_r[0]*gl.t_actual
		gl.t_arco = time.time()
	a_s = (a_sr+a_sl)*0.5
	b_s = (b_sr+b_sl)*0.5
	c_s = (c_sr+c_sl)*0.5
	if(gl.Input_vel<0.1):
		a_curvatura = 0
		b_curvatura = 0
		c_curvatura = 0
		a_sl = 0
		a_sr = 0
		b_sl = 0
		b_sr = 0
		c_sl = 0
		c_sr = 0
	elif (a_s >= 3 and b_s>=10):
		b_curvatura = abs(((b_sr-b_sl)*0.5)/(configuracion.l*b_s))
		b_sl = 0
		b_sr = 0
	elif (a_s>=3 and a_s == b_s):
		b_sl=0
		b_sr=0
	elif (a_s>=6 and c_s>=10):
		c_curvatura = abs(((c_sr-c_sl)*0.5)/(configuracion.l*c_s))
		c_sl = 0
		c_sr = 0
	elif (a_s>=6 and a_s == c_s):
		c_sl=0
		c_sr=0
	elif (a_s>=10):
		a_curvatura = abs(((a_sr-a_sl)*0.5)/(configuracion.l*a_s))
		a_sl = 0
		a_sr = 0
	if(a_curvatura<0.01 and b_curvatura<0.01 and c_curvatura<0.01):
		gl.recta=1
	elif(a_curvatura>0.02 and b_curvatura>0.02 and c_curvatura>0.02):
		gl.recta=0
	if (gl.recta==1):
		if(a_curvatura>= b_curvatura and a_curvatura>= c_curvatura):
			gl.curvatura= a_curvatura
		elif(b_curvatura>= a_curvatura and b_curvatura>= c_curvatura):
			gl.curvatura= b_curvatura
		elif(c_curvatura>= a_curvatura and c_curvatura>= b_curvatura):
			gl.curvatura= c_curvatura
		else:
			gl.curvatura= a_curvatura
	else:
		if(a_curvatura< b_curvatura and a_curvatura< c_curvatura):
			gl.curvatura= a_curvatura
		elif(b_curvatura< a_curvatura and b_curvatura< c_curvatura):
			gl.curvatura= b_curvatura
		elif(c_curvatura< a_curvatura and c_curvatura< b_curvatura):
			gl.curvatura= c_curvatura
		else:
			gl.curvatura= a_curvatura


