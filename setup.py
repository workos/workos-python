import os
import sys
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

with open("README.md", "r") as f:
    long_description = f.read()

about = {}
with open(os.path.join(base_dir, "workos", "__about__.py")) as f:
    exec(f.read(), about)

dev_requirements = [
    "flake8",
    "pytest==4.6.9",
    "pytest-cov==2.8.1",
    "six==1.13.0",
]
if sys.version_info.major == 3:
    dev_requirements.extend(
        ["black==19.10b0", "twine==3.1.1",]
    )

setup(
    name=about["__package_name__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__package_url__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*",]),
    zip_safe=False,
    license=about["__license__"],
    install_requires=["requests>=2.22.0"],
    extras_require={"dev": dev_requirements, ":python_version<'3.4'": ["enum34"],},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
