from setuptools import setup, find_packages

setup(
    name="jules_task",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6",
    ],
    entry_points={
        "console_scripts": [
            "jules-task = jules_task.main:main",
        ]
    },
)
