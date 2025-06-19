#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesa todas las canciones y clips para generar embeddings para entrenamiento de IA.
Estructura centralizada: embeddings/songs/ y embeddings/clips/

embeddings/
├── songs/
│   ├── clocks_coldplay_openl3_512d_48000sr_0.1s.npz
│   ├── enemy_imagine_dragons_openl3_512d_48000sr_0.1s.npz
│   └── ...
└── clips/
    ├── clocks_coldplay/
    │   ├── youtube_clip01.npz
    │   ├── youtube_clip02.npz
    │   ├── personal_clip01.npz
    │   └── ...
    └── enemy_imagine_dragons/
        ├── youtube_clip01.npz
        └── ...
"""

from pathlib import Path
import sys
import argparse
import numpy as np
import openl3
import librosa
from typing import List, Tuple

# -------------------- CLI --------------------
parser = argparse.ArgumentParser(
    description="Procesa todas las canciones y clips para generar embeddings centralizados."
)
parser.add_argument("--force-extract", action="store_true",
                    help="Extraer audio siempre, incluso si el WAV ya existe")
parser.add_argument("--refresh-embeddings", action="store_true",
                    help="Recalcular y sobrescribir todos los embeddings existentes")
parser.add_argument("--songs-only", action="store_true",
                    help="Procesar solo las canciones completas, omitir clips")
parser.add_argument("--clips-only", action="store_true",
                    help="Procesar solo los clips, omitir canciones completas")
args = parser.parse_args()

# -------------------- Parámetros fijos --------------------
SR_TARGET = 48_000
HOP_SIZE  = 0.1
EMB_SIZE  = 512

# -------------------- Rutas centralizadas --------------------
BASE_DIR = Path("clips_syntrack")
EMBEDDINGS_DIR = Path("embeddings")
SONGS_EMBEDDINGS_DIR = EMBEDDINGS_DIR / "songs"
CLIPS_EMBEDDINGS_DIR = EMBEDDINGS_DIR / "clips"

# Crear directorios
SONGS_EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

def find_all_songs() -> List[str]:
    """Encuentra todos los IDs de canciones disponibles."""
    if not BASE_DIR.exists():
        sys.exit(f"❌ Directorio base no encontrado: {BASE_DIR.resolve()}")
    
    songs = []
    for song_dir in BASE_DIR.iterdir():
        if song_dir.is_dir() and (song_dir / "cancion_estudio").exists():
            songs.append(song_dir.name)
    
    return sorted(songs)

def find_clip_sources(song_id: str) -> List[str]:
    """Encuentra todas las fuentes de clips para una canción (youtube, personal, etc.)."""
    song_dir = BASE_DIR / song_id
    sources = []
    
    for item in song_dir.iterdir():
        if item.is_dir() and item.name.startswith("clips_"):
            source = item.name.replace("clips_", "")
            sources.append(source)
    
    return sorted(sources)

def find_clips_in_source(song_id: str, source: str) -> List[Tuple[Path, str]]:
    """Encuentra todos los clips en una fuente específica."""
    clips_dir = BASE_DIR / song_id / f"clips_{source}"
    if not clips_dir.exists():
        return []
    
    clips = []
    
    # Buscar archivos mp4 directamente
    for mp4_file in clips_dir.glob("*.mp4"):
        clip_name = mp4_file.stem
        # Solo procesar archivos que sigan el patrón clipXX
        if clip_name.lower().startswith('clip') and len(clip_name) >= 6:
            # Verificar que después de "clip" hay al menos 2 dígitos
            suffix = clip_name[4:]  # Todo después de "clip"
            if suffix[:2].isdigit():
                clips.append((mp4_file, clip_name))
    
    # Buscar archivos mp4 en subdirectorios
    for subdir in clips_dir.iterdir():
        if subdir.is_dir():
            for mp4_file in subdir.glob("*.mp4"):
                clip_name = mp4_file.stem
                # Solo procesar archivos que sigan el patrón clipXX
                if clip_name.lower().startswith('clip') and len(clip_name) >= 6:
                    # Verificar que después de "clip" hay al menos 2 dígitos
                    suffix = clip_name[4:]  # Todo después de "clip"
                    if suffix[:2].isdigit():
                        clips.append((mp4_file, clip_name))
    
    return clips

def extract_audio_if_needed(video_path: Path, wav_path: Path) -> bool:
    """Extrae audio si es necesario. Retorna True si se procesó correctamente."""
    if args.force_extract or not wav_path.exists():
        print(f"   🎵 Extrayendo audio: {video_path.name}")
        try:
            import moviepy as mp
            wav_path.parent.mkdir(parents=True, exist_ok=True)
            clip = mp.VideoFileClip(str(video_path))
            clip.audio.write_audiofile(str(wav_path))
            clip.close()
            return True
        except Exception as e:
            print(f"   ❌ Error extrayendo {video_path.name}: {e}")
            return False
    return True

def process_song_embedding(song_id: str):
    """Procesa el embedding de una canción completa."""
    print(f"\n🎵 Procesando canción: {song_id}")
    
    # Rutas
    studio_mp3 = BASE_DIR / song_id / "cancion_estudio" / f"{song_id}.mp3"
    embed_file = SONGS_EMBEDDINGS_DIR / f"{song_id}_openl3_{EMB_SIZE}d_{SR_TARGET}sr_{HOP_SIZE}s.npz"
    
    # Verificar si existe la canción
    if not studio_mp3.exists():
        print(f"   ❌ Canción no encontrada: {studio_mp3}")
        return
    
    # Verificar si ya existe el embedding
    if embed_file.exists() and not args.refresh_embeddings:
        print(f"   ✅ Embedding ya existe: {embed_file.name}")
        return
    
    try:
        # Cargar audio
        print(f"   📁 Cargando: {studio_mp3.name}")
        song, sr = librosa.load(studio_mp3, sr=SR_TARGET)
        
        # Generar embedding
        print(f"   🧠 Generando embedding...")
        emb_song, ts_song = openl3.get_audio_embedding(
            song, sr,
            input_repr="mel256", content_type="music",
            embedding_size=EMB_SIZE, hop_size=HOP_SIZE
        )
        
        # Guardar
        np.savez_compressed(embed_file, emb=emb_song, ts=ts_song)
        print(f"   ✅ Guardado: {embed_file.name}")
        
    except Exception as e:
        print(f"   ❌ Error procesando {song_id}: {e}")

def process_clip_embedding(song_id: str, source: str, video_path: Path, clip_name: str):
    """Procesa el embedding de un clip específico."""
    # Rutas
    wav_dir = BASE_DIR / song_id / f"clips_{source}" / "wavs"
    wav_file = wav_dir / f"{clip_name}.wav"
    
    embed_dir = CLIPS_EMBEDDINGS_DIR / song_id
    embed_dir.mkdir(exist_ok=True)
    embed_file = embed_dir / f"{source}_{clip_name}.npz"
    
    # Verificar si ya existe el embedding
    if embed_file.exists() and not args.refresh_embeddings:
        print(f"     ✅ Embedding ya existe: {embed_file.name}")
        return
    
    # Extraer audio si es necesario
    if not extract_audio_if_needed(video_path, wav_file):
        return
    
    try:
        # Cargar audio
        print(f"     📁 Cargando: {wav_file.name}")
        clip, sr = librosa.load(wav_file, sr=SR_TARGET)
        clip = librosa.util.normalize(clip)
        
        # Generar embedding
        print(f"     🧠 Generando embedding...")
        emb_clip, ts_clip = openl3.get_audio_embedding(
            clip, sr,
            input_repr="mel256", content_type="music",
            embedding_size=EMB_SIZE, hop_size=HOP_SIZE
        )
        
        # Guardar
        np.savez_compressed(embed_file, emb=emb_clip, ts=ts_clip)
        print(f"     ✅ Guardado: {embed_file.name}")
        
    except Exception as e:
        print(f"     ❌ Error procesando {clip_name}: {e}")

def main():
    print("🚀 Iniciando procesamiento masivo de embeddings...")
    print(f"📂 Directorio base: {BASE_DIR.resolve()}")
    print(f"💾 Embeddings en: {EMBEDDINGS_DIR.resolve()}")
    
    ## Encontrar todas las canciones
    songs = find_all_songs()
    if not songs:
        sys.exit("❌ No se encontraron canciones en clips_syntrack/")

    # Test with just one song
    # songs = ["clocks_coldplay"]  # Instead of find_all_songs()
    
    print(f"\n📋 Canciones encontradas: {len(songs)}")
    for song in songs:
        print(f"   - {song}")
    
    # Procesar canciones completas
    if not args.clips_only:
        print(f"\n{'='*50}")
        print("🎼 PROCESANDO CANCIONES COMPLETAS")
        print(f"{'='*50}")
        
        for song_id in songs:
            process_song_embedding(song_id)
    
    # Procesar clips
    if not args.songs_only:
        print(f"\n{'='*50}")
        print("🎬 PROCESANDO CLIPS")
        print(f"{'='*50}")
        
        for song_id in songs:
            print(f"\n🎵 Clips de: {song_id}")
            
            # Encontrar fuentes de clips
            sources = find_clip_sources(song_id)
            if not sources:
                print(f"   ⚠️  No se encontraron fuentes de clips")
                continue
            
            for source in sources:
                print(f"   📁 Fuente: {source}")
                clips = find_clips_in_source(song_id, source)
                
                if not clips:
                    print(f"     ⚠️  No se encontraron clips")
                    continue
                
                for video_path, clip_name in clips:
                    print(f"     🎬 {clip_name}")
                    process_clip_embedding(song_id, source, video_path, clip_name)
    
    print(f"\n🎉 ¡Procesamiento completado!")
    print(f"📊 Revisa los embeddings en: {EMBEDDINGS_DIR.resolve()}")

if __name__ == "__main__":
    main()