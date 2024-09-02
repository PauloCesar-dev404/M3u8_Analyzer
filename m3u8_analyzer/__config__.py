import os
import shutil
import stat
import sys
import time
import zipfile
import requests
from colorama import Fore, Style
from .exeptions import *


class Configurate:
    """Esta classe configura variáveis de ambiente no ambiente virtual ou globalmente."""

    def __init__(self):
        # Define a versão e lê as variáveis de ambiente existentes
        self.VERSION = self.__read_version()
        self.FFMPEG_URL = os.getenv('FFMPEG_URL')
        self.FFMPEG_BINARY = os.getenv('FFMPEG_BINARY')
        self.is_venv = self.__is_venv()
        if not self.is_venv:
            PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)).split('.')[0], 'ffmpeg')
            os.makedirs(PATH, exist_ok=True)
            self.INSTALL_DIR = os.getenv('INSTALL_DIR', PATH)
        else:
            dirpath = fr"{self.is_venv}\ffmpeg"
            self.INSTALL_DIR = os.getenv('INSTALL_DIR',dirpath)
        self.VENV_PATH = os.getenv('VENV_PATH', self.INSTALL_DIR)
        # Configura as variáveis de ambiente
        self.configure()

    def __is_venv(self):
        """Verifica se o script está sendo executado em um ambiente virtual e retorna o caminho até o diretório do script se estiver em um ambiente virtual."""
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # Retorna o diretório onde o script está localizado
            return os.path.dirname(os.path.abspath(__file__))
        return None

    def configure(self):
        """Define variáveis de ambiente com base no sistema operacional."""
        if self.FFMPEG_URL is None or self.FFMPEG_BINARY is None:
            if os.name == 'nt':
                # Configuração para Windows
                self.FFMPEG_URL = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg2024-07-15-git-350146a1ea-essentials_build.zip'
                self.FFMPEG_BINARY = 'ffmpeg.exe'
            elif os.name == 'posix':
                # Configuração para Unix-like (Linux/macOS)
                self.FFMPEG_URL = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg_linux.zip'
                self.FFMPEG_BINARY = 'ffmpeg'
            else:
                raise M3u8FileError(f"Sistema operacional '{os.name}' ainda não incluso na lib")
            # Atualiza variáveis de ambiente
            os.environ['FFMPEG_URL'] = self.FFMPEG_URL
            os.environ['FFMPEG_BINARY'] = self.FFMPEG_BINARY
        # Atualiza a variável INSTALL_DIR se não estiver definida
        if not os.getenv('INSTALL_DIR'):
            os.environ['INSTALL_DIR'] = self.INSTALL_DIR

    def __read_version(self):
        """Lê a versão do arquivo __version__.py."""
        version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)).split('.')[0], '__version__.py')
        if os.path.isfile(version_file):
            with open(version_file, 'r') as file:
                version_line = file.readline().strip()
                if version_line.startswith('__version__'):
                    version = version_line.split('=')[1].strip().strip("'")
                    return version
        return 'Unknown Version'

    def __download_file(self, url: str, local_filename: str):
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
                        f"\r{Fore.LIGHTCYAN_EX}Baixando Binários do ffmpeg: {Style.RESET_ALL}{Fore.LIGHTGREEN_EX}"
                        f"{percent_done:.2f}%{Style.RESET_ALL} | {Fore.LIGHTCYAN_EX}Velocidade:{Style.RESET_ALL}"
                        f"{Fore.LIGHTGREEN_EX} {speed_kbps:.2f} KB/s{Style.RESET_ALL} | "
                        f"{Fore.LIGHTCYAN_EX}Tempo decorrido:{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{int(elapsed_time)}s"
                        f"{Style.RESET_ALL}")
                    sys.stdout.flush()
                sys.stdout.write("\nDownload completo.\n")
                sys.stdout.flush()


        except requests.exceptions.InvalidProxyURL as e:
            raise M3u8NetworkingError(f"Erro: URL de proxy inválida: {e}")
        except requests.exceptions.InvalidURL:
            raise M3u8NetworkingError("Erro: URL inválida fornecida.")
        except requests.exceptions.InvalidSchema:
            raise M3u8NetworkingError("Erro: URL inválida, esquema não suportado.")
        except requests.exceptions.MissingSchema:
            raise M3u8NetworkingError("Erro: URL inválida, esquema ausente.")
        except requests.exceptions.InvalidHeader as e:
            raise M3u8NetworkingError(f"Erro de cabeçalho inválido: {e}")
        except ValueError as e:
            raise M3u8FileError(f"Erro de valor: {e}")
        except requests.exceptions.ContentDecodingError as e:
            raise M3u8NetworkingError(f"Erro de decodificação de conteúdo: {e}")
        except requests.exceptions.BaseHTTPError as e:
            raise M3u8NetworkingError(f"Erro HTTP básico: {e}")
        except requests.exceptions.SSLError as e:
            raise M3u8NetworkingError(f"Erro SSL: {e}")
        except requests.exceptions.ProxyError as e:
            raise M3u8NetworkingError(f"Erro de proxy: {e}")
        except requests.exceptions.ConnectionError:
            raise M3u8NetworkingError("Erro: O servidor ou o servidor encerrou a conexão.")
        except requests.exceptions.HTTPError as e:
            raise M3u8NetworkingError(f"Erro HTTP: {e}")
        except requests.exceptions.Timeout:
            raise M3u8NetworkingError(
                "Erro de tempo esgotado: A conexão com o servidor demorou muito para responder.")
        except requests.exceptions.TooManyRedirects:
            raise M3u8NetworkingError("Erro de redirecionamento: Muitos redirecionamentos.")
        except requests.exceptions.URLRequired:
            raise M3u8NetworkingError("Erro: URL é necessária para a solicitação.")
        except requests.exceptions.ChunkedEncodingError as e:
            raise M3u8NetworkingError(f"Erro de codificação em partes: {e}")
        except requests.exceptions.StreamConsumedError:
            raise M3u8NetworkingError("Erro: Fluxo de resposta já consumido.")
        except requests.exceptions.RetryError as e:
            raise M3u8NetworkingError(f"Erro de tentativa: {e}")
        except requests.exceptions.UnrewindableBodyError:
            raise M3u8NetworkingError("Erro: Corpo da solicitação não pode ser rebobinado.")
        except requests.exceptions.RequestException as e:
            raise M3u8NetworkingError(f"Erro de conexão: Não foi possível se conectar ao servidor. Detalhes: {e}")

    def __extract_zip(self, zip_path: str, extract_to: str):
        """Descompacta o arquivo ZIP no diretório especificado e ajusta permissões de arquivos e diretórios."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

            # Ajustar permissões de todos os arquivos e diretórios extraídos
            for root, dirs, files in os.walk(extract_to):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    os.chmod(dir_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

        except zipfile.BadZipFile as e:
            sys.stderr.write(f"Erro ao descompactar o arquivo: {e}\n")
            raise
        finally:
            # Remover o arquivo ZIP original após a extração
            os.remove(zip_path)

    def __remove_file(self, file_path: str):
        """Remove o arquivo especificado."""
        if os.path.exists(file_path):
            try:
                sys.stdout.flush()  # Certificar-se de que toda a saída foi impressa antes de remover o diretório
                shutil.rmtree(file_path, onerror=self.__handle_remove_readonly)
            except PermissionError as e:
                print(f"{Fore.LIGHTRED_EX}Permissão negada ao tentar remover o diretório{Style.RESET_ALL}"
                      f"{Fore.LIGHTCYAN_EX} {file_path}: {e}{Style.RESET_ALL}")
            except OSError as e:
                print(
                    f"{Fore.LIGHTRED_EX}Erro ao remover o diretório {Fore.LIGHTCYAN_EX}{file_path}:"
                    f" {e}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.LIGHTRED_EX}Erro inesperado ao remover o diretório {Fore.LIGHTCYAN_EX}"
                      f"{file_path}: {e}{Style.RESET_ALL}")
                raise

    def install_bins(self):
        """Instala o ffmpeg baixando e descompactando o binário apropriado."""
        zip_path = os.path.join(self.INSTALL_DIR, "ffmpeg.zip")
        # Criar o diretório de destino se não existir
        os.makedirs(self.INSTALL_DIR, exist_ok=True)
        # Baixar o arquivo ZIP
        self.__download_file(self.FFMPEG_URL, zip_path)
        # Descompactar o arquivo ZIP
        self.__extract_zip(zip_path, self.INSTALL_DIR)
        # Remover o arquivo ZIP
        self.__remove_file(zip_path)

    def __handle_remove_readonly(self, func, path, exc_info):
        """Função de callback para lidar com arquivos somente leitura."""
        os.chmod(path, stat.S_IWRITE)
        func(path)


if __name__ == "__main__":
    M3u8Error("erro de runtime...")