from setuptools import setup, find_packages

setup(
    name="constellation_schedular",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["skyfield", "numpy", "fastapi", "pyyaml"],
    entry_points={
        "console_scripts": [
            "constellation-schedular=constellation_schedular.cli:main"
        ]
    },
)