from setuptools import setup, find_packages

setup(
    name="cookinumnetwork",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6",
        # Add other dependencies from requirements.txt as needed
    ],
    python_requires=">=3.6",
)
