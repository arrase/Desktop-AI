from setuptools import setup, find_packages

setup(
    name="taskagent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6",
    ],
    entry_points={
        "console_scripts": [
            "taskagent = task_agent.main:main",
        ]
    },
)
