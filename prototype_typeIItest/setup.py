from setuptools import setup, find_packages

setup(
    name="problem2",
    version="1.0",
    packages=find_packages(include=["src", "specs", "src.*"])
)

# to install run: pip install -e .