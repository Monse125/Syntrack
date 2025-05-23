import openl3 
import soundfile as sf
import numpy as np
import moviepy as mp
import librosa
from scipy.spatial.distance import cdist

# === Archivos ===
CANCION_PATH = "docs_test/audios_limpios/Bad Bunny - Me porto bonito.mp3"
VIDEO_PATH = "docs_test/videos_prueba/VID_20221029_211501.mp4"
AUDIO_EXTRAIDO_PATH = "docs_test/videos_prueba/clip_audio.wav"

# === 1. Extraer audio del video ===
print("Extrayendo audio del video...")
video = mp.VideoFileClip(VIDEO_PATH)
video.audio.write_audiofile(AUDIO_EXTRAIDO_PATH) 

# === 2. Cargar ambos audios con librosa para asegurar formato consistente ===
print("Cargando audios...")
audio_cancion, sr_cancion = librosa.load(CANCION_PATH, sr=48000)
audio_clip, sr_clip = librosa.load(AUDIO_EXTRAIDO_PATH, sr=48000)

# Normalizar el volumen
audio_clip = librosa.util.normalize(audio_clip)

# === 3. Extraer embeddings con OpenL3 ===
HOP_SIZE = 0.1  
print("Extrayendo embeddings...")
emb_cancion, ts_cancion = openl3.get_audio_embedding(
    audio_cancion,
    sr_cancion,
    input_repr="mel256",
    content_type="music",
    embedding_size=512,
    hop_size=HOP_SIZE
)

emb_clip, ts_clip = openl3.get_audio_embedding(
    audio_clip,
    sr_clip,
    input_repr="mel256",
    content_type="music",
    embedding_size=512,
    hop_size=HOP_SIZE
)

# === 4. Comparar los embeddings ===
print("Comparando embeddings...")
distancias = cdist(emb_clip, emb_cancion, metric="euclidean")  # cada fila = frame del clip
minimos = np.argmin(distancias, axis=1)  # mejor match por frame
conteo = np.bincount(minimos)
mejor_match = np.argmax(conteo)

print(f"\n🎯 El clip coincide mejor con el segundo {int(ts_cancion[mejor_match])} de la canción original.")
