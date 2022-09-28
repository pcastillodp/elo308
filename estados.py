# coding=utf-8
import actuadores
import configuracion
import sensores
import conexion
import main
import time
import gl
import logging	#para crear el archivo que almacena los datos 
import threading    #hilos


def ciclo_de_inicio():
	if (gl.flag_udp):
		conexion.udp_recep() 
	gl.PID_theta = "MANUAL"
	gl.PID_vel = "MANUAL"
	gl.PID_d = "MANUAL"
	gl.error_ant_d[0]=0.0
	gl.integral_d[0]=0.0
	gl.error_ant_vel[0]=0.0
	gl.integral_vel[0]=0.0
	gl.error_ant_theta[0]=0.0
	gl.integral_theta[0]=0.0
	gl.Output_d=0.0
	gl.Output_vel=0.0
	gl.Output_theta=0.0
	#configuracion.d_ref = sensores.distancia()
	#gl.sp_vel = 0.0
	gl.Input_vel=0.0
	#configuracion.vel_ref=0.0
	actuadores.motor(0,0)
	configuracion.encoderD.write(0)   
	configuracion.encoderL.write(0)
	sensores.obtenerPosicion(1)
	gl.t_controlador=time.time()
	if (gl.flag_udp):
		conexion.udp_transm()
		if(gl.flag_debug_udp):
			print("se intenta mandar informacion udp")

def ciclo_de_calibracion():
	if(gl.flag_calibrar):
		sensores.calibrarSensores ()
	gl.calibrar = 0
	gl.parar = "no"
	
def ciclo_de_control():
	if (gl.flag_udp):
		conexion.udp_recep()
	gl.Input_d = sensores.distancia()

	if (gl.flag_robot != "L"):
		gl.error_d = gl.Input_d - configuracion.d_ref
	else:
		gl.error_d = 0

	sensores.velocidades()	
	sensores.curvaturaPista()

	if (gl.flag_control):
		gl.control = ((gl.curvatura_predecesor <= 0.01) and (gl.curvatura <= 0.01))
	
	if (gl.Output_vel<0):		#calcula entrada de PID angulo linea			
		gl.Input_theta=-1*sensores.obtenerPosicion(0)/configuracion.d2		#recorrido inverso
	else:
		gl.Input_theta= sensores.obtenerPosicion(1)/configuracion.d1		#recorrido hacia delante

	gl.PID_vel="AUTO"
	gl.PID_theta="AUTO"
	gl.PID_d="AUTO"
	
	if((abs(gl.error_d) >= gl.delta + 1) or (gl.flag_robot == "L")):
		gl.PID_theta="AUTO"
		gl.PID_vel="AUTO"
		if (gl.control):
			gl.PID_d="AUTO"
		else:
			gl.PID_d="MANUAL"
			gl.Output_vel = gl.vel_crucero
			gl.error_ant_d = [0.0]
			gl.integral_d = [gl.vel_crucero / gl.Ki_d - gl.error_d * 0.04]
		if (gl.flag_robot == "L"):
			gl.PID_d = "MANUAL"
			gl.Output_d = 0
			gl.error_ant_d = [0.0]
			gl.integral_d = [0.0]
			gl.error_d = 0

	if ((abs(gl.Input_vel) <= 6) and (abs(gl.Input_theta) <= 0.015) and (abs(gl.error_d)<gl.delta) and ((gl.sp_vel == 0) or gl.flag_robot != "L")):
		gl.PID_d="MANUAL"
		gl.PID_vel="MANUAL"
		gl.PID_theta="MANUAL"
		gl.Output_d = 0
		gl.Output_vel = 0
		gl.Output_theta = 0
		gl.error_ant_d=[0.0]
		gl.integral_d=[0.0]
		gl.error_ant_vel=[0.0]
		gl.integral_vel=[0.0]
		gl.error_ant_theta=[0.0]
		gl.integral_theta=[0.0]
	
	if (gl.flag_udp):
		conexion.udp_transm()

	gl.t_actual = time.time() - gl.t_controlador
	if (gl.t_actual >= 0.04):							#se activa cada 40 ms
		if(gl.flag_saturacion_predecesor):
			gl.Output_d=calculoPIDd(gl.Input_d, configuracion.d_ref, gl.error_ant_d, gl.integral_d, gl.Kp_d, gl.Ki_d, gl.Kd_d, configuracion.sat_d, gl.PID_d, gl.Output_d, "INVERSO")
		else:
			gl.Output_d=calculoPIDd(gl.Input_d, configuracion.d_ref, gl.error_ant_d, gl.integral_d, gl.Kp_d, gl.Ki_d, gl.Kd_d, configuracion.sat_d, gl.PID_d, gl.Output_d, "INVERSO")
		if (gl.flag_robot == "L"):
			configuracion.vel_ref=gl.sp_vel
		else:
			configuracion.vel_ref=gl.Output_d
		gl.Output_vel=calculoPID(gl.Input_vel, configuracion.vel_ref, gl.error_ant_vel, gl.integral_vel, gl.Kp_vel, gl.Ki_vel, gl.Kd_vel, configuracion.sat_vel, gl.PID_vel, gl.Output_vel, "DIRECTO")
		gl.Output_theta=calculoPID(gl.Input_theta, configuracion.theta_ref, gl.error_ant_theta, gl.integral_theta, gl.Kp_theta, gl.Ki_theta, gl.Kd_theta, configuracion.sat_theta, gl.PID_theta, gl.Output_theta, "DIRECTO")

		if(gl.flag_udp):
			conexion.udp_monitor()
		gl.t_controlador=time.time()

	
	if (gl.t_actual >= 0.05):							#se activa cada 0.5s
		if (gl.flag_debug):
			print("\n*****VELOCIDAD	**")
			print("Input: " + str(gl.Input_vel))
			print("ref: " + str(configuracion.vel_ref) + " sp_vel: " + str(gl.sp_vel))
			print("error_ant: " + str(gl.error_ant_vel[0]))
			print("Output: " + str(gl.Output_vel))
			print("KP : " + str(gl.Kp_vel) + " KI: " +  str(gl.Ki_vel) + " KD: "+  str(gl.Ki_vel))
			print("\n******THETA	**")
			print("Input: " + str(gl.Input_theta))
			print("ref: " + str(configuracion.theta_ref))
			print("error_ant: " + str(gl.error_ant_theta[0]))
			print("Output: " + str(gl.Output_theta))
			print("KP : " + str(gl.Kp_theta) + " KI: " +  str(gl.Ki_theta) + " KD: "+  str(gl.Ki_theta))
			print("\n*****DISTANCIA	**")
			print("Input: " + str(gl.Input_d))
			print("ref: " + str(configuracion.d_ref))
			print("error_ant: " + str(gl.error_ant_d[0]))
			print("Output: " + str(gl.Output_d))
			print("KP : " + str(gl.Kp_d) + " KI: " +  str(gl.Ki_d) + " KD: "+  str(gl.Kd_d))
			print("\n*****CURVATURA**")
			print("recta: " + str(gl.recta) + " curvatura: " + str(gl.curvatura))
			print("parar: " + str(gl.parar))
			print("***")
		
		if(gl.flag_logger):
			logging.info("velocidad: " + str(gl.Input_vel))
			logging.info("theta: " + str(gl.Input_theta))
			logging.info("distancia: " + str(gl.Input_d))
	
	#actuadores.motor(gl.Output_vel - gl.Output_theta - gl.Output_d, gl.Output_vel + gl.Output_theta + gl.Output_d)
	actuadores.motor(gl.Output_vel - gl.Output_theta , gl.Output_vel + gl.Output_theta)
	

def calculoPID (y, ref, error_ant, error_integral, kp, ki, kd, limite, MODO, out_manual, direccion):
	if (MODO == "MANUAL"):
		return out_manual
	
	elif (MODO == "AUTO"):
		if(direccion=="DIRECTO"):
			error=ref-y
		elif(direccion =="INVERSO"):
			error=y-ref
		error_integral[0] = error_integral[0] + error*gl.t_actual
		if(error_integral[0] * ki > limite):
			error_integral[0] = limite /ki
		elif(ki*error_integral[0] < -limite):
			error_integral[0] = -limite /ki
		u=kp*error + error_integral[0]*ki + kd*(error-error_ant[0] )/(gl.t_actual)
		if (gl.flag_debug):
			print("u: " + str(u))
		error_ant[0] = error

		if(u>limite):
			return limite
		elif (u<-limite):
			return -limite
		else:
			return u

def calculoPIDd (y, ref, error_ant, error_integral, kp, ki, kd, limite, MODO, out_manual, direccion):
	if (MODO == "MANUAL"):
		return out_manual
	
	elif (MODO == "AUTO"):
		if(direccion=="DIRECTO"):
			error=ref-y
		elif(direccion =="INVERSO"):
			error=y-ref
		error_integral[0] = error_integral[0] + error*gl.t_actual
		if(error_integral[0] * ki > limite):
			error_integral[0] = limite /ki
		elif(ki*error_integral[0] < -limite):
			error_integral[0] = -limite /ki
		u=kp*error + error_integral[0]*ki + kd*(error-error_ant[0] )/(gl.t_actual)
		if (gl.flag_debug):
			print("u: " + str(u))
		error_ant[0] = error

		if(u> (limite * 1.1 + 1)):
			return limite * 1.1 + 1
		elif (u< (limite * 0.9 - 1)):
			return limite * 0.9 - 1
		else:
			return u
