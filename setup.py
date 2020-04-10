import setuptools
from setuptools import setup

setup(
    name = 'cord19utils',
    version = '0.1',
    description = 'Python tools and scripts for processing CORD19 Kaggle Challenge data',
    url = 'https://github.com/ReReMLclub/cord19utils',
    author = 'Leland Barnard',
    author_email = 'leland.barnard@gmail.com',
    packages = setuptools.find_packages(),
    install_requires=[
        "networkx",
        "holoviews >= 1.13.0",
        "pandas",
        "numpy",
        "gensim",
        "nltk"
    ],
    zip_safe = False
)