import os
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

with open("README.md", "r") as f:
    long_description = f.read()

about = {}
with open(os.path.join(base_dir, "workos", "__about__.py")) as f:
    exec(f.read(), about)


def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name=about["__package_name__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__package_url__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={"workos": ["py.typed"]},
    packages=find_packages(
        exclude=[
            "tests*",
        ]
    ),
    zip_safe=False,
    license=about["__license__"],
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
