from setuptools import setup, find_packages

setup(
    name="email_classifier",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai>=1.3.0",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
)