import cv2 as cv
import numpy as np
import time

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", help="video de entrada como video.mp4")
parser.add_argument("-o", "--output", help="video de salida como video_seg.mp4")
parser.add_argument("-c", "--camera", help="ID de camara como 0")

args = parser.parse_args()

video_input = cv.VideoCapture()
output_name = ""

if((args.camera is None) and (args.input is None)):
    print("No se ha indicado un id de camara ni un video de entrada.\nPor favor vuelva a intentarlo indicando la opción -i, -c o -h para ayuda")
    video_input.release()
    exit(0)
elif((args.camera is not None) and (args.input is not None)):
    print("Sólo debe indicarse uno de estos argumentos: -i o -c, no ambos al mismo tiempo.\nPor favor reintentar ...")
    video_input.release()
    exit(0)
elif(args.camera is not None):
    print("El id de la camara es: ", args.camera, ". Procesando flujo de video entrante en tiempo real.\nPulsa la tecla 'Q' para terminar procesamiento ...")
elif(args.input is not None):
    print("Procesando video: ", args.input, "\nPulsa la tecla 'Q' para terminar procesamiento ...")
    video_input.release()
    video_input = cv.VideoCapture(str(args.input))
else:
    print("algo malo ocurrió ... ")
    exit(-1)
if(args.output is None):
    output_name = str(args.input).split(".")[0] + "_seg.mp4"
    print("No se ha indicado nombre para el video de salida, así que este será: ", output_name)
else:
    output_name = str(args.output)
    print("El output indicado es: ", output_name)

print("iniciando análisis ...")

#video_input = cv.VideoCapture('atras_abajo.mp4')

ret, frame = video_input.read()
frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
zeros = np.zeros(frame_gray.shape, dtype='uint8')

video_seg_out = cv.VideoWriter(output_name,cv.VideoWriter_fourcc(*'MP4V'), 25, (frame_gray.shape[:2][1],int(frame_gray.shape[:2][0]/2)))

time_start = int(time.time())
last_time = time_start

while video_input.isOpened():
    ret, frame = video_input.read()
    if time.time() - last_time > 1:
        last_time = time.time()
        print(last_time - time_start)
    if ret == True:
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        th1 = cv.adaptiveThreshold(frame_gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
        blur = cv.GaussianBlur(frame_gray,(5,5),0)
        ret2,th2 = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
        th3 = cv.merge([zeros,zeros,th2])  

        small_frame = cv.resize(frame, (0, 0), None, .5, .5)
        small_th3 = cv.resize(th3, (0, 0), None, .5, .5)

        concat_frame = np.hstack((small_frame,small_th3))

        video_seg_out.write(concat_frame)

        cv.imshow("segmentation", concat_frame)

        if cv.waitKey(5) & 0xFF == ord('q'):
            break
    else:
        break

print("Procesamiento terminado")
video_input.release()
video_seg_out.release()
print("video guardado como: ", output_name)
cv.destroyAllWindows()
