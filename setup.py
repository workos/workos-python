import os
import sys
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

with open("README.md", "r") as f:
    long_description = f.read()

about = {}
with open(os.path.join(base_dir, "workos", "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about["__package_name__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__package_url__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(
        exclude=[
            "tests*",
        ]
    ),
    zip_safe=False,
    license=about["__license__"],
    install_requires=[
        "httpx>=0.27.0",
        "requests>=2.22.0",
        "pydantic==2.8.2",
        "types-requests==2.32.0.20240712",
    ],
    extras_require={
        "dev": [
            "flake8",
            "pytest==8.1.1",
            "pytest-asyncio==0.23.8",
            "pytest-cov==2.8.1",
            "six==1.13.0",
            "black==22.3.0",
            "twine==4.0.2",
            "requests==2.30.0",
            "urllib3==2.0.2",
            "mypy==1.10.1",
            "httpx>=0.27.0",
        ],
        ":python_version<'3.4'": ["enum34"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
