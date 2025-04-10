from setuptools import setup, find_packages

setup(
    name="banking_app",
    version="0.1",
    packages=find_packages(),
    package_dir={
        '': '.',  # Important for non-standard structure
    },
)