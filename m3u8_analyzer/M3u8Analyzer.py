import os
import re
import shutil
import stat
import subprocess
import sys
import time
from typing import List, Dict, Tuple
import requests
from colorama import Fore, Style
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from .__config__ import Configurate
from .exeptions import M3u8Error, M3u8NetworkingError, M3u8FileError, M3u8FfmpegDownloadError

parser = Configurate()
parser.configure()
INSTALL_DIR = os.getenv('INSTALL_DIR')
FFMPEG_BINARY = os.getenv('FFMPEG_BINARY')
__version__ = parser.VERSION
__author__ = 'PauloCesar0073-dev404'
__ossystem = os.name
HOME = INSTALL_DIR
ffmpeg_bin = fr'{INSTALL_DIR}\{FFMPEG_BINARY}'
temp_dir = os.path.devnull


class M3u8Analyzer:
    def __init__(self):
        """
        Classe para análise e manipulação de streams M3U8.
        Fornece métodos para obter o conteúdo de URLs M3U8, identificar o tipo de conteúdo,
        extrair informações de playlists, e suporte a decriptografia AES128 de segmentos.
        """
        pass

    @staticmethod
    def get_m3u8(url_m3u8: str, headers: dict = None, save_in_file=None, timeout: int = None):
        """
        Obtém o conteúdo de um arquivo M3U8 a partir de uma URL HLS.

        Este método permite acessar, visualizar ou salvar playlists M3U8 utilizadas em transmissões de vídeo sob
        demanda.

        Args: url_m3u8 (str): A URL do arquivo M3U8 que você deseja acessar. headers (dict, optional): Cabeçalhos
        HTTP opcionais para a requisição. Se não forem fornecidos, serão usados cabeçalhos padrão. save_in_file (str,
        optional): Nome do arquivo para salvar o conteúdo M3U8. Se fornecido, o conteúdo da playlist será salvo no
        diretório atual com a extensão `.m3u8`. timeout (int, optional): Tempo máximo (em segundos) para aguardar uma
        resposta do servidor. O padrão é 20 segundos.

        Returns:
            str: O conteúdo do arquivo M3U8 como uma string se a requisição for bem-sucedida.
            None: Se a requisição falhar ou se o servidor não responder com sucesso.

        Raises:
            ValueError: Se a URL não for válida ou se os headers não forem um dicionário.
            ConnectionAbortedError: Se o servidor encerrar a conexão inesperadamente.
            ConnectionRefusedError: Se a conexão for recusada pelo servidor.
            TimeoutError: Se o tempo de espera pela resposta do servidor for excedido.
            ConnectionError: Se não for possível se conectar ao servidor por outros motivos.

        Example:
            ```python
            from m3u8_analyzer import M3u8Analyzer

            url = "https://example.com/playlist.m3u8"
            headers = {"User-Agent": "Mozilla/5.0"}
            playlist_content = M3u8Analyzer.get_m3u8(url, headers=headers, save_in_file="minha_playlist", timeout=30)

            if playlist_content:
                print("Playlist obtida com sucesso!")
            else:
                print("Falha ao obter a playlist.")
            ```
        """

        if headers:
            if not isinstance(headers, dict):
                raise M3u8Error("headers deve ser um dicionário válido!", errors=['headers not dict'])
        if not (url_m3u8.startswith('https://') or url_m3u8.startswith('http://')):
            raise M3u8Error(f"Este valor não se parece ser uma url válida!")
        try:
            time = 20
            respo = ''
            headers_default = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "Content-Length": "583",
                "Content-Type": "text/plain",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Ch-Ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"118\", \"Chromium\";v=\"118\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/118.0.0.0 Safari/537.36"
            }
            session = requests.session()
            if timeout:
                time = timeout
                if not headers:
                    headers = headers_default
            r = session.get(url_m3u8, timeout=time, headers=headers)
            if r.status_code == 200:
                if save_in_file:
                    local = os.getcwd()
                    with open(fr"{local}\{save_in_file}.m3u8", 'a', encoding='utf-8') as e:
                        e.write(r.text)
                return r.text
            else:
                return None
        except requests.exceptions.SSLError as e:
            raise M3u8NetworkingError(f"Erro SSL: {e}")
        except requests.exceptions.ProxyError as e:
            raise M3u8NetworkingError(f"Erro de proxy: {e}")
        except requests.exceptions.ConnectionError:
            raise M3u8NetworkingError("Erro: O servidor ou o servidor encerrou a conexão.")
        except requests.exceptions.HTTPError as e:
            raise M3u8NetworkingError(f"Erro HTTP: {e}")
        except requests.exceptions.Timeout:
            raise M3u8NetworkingError("Erro de tempo esgotado: A conexão com o servidor demorou muito para responder.")
        except requests.exceptions.TooManyRedirects:
            raise M3u8NetworkingError("Erro de redirecionamento: Muitos redirecionamentos.")
        except requests.exceptions.URLRequired:
            raise M3u8NetworkingError("Erro: URL é necessária para a solicitação.")
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
        except requests.exceptions.ChunkedEncodingError as e:
            raise M3u8NetworkingError(f"Erro de codificação em partes: {e}")
        except requests.exceptions.ContentDecodingError as e:
            raise M3u8NetworkingError(f"Erro de decodificação de conteúdo: {e}")
        except requests.exceptions.StreamConsumedError:
            raise M3u8NetworkingError("Erro: Fluxo de resposta já consumido.")
        except requests.exceptions.RetryError as e:
            raise M3u8NetworkingError(f"Erro de tentativa: {e}")
        except requests.exceptions.UnrewindableBodyError:
            raise M3u8NetworkingError("Erro: Corpo da solicitação não pode ser rebobinado.")
        except requests.exceptions.RequestException as e:
            raise M3u8NetworkingError(f"Erro de conexão: Não foi possível se conectar ao servidor. Detalhes: {e}")
        except requests.exceptions.BaseHTTPError as e:
            raise M3u8NetworkingError(f"Erro HTTP básico: {e}")

    @staticmethod
    def get_high_resolution(m3u8_content: str):
        """
        Obtém a maior resolução disponível em um arquivo M3U8 e o URL correspondente.

        Este método analisa o conteúdo de um arquivo M3U8 para identificar a maior resolução
        disponível entre os fluxos de vídeo listados. Também retorna o URL associado a essa
        maior resolução, se disponível.

        Args:
            m3u8_content (str): O conteúdo do arquivo M3U8 como uma string. Este conteúdo deve
                                incluir as tags e atributos típicos de uma playlist HLS.

        Returns:
            tuple: Uma tupla contendo:
                - str: A maior resolução disponível no formato 'Largura x Altura' (ex.: '1920x1080').
                - str: O URL correspondente à maior resolução. Se o URL não for encontrado,
                       retorna None.
                Se o tipo de playlist não contiver resoluções, retorna uma mensagem indicando
                o tipo de playlist.

        Raises:
            ValueError: Se o conteúdo do M3U8 não contiver resoluções e a função não conseguir
                        determinar o tipo de playlist.

        Examples:
            ```python
            m3u8_content = '''
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=640x360
            http://example.com/360p.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=1280x720
            http://example.com/720p.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=3000000,RESOLUTION=1920x1080
            http://example.com/1080p.m3u8
            '''
            result = M3u8Analyzer.get_high_resolution(m3u8_content)
            print(result)  # Saída esperada: ('1920x1080', 'http://example.com/1080p.m3u8')
            ```

            ```python
            m3u8_content_no_resolutions = '''
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=500000
            http://example.com/360p.m3u8
            '''
            result = M3u8Analyzer.get_high_resolution(m3u8_content_no_resolutions)
            print(result)  # Saída esperada: 'Playlist type: <TIPO DA PLAYLIST> not resolutions...'
            ```
        """
        resolutions = re.findall(r'RESOLUTION=(\d+x\d+)', m3u8_content)
        if not resolutions:
            tip = M3u8Analyzer.get_type_m3u8_content(m3u8_content=m3u8_content)
            return f"Playlist type: {Fore.LIGHTRED_EX}{tip}{Style.RESET_ALL} not resolutions..."
        max_resolution = max(resolutions, key=lambda res: int(res.split('x')[0]) * int(res.split('x')[1]))
        url = re.search(rf'#EXT-X-STREAM-INF:[^\n]*RESOLUTION={max_resolution}[^\n]*\n([^\n]+)', m3u8_content).group(1)
        if not url:
            return max_resolution, None
        if not max_resolution:
            return None, url
        else:
            return max_resolution, url

    @staticmethod
    def get_type_m3u8_content(m3u8_content: str) -> str:
        """
        Determina o tipo de conteúdo de um arquivo M3U8 (Master ou Segmentos).

        Este método analisa o conteúdo de um arquivo M3U8 para identificar se ele é do tipo
        'Master', 'Master encrypted', 'Segments', 'Segments encrypted', 'Segments Master', ou
        'Desconhecido'. A identificação é baseada na presença de tags e chaves específicas no
        conteúdo da playlist M3U8.

        Args:
            m3u8_content (str): O conteúdo do arquivo M3U8 como uma string. Pode ser uma URL ou o
                                próprio conteúdo da playlist.

        Returns:
            str: O tipo de conteúdo identificado. Os possíveis valores são:
                - 'Master': Playlist mestre sem criptografia.
                - 'Master encrypted': Playlist mestre com criptografia.
                - 'Segments': Playlist de segmentos sem criptografia.
                - 'Segments encrypted': Playlist de segmentos com criptografia.
                - 'Segments .ts': Playlist de segmentos com URLs terminando em '.ts'.
                - 'Segments .m4s': Playlist de segmentos com URLs terminando em '.m4s'.
                - 'Segments Master': Playlist de segmentos com URLs variadas.
                - 'Desconhecido': Se o tipo não puder ser identificado.

        Examples:
            ```python
            m3u8_content_master = '''
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=500000
            http://example.com/master.m3u8
            '''
            result = M3u8Analyzer.get_type_m3u8_content(m3u8_content_master)
            print(result)  # Saída esperada: 'Master'

            m3u8_content_master_encrypted = '''
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=500000
            #EXT-X-KEY:METHOD=AES-128,URI="http://example.com/key.key"
            http://example.com/master.m3u8
            '''
            result = M3u8Analyzer.get_type_m3u8_content(m3u8_content_master_encrypted)
            print(result)  # Saída esperada: 'Master encrypted'

            m3u8_content_segments = '''
            #EXTM3U
            #EXTINF:10,
            http://example.com/segment1.ts
            #EXTINF:10,
            http://example.com/segment2.ts
            '''
            result = M3u8Analyzer.get_type_m3u8_content(m3u8_content_segments)
            print(result)  # Saída esperada: 'Segments .ts'

            m3u8_content_unknown = '''
            #EXTM3U
            #EXTINF:10,
            http://example.com/unknown_segment
            '''
            result = M3u8Analyzer.get_type_m3u8_content(m3u8_content_unknown)
            print(result)  # Saída esperada: 'Segments Master'
            ```

        Raises:
            Exception: Em caso de erro durante o processamento do conteúdo, o método retornará uma
                       mensagem de erro descritiva.
        """
        try:
            conteudo = m3u8_content
            if '#EXT-X-STREAM-INF' in conteudo:
                if '#EXT-X-KEY' in conteudo:
                    return 'Master encrypted'
                else:
                    return 'Master'
            elif '#EXTINF' in conteudo:
                if '#EXT-X-KEY' in conteudo:
                    return 'Segments encrypted'
                else:
                    # Verifica se URLs dos segmentos possuem a extensão .ts ou .m4s
                    segment_urls = re.findall(r'#EXTINF:[0-9.]+,\n([^\n]+)', conteudo)
                    if all(url.endswith('.ts') for url in segment_urls):
                        return 'Segments .ts'
                    elif all(url.endswith('.m4s') for url in segment_urls):
                        return 'Segments .m4s'
                    else:
                        return 'Segments Master'
            else:
                return 'Desconhecido'
        except re.error as e:
            raise M3u8FileError(f"Erro ao processar o conteúdo M3U8: {str(e)}")
        except Exception as e:
            raise M3u8FileError(f"Erro inesperado ao processar o conteúdo M3U8: {str(e)}")

    @staticmethod
    def get_player_playlist(m3u8_url: str) -> str:
        """
        Obtém o caminho do diretório base do arquivo M3U8, excluindo o nome do arquivo.

        Este método analisa a URL fornecida do arquivo M3U8 e retorna o caminho do diretório onde o arquivo M3U8 está localizado.
        A URL deve ser uma URL completa e o método irá extrair o caminho do diretório base.

        Args:
            m3u8_url (str): A URL completa do arquivo M3U8. Pode incluir o nome do arquivo e o caminho do diretório.

        Returns:
            str: O caminho do diretório onde o arquivo M3U8 está localizado. Se a URL não contiver um arquivo M3U8,
                 retornará uma string vazia.

        Examples:
            ```python
            # Exemplo 1
            url = 'http://example.com/videos/playlist.m3u8'
            path = M3u8Analyzer.get_player_playlist(url)
            print(path)  # Saída esperada: 'http://example.com/videos/'

            # Exemplo 2
            url = 'https://cdn.example.com/streams/segment.m3u8'
            path = M3u8Analyzer.get_player_playlist(url)
            print(path)  # Saída esperada: 'https://cdn.example.com/streams/'

            # Exemplo 3
            url = 'https://example.com/playlist.m3u8'
            path = M3u8Analyzer.get_player_playlist(url)
            print(path)  # Saída esperada: 'https://example.com/'

            # Exemplo 4
            url = 'https://example.com/videos/'
            path = M3u8Analyzer.get_player_playlist(url)
            print(path)  # Saída esperada: ''
            ```

        """
        if m3u8_url.endswith('/'):
            m3u8_url = m3u8_url[:-1]
        partes = m3u8_url.split('/')
        for i, parte in enumerate(partes):
            if '.m3u8' in parte:
                return '/'.join(partes[:i]) + "/"
        return ''

    @staticmethod
    def get_audio_playlist(m3u8_content: str):
        """
        Extrai o URL da playlist de áudio de um conteúdo M3U8.

        Este método analisa o conteúdo fornecido de um arquivo M3U8 e retorna o URL da playlist de áudio incluída na playlist M3U8.
        O método busca a linha que contém a chave `#EXT-X-MEDIA` e extrai a URL associada ao áudio.

        Args:
            m3u8_content (str): Conteúdo da playlist M3U8 como uma string. Deve incluir informações sobre áudio se disponíveis.

        Returns:
            str: URL da playlist de áudio encontrada no conteúdo M3U8. Retorna `None` se a URL da playlist de áudio não for encontrada.

        Examples:
            ```python
            # Exemplo 1
            content = '''
            #EXTM3U
            #EXT-X-VERSION:3
            #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="English",DEFAULT=YES,URI="http://example.com/audio.m3u8"
            #EXT-X-STREAM-INF:BANDWIDTH=256000,AUDIO="audio"
            http://example.com/stream.m3u8
            '''
            url = M3u8Analyzer.get_audio_playlist(content)
            print(url)  # Saída esperada: 'http://example.com/audio.m3u8'

            # Exemplo 2
            content = '''
            #EXTM3U
            #EXT-X-VERSION:3
            #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="French",DEFAULT=NO,URI="http://example.com/french_audio.m3u8"
            #EXT-X-STREAM-INF:BANDWIDTH=256000,AUDIO="audio"
            http://example.com/stream.m3u8
            '''
            url = M3u8Analyzer.get_audio_playlist(content)
            print(url)  # Saída esperada: 'http://example.com/french_audio.m3u8'

            # Exemplo 3
            content = '''
            #EXTM3U
            #EXT-X-VERSION:3
            #EXT-X-STREAM-INF:BANDWIDTH=256000
            http://example.com/stream.m3u8
            '''
            url = M3u8Analyzer.get_audio_playlist(content)
            print(url)  # Saída esperada: None
            ```

        """
        match = re.search(r'#EXT-X-MEDIA:.*URI="([^"]+)"(?:.*,IV=(0x[0-9A-Fa-f]+))?', m3u8_content)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def get_segments(content: str) -> Dict[str, List[Tuple[str, str]]]:
        """
        Extrai URLs de segmentos de uma playlist M3U8 e fornece informações detalhadas sobre os segmentos.

        Este método analisa o conteúdo de uma playlist M3U8 para extrair URLs de segmentos, identificar resoluções associadas,
        e retornar um dicionário com informações sobre as URLs dos segmentos, a quantidade total de segmentos,
        e a ordem de cada URI.

        Args:
            content (str): Conteúdo da playlist M3U8 como uma string. Não deve ser uma URL. Deve incluir as informações
                           sobre segmentos e, opcionalmente, informações sobre resoluções e URLs de stream.

        Returns:
            dict: Um dicionário com as seguintes chaves:
                - 'uris' (List[str]): Lista de URLs dos segmentos.
                - 'urls' (List[str]): Lista de URLs de stream extraídas do conteúdo.
                - 'len' (int): Contagem total de URLs de stream encontradas.
                - 'enumerated_uris' (List[Tuple[int, str]]): Lista de tuplas contendo a ordem e o URL de cada segmento.
                - 'resolutions' (Dict[str, str]): Dicionário mapeando resoluções para suas URLs correspondentes.

        Raises:
            ValueError: Se o conteúdo fornecido for uma URL em vez de uma string de conteúdo M3U8.

        Examples:
            ```python
            # Exemplo 1: Conteúdo simples de M3U8 com URLs de segmentos e stream
            content = '''
            #EXTM3U
            #EXTINF:10.0,
            http://example.com/segment1.ts
            #EXTINF:10.0,
            http://example.com/segment2.ts
            #EXT-X-STREAM-INF:BANDWIDTH=256000,RESOLUTION=1280x720
            http://example.com/stream_720p.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=512000,RESOLUTION=1920x1080
            http://example.com/stream_1080p.m3u8
            '''
            result = M3u8Analyzer.get_segments(content)
            print(result)
            # Saída esperada:
            # {
            #     'uris': ['http://example.com/segment1.ts', 'http://example.com/segment2.ts'],
            #     'urls': ['http://example.com/stream_720p.m3u8', 'http://example.com/stream_1080p.m3u8'],
            #     'len': 2,
            #     'enumerated_uris': [(1, 'http://example.com/segment1.ts'), (2, 'http://example.com/segment2.ts')],
            #     'resolutions': {'1280x720': 'http://example.com/stream_720p.m3u8', '1920x1080': 'http://example.com/stream_1080p.m3u8'}
            # }

            # Exemplo 2: Conteúdo sem informações de resolução
            content = '''
            #EXTM3U
            #EXTINF:10.0,
            http://example.com/segment1.ts
            #EXTINF:10.0,
            http://example.com/segment2.ts
            '''
            result = M3u8Analyzer.get_segments(content)
            print(result)
            # Saída esperada:
            # {
            #     'uris': ['http://example.com/segment1.ts', 'http://example.com/segment2.ts'],
            #     'urls': [],
            #     'len': 0,
            #     'enumerated_uris': [(1, 'http://example.com/segment1.ts'), (2, 'http://example.com/segment2.ts')],
            #     'resolutions': {}
            # }
            ```

        """
        # Verifica se o conteúdo é uma URL
        if re.match(r'^https?://', content):
            raise M3u8Error(f"Este valor não se parece ser uma string de uma playlist m3u8 válida!")

        # Separação das linhas da playlist, ignorando linhas vazias e comentários
        urls_segmentos = [linha for linha in content.splitlines() if linha and not linha.startswith('#')]

        # Inicializa o dicionário para armazenar os dados dos segmentos
        data_segments = {
            'uris': urls_segmentos,
            'urls': [],
            'len': 0,
            'enumerated_uris': [(index + 1, url) for index, url in enumerate(urls_segmentos)],
            'resolutions': {}
        }

        # Busca por resoluções na playlist e armazena suas URLs correspondentes
        resolutions = re.findall(r'RESOLUTION=(\d+x\d+)', content)
        for res in resolutions:
            match = re.search(rf'#EXT-X-STREAM-INF:[^\n]*RESOLUTION={re.escape(res)}[^\n]*\n([^\n]+)', content)
            if match:
                url = match.group(1)
                data_segments['urls'].append(url)
                data_segments['resolutions'][res] = url

        # Adiciona a contagem de URLs de stream encontradas ao dicionário
        data_segments['len'] = len(data_segments['urls'])

        # Retorna o dicionário com todas as informações encontradas
        return data_segments

    @classmethod
    class EncryptSuport:
        """
        Classe interna para suporte a operações de criptografia AES-128 relacionadas a M3U8.

        Fornece métodos para obter a URL da chave de criptografia e o IV (vetor de inicialização) associado,
        necessários para descriptografar conteúdos M3U8 protegidos por AES-128.

        Métodos:
            - get_url_key_m3u8: Extrai a URL da chave de criptografia e o IV de um conteúdo M3U8.
        """

        @staticmethod
        def get_url_key_m3u8(m3u8_content: str, player: str, headers=None):
            """
            Extrai a URL da chave de criptografia AES-128 e o IV (vetor de inicialização) de um conteúdo M3U8.

            Este método analisa o conteúdo M3U8 para localizar a URL da chave de criptografia e o IV, se disponível.
            Em seguida, faz uma requisição HTTP para obter a chave em formato hexadecimal.

            Args:
                m3u8_content (str): String contendo o conteúdo do arquivo M3U8.
                player (str): URL base para formar o URL completo da chave, se necessário.
                headers (dict, optional): Cabeçalhos HTTP opcionais para a requisição da chave. Se não fornecido,
                                          cabeçalhos padrão serão utilizados.

            Returns:
                dict: Um dicionário contendo as seguintes chaves:
                    - 'key' (str): A chave de criptografia em hexadecimal.
                    - 'iv' (str): O vetor de inicialização (IV) em hexadecimal, se disponível.

                Caso não seja possível extrair a URL da chave ou o IV, retorna None.

            Examples:
                ```python
                m3u8_content = '''
                #EXTM3U
                #EXT-X-KEY:METHOD=AES-128,URI="https://example.com/key.bin",IV=0x1234567890abcdef
                #EXTINF:10.0,
                http://example.com/segment1.ts
                '''
                player = "https://example.com"
                result = EncryptSuport.get_url_key_m3u8(m3u8_content, player)
                print(result)
                # Saída esperada:
                # {'key': 'aabbccddeeff...', 'iv': '1234567890abcdef'}

                # Com cabeçalhos personalizados
                headers = {
                    "Authorization": "Bearer your_token"
                }
                result = EncryptSuport.get_url_key_m3u8(m3u8_content, player, headers=headers)
                print(result)
                ```

            Raises:
                requests.HTTPError: Se a requisição HTTP para a chave falhar.
            """
            pattern = r'#EXT-X-KEY:.*URI="([^"]+)"(?:.*,IV=(0x[0-9A-Fa-f]+))?'
            match = re.search(pattern, m3u8_content)
            data = {}
            if match:
                url_key = f"{player}{match.group(1)}"
                iv_hex = match.group(2)
                if not headers:
                    headers_default = {
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Content-Length": "583",
                        "Content-Type": "text/plain",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Ch-Ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"118\", \"Chromium\";v=\"118\"",
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": "\"Windows\"",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                      "Chrome/118.0.0.0 Safari/537.36"
                    }
                    headers = headers_default

                    try:
                        resp = requests.get(url_key, headers=headers)
                        resp.raise_for_status()
                        key_bytes = resp.content
                        key_hex = key_bytes.hex()
                        data['key'] = key_hex
                        if iv_hex:
                            data['iv'] = iv_hex[2:]  # Remove '0x' prefix
                        return data
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
                        raise M3u8NetworkingError(
                            f"Erro de conexão: Não foi possível se conectar ao servidor. Detalhes: {e}")

            else:
                return None

    @classmethod
    class M3u8AnalyzerDownloader:
        """Requer ffmpeg,use o comando configure-ffmpeg"""

        @staticmethod
        def downloader_and_remuxer_segments(
                url_playlist: str,
                output: str,
                key_hex: str = None,
                iv_hex: str = None,
                player: str = None,
                headers: dict = None,
                segmentsType: str = None,
                logs: bool = None
        ) -> None:
            """
            Baixa os segmentos de uma playlist M3U8, opcionalmente descriptografa-os, e os combina em um arquivo de vídeo.

            Este método faz o download dos segmentos de uma playlist M3U8, possibilita a descriptografia dos segmentos usando uma
            chave e um IV fornecidos, e combina os segmentos em um único arquivo de vídeo. O tipo de segmento (por exemplo,
            '.ts' ou '.m4s') pode ser especificado. Após o processamento, o método remove os arquivos temporários criados durante
            o processo.

            Args:
                url_playlist (str): URL da playlist M3U8 contendo a lista de segmentos.
                output (str): Caminho para o arquivo de saída final (por exemplo, 'dir/nome.mp4').
                key_hex (Optional[str]): Chave de descriptografia em formato hexadecimal (opcional).
                iv_hex (Optional[str]): IV (vetor de inicialização) em formato hexadecimal (opcional).
                player (Optional[str]): URL base para os segmentos, se necessário para formar URLs completas.
                headers (Optional[dict]): Cabeçalhos HTTP adicionais para as requisições (opcional).
                segmentsType (Optional[str]): Tipo de segmento de saída, como '.ts' ou '.m4s' (opcional).
                logs (Optional[bool]): Se True, exibe a saída do processo de download e concatenação.

            Returns:
                None

            Raises:
                ValueError: Se a URL da playlist não for válida ou se não houver URL base para os segmentos quando necessário.
                OSError: Se houver erros ao remover arquivos temporários ou o diretório temporário.
                requests.exceptions.RequestException: Se ocorrer um erro ao fazer a requisição HTTP.

            Examples:
                ```python
                url_playlist = "https://example.com/playlist.m3u8"
                output = "output/video.mp4"
                key_hex = "00112233445566778899aabbccddeeff"
                iv_hex = "00112233445566778899aabbccddeeff"
                player = "https://example.com/"
                headers = {
                    "Accept": "application/json",
                    "User-Agent": "CustomAgent/1.0"
                }
                segmentsType = ".ts"

                M3u8Analyzer.downloader_and_remuxer_segments(
                    url_playlist=url_playlist,
                    output=output,
                    key_hex=key_hex,
                    iv_hex=iv_hex,
                    player=player,
                    headers=headers,
                    segmentsType=segmentsType,
                    logs=True
                )
                ```

            Notes:
                - O método cria um diretório temporário para armazenar os segmentos baixados e, em seguida, remove-o após a concatenação.
                - Se ocorrer um erro durante a requisição HTTP ou o processo de concatenação, o método tentará remover arquivos temporários criados.
                - A chave e o IV fornecidos são usados para descriptografar os segmentos se fornecidos; caso contrário, os segmentos são baixados diretamente.
            """
            if not M3u8Analyzer.M3u8AnalyzerDownloader.__verific_path_bin(binPath=ffmpeg_bin, typePath='file'):
                parser.install_bins()

            if not (url_playlist.startswith('http://') or url_playlist.startswith('https://')):
                raise M3u8Error("A URL é inválida!")

            resposta = requests.get(url_playlist, headers=headers)
            resposta.raise_for_status()
            playlist = resposta.text
            urls_segmentos = [linha for linha in playlist.splitlines() if linha and not linha.startswith('#')]
            arquivos_temporarios = []
            extens = '.ts'

            try:
                for i, url_segmento in enumerate(urls_segmentos):
                    if segmentsType:
                        if '.m4s' in segmentsType:
                            extens = '.m4s'

                    arquivo_temporario = fr'{temp_dir}\seg_{i}{extens}'
                    arquivos_temporarios.append(arquivo_temporario)

                    if not url_segmento.startswith("https://"):
                        if player:
                            url_segmento = f"{player}{url_segmento}"
                        else:
                            raise ValueError("Não há URL base para os segmentos.")

                    if key_hex and iv_hex:
                        key = bytes.fromhex(key_hex)
                        iv = bytes.fromhex(iv_hex)
                        M3u8Analyzer.M3u8AnalyzerDownloader.__baixar_segmento(
                            url_segmento=url_segmento,
                            path=arquivo_temporario,
                            key=key,
                            iv=iv,
                            headers=headers,
                            index=i + 1,
                            total=len(urls_segmentos),
                            logs=logs
                        )
                    else:
                        M3u8Analyzer.M3u8AnalyzerDownloader.__baixar_segmento(
                            url_segmento=url_segmento,
                            path=arquivo_temporario,
                            headers=headers,
                            index=i + 1,
                            total=len(urls_segmentos),
                            logs=logs
                        )

                # Concatena os segmentos em um arquivo de vídeo final
                M3u8Analyzer.M3u8AnalyzerDownloader.__ffmpeg_concatener(output=output, extension=extens)

            except requests.exceptions.ChunkedEncodingError as e:
                raise M3u8NetworkingError(f"Erro de codificação em partes: {e}")
            except requests.exceptions.UnrewindableBodyError:
                raise M3u8NetworkingError("Erro: Corpo da solicitação não pode ser rebobinado.")
            except requests.exceptions.RetryError as e:
                raise M3u8NetworkingError(f"Erro de tentativa: {e}")
            except requests.exceptions.StreamConsumedError:
                raise M3u8NetworkingError("Erro: Fluxo de resposta já consumido.")
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
            except requests.exceptions.ContentDecodingError as e:
                raise M3u8NetworkingError(f"Erro de decodificação de conteúdo: {e}")
            except requests.exceptions.HTTPError as e:
                raise M3u8NetworkingError(f"Erro HTTP: {e}")
            except requests.exceptions.ProxyError as e:
                raise M3u8NetworkingError(f"Erro de proxy: {e}")
            except requests.exceptions.SSLError as e:
                raise M3u8NetworkingError(f"Erro SSL: {e}")
            except requests.exceptions.ConnectionError:
                raise M3u8NetworkingError("Erro: O servidor ou o servidor encerrou a conexão.")
            except requests.exceptions.Timeout:
                raise M3u8NetworkingError(
                    "Erro de tempo esgotado: A conexão com o servidor demorou muito para responder.")
            except requests.exceptions.TooManyRedirects:
                raise M3u8NetworkingError("Erro de redirecionamento: Muitos redirecionamentos.")
            except requests.exceptions.URLRequired:
                raise M3u8NetworkingError("Erro: URL é necessária para a solicitação.")
            except requests.exceptions.RequestException as e:
                raise M3u8NetworkingError(f"Erro de conexão: Não foi possível se conectar ao servidor. Detalhes: {e}")
            except OSError as e:
                print(f"Erro ao acessar o sistema de arquivos: {e}")

            except ValueError as e:
                raise M3u8FileError(f"Erro de valor: {e}")
            except requests.exceptions.BaseHTTPError as e:
                raise M3u8NetworkingError(f"Erro HTTP básico: {e}")

            finally:
                # Remover arquivos temporários
                for arquivo in arquivos_temporarios:
                    if os.path.isfile(arquivo):
                        try:
                            os.remove(arquivo)
                        except OSError as e:
                            print(f"Erro ao remover o arquivo {arquivo}: {e}")

                # Remover o diretório temporário
                if os.path.exists(temp_dir):
                    try:
                        sys.stdout.flush()
                        shutil.rmtree(temp_dir, onerror=M3u8Analyzer.M3u8AnalyzerDownloader.__handle_remove_readonly)
                    except PermissionError as e:
                        print(f"Permissão negada ao tentar remover o diretório {temp_dir}: {e}")
                    except OSError as e:
                        print(f"Erro ao remover o diretório {temp_dir}: {e}")
                    except Exception as e:
                        print(f"Erro inesperado ao remover o diretório {temp_dir}: {e}")

        @staticmethod
        def __handle_remove_readonly(func, path, exc_info):
            """Função de callback para lidar com arquivos somente leitura."""
            os.chmod(path, stat.S_IWRITE)
            func(path)

        @staticmethod
        def __baixar_segmento(url_segmento: str, path: str, index, total, key: bytes = None, iv: bytes = None,
                              headers: dict = None, logs=None):
            global Novideo, Noaudio
            """
            Baixa um segmento de vídeo e, se necessário, o descriptografa.
            Em seguida, verifica se o vídeo possui áudio.
            Args:
                url_segmento(str): URL do segmento.
                path(str): Caminho de saída para salvar o segmento.
                key(bytes,opcional): Chave de descriptografia em bytes (opcional).
                iv(bytes,opcional): IV (vetor de inicialização) em bytes (opcional).
                headers(dict,opcional): Cabeçalhos HTTP adicionais para a requisição (opcional).
                logs(bool,opcional): Exibe o progresso.
            Returns: 
                  None
            """
            headers_default = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "Content-Length": "583",
                "Content-Type": "text/plain",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Ch-Ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"118\", \"Chromium\";v=\"118\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/118.0.0.0 Safari/537.36"
            }
            try:
                if not headers:
                    headers = headers_default
                resposta = requests.get(url_segmento, headers=headers, stream=True)
                total_bytes = 0
                chunk_size = 1024  # Definir o tamanho do chunk (1 KB)
                if logs:
                    print(f"Baixando Segmentos [{index}/{total}]", end=" ")
                with open(path, 'wb') as arquivo_segmento:
                    for chunk in resposta.iter_content(chunk_size=chunk_size):
                        if chunk:
                            arquivo_segmento.write(chunk)
                            total_bytes += len(chunk)
                    arquivo_segmento.close()
                # Descriptografar se necessário
                if key and iv:
                    M3u8Analyzer.M3u8AnalyzerDownloader.__descriptografar_segmento(path, key, iv, logs)
                # Verificar se o vídeo tem áudio e vídeo
                has_audio = M3u8Analyzer.M3u8AnalyzerDownloader.__verificar_audio(path)
                has_video = M3u8Analyzer.M3u8AnalyzerDownloader.__verificar_video(path)
                if has_audio:
                    Noaudio = None
                else:
                    if logs:
                        print(" NOT audio ")
                    Noaudio = True
                if has_video:
                    Novideo = None
                else:
                    Novideo = True
                    if logs:
                        print(" NOT video ")
            except FileNotFoundError:
                raise M3u8FileError(f"Erro: Arquivo ou diretório '{path}' não encontrado.")
            except PermissionError:
                raise M3u8FileError(f"Erro: Permissão negada ao tentar acessar '{path}'.")
            except IsADirectoryError:
                raise M3u8FileError(f"Erro: '{path}' é um diretório, mas um arquivo era esperado.")
            except NotADirectoryError:
                raise M3u8FileError(f"Erro: '{path}' é um arquivo, mas um diretório era esperado.")
            except BlockingIOError:
                raise M3u8FileError(f"Erro: Operação de E/S bloqueada ao tentar acessar '{path}'.")
            except EOFError:
                raise M3u8FileError(f"Erro: Fim inesperado do arquivo '{path}'.")
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
            except Exception as e:  # Captura todas as outras exceções, incluindo OSError e IOError
                raise M3u8FileError(f"Erro inesperado ao manipular arquivo: {e}")
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

        @staticmethod
        def __descriptografar_segmento(path: str, key: bytes, iv: bytes, logs=None):
            """
            Descriptografa um segmento de vídeo se necessário.

            Args:
                path (str): Caminho do arquivo a ser descriptografado.
                key (bytes): Chave de descriptografia em bytes.
                iv (bytes): IV (vetor de inicialização) em bytes.
                logs (bool, optional): Se True, exibe a barra de progresso.
            Returns:
                None
            """
            try:
                # Abre o arquivo e lê os bytes do segmento
                with open(path, 'rb') as arquivo_segmento:
                    segmento_bytes = arquivo_segmento.read()

                # Configura o backend e o cipher
                backend = default_backend()
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
                decryptor = cipher.decryptor()
                unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

                # Define o tamanho do buffer e o progresso
                buffer_size = 64 * 1024  # 64 KB
                total_size = len(segmento_bytes)
                decrypted_segment = bytearray()

                if logs:
                    # Exibe a barra de progresso se logs for True
                    for i in range(0, total_size, buffer_size):
                        chunk = segmento_bytes[i:i + buffer_size]
                        decrypted_chunk = decryptor.update(chunk)
                        decrypted_segment.extend(decrypted_chunk)

                        # Atualiza a barra de progresso
                        progress = (i + len(chunk)) / total_size * 100
                        sys.stdout.write(f'\rDescriptografando: {progress:.2f}%')
                        sys.stdout.flush()

                    decrypted_segment.extend(decryptor.finalize())
                    segment = unpadder.update(decrypted_segment) + unpadder.finalize()

                    # Conclui a barra de progresso
                    sys.stdout.write('\rDescriptografado com sucesso!            \n')
                    sys.stdout.flush()

                else:
                    # Sem barra de progresso
                    for i in range(0, total_size, buffer_size):
                        chunk = segmento_bytes[i:i + buffer_size]
                        decrypted_chunk = decryptor.update(chunk)
                        decrypted_segment.extend(decrypted_chunk)

                    decrypted_segment.extend(decryptor.finalize())
                    segment = unpadder.update(decrypted_segment) + unpadder.finalize()

                # Escreve o segmento descriptografado de volta ao arquivo
                with open(path, 'wb') as arquivo_segmento:
                    arquivo_segmento.write(segment)

            except FileNotFoundError as e:
                # Erro ao abrir ou localizar o arquivo
                raise M3u8FileError(f"Erro: Arquivo não encontrado - {e}\n")
            except IOError as e:
                # Erro de I/O durante leitura ou escrita
                raise M3u8FileError(f"Erro de I/O ao acessar o arquivo - {e}\n")
            except ValueError as e:
                # Erro relacionado ao valor fornecido (por exemplo, chave ou IV incorretos)
                raise M3u8FileError(f"Erro de valor - {e}\n")
            except Exception as e:
                # Captura qualquer outro erro inesperado
                raise M3u8Error(f"Erro inesperado: {e}\n")

        @staticmethod
        def __verificar_audio(path: str) -> bool:
            """
            Verifica se o vídeo contém faixas de áudio usando ffmpeg.

            Args:
                path: Caminho do arquivo de vídeo.

            Returns:
                 bool: True se o vídeo contiver áudio, False caso contrário.
            """
            if not M3u8Analyzer.M3u8AnalyzerDownloader.__verific_path_bin(binPath=ffmpeg_bin, typePath='file'):
                parser.install_bins()
            try:
                # Comando para obter informações sobre o arquivo usando ffmpeg
                resultado = subprocess.run(
                    [ffmpeg_bin, '-i', path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                # Procurar por linhas contendo "Audio:" no stderr
                return 'Audio:' in resultado.stderr
            except FileNotFoundError:
                sys.stderr.write(
                    "ffmpeg não encontrado..\n")
                return False
            except subprocess.CalledProcessError as e:
                sys.stderr.write(f"Erro ao executar ffmpeg: {e}\n")
                return False

        @staticmethod
        def __verificar_video(path: str) -> bool:
            """
            Verifica se o vídeo contém faixas de vídeo usando ffmpeg.

            Args:
                path: Caminho do arquivo de vídeo.

            Returns:
                bool: True se o vídeo contiver vídeo, False caso contrário.
            """
            if not M3u8Analyzer.M3u8AnalyzerDownloader.__verific_path_bin(binPath=ffmpeg_bin, typePath='file'):
                parser.install_bins()
            try:
                # Comando para obter informações sobre o arquivo usando ffmpeg
                resultado = subprocess.run(
                    [ffmpeg_bin, '-i', path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                # Procurar por linhas contendo "Video:" no stderr
                return 'Video:' in resultado.stderr
            except FileNotFoundError:
                sys.stderr.write(
                    "ffmpeg não encontrado..\n")
                return False
            except subprocess.CalledProcessError as e:
                sys.stderr.write(f"Erro ao executar ffmpeg: {e}\n")
                return False

        @staticmethod
        def __clear_line():
            """
            Limpa a linha atual no terminal de forma compatível com diferentes sistemas.

            Essa função utiliza o caractere de retrocesso para mover o cursor para o
            início da linha e sobrescreve o conteúdo da linha com espaços em branco,
            limpando assim a linha no terminal.

            """
            # Mover o cursor para o início da linha e sobrescrever com espaços
            sys.stdout.write('\r' + ' ' * 100 + '\r')
            sys.stdout.flush()

        @staticmethod
        def __filter_ffmpeg_output(line: bytes, index: int):
            """
            Filtra e imprime apenas as linhas que contêm a palavra 'Opening' na saída do ffmpeg.
            Args:
                line(bytes): Linha de saída do ffmpeg.
                index(int): Índice de progresso.
            Returns:
                 None
            """
            lines = line.decode('utf-8').strip()
            # Verifica se a linha contém a palavra 'Opening'
            if re.search(r'Opening', lines):
                M3u8Analyzer.M3u8AnalyzerDownloader.__clear_line()  # Limpa a linha anterior
                message = f'\rO {Fore.LIGHTBLUE_EX}ffmpeg{Style.RESET_ALL} está obtendo o segmento {Fore.LIGHTRED_EX}[nº{index}]{Style.RESET_ALL}'
                sys.stdout.write(message)
                sys.stdout.flush()
                time.sleep(0.1)
                return True  # Indica que o índice deve ser incrementado
            return False  # Indica que o índice não deve ser incrementado

        @staticmethod
        def __filter_ffmpeg_stdout(line: bytes, filtering: str):
            """
            Filtra apenas as linhas que contêm o filtro na saída do ffmpeg.
            Args:
                line(bytes): Linha de saída do ffmpeg.
                filtering(str): o filtro desejado
            Returns:
                 o valor da linha
            """
            lines = line.decode('utf-8').strip()
            # Verifica se a linha contém o filtro
            if re.search(fr'{filtering}', lines):
                return True
            else:
                return False

        @staticmethod
        def __ffmpeg_concatener(output: str, extension: str):
            """
            Concatena os segmentos de vídeo em um único arquivo de vídeo usando FFmpeg.

            Args:
                output (str): Caminho de saída para o vídeo final, incluindo o nome do arquivo e extensão (ex: 'dir/nome.mp4').
                extension (str): Extensão dos arquivos de vídeo a serem concatenados (ex: '.ts').

            Returns:
                None
            """
            if not M3u8Analyzer.M3u8AnalyzerDownloader.__verific_path_bin(binPath=ffmpeg_bin, typePath='file'):
                parser.install_bins()
            # Defina o nome do arquivo de lista
            arquivo_lista = fr'{temp_dir}\lista.txt'

            def extrair_numero(nome_arquivo):
                match = re.search(r'(\d+)', nome_arquivo)
                return int(match.group(1)) if match else float('inf')

            # Defina o diretório onde estão os arquivos .ts
            diretorio_ts = temp_dir
            # Abre o arquivo lista.txt para escrita
            with open(arquivo_lista, 'w') as f:
                # Lista todos os arquivos no diretório e filtra apenas os arquivos .ts
                arquivos_ts = [arquivo for arquivo in os.listdir(diretorio_ts) if arquivo.endswith(f'{extension}')]
                # Ordena os arquivos com base no número extraído
                arquivos_ts.sort(key=extrair_numero)
                # Escreve cada arquivo no lista.txt
                for arquivo in arquivos_ts:
                    caminho_absoluto = os.path.join(diretorio_ts, arquivo)
                    f.write(f"file '{caminho_absoluto}'\n")
            cmd = [
                fr'{ffmpeg_bin}',
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', arquivo_lista,
                '-c', 'copy',
                f'{output}'
            ]
            process = ''
            So = M3u8Analyzer.M3u8AnalyzerDownloader.__ocute_terminal()
            if So == 'w':
                # Configura o startupinfo para ocultar o terminal no Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                # Executa o comando FFmpeg ocultando o terminal
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           startupinfo=startupinfo)
            elif So == 'l':
                # Executa o comando FFmpeg ocultando saídas no terminal Linux
                process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            index = 0
            while True:
                output = process.stdout.readline()
                # print(output.decode('utf-8').strip())
                if process.poll() is not None and output == b'':
                    break
                if output:
                    if M3u8Analyzer.M3u8AnalyzerDownloader.__filter_ffmpeg_output(output, index):
                        index += 1  # Incrementa o índice apenas se a linha corresponder ao filtro
            if Noaudio:
                print(f'Video foi salvo mais não tem áudio!', end='')
                print("obtenha a playlist de áudio e a remuxe nesse vídeo")
                sys.stdout.flush()
            if Novideo:
                print(f'Video foi salvo mais não tem vídeo!', end='')
                print(" obtenha a playlist de áudio e a remuxe nesse áudio")
                sys.stdout.flush()
            print("Processo Finalisado: ", end=" ")
            if Noaudio is None:
                print("Audio\t\t\tOK", end="")
            if Novideo:
                print("Video\t\t\tOK", end="")

        @staticmethod
        def ffmpeg_donwloader(
                input_url: str,
                output: str,
                type_playlist: str,
                resolution: str = None,
                logs: bool = None
        ) -> None:
            """
            Baixa um vídeo ou áudio usando FFmpeg a partir de uma URL de playlist M3U8.

            Este método utiliza FFmpeg para baixar e salvar vídeo ou áudio de uma URL M3U8. Dependendo do tipo de
            playlist ('audio' ou 'video'), o método pode especificar a resolução para vídeos ou escolher um formato
            padrão para áudios.

            Args:
                input_url (str): URL da playlist M3U8 contendo os segmentos de vídeo ou áudio.
                output (str): Caminho para o arquivo final a ser salvo, com extensão apropriada (por exemplo, 'dir/nome.mp4' ou 'dir/nome.mp3').
                type_playlist (str): Tipo da playlist, deve ser 'audio' ou 'video'.
                resolution (Optional[str]): Define a resolução desejada para o vídeo ('lower', 'medium', 'high'). Ignorado para áudio.
                logs (Optional[bool]): Se True, exibe a saída do FFmpeg. Se False ou None, a saída é suprimida.

            Returns:
                None

            Raises:
                SyntaxError: Se o parâmetro 'type_playlist' não for fornecido como string.
                ValueError: Se o tipo de playlist fornecido não for 'audio' ou 'video'.

            Examples:
                ```python
                # Para baixar um vídeo com resolução 'medium'
                ffmpeg_donwloader(
                    input_url="https://example.com/video_playlist.m3u8",
                    output="output/video.mp4",
                    type_playlist="video",
                    resolution="medium",
                    logs=True
                )

                # Para baixar áudio sem especificar resolução
                ffmpeg_donwloader(
                    input_url="https://example.com/audio_playlist.m3u8",
                    output="output/audio.mp3",
                    type_playlist="audio",
                    logs=False
                )
                ```

            Notes:
                - O comando FFmpeg é executado de forma oculta no Windows e Linux para evitar exibição de terminal.
                - O parâmetro `resolution` é usado somente para vídeos, e o padrão é 'high' se a resolução não for reconhecida.
                - A saída do FFmpeg pode ser controlada com o parâmetro `logs`, que, se definido como True, exibe as mensagens de progresso e erros.

            """
            if not M3u8Analyzer.M3u8AnalyzerDownloader.__verific_path_bin(binPath=ffmpeg_bin, typePath='file'):
                parser.install_bins()
            if not isinstance(type_playlist, str):
                raise M3u8Error("O parâmetro 'type_playlist' deve ser uma string!")
            if type_playlist not in ['audio', 'video']:
                raise M3u8Error("O parâmetro 'type_playlist' deve ser 'audio' ou 'video'")

            def run_ffmpeg(cmd):
                process = ''
                So = M3u8Analyzer.M3u8AnalyzerDownloader.__ocute_terminal()
                if So == 'w':
                    # Configura o startupinfo para ocultar o terminal no Windows
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    # Executa o comando FFmpeg ocultando o terminal
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               startupinfo=startupinfo)
                elif So == 'l':
                    # Executa o comando FFmpeg ocultando saídas no terminal Linux
                    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                index = 0
                while True:
                    output_line = process.stdout.readline()
                    if M3u8Analyzer.M3u8AnalyzerDownloader.__filter_ffmpeg_stdout(line=output_line,
                                                                                  filtering="Stream map 'v:2' matches "
                                                                                            "no streams."):

                        process.kill()
                        return False
                    elif M3u8Analyzer.M3u8AnalyzerDownloader.__filter_ffmpeg_stdout(line=output_line,
                                                                                    filtering='Error opening input:'):
                        process.kill()
                        raise M3u8FfmpegDownloadError("este arquivo de entrada especificado é inválido!")
                    # Error opening output fil
                    elif (M3u8Analyzer.M3u8AnalyzerDownloader.__filter_ffmpeg_stdout(line=output_line,
                                                                                     filtering='Error opening output '
                                                                                               'file') or M3u8Analyzer.
                                  M3u8AnalyzerDownloader.__filter_ffmpeg_stdout(line=output_line,
                                                                                filtering='Unable to choose an '
                                                                                          'output format for '';'
                                                                                          ' use'
                                                                                          ' a standard extension'
                                                                                          ' for'
                                                                                          ' the filename or specify'
                                                                                          ' the format manually')):
                        process.kill()
                        raise M3u8FfmpegDownloadError("este arquivo de saída especificado é inválido!")

                    if logs:
                        clean_output = "\n".join(
                            line for line in output_line.decode('utf-8').splitlines() if line.strip())
                        if clean_output:
                            print(clean_output)

                    if process.poll() is not None and output_line == b'':
                        break
                    if logs is None and output_line:
                        if M3u8Analyzer.M3u8AnalyzerDownloader.__filter_ffmpeg_output(output_line, index):
                            index += 1

                return process.returncode == 0

            # Inicializa o comando FFmpeg
            cmd = []
            resolution_map = {}
            if type_playlist == 'video':
                resolution_map = {
                    'lower': 'v:0',
                    'medium': 'v:1',
                    'high': 'v:2'
                }
                video_map = resolution_map.get(resolution, 'v:2')
                cmd = [
                    f'{ffmpeg_bin}',
                    '-y',
                    '-i', input_url,
                    '-map', video_map,
                    '-c', 'copy',
                    output
                ]
            elif type_playlist == 'audio':
                resolution_map = {
                    'lower': 'a:0',
                    'medium': 'a:1',
                    'high': 'a:2'
                }
                audio_map = resolution_map.get(resolution, 'a:0')
                cmd = [
                    f'{ffmpeg_bin}',
                    '-y',
                    '-i', input_url,
                    '-map', audio_map,
                    '-c', 'copy',
                    output
                ]

            # Tenta baixar com o mapeamento especificado
            success = run_ffmpeg(cmd)

            # Se falhar devido a mapeamento, tenta sem map
            if not success:
                cmd = cmd[:4]  # Remove o mapeamento '-map' e a opção correspondente
                if type_playlist == 'video':
                    cmd += ['-c:v', 'copy', output]
                elif type_playlist == 'audio':
                    cmd += ['-c:a', 'copy', output]
                success = run_ffmpeg(cmd)
                if not success:
                    raise M3u8FfmpegDownloadError(f"Falha ao baixar o conteúdo com FFmpeg")

        @staticmethod
        def remuxer_audio_and_video(
                audioPath: str,
                videoPath: str,
                outputPath: str,
                logs: bool = None
        ) -> None:
            """
            Remuxa um arquivo de áudio e um arquivo de vídeo em um único arquivo MP4 usando FFmpeg.

            Este método combina um arquivo de áudio e um arquivo de vídeo em um único arquivo MP4 sem recodificação dos
            streams, o que preserva a qualidade original dos arquivos de entrada.

            Args:
                audioPath (str): Caminho para o arquivo de áudio que será combinado.
                videoPath (str): Caminho para o arquivo de vídeo que será combinado.
                outputPath (str): Caminho de saída para o arquivo remuxado, por exemplo, 'dir/nome.mp4'.
                logs (Optional[bool]): Se True, exibe a saída do FFmpeg durante o processamento. Se False ou None, a saída é suprimida.

            Returns:
                None

            Raises:
                ValueError: Se os caminhos dos arquivos de áudio ou vídeo não existirem.

            Examples:
                ```python
                # Para remuxar áudio e vídeo em um único arquivo MP4 com logs ativados
                remuxer_audio_and_video(
                    audioPath="path/to/audio.mp3",
                    videoPath="path/to/video.mp4",
                    outputPath="output/combined.mp4",
                    logs=True
                )

                # Para remuxar áudio e vídeo em um arquivo MP4 sem exibir logs
                remuxer_audio_and_video(
                    audioPath="path/to/audio.mp3",
                    videoPath="path/to/video.mp4",
                    outputPath="output/combined.mp4"
                )
                ```

            Notes:
                - O comando FFmpeg usa a opção `-c copy` para copiar os streams de áudio e vídeo sem recodificação, o que preserva a qualidade original.
                - A remoção dos arquivos de áudio e vídeo de entrada após o remuxing é tentada, mas qualquer falha na remoção é ignorada.
                - O comportamento da exibição de logs é controlado pelo parâmetro `logs`. Se `logs` for True, as mensagens de saída do FFmpeg são impressas no console.
            """
            if not M3u8Analyzer.M3u8AnalyzerDownloader.__verific_path_bin(binPath=ffmpeg_bin, typePath='file'):
                parser.install_bins()

            if not os.path.exists(audioPath) or not os.path.exists(videoPath):
                raise M3u8Error("Os caminhos dos arquivos de áudio ou vídeo não foram encontrados...")

            cmd = [
                ffmpeg_bin,
                '-y',  # Sobrescrever o arquivo de saída se já existir
                '-i', audioPath,  # Caminho do arquivo de áudio
                '-i', videoPath,  # Caminho do arquivo de vídeo
                '-c', 'copy',  # Copia os streams de áudio e vídeo sem recodificação
                '-map', '0:a',  # Mapeia o áudio da primeira entrada (0) - arquivo de áudio
                '-map', '1:v',  # Mapeia o vídeo da segunda entrada (1) - arquivo de vídeo
                outputPath
            ]

            process = ''
            So = M3u8Analyzer.M3u8AnalyzerDownloader.__ocute_terminal()
            if So == 'w':
                # Configura o startupinfo para ocultar o terminal no Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                # Executa o comando FFmpeg ocultando o terminal
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           startupinfo=startupinfo)
            elif So == 'l':
                # Executa o comando FFmpeg ocultando saídas no terminal Linux
                process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            # Envia a saída em tempo real para o cliente
            for line in iter(process.stdout.readline, b''):
                try:
                    # Tente decodificar os bytes como UTF-8
                    decoded_line = line.decode('utf-8').strip()
                    if logs:
                        print(decoded_line)
                except UnicodeDecodeError:
                    # Em caso de erro de decodificação, você pode ignorar a linha ou tratar de outra forma
                    continue

            # Tenta remover os arquivos de áudio e vídeo após o remuxing
            try:
                os.remove(audioPath)
                os.remove(videoPath)
            except Exception:
                pass

        @staticmethod
        def ffmpegImage(
                commands: list,
                logs: bool = None,
                callback: callable = None
        ) -> None:
            """
            Executa comandos personalizados no FFmpeg e processa a saída.

            Este método permite executar comandos FFmpeg fornecidos pelo usuário e oferece a opção de visualizar
            a saída do FFmpeg em tempo real. Além disso, é possível fornecer uma função de callback que será chamada
            com cada linha de saída gerada pelo FFmpeg.

            Args:
                commands (list): Lista de argumentos de comando para o FFmpeg. O binário do FFmpeg será adicionado automaticamente
                                 no início da lista de comandos fornecida.
                logs (Optional[bool]): Se True, exibe a saída do FFmpeg no console. Se False ou None, a saída é suprimida.
                callback (Optional[callable]): Função opcional que será chamada com cada linha de saída gerada pelo FFmpeg.
                                                A função deve aceitar um argumento, que é a linha de saída como uma string.

            Returns:
                None

            Raises:
                TypeError: Se o parâmetro 'commands' não for uma lista.

            Examples:
                ```python
                # Para executar um comando FFmpeg e exibir a saída
                ffmpegImage(
                    commands=['-i', 'input.mp4', '-vf', 'scale=1280:720', 'output.mp4'],
                    logs=True
                )

                # Para executar um comando FFmpeg com uma função de callback para processar a saída
                def process_output(line):
                    print(f"Saída do FFmpeg: {line}")

                ffmpegImage(
                    commands=['-i', 'input.mp4', '-vf', 'scale=1280:720', 'output.mp4'],
                    callback=process_output
                )
                ```

            Notes:
                - O parâmetro `commands` deve ser uma lista de argumentos de linha de comando válidos para o FFmpeg. O binário do FFmpeg é automaticamente adicionado à lista de comandos.
                - Se `logs` for True, a saída do FFmpeg será exibida no console, removendo as linhas em branco.
                - Se `callback` for fornecido, a função será chamada com cada linha de saída do FFmpeg, permitindo processamento personalizado da saída.
                - O método é capaz de ocultar a janela do terminal no Windows e suprimir a saída no Linux conforme a configuração do terminal.
            """
            if not M3u8Analyzer.M3u8AnalyzerDownloader.__verific_path_bin(binPath=ffmpeg_bin, typePath='file'):
                parser.install_bins()
            if not isinstance(commands, list):
                raise M3u8Error("O parâmetro 'commands' deve ser uma lista.")

            # Adiciona o binário FFmpeg no início da lista de comandos
            cmd = [ffmpeg_bin] + commands
            process = ''
            So = M3u8Analyzer.M3u8AnalyzerDownloader.__ocute_terminal()
            if So == 'w':
                # Configura o startupinfo para ocultar o terminal no Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                # Executa o comando FFmpeg ocultando o terminal
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                           startupinfo=startupinfo)
            elif So == 'l':
                # Executa o comando FFmpeg ocultando saídas no terminal Linux
                process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT, text=True)
            while True:
                output_line = process.stdout.readline()
                if output_line == '' and process.poll() is not None:
                    break
                if logs:
                    # Exibir a saída e remover linhas em branco
                    clean_output = "\n".join(
                        line for line in output_line.splitlines() if line.strip())
                    if clean_output:
                        print(clean_output)

                if callback and output_line:
                    # Chama o callback com a linha de saída
                    callback(output_line.strip())

        @staticmethod
        def __ocute_terminal():
            """
            Verifica o sistema operacional do usuário e retorna uma inicial correspondente.

            O método utiliza a biblioteca `platform` para identificar o sistema operacional e retorna:
            - 'w' para Windows
            - 'l' para Linux ou macOS (Darwin)
            - 'null' para outros sistemas operacionais não suportados

            Returns:
                str: Inicial correspondente ao sistema operacional do usuário.

            Example:
                ```python
                os_initial = M3U8Analyzer.__ocute_terminal()
                print(os_initial)
                ```
                'w','l', ou 'null', dependendo do sistema operacional
            """
            import platform
            system = platform.system()
            if system == 'Windows':
                return 'w'
            elif system == 'Linux' or system == 'Darwin':
                return 'l'
            else:
                return 'null'

        @staticmethod
        def __verific_path_bin(binPath, typePath):
            """
                    Esta função verifica se um caminho de arquivo ou diretório existe
                    e retorna True ou False.

                    Args:
                        binPath (str): O caminho a ser verificado.
                        typePath (str): O tipo de caminho a verificar ('file' para arquivo, 'dir' para diretório).

                    Returns:
                        bool: True se o caminho existir e for do tipo especificado, False caso contrário.
                    """

            if typePath == 'file':
                # Verifica se o caminho existe e é um arquivo
                return os.path.isfile(binPath)
            elif typePath == 'dir':
                # Verifica se o caminho existe e é um diretório
                return os.path.isdir(binPath)
            else:
                # Retorna False se o tipo de caminho não for 'file' ou 'dir'
                return False


class M3U8Playlist:
    def __init__(self, url: str, headers: dict = None):
        self.__parsing = M3u8Analyzer()
        self.__url = url
        self.__version = ''
        self.__number_segments = []
        self.__uris = []
        self.__playlist_type = None
        self.__headers = headers
        if not (url.startswith('https://') or url.startswith('http://')):
            raise ValueError("O Manifesto deve ser uma URL HTTPS ou HTTP!")

        self.__load_playlist()

    def __load_playlist(self):
        """
        Método privado para carregar a playlist a partir de uma URL ou arquivo.
        """
        self.__parsing = M3u8Analyzer()
        self.__content = self.__parsing.get_m3u8(url_m3u8=self.__url, headers=self.__headers)
        # Simulação do carregamento de uma playlist para este exemplo:
        self.__uris = self.__parsing.get_segments(self.__content).get('enumerated_uris')
        self.__number_segments = len(self.__uris)
        self.__playlist_type = self.__parsing.get_type_m3u8_content(self.__content)
        self.__version = self.__get_version_manifest(content=self.__content)
        self.__resolutions = self.__parsing.get_segments(self.__content).get('resolutions')

    def __get_version_manifest(self, content):
        """
        Obtém a versão do manifesto #EXTM em uma playlist m3u8.
        #EXT-X-VERSION:4
        #EXT-X-VERSION:3
        etc...
        :param content: Conteúdo da playlist m3u8.
        :return: A versão do manifesto encontrada ou None se não for encontrado.
        """
        # Expressão regular para encontrar o manifesto
        pattern = re.compile(r'#EXT-X-VERSION:(\d*)')
        match = pattern.search(content)

        if match:
            # Retorna a versão encontrada
            ver = f"#EXT-X-VERSION:{match.group(1)}"
            return ver

        else:
            return '#EXT-X-VERSION:Undefined'  # Default para versão 1 se não houver número

    def info(self):
        """
        Retorna informações básicas sobre a playlist.

        Returns:
            dict: Informações sobre a URL, versão do manifesto, número de segmentos, tipo da playlist, se é criptografada e URIs dos segmentos.
        """
        info = {
            "url": self.__url,
            "version_manifest": self.__version,
            "number_of_segments": self.__number_segments,
            "playlist_type": self.__playlist_type,
            "encript": self.__is_encrypted(url=self.__url, headers=self.__headers),
            "uris": self.__uris,
        }
        return info

    def __is_encrypted(self, url, headers: dict = None):
        parser = M3u8Analyzer()
        m3u8_content = parser.get_m3u8(url)
        player = parser.get_player_playlist(url)
        try:
            cript = parser.EncryptSuport.get_url_key_m3u8(m3u8_content=m3u8_content,
                                                          player=player,
                                                          headers=headers)
        except Exception as e:
            raise ValueError(f"erro {e}")
        return cript

    def this_encrypted(self):
        """
        Verifica se a playlist M3U8 está criptografada.

        Returns:
            bool: True se a playlist estiver criptografada, False caso contrário.
        """
        return self.__is_encrypted(url=self.__url, headers=self.__headers)

    def uris(self):
        """
        Retorna a lista de URIs dos segmentos.

        Returns:
            list: Lista de URIs dos segmentos.
        """
        return self.__uris

    def version_manifest(self):
        """
        Retorna a versão do manifesto da playlist M3U8.

        Returns:
            str: Versão do manifesto.
        """
        return self.__version

    def number_segments(self):
        """
        Retorna o número total de segmentos na playlist.

        Returns:
            int: Número de segmentos.
        """
        return self.__number_segments

    def playlist_type(self):
        """
        Retorna o tipo da playlist M3U8.

        Returns:
            str: Tipo da playlist.
        """
        return self.__playlist_type

    def get_resolutions(self):
        """
        Retorna as resoluções disponíveis na playlist M3U8.

        Returns:
            list: Lista de resoluções.
        """
        data = self.__resolutions
        resolutions = []
        for r in data:
            resolutions.append(r)
        return resolutions

    def filter_resolution(self, filtering: str):
        """
        Filtra e retorna a URL do segmento com a resolução especificada.

        Args:
            filtering (str): Resolução desejada (ex: '1920x1080').

        Returns:
            Optional[str]: URL do segmento correspondente à resolução, ou None se não encontrado.
        """
        data = self.__resolutions
        if filtering in data:
            return data.get(filtering)
        else:
            return None


class ParsingM3u8:
    """Classe para parsear playlists M3U8."""

    @staticmethod
    def parsing_m3u8(url: str, headers: dict = None) -> M3U8Playlist:
        """
        Cria uma instância de M3U8Playlist a partir de uma URL de playlist M3U8.

        Este método estático é utilizado para inicializar e retornar um objeto da classe `M3U8Playlist`,
        que fornece funcionalidades para análise e manipulação de playlists M3U8.

        Args:
            url (str): URL da playlist M3U8 que deve ser parseada.
            headers (Optional[dict]): Cabeçalhos HTTP adicionais para a requisição (opcional).

        Returns:
            M3U8Playlist: Uma instância da classe `M3U8Playlist` inicializada com a URL fornecida.

        Raises:
            ValueError: Se a URL não for uma URL válida.

        Examples:
            ```python
            url_playlist = "https://example.com/playlist.m3u8"
            headers = {
                "User-Agent": "CustomAgent/1.0"
            }

            playlist = ParsingM3u8.parsing_m3u8(url=url_playlist, headers=headers)

            print(playlist.info())
            ```

        Notes:
            - Certifique-se de que a URL fornecida é uma URL válida e acessível.
            - Se os cabeçalhos forem fornecidos, eles serão utilizados na requisição para obter o conteúdo da playlist.
        """
        return M3U8Playlist(url=url, headers=headers)


wrapper_playlists = ParsingM3u8()
