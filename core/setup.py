from setuptools import setup, find_packages

setup(
    name="icbm_game",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "open_spiel",
    ],
    package_data={
        "icbm_game": ["*.csv"],  # Include CSV files in the package
    },
    # Development dependencies
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
    },
)
