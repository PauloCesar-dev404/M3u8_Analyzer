from setuptools import setup
import pathlib

# Lê o conteúdo do README.md
long_description = """
<div align="center">
  <h1>M3u8Analyzer</h1>
</div>

<p align="center">
  <code>version: 1.0.1</code> | <code>author: PauloCesar-dev404</code> | <code>LICENSE: MIT</code>
</p>



Este módulo Python nos permite extrair conteúdos de playlists de stream m3u8.


---
# instalação via git
````commandline
 pip install git+https://github.com/PauloCesar-dev404/M3u8_Analyzer

````
# instalação via Pypi
````commandline
pip install m3u8-analyzer
````
---
[Documentação](https://paulocesar-dev404.github.io/M3u8_Analyzer/)
💲[Apoie o projeto](https://apoia.se/paulocesar-dev404)

"""

setup(
    name="m3u8_analyzer",
    url='https://paulocesar-dev404.github.io/M3u8_Analyzer/',
    version="1.0.1",
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
