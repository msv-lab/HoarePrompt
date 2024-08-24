from setuptools import setup, find_packages

setup(
    name='HoarePrompt',
    version='0.1.0',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openai",
        "tenacity",
        "astor",
        "groq",
    ],
    description='A library for HoarePrompt',
)
