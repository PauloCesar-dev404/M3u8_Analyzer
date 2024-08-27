import os
import platform
import shutil
import stat
import subprocess
import sys
import time
import zipfile
from http.client import IncompleteRead

import requests
from colorama import Fore, Style

from M3u8_Analyzer.m3u8_analyzer.exeptions import M3u8NetworkingError, M3u8FileError

v = '1.0.3.4'


class Configurate:
    """Esta classe cria variáveis de ambiente no ambiente virtual ou, se não for, cria no path global."""

    def __init__(self):
        self.config_file_path = os.path.join(sys.prefix,
                                             '.m3u8_analyzer_config') if self.is_virtualenv() \
            else '.m3u8_analyzer_config'
        self.BIN_DIR = 'ffmpeg-binaries'
        self.config = self.load_config(self.config_file_path)
        self.OS_SYSTEM = self.config.get('OS_SYSTEM', os.name)
        self.VERSION = self.config.get('VERSION', v)
        self.FFMPEG_URL = self.config.get('FFMPEG_URL')
        self.FFMPEG_BINARY = self.config.get('FFMPEG_BINARY')
        self.INSTALL_DIR = self.config.get('INSTALL_DIR')
        self.STATUS = self.config.get('STATUS')
        self.VENV_PATH = self.config.get('VENV_PATH', os.path.dirname(self.config_file_path))

        if not self.INSTALL_DIR:
            self.INSTALL_DIR = os.path.join(sys.prefix, self.BIN_DIR) if self.is_virtualenv() else os.path.join(
                os.getcwd(), self.BIN_DIR)
            self.config['INSTALL_DIR'] = self.INSTALL_DIR
            self.save_config(self.config_file_path, self.config)

        if not os.path.exists(self.config_file_path):
            self.configure()

    def loader(self):
        """Carrega a configuração do arquivo e retorna um dicionário."""
        self.configure()
        return self.load_config(self.config_file_path)

    def load_config(self, file_path):
        """Função para ler variáveis de configuração de um arquivo .config."""
        config = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):  # Ignorar linhas em branco e comentários
                        key, value = line.strip().split('=', 1)
                        config[key.strip()] = value.strip()

        return config

    def save_config(self, file_path, config):
        """Função para criar/atualizar o arquivo .config."""
        with open(file_path, 'w') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")

    def check_files(self, path):
        """Verifica se o diretório de binários existe."""
        binary_path = os.path.join(self.VENV_PATH)
        if binary_path:
            return True
        return None

    def configure(self):
        """Função para obter entradas do usuário e atualizar o arquivo de configuração."""
        config = {
            'OS_SYSTEM': os.name,
            'VERSION': self.VERSION
        }
        if os.name == 'nt':
            config[
                'FFMPEG_URL'] = ('https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg2024-07-15'
                                 '-git-350146a1ea-essentials_build.zip')
            config['FFMPEG_BINARY'] = 'ffmpeg.exe'
        elif os.name == 'posix':
            config[
                'FFMPEG_URL'] = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg_linux.zip'
            config['FFMPEG_BINARY'] = 'ffmpeg'
        config['STATUS'] = 'TRUE'
        config['VENV_PATH'] = os.path.dirname(self.config_file_path)
        config['INSTALL_DIR'] = self.INSTALL_DIR
        self.save_config(self.config_file_path, config)

    def is_virtualenv(self):
        """Função para detectar se estamos em um ambiente virtual."""
        return (
                hasattr(sys, 'real_prefix') or
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )

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
        """Descompacta o arquivo ZIP no diretório especificado."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

        except zipfile.BadZipFile as e:
            sys.stderr.write(f"Erro ao descompactar o arquivo: {e}\n")
            raise
        finally:
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

    def __add_path(self, var, path):
        """
        Adiciona o caminho do executável à variável de ambiente PATH do sistema.

        :param var: Nome da variável de ambiente a ser modificada.
        :param path: Caminho completo para o executável.
        """
        sistema = platform.system()

        if sistema == "Windows":
            try:
                # Obtém o PATH atual
                path_atual = os.environ.get("PATH", "")
                novo_path = f"{path};{path_atual}"

                # Usando o PowerShell para adicionar o caminho ao PATH de forma persistente
                command = f"[System.Environment]::SetEnvironmentVariable('Path', '{novo_path}', 'User')"
                subprocess.run(["powershell", "-Command", command], check=True)

            except subprocess.CalledProcessError as e:
                print(f"Erro ao adicionar ao PATH no Windows: {e}")
            except Exception as e:
                print(f"Erro geral ao adicionar ao PATH no Windows: {e}")

        elif sistema in ["Linux", "Darwin"]:
            # Para sistemas Unix-like (Linux/macOS)
            bashrc_path = os.path.expanduser("~/.bashrc")
            zshrc_path = os.path.expanduser("~/.zshrc")
            shell_rc_path = bashrc_path if os.path.exists(bashrc_path) else zshrc_path
            try:
                # Adiciona o caminho ao arquivo de configuração do shell
                with open(shell_rc_path, "a") as file:
                    file.write(f"\nexport PATH=\"{path}:$PATH\"\n")

            except Exception as e:
                print(f"Erro ao adicionar ao PATH: {e}")
        else:
            print(f"Sistema operacional '{sistema}' não suportado para configuração automática de PATH.")

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
        ## addpath
        bina = os.path.join(self.INSTALL_DIR, self.FFMPEG_BINARY)
        self.__add_path(var='ffmpeg-binarie', path=bina)

    def __handle_remove_readonly(self, func, path, exc_info):
        """Função de callback para lidar com arquivos somente leitura."""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def uninstall_bins(self):
        """Remove os binários"""
        dt = self.loader()
        install_dir = dt.get('INSTALL_DIR')
        configpath = os.path.join(self.VENV_PATH, ".m3u8_analyzer_config")
        if install_dir and os.path.exists(install_dir):
            try:
                bin_path = os.path.join(install_dir, self.FFMPEG_BINARY)
                if os.path.exists(bin_path):
                    os.remove(bin_path)
                    os.remove(configpath)
                shutil.rmtree(install_dir, onerror=self.__handle_remove_readonly)
                print(f"{Fore.LIGHTGREEN_EX}Removido com sucesso{Style.RESET_ALL}")

            except PermissionError as e:
                print(f"{Fore.LIGHTRED_EX}Permissão negada ao tentar remover o diretório{Style.RESET_ALL}"
                      f"{Fore.LIGHTCYAN_EX} {install_dir}: {e}{Style.RESET_ALL}")
            except OSError as e:
                print(
                    f"{Fore.LIGHTRED_EX}Erro ao remover o diretório {Fore.LIGHTCYAN_EX}{install_dir}: {e}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.LIGHTRED_EX}Erro inesperado ao remover o diretório {Fore.LIGHTCYAN_EX}"
                      f"{install_dir}: {e}{Style.RESET_ALL}")
                raise

        else:
            print(f"{Fore.LIGHTRED_EX}ffmpeg já está desinstalado ou nunca foi instalado{Style.RESET_ALL}")

    def run(self):
        try:
            self.configure()  # Carrega ou cria a configuração inicial
            if not self.check_files(self.INSTALL_DIR):
                print("Binários ffmpeg não encontrados. Iniciando a instalação.")
                self.install_bins()
                print("Binários ffmpeg instalados com sucesso.")
            else:
                print("Binários ffmpeg já instalados.")
        except Exception as e:
            M3u8FileError(f"Erro ao configurar os binários: {e}")


def install_bins():
    c = Configurate()
    c.install_bins()


def uninstall_bins():
    c = Configurate()
    c.uninstall_bins()
