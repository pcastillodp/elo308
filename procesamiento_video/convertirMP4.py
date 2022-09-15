from subprocess import call 

def convert(file_h264, file_mp4):
    command = "MP4Box -add " + file_h264 + " " + file_mp4
    call([command], shell=True)
    print("\r\nRasp_Pi => Video Converted! \r\n")

nombreArchivo = input("escribe el nombre del archivo .264 a convertir: ")

if(nombreArchivo is None):
    print("No se ha indicado nombre del archivo.\nPor favor vuelva a intentarlo.")
    exit(0)

elif(nombreArchivo is not None):
    print("Se convertirá el archivo " + nombreArchivo)
    convert(nombreArchivo, nombreArchivo.split(".")[0] + ".mp4")


