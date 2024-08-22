from setuptools import setup
import pathlib

# Lê o conteúdo do README.md
long_description = (pathlib.Path(__file__).parent / "README.md").read_text(encoding='utf-8')

setup(
    name="m3u8_analyzer",
    url='https://paulocesar-dev404.github.io/M3u8_Analyzer/',
    version="1.0.0",
    license="MIT",
    author="PauloCesar0073-dev404",
    author_email="paulocesar0073dev404@gmail.com",
    description="Análise de dados de HLS m3u8",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["hls", "m3u8"],
    packages=["m3u8_analyzer"],
    install_requires=['cryptography', 'requests'],
    include_package_data=True,  # Inclui dados adicionais do pacote, como README.md
)
