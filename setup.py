import setuptools

import entomb


with open("README.rst", "r") as f:
    LONG_DESCRIPTION = f.read()

NAME = entomb.__title__.lower()

setuptools.setup(
    name=NAME,
    version=entomb.__version__,
    description=entomb.__description__,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    author=entomb.__author__,
    author_email=entomb.__author_email__,
    license=entomb.__licence__,
    url=entomb.__url__,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
    keywords="immutable",
    python_requires=">=3.5",
    entry_points={
        "console_scripts": [
            "{}=entomb.core:run".format(NAME),
        ],
    },
)
