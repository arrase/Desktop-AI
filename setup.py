from setuptools import setup, find_packages

setup(
    name="desktop-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6",
        "openai-agents"
    ],
    entry_points={
        "console_scripts": [
            "desktop-ai = desktop_ai.main:main",
        ]
    },
)
