class M3u8AnalyzerExceptions(Exception):
    def __init__(self, message="Erro na análise da playlist M3U8", errors=None):
        """
        Exceção base para erros relacionados à análise de playlists M3U8.

        Args:
            message (str): Mensagem descritiva do erro. Padrão é "Erro na análise da playlist M3U8".
            errors (list, optional): Lista de erros adicionais ou detalhes para diagnóstico. Padrão é None.
        """
        super().__init__(message)
        self.errors = errors

    def __str__(self):
        """
        Retorna a representação em string da exceção.

        Returns:
            str: Mensagem de erro formatada com detalhes adicionais, se presentes.
        """
        if self.errors:
            return f"{super().__str__()} | Erros adicionais: {self.errors}"
        return super().__str__()


class M3u8DownloadError(M3u8AnalyzerExceptions):
    def __init__(self, message="Erro durante o download da playlist M3U8", errors=None):
        """
        Exceção para erros específicos ocorridos durante o download de uma playlist M3U8.

        Args:
            message (str): Mensagem descritiva do erro. Padrão é "Erro durante o download da playlist M3U8".
            errors (list, optional): Lista de erros adicionais ou detalhes para diagnóstico. Padrão é None.
        """
        super().__init__(message, errors)


class M3u8FfmpegDownloadError(M3u8AnalyzerExceptions):
    def __init__(self, message="Erro durante o download da playlist M3U8 com ffmpeg", errors=None):
        """
        Exceção para erros específicos ocorridos durante o download de uma playlist M3U8 usando ffmpeg.

        Args:
            message (str): Mensagem descritiva do erro. Padrão é "Erro durante o download da playlist M3U8 com ffmpeg".
            errors (list, optional): Lista de erros adicionais ou detalhes para diagnóstico. Padrão é None.
        """
        super().__init__(message, errors)


class M3u8NetworkingError(M3u8AnalyzerExceptions):
    def __init__(self, message="Erro de rede durante o download da playlist M3U8", errors=None):
        """
        Exceção para erros relacionados à rede durante o download de uma playlist M3U8.

        Args:
            message (str): Mensagem descritiva do erro. Padrão é "Erro de rede durante o download da playlist M3U8".
            errors (list, optional): Lista de erros adicionais ou detalhes para diagnóstico. Padrão é None.
        """
        super().__init__(message, errors)


class M3u8Error(M3u8AnalyzerExceptions):
    def __init__(self, message="Erro inesperado na análise de playlist M3U8", errors=None):
        """
        Exceção para erros inesperados que não se encaixam em outras categorias.

        Args:
            message (str): Mensagem descritiva do erro. Padrão é "Erro inesperado na análise de playlist M3U8".
            errors (list, optional): Lista de erros adicionais ou detalhes para diagnóstico. Padrão é None.
        """
        super().__init__(message, errors)


class M3u8FileError(M3u8AnalyzerExceptions):
    def __init__(self, message="Erro ao manipular o arquivo da playlist M3U8", errors=None):
        """
        Exceção para erros ocorridos ao manipular arquivos relacionados a playlists M3U8.

        Args:
            message (str): Mensagem descritiva do erro. Padrão é "Erro ao manipular o arquivo da playlist M3U8".
            errors (list, optional): Lista de erros adicionais ou detalhes para diagnóstico. Padrão é None.
        """
        super().__init__(message, errors)
