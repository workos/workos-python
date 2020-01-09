import os
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, "workos", "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about['__package_name__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__package_url__'],
    description=about['__description__'],
    packages=find_packages(exclude=['tests*', ]),
    zip_safe=False,
    license=about['__license__'],
    install_requires=["requests>=2.22.0"],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)