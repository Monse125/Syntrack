# Syntrack
Proyecto de IA que permite identificar automáticamente en qué parte de una canción ocurre un fragmento de audio grabado, incluso con ruido.  
Sincroniza clips con la pista original para facilitar la creación de videos colaborativos.  
Ideal para bandas que buscan contenido auténtico y bien editado.

---

## Tabla de contenidos
1. [Introducción](#introducción)  
2. [Requisitos](#requisitos)  
3. [Instalación rápida (si tu Python ≤ 3.11)](#instalación-rápida-si-tu-python-≤-311)  
4. [Instalación de **pyenv** (si tu sistema ya trae Python 3.12 o superior)](#instalación-de-pyenv-si-tu-sistema-ya-trae-python-312-o-superior)  
   [Paso 0 – dependencias de compilación](#paso-0-dependencias-de-compilación)  
   [Paso 1 – instalar pyenv](#paso-1-instalar-pyenv)  
   [Paso 2 – compilar Python 3.11](#paso-2-compilar-python-311)  
   [Paso 3 – crear y activar el entorno virtual](#paso-3-crear-y-activar-el-entorno-virtual)  
5. [Uso básico](#uso-básico)  
6. [Créditos](#créditos)
---

## Introducción
Syntrack extrae descriptores de audio con **OpenL3** y los alinea con la pista original usando técnicas de *audio fingerprinting*.  
Para garantizar compatibilidad con versiones antiguas de OpenL3 (0.4.x) es necesario trabajar con Python 3.11; Python 3.12 elimina el módulo `imp` usado por dichas versiones.

---

## Requisitos
- Linux (probado en Ubuntu 20.04 / 22.04)  
- Git  
- Herramientas de compilación (`gcc`, `make`, etc.)  
- Python 3.11 (vía sistema o pyenv)  
- FFmpeg (opcional, para convertir formatos)

---

## Instalación rápida (si tu Python ≤ 3.11)
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Instalación de pyenv (si tu sistema ya trae Python 3.12 o superior)
### Paso 0 dependencias de compilación

Para evitar instalar otra versión de python globalmente que pueda entrar en conflicto con la versión de tu sistema, se hara una instalación local de la versión de python para el entorno virtual usando pyenv

```bash
sudo apt update
sudo apt install -y --no-install-recommends \
  make build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev llvm libncursesw5-dev \
  xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
  git curl
```
### Paso 1 instalar pyenv
```bash
curl https://pyenv.run | bash
```
Añade al final de ~/.bashrc (o ~/.zshrc si usas zsh):
```bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
Recarga la shell:
```bash
exec "$SHELL"      # o simplemente abre una nueva terminal
```

### Paso 2 compilar Python 3.11
```bash
pyenv install 3.11.9          # última de la serie 3.11
```

### Paso 3 crear y activar el entorno virtual
```bash
# Con el plugin virtualenv de pyenv (recomendado)
pyenv virtualenv 3.11.9 syntrack-3.11
pyenv activate syntrack-3.11

# O con venv “normal”
# pyenv local 3.11.9
# python -m venv venv
# source venv/bin/activate
```
Finalmente:
```bash
pip install -r requirements.txt
```

## Créditos

Proyecto mantenido por la comunidad de Syntrack.