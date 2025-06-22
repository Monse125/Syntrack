import os
from moviepy import VideoFileClip

def extraer_audio_wav_de_carpeta(ruta_carpeta):
    for archivo in os.listdir(ruta_carpeta):
        if archivo.lower().endswith(".mp4"):
            ruta_video = os.path.join(ruta_carpeta, archivo)
            nombre_sin_ext = os.path.splitext(archivo)[0]
            ruta_audio = os.path.join(ruta_carpeta, nombre_sin_ext + ".wav")

            print(f"Procesando {archivo} -> {nombre_sin_ext}.wav")
            video = VideoFileClip(ruta_video)
            video.audio.write_audiofile(ruta_audio, codec='pcm_s16le')
            video.close()

if __name__ == "__main__":
    carpeta = "clips_syntrack\pastel_con_nutella_ysy_a\clips_camera"  # Cambia acá por la ruta a la carpeta que quieres procesar
    extraer_audio_wav_de_carpeta(carpeta)
    print("Proceso finalizado.")