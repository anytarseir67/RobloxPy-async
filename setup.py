from setuptools import setup
import pathlib
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

setup(name='robloxpy-async',
    version='1.0.0.a1',
    description='robloxpy-async is an async/await object oriented roblox API wrapper for python',
    long_description=README,
    long_description_content_type="text/markdown",
    author='anytarseir67 & KristanSmout',
    author_email = '',
    url='https://github.com/anytarseir67/RobloxPy-async',
    license="GPLv3",
    packages=['robloxpy_async'],
    install_requires=requirements,
    )