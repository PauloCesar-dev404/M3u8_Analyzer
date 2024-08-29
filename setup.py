from setuptools import setup, find_packages

# Lê o conteúdo do README.md
with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

# Lê o conteúdo do CHANGELOG.md
with open('CHANGELOG.md', 'r', encoding='utf-8') as file:
    changelog = file.read()

# Concatena o CHANGELOG.md ao README.md
long_description += "\n\n# CHANGELOG\n\n" + changelog

setup(
    name="m3u8-analyzer",
    version="1.0.3.7",
    description="Análise de dados de HLS m3u8",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PauloCesar0073-dev404",
    author_email="paulocesar0073dev404@gmail.com",
    url='https://paulocesar-dev404.github.io/M3u8_Analyzer/',
    license="MIT",
    keywords=["hls", "m3u8", "m3u8_analyzer", "M3u8Analyzer"],
    packages=find_packages(),
    include_package_data=True,
    platforms=["any"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)
