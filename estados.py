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
	#gl.d_ref = sensores.distancia()
	#gl.sp_vel = 0.0
	gl.Input_vel=0.0
	actuadores.motor(0,0)
	configuracion.encoderD.write(0)   
	configuracion.encoderL.write(0)
	sensores.obtenerPosicion(1)
	gl.t_controlador=time.time()

def ciclo_de_calibracion():
	if(gl.flag_calibrar):
		sensores.calibrarSensores ()
	gl.calibrar = 0
	gl.parar = "no"
	
def ciclo_de_control():
	gl.PID_vel="AUTO"
	gl.PID_theta="AUTO"
	gl.PID_d="AUTO"
	
	gl.Input_d = sensores.distancia()		#mide entrada de PID distancia
	sensores.velocidades()					#calcula entrada de PID velocidad
	sensores.curvaturaPista()				#revisa si está en una recta o curvatura

	if (gl.Output_vel<0):		#calcula entrada de PID angulo linea			
		gl.Input_theta=-1*sensores.obtenerPosicion(0)/configuracion.d2		#recorrido inverso
	else:
		gl.Input_theta= sensores.obtenerPosicion(1)/configuracion.d1		#recorrido hacia delante

	#if(abs(gl.error_d) >= gl.delta + 1):
	#	gl.PID_theta="AUTO"
	#	gl.PID_vel="AUTO"
	#	gl.PID_d="MANUAL"
	#	gl.Output_d=0
	#	gl.error_ant_d=0
	#	gl.integral_d=0
	#	gl.error_d=0



	#if (abs(gl.Input_vel) <= 6 & abs(gl.Input_theta) <= 0.015 & (abs(gl.error_d)<gl.delta)&(gl.sp_vel == 0)):
	#	gl.PID_d="MANUAL"
	#	gl.PID_vel="MANUAL"
	#	gl.PID_theta="MANUAL"
	#	gl.Output_d = 0
	#	gl.Output_vel = 0
	#	gl.Output_theta = 0
	#	gl.error_ant_d=0
	#	gl.integral_d=0
	#	gl.error_ant_vel=0
	#	gl.integral_vel=0
	#	gl.error_ant_theta=0
	#	gl.integral_theta=0

	gl.t_actual = time.time() - gl.t_controlador
	if (gl.t_actual >= 0.04):							#se activa cada 40 ms
		gl.Output_d=calculoPID(gl.Input_d, configuracion.d_ref, gl.error_ant_d, gl.integral_d, gl.Kp_d, gl.Ki_d, gl.Kd_d, configuracion.sat_d, gl.PID_d, gl.Output_d, "INVERSO")
		#gl.vel_ref=gl.Output_d*gl.sp_vel
		gl.Output_vel=calculoPID(gl.Input_vel, configuracion.vel_ref, gl.error_ant_vel, gl.integral_vel, gl.Kp_vel, gl.Ki_vel, gl.Kd_vel, configuracion.sat_vel, gl.PID_vel, gl.Output_vel, "DIRECTO")
		gl.Output_theta=calculoPID(gl.Input_theta, configuracion.theta_ref, gl.error_ant_theta, gl.integral_theta, gl.Kp_theta, gl.Ki_theta, gl.Kd_theta, configuracion.sat_theta, gl.PID_theta, gl.Output_theta, "DIRECTO")
		gl.t_controlador=time.time()
	
	if (gl.t_actual >= 0.05):							#se activa cada 0.5s
		if (gl.flag_debug):
			print("\n*****VELOCIDAD	**")
			print("Input: " + str(gl.Input_vel))
			print("ref: " + str(configuracion.vel_ref))
			print("error_ant: " + str(gl.error_ant_vel[0]))
			print("Output: " + str(gl.Output_vel))
			print("\n******THETA	**")
			print("Input: " + str(gl.Input_theta))
			print("ref: " + str(configuracion.theta_ref))
			print("error_ant: " + str(gl.error_ant_theta[0]))
			print("Output: " + str(gl.Output_theta))
			print("\n*****DISTANCIA	**")
			print("Input: " + str(gl.Input_d))
			print("ref: " + str(configuracion.d_ref))
			print("error_ant: " + str(gl.error_ant_d[0]))
			print("Output: " + str(gl.Output_d))
			print("***")
		
		if(gl.flag_logger):
			logging.info("velocidad: " + str(gl.Input_vel))
			logging.info("theta: " + str(gl.Input_theta))
			logging.info("distancia: " + str(gl.Input_d))

		if(gl.flag_ubidots):
			t2 = threading.Thread(target = conexion.publicar, args =("velocidad", gl.Input_vel) )
			t2.setDaemon(True)
			t2.start()
			t3 = threading.Thread(target = conexion.publicar, args =("theta", gl.Input_theta) )
			t3.setDaemon(True)
			t3.start()
			t4 = threading.Thread(target = conexion.publicar, args =("distancia", gl.Input_d) )
			t4.setDaemon(True)
			t4.start()
	
	actuadores.motor(gl.Output_vel - gl.Output_theta - gl.Output_d, gl.Output_vel + gl.Output_theta + gl.Output_d)
	

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
