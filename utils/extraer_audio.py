from moviepy import VideoFileClip, AudioFileClip
from pathlib import Path

def extraer_audio(video_path, salida_path, sr=48000):
    """
    Extrae el audio de un video MP4 o carga un archivo de audio y lo guarda como WAV con sample rate fijo.

    Args:
        video_path (str or Path): ruta al video .mp4 o archivo de audio (.mp3, .wav, etc.)
        salida_path (str or Path): ruta donde guardar el .wav
        sr (int): sample rate de salida (default: 48000 Hz)
    """
    video_path = Path(video_path)
    salida_path = Path(salida_path)
    salida_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎧 Extrayendo audio de: {video_path.name}")
    
    # Detectar si es un archivo de video o audio
    if video_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
        clip = VideoFileClip(str(video_path))
        audio = clip.audio
    else:
        # Para archivos de audio (.mp3, .wav, etc.)
        audio = AudioFileClip(str(video_path))
    
    audio.write_audiofile(str(salida_path), fps=sr)
    print(f"✅ Guardado en: {salida_path}")

"""
"clips_syntrack\mai_milo_j\cancion_estudio\mai_milo_j.mp3"
"clips_syntrack\pastel_con_nutella_ysy_a\cancion_estudio\pastel_con_nutella_ysy_a.mp3"
"clips_syntrack\tu_me_dejaste_de_querer_c_tangana\cancion_estudio\tu_me_dejaste_de_querer_c_tangana.mp3"


"""
# Para correr desde consola:
# python /c:/Users/monse/OneDrive/Escritorio/proyectoIA/Syntrack/utils/extraer_audio.py <ruta_video> <ruta_salida_wav>


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python extraer_audio.py <video_path> <salida_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    salida_path = sys.argv[2]
    extraer_audio(video_path, salida_path)

