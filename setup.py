
from setuptools import setup


setup(
    name = 'pyepuck',
    version = '1.0.0',
    description = 'Python library and utilities for e-puck robot',
    url = 'https://github.com/Vykstorm/pyepuck',
    author = 'Vykstorm',
    author_email = 'victorruizgomezdev@gmail.com',
    license = 'MIT',
    zip_safe = False,
    packages = [''],
    install_requires = ['numpy', 'Pillow', 'PyBluez'],
    include_package_data = True
)