import os
import sys

# Determina o sistema operacional
OS_SYSTEM = os.name

# URLs e binários de acordo com o sistema operacional
if OS_SYSTEM == 'nt':
    FFMPEG_URL = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg2024-07-15-git-350146a1ea-essentials_build.zip'
    FFMPEG_BINARY = 'ffmpeg.exe'
elif OS_SYSTEM == 'posix':
    FFMPEG_URL = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg_6.1.1_3UBUNTU5.zip'
    FFMPEG_BINARY = 'ffmpeg'
else:
    raise DeprecationWarning("Este sistema ainda não é compatível.")


# Função para detectar se estamos em um ambiente virtual
def is_virtualenv():
    return (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )


# Diretório de instalação dos binários
BIN_DIR = 'ffmpeg-binaries'

# Caminho do ambiente virtual ou diretório corrente
INSTALL_DIR = os.path.join(sys.prefix, BIN_DIR) if is_virtualenv() else os.path.join(os.getcwd(), BIN_DIR)
