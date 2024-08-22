import os
import sys
import time
from http.client import IncompleteRead

import requests
import zipfile
import site
from .M3u8Analyzer import M3u8Analyzer
__ossystem = os.name
if __ossystem == 'nt':
    __url = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg2024-07-15-git-350146a1ea-essentials_build.zip'
    __bina = 'ffmpeg.exe'
elif __ossystem == 'posix':
    __url = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg_6.1.1_3UBUNTU5.zip'
    __bina = 'ffmpeg'
else:
    raise DeprecationWarning("Este sistema ainda não é compatível.")


def __update_activation_script():
    # Obter o caminho do ambiente virtual
    virtual_env_path = os.getenv('VIRTUAL_ENV')
    if not virtual_env_path:
        print("Variável de ambiente VIRTUAL_ENV não definida.")
        return

    # Definir o nome do ambiente virtual e o caminho para o diretório bin
    venv_path = os.path.abspath(virtual_env_path)

    if sys.platform == 'win32':
        activate_path = os.path.join(venv_path, 'Scripts', 'activate.bat')
        line_to_add = f'@set "PATH=%VIRTUAL_ENV%\\Lib\\site-packages\\m3u8_analyzer\\bin;%PATH%"'
    elif sys.platform == 'linux' or sys.platform == 'darwin':
        activate_path = os.path.join(venv_path, 'bin', 'activate')
        line_to_add = f'export PATH="$VIRTUAL_ENV/lib/site-packages/m3u8_analyzer/bin:$PATH"'
    else:
        print("Sistema operacional não suportado.")
        return

    try:
        # Adicionar a linha ao arquivo de ativação se ainda não estiver presente
        with open(activate_path, 'r+') as f:
            lines = f.readlines()
            if line_to_add + '\n' not in lines:
                f.write('\n' + line_to_add + '\n')
                print("pode usar o ffmpeg pelo terminal no ambiente virtual")
                pass
            else:
                print("pode usar o ffmpeg pelo terminal no ambiente virtual")
                pass
    except FileNotFoundError:
        print(f"Arquivo de ativação não encontrado: {activate_path}")
    except IOError as e:
        print(f"Erro ao escrever no arquivo de ativação: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


def __installbins():
    try:
        zip_path = "ffmpeg.zip"
        extract_to = os.path.join(site.getsitepackages()[0], 'Lib', 'site-packages', 'm3u8_analyzer', 'bin')

        # Criar o diretório de destino se não existir
        os.makedirs(extract_to, exist_ok=True)

        # Iniciar o download do arquivo ZIP
        try:
            response = requests.get(__url, stream=True)
            response.raise_for_status()  # Verifica se o download foi bem-sucedido
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"Erro ao baixar o arquivo: {e}\n")
            return

        total_length = int(response.headers.get('content-length', 0))

        start_time = time.time()
        downloaded = 0

        try:
            with open(zip_path, 'wb') as f:
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    f.write(data)

                    elapsed_time = time.time() - start_time
                    if elapsed_time == 0:
                        elapsed_time = 0.001  # Prevenir divisão por zero
                    speed_kbps = (downloaded / 1024) / elapsed_time
                    percent_done = (downloaded / total_length) * 100
                    sys.stdout.write(
                        f"\rBaixando Binários ffmpeg: {percent_done:.2f}% | Velocidade: {speed_kbps:.2f} KB/s | "
                        f"Tempo decorrido: {int(elapsed_time)}s")
                    sys.stdout.flush()
            print("\nDownload completo, ffmpeg instalado em seu ambiente virtual.")
        except IOError as e:
            if isinstance(e, IncompleteRead):
                sys.stderr.write("Erro de conexão: Leitura incompleta\n")
            else:
                sys.stderr.write(f"Ocorreu um erro de I/O: {str(e)}\n")

        # Descompactar o arquivo ZIP
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        except zipfile.BadZipFile as e:
            sys.stderr.write(f"Erro ao descompactar o arquivo: {e}\n")
            return

        # Remover o arquivo ZIP
        try:
            os.remove(zip_path)
        except OSError as e:
            sys.stderr.write(f"Erro ao remover o arquivo ZIP: {e}\n")

        # Adicionar o diretório do ffmpeg ao PATH do ambiente atual
        __update_activation_script()
    except Exception as e:
        sys.stderr.write(f"Ocorreu um erro inesperado: {e}\n")


if not os.path.exists(os.path.join(site.getsitepackages()[0], 'Lib', 'site-packages', 'm3u8_analyzer', 'bin', __bina)):
    print("ffmpeg não instalado. Aguarde...\n")
    __installbins()
