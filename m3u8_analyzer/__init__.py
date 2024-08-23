import os
import sys
import time
import requests
import zipfile
import shutil
from http.client import IncompleteRead
from .M3u8Analyzer import M3u8Analyzer
from .__constants import FFMPEG_URL, FFMPEG_BINARY, INSTALL_DIR  # Importa as constantes do arquivo `constants.py`



# Função para baixar o arquivo
def download_file(url: str, local_filename: str):
    """Baixa um arquivo do URL para o caminho local especificado."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_length = int(response.headers.get('content-length', 0))

        with open(local_filename, 'wb') as f:
            start_time = time.time()
            downloaded = 0

            for data in response.iter_content(chunk_size=4096):
                downloaded += len(data)
                f.write(data)

                elapsed_time = time.time() - start_time
                elapsed_time = max(elapsed_time, 0.001)  # Prevenir divisão por zero
                speed_kbps = (downloaded / 1024) / elapsed_time
                percent_done = (downloaded / total_length) * 100

                sys.stdout.write(
                    f"\rBaixando Binários ffmpeg: {percent_done:.2f}% | Velocidade: {speed_kbps:.2f} KB/s | "
                    f"Tempo decorrido: {int(elapsed_time)}s")
                sys.stdout.flush()

            sys.stdout.write("\nDownload completo.\n")
            sys.stdout.flush()
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"Erro ao baixar o arquivo: {e}\n")
        raise
    except IOError as e:
        if isinstance(e, IncompleteRead):
            sys.stderr.write("Erro de conexão: Leitura incompleta\n")
        else:
            sys.stderr.write(f"Ocorreu um erro de I/O: {str(e)}\n")
        raise


# Função para extrair o arquivo ZIP
def extract_zip(zip_path: str, extract_to: str):
    """Descompacta o arquivo ZIP no diretório especificado."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except zipfile.BadZipFile as e:
        sys.stderr.write(f"Erro ao descompactar o arquivo: {e}\n")
        raise


# Função para remover o arquivo
def remove_file(file_path: str):
    """Remove o arquivo especificado."""
    try:
        os.remove(file_path)
    except OSError as e:
        sys.stderr.write(f"Erro ao remover o arquivo ZIP: {e}\n")
        raise


# Função para instalar os binários
def install_bins():
    """Instala o ffmpeg baixando e descompactando o binário apropriado."""
    zip_path = os.path.join(INSTALL_DIR, "ffmpeg.zip")

    # Criar o diretório de destino se não existir
    os.makedirs(INSTALL_DIR, exist_ok=True)

    # Baixar o arquivo ZIP
    download_file(FFMPEG_URL, zip_path)

    # Descompactar o arquivo ZIP
    extract_zip(zip_path, INSTALL_DIR)

    # Remover o arquivo ZIP
    remove_file(zip_path)


# Função para desinstalar os binários
def uninstall_bins():
    """Remove os binários do ffmpeg instalados no ambiente virtual."""
    if os.path.exists(INSTALL_DIR):
        try:
            shutil.rmtree(INSTALL_DIR)
            print(f"ffmpeg desinstalado com sucesso do diretório: {INSTALL_DIR}")
        except OSError as e:
            sys.stderr.write(f"Erro ao remover o diretório ffmpeg-binaries: {e}\n")
            raise
    else:
        print("ffmpeg já está desinstalado ou nunca foi instalado.")


# Verifica se o binário já está instalado
ffmpeg_binary_path = os.path.join(INSTALL_DIR, FFMPEG_BINARY)
if not os.path.exists(ffmpeg_binary_path):
    install_bins()
else:
    pass
