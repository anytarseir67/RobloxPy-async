from setuptools import setup

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

setup(name='robloxpy-async',
    version='1.0.0.a1',
    description='robloxpy-async is an async/await object oriented roblox API wrapper for python',
    author='anytarseir67 & KristanSmout',
    author_email = '',
    url='https://github.com/anytarseir67/RobloxPy-async',
    packages=['robloxpy_async'],
    install_requires=requirements,
    )