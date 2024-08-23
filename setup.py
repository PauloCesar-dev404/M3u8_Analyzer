from setuptools import setup

# Lê o conteúdo do README.md
long_description = '''
<div align="center">
![logo](https://github.com/PauloCesar-dev404/M3u8_Analyzer/blob/main/logo.ico)
![Versão](https://img.shields.io/badge/version-1.0.2-orange)
![Licença](https://img.shields.io/badge/license-MIT-orange)![Estrelas](https://img.shields.io/github/stars/PauloCesar-dev404/M3u8_Analyzer?style=social)
![Downloads](https://img.shields.io/pypi/dm/m3u8-analyzer)


</div>
    
    
    biblioteca Python projetada para trabalhar com playlists M3U8. Ela fornece ferramentas para:
    
    - Analisar e extrair informações de arquivos M3U8, incluindo URLs de segmentos e chaves de criptografia.
    - Baixar e concatenar segmentos de vídeo e áudio em arquivos finais.
    - Suporte a criptografia AES-128, incluindo obtenção de chaves e vetores de inicialização (IV).
    - Manipulação de segmentos de mídia com FFmpeg, incluindo remuxing de áudio e vídeo.
    Esta biblioteca é útil para desenvolvedores ou usuários comuns que precisam trabalhar com conteúdo de streaming HLS (HTTP Live Streaming) e realizar operações avançadas de processamento de mídia.
    '''

setup(
    name="m3u8_analyzer",
    url='https://paulocesar-dev404.github.io/M3u8_Analyzer/',
    include_dirs=['bin'],
    version="1.0.2",
    license="MIT",
    author="PauloCesar0073-dev404",
    author_email="paulocesar0073dev404@gmail.com",
    description="Análise de dados de HLS m3u8",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["hls", "m3u8","m3u8analyzer","m3u8_analyzer","M3u8Analyzer","M3u8_Analyzer"],
    packages=["m3u8_analyzer"],
    install_requires=['cryptography', 'requests'],
    include_package_data=True,  # Inclui dados adicionais do pacote, como README.md
)
